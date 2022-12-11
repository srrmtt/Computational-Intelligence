import math
import random
import time
from expert_strategy import ExpertSystem,System
from nim import Nim
from utility import nim_sum
class NimAI():

    def __init__(self, alpha=0.5, epsilon=0.1):
        """
        Initialize AI with an empty Q-learning dictionary,
        an alpha (learning) rate, and an epsilon rate.

        The Q-learning dictionary maps `(state, action)`
        pairs to a Q-value (a number).
         - `state` is a tuple of remaining piles, e.g. (1, 1, 4, 4)
         - `action` is a tuple `(i, j)` for an action
        """
        self.q = dict()
        self.alpha = alpha
        self.epsilon = epsilon

    def update(self, old_state, action, new_state, reward):
        """
        Update Q-learning model, given an old state, an action taken
        in that state, a new resulting state, and the reward received
        from taking that action.
        """
        old = self.get_q_value(old_state, action)
        best_future = self.best_future_reward(new_state)
        self.update_q_value(old_state, action, old, reward, best_future)

    def get_q_value(self, state, action):
        """
        Return the Q-value for the state `state` and the action `action`.
        If no Q-value exists yet in `self.q`, return 0.
        """
        return self.q.setdefault((tuple(state), action), 0)

    def update_q_value(self, state, action, old_q, reward, future_rewards):
        """
        Update the Q-value for the state `state` and the action `action`
        given the previous Q-value `old_q`, a current reward `reward`,
        and an estiamte of future rewards `future_rewards`.

        Use the formula:

        Q(s, a) <- old value estimate
                   + alpha * (new value estimate - old value estimate)

        where `old value estimate` is the previous Q-value,
        `alpha` is the learning rate, and `new value estimate`
        is the sum of the current reward and estimated future rewards.
        """
        
        q_value = old_q + self.alpha * (reward + future_rewards - old_q)
        self.q[(tuple(state), action)] = q_value

    def best_future_reward(self, state):
        """
        Given a state `state`, consider all possible `(state, action)`
        pairs available in that state and return the maximum of all
        of their Q-values.

        Use 0 as the Q-value if a `(state, action)` pair has no
        Q-value in `self.q`. If there are no available actions in
        `state`, return 0.
        """
        q_values = [0]
        for action in Nim.available_actions(state):
            q_val = self.q.setdefault((tuple(state), action), 0)
            q_values.append(q_val)
        return max(q_values)


    def choose_action(self, state, epsilon=True):
        """
        Given a state `state`, return an action `(i, j)` to take.

        If `epsilon` is `False`, then return the best action
        available in the state (the one with the highest Q-value,
        using 0 for pairs that have no Q-values).

        If `epsilon` is `True`, then with probability
        `self.epsilon` choose a random available action,
        otherwise choose the best action available.

        If multiple actions have the same Q-value, any of those
        options is an acceptable return value.
        """
        best_q = None
        best_a = None
        actions = Nim.available_actions(state)
        for action in actions:
            if best_q == None:
                best_a = action
                continue
            q = self.q.setdefault((tuple(state),action), 0)
            if q > best_q:
                best_a = action
                best_q = q
        
        if epsilon:
            if random.random() <= self.epsilon:
                return random.choice(list(actions))
        return best_a





def train(n_iter: int, board_dim: int, alpha: float, espilon: float):
    """
    Train an AI by playing `n` games against itself, against a random system and in the end against 
    an expert system.
    """

    player = NimAI(alpha=alpha, epsilon=espilon)

    # Play n games
    for i in range(n_iter):
        # print(f"Playing training game {i + 1}")
        game = Nim(board_dim)

        # Keep track of last move made by either player
        last = {
            0: {"state": None, "action": None},
            1: {"state": None, "action": None}
        }

        # Game loop
        while True:

            # Keep track of current state and action
            state = game._rows.copy()
            if game.player == 0:
                if i < int(n_iter / 3):
                    action = System().random_move(game)
                elif i < int(n_iter / (2/3)):
                    action = player.choose_action(game._rows)
                else:
                    action = ExpertSystem().next_move(game)
            else:
                action = ExpertSystem().next_move(game)
            # Keep track of last state and action
            last[game.player]["state"] = state
            last[game.player]["action"] = action
            
            # Make move
            game.niming(*action)
            new_state = game._rows.copy()

            # When game is over, update Q values with rewards
            if game.winner is not None:
                player.update(state, action, new_state, 1)
                player.update(
                    last[game.player]["state"],
                    last[game.player]["action"],
                    new_state,
                    -1
                )
                break

            # If game is continuing, no rewards yet
            elif last[game.player]["state"] is not None:
                reward = 0
                if nim_sum(game._rows) == 0:
                    reward = 0.3 if game.player == 0 else -0.3
                player.update(
                    last[game.player]["state"],
                    last[game.player]["action"],
                    new_state,
                    reward
                )    
            player.epsilon -= 1e-5
            player.alpha = 0.9 * player.alpha
    # Return the trained AI
    return player


def play(ai, human_player=None):
    """
    Play human game against the AI.
    `human_player` can be set to 0 or 1 to specify whether
    human player moves first or second.
    """

    # If no player order set, choose human's order randomly
    if human_player is None:
        human_player = random.randint(0, 1)

    # Create new game
    game = Nim()

    # Game loop
    while True:

        # Print contents of piles
        print()
        print("Piles:")
        for i, pile in enumerate(game._rows):
            print(f"Pile {i}: {pile}")
        print()

        # Compute available actions
        available_actions = Nim.available_actions(game._rows)
        time.sleep(1)

        # Let human make a move
        if game.player == human_player:
            print("Your Turn")
            while True:
                pile = int(input("Choose Pile: "))
                count = int(input("Choose Count: "))
                if (pile, count) in available_actions:
                    break
                print("Invalid move, try again.")

        # Have AI make a move
        else:
            print("AI's Turn")
            pile, count = ai.choose_action(game._rows, epsilon=False)
            print(f"AI chose to take {count} from pile {pile}.")

        # Make move
        game.move((pile, count))

        # Check for winner
        if game.winner is not None:
            print()
            print("GAME OVER")
            winner = "Human" if game.winner == human_player else "AI"
            print(f"Winner is {winner}")
            return
