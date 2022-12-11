import numpy
from nim import Nim
from functools import reduce
from expert_strategy import System, ExpertSystem
from minmax import MinMaxAgent
import random
from utility import run_benchmark
import pickle


class RLAgent(object):
    def __init__(self, states, alpha=0.15, random_factor=0.2):  # 80% explore, 20% exploit
        self.state_history = [(tuple(states),0)]  # state, reward
        self.alpha = alpha
        self.random_factor = random_factor
        self.G = {}
        self.init_reward(states,0)

    def init_reward(self,nim_rows,row):
        if row>=len(nim_rows):
            return
        for k in range(0,nim_rows[row]+1):
            new_state = nim_rows[:row] + [nim_rows[row] - k] + nim_rows[row+1:]
            #print(new_state)
            self.G[tuple(new_state)] = numpy.random.uniform(low=1.0, high=0.1)
            self.init_reward(new_state,row+1)
    def get_reward(self,state):
        return self.G[state]

    def choose_action(self, state): 
        maxG = -10e15
        next_move = None
        randomN = numpy.random.random()
        if randomN < self.random_factor:
            # if random number below random factor, choose random action
            next_move = System.random_move(state)
        else:
            # if exploiting, gather all possible actions and choose one with the highest G (reward)
            for (row,k) in state.possible_actions():
                #new_state = tuple([sum(x) for x in zip(state, ACTIONS[action])])
                new_state = state._rows[:row] + [state._rows[row] - k] + state._rows[row+1:]
                if self.G[tuple(new_state)] >= maxG:
                    next_move = (row,k)
                    maxG = self.G[tuple(new_state)]

        return next_move

    def update_state_history(self, state, reward):
        #print(f"update state history: state: {state} reward: {reward}")
        self.state_history.append((tuple(state), reward))

    def learn(self):
        target = 0
        #print(f"learn: {self.state_history}")
        for prev, reward in reversed(self.state_history):
            #print(prev,reward)
            prev = tuple(prev)
            self.G[prev] = self.G[prev] + self.alpha * (target - self.G[prev])
            target += reward

        self.state_history = []
        
        self.random_factor -= 10e-5  # decrease random factor each episode of play
    
    def train(self, nim_dim: int ,n_rounds: int = 10_000, show_epoch_results: bool = False):
        """
        This method trains the RL agent using different agents: the first 1000 iterations it plays against
        the worst possible player, and then it play against stronger opponent (random move, min max agent and expert system).
        """
        def make_player(strategy,robot = None):
            def player(nim:Nim):
                if robot:
                    row,k = strategy(nim,robot)
                else:
                    row,k = strategy(nim)
                nim.niming(row,k)
            return player


        for i in range(n_rounds):
            if i == 0:
                self.random_factor = 0.3
                print(f"play against worst player")
                opponent_move = System.worst_move
            elif i == 2000:
                self.random_factor = 0.3
                print(f"play against random player")
                opponent_move = System.random_move
            elif i == 3000:
                self.random_factor = 0.3
                print(f"play against robot player")
                opponent_move = self.choose_action
            elif i == 6000:
                self.random_factor = 0.3
                print(f"play against minmax player")
                minmax = MinMaxAgent()
                opponent_move = minmax.next_move
            elif i == 9000:
                self.random_factor = 0.1
                print(f"play against expert player")
                opponent_move = ExpertSystem.next_move

            turn = random.randint(0,1)
            nim = Nim(nim_dim)
            #print(nim._rows)
            #print(turn)
            while not nim.is_finished():
                if turn:
                    row,k = self.choose_action(nim)
                    #print(f"robot move: row:{row} k:{k}")
                    nim.niming(row,k)
                    reward = 0
                    if nim.is_finished():
                        reward -= 1
                    else:
                        n_one = nim._rows.count(1)
                        n_zero = nim._rows.count(0)
                        if nim.evaluate():
                            reward -= 3
                            #if the state is like 2,2,0,0 or 1,1,0,0 add a reward
                            if len(nim._rows) - n_zero == 2:
                                if nim._rows.count(max(nim._rows)) == 2:
                                    reward -= 3
                        else:
                            #if the state is not safe, subtruact a reward and the same if the state is like 1,2,0,0 or 3,0,4,0
                            reward += 1
                            if len(nim._rows) - n_zero == 2:
                                if nim._rows.count(max(nim._rows)) != 2:
                                    reward += 1
                        if len(nim._rows) - n_zero == 1:
                            reward +=0.2

                    self.update_state_history(nim._rows, reward)
                else:
                    row, k  = opponent_move(nim)
                    nim.niming(row, k)
                    
                    self.update_state_history(nim._rows, 0)
                turn = not turn
            #print(f"G before learn: {robot.G}")
            self.learn()  # robot should learn after every episode
            #print(f"G after learn: {robot.G}")
            if i % 1000 == 0 and show_epoch_results:
                old_random_factor = self.random_factor
                wr = run_benchmark(10000,nim_dim,self.choose_action,opponent_move)
                print(f"win rate: {wr}")
                self.random_factor = old_random_factor
    def dump(self, path):
        """
        Serialize the object in the path file. Opposite action: EvolvedRulesAgent.load(path)
        """
        f_out = open(path, 'wb')
        pickle.dump(self, f_out)
        f_out.close()

    @classmethod
    def from_file(cls, path):
        """
        Factory method that deserializes the object contained in the path file.
        @return
            - EvolvedRulesAgent: the agent that was previously serialized.
        """
        with open(path, 'rb') as f_in:
            return pickle.load(f_in)