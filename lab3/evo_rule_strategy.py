from nim import Nim
from utility import generate_random_probabilities, play, run_benchmark
import random
from expert_strategy import System
from tqdm import tqdm
import pickle


def cook_status(nim: Nim):
    """
    This function takes a game of nim as parameter and learns some information from it.
    @param
        - nim: a stage of a nim game
    @return 
        - a list with some information of the game (max len, max take ...)  

    """
    # set of possible move with the different strategies
    cooked = []
    nim_without_zero = [e for e in nim._rows if e != 0]
    k = nim._k if nim._k else max(nim._rows)
    # longest_row_max_take
    cooked.append((nim._rows.index(max(nim._rows)), k if k <
                  max(nim._rows) else max(nim._rows)))
    # longest_row_min_take
    cooked.append((nim._rows.index(max(nim._rows)), 1))
    # shortest_row_min_take
    cooked.append((nim._rows.index(min(nim_without_zero)), 1))
    # leave one or remove max row
    if not nim._k:
        num_one_rows = nim._rows.count(1)
        cooked.append((nim._rows.index(max(nim._rows)), max(
            nim._rows) if num_one_rows % 2 == 0 else max(nim._rows)-1))
        # longest_row_rand_take
        cooked.append((nim._rows.index(max(nim._rows)),
                      random.randint(1, min(k, max(nim._rows)))))
        # shortest_row_rand_take
        k = nim._k if nim._k else min(nim_without_zero)
        cooked.append((nim._rows.index(min(nim_without_zero)),
                      random.randint(1, min(k, min(nim_without_zero)))))
        # shortest_row_max_take
        cooked.append((nim._rows.index(min(nim_without_zero)), k if k < min(
            nim_without_zero) else min(nim_without_zero)))
        # random_move
        cooked.append(System.random_move(nim))
        # print(cooked)
    return cooked


class EvolvedRulesAgent(System):
    def __init__(self, n_generations: int, nim_dim: int, num_iter: int, num_round: int, cook_status: int, pop_size: int = 30, q: float = 0.01, probs: list = None):
        self.num_generations = n_generations
        self.pop_size = pop_size
        self.nim_dim = nim_dim
        self.num_iter = num_iter
        self.num_round = num_round
        self.num_cook_status = cook_status
        self.q = q
        self.probabilities = []

    @classmethod
    def from_probabilities(cls, probabilities: list):
        """
        Build an agent from a vector of probabilities
        """
        return cls(0, 0, 0, 0, 0, 0, probabilities)

    def next_move(self, nim: Nim):
        """
        Select the move with highest probability and play it.
        """
        # select one strategy relying on the probabilities
        data = cook_status(nim)
        # if round(sum(probabilities),0)!= 1.0:
        #     print("Probabilità errate")
        #     return None
        random_number = random.random()
        prec_probability = 0.0
        for i, e in enumerate(self.probabilities):
            if random_number < prec_probability + e:
                # print(f"strategy selected {i}")
                return data[i]
            prec_probability += e
        return data[-1]

    def train(self):
        """
        Run an evolutionary algorithm with the parameters specified in the class constructor, at the end
        it returns a list of porobability for each cooked status.
        @return
         a list of porobability for each cooked status
        """
        def tournament(population, tournamen_size=2):
            # select the element with highest victory
            return population.index(max(random.choices(population, k=tournamen_size), key=lambda i: i[1]))
        # start with a random population
        # select two stategies and see whitch is the best and increment the victory count of that stategy
        # do it for self.num_round times
        # discard the worst
        # reset the victory counters
        # add new element to the population
        population = [(generate_random_probabilities(self.num_cook_status), 0)
                      for _ in range(self.pop_size)]
        for i in tqdm(range(self.num_generations)):
            
            for _ in range(self.num_round):
                index_p1 = tournament(population)
                index_p2 = tournament(population)
                nim = Nim(self.nim_dim)
                p1_strategy = EvolvedRulesAgent.from_probabilities(
                    population[index_p1][0])
                p2_strategy = EvolvedRulesAgent.from_probabilities(
                    population[index_p2][0])
                if run_benchmark(self.num_iter, self.nim_dim, p1_strategy.next_move, p2_strategy.next_move) > 50.0:
                    population[index_p1] = (
                        population[index_p1][0], population[index_p1][1] + 1)
                else:
                    population[index_p2] = (
                        population[index_p2][0], population[index_p2][1] + 1)
            population = sorted(population, key=lambda i: i[1], reverse=True)[
                :self.pop_size//2]
            population = [(e[0], 0) for _, e in enumerate(population)]
            population += [(generate_random_probabilities(self.num_cook_status), 0)
                           for _ in range(self.pop_size//2)]
        self.probabilities = population[0][0]
        return population[0][0]

    def train_with_rewards(self):
        """
        This method compute the probability of each move, it starts with all strategies 
        with the same probability and then select two strategies and makes them play one against the other
        who wins increment its strategy probability and decrement the strategy of the other one.
        @return 
            - a list of probabilities, assign the probabilities to self
        """

        def select_stategies():
            # choose two random strategies for the list
            p1_strategy = random.randint(0, self.num_cook_status-1)
            p2_strategy = random.randint(0, self.num_cook_status-1)
            while p2_strategy == p1_strategy:
                p2_strategy = random.randint(0, self.num_cook_status-1)
            return p1_strategy, p2_strategy

        probabilities = [
        1/self.num_cook_status for _ in range(self.num_cook_status)]
        for _ in tqdm(range(self.num_round)):
            prob1, prob2 = select_stategies()
            p1_strategy = EvolvedRulesAgent.from_probabilities(prob1)
            p2_strategy = EvolvedRulesAgent.from_probabilities(prob2)
            if run_benchmark(self.num_iter, self.nim_dim, p1_strategy.next_move, p2_strategy.next_move) > 50.0:
                if probabilities[prob1] + self.q < 1 and probabilities[prob2] - self.q >= 0:
                    probabilities[prob1] += self.q
                    probabilities[prob2] -= self.q
            else:
                if probabilities[prob2] + self.q < 1 and probabilities[prob1] - self.q >= 0:
                    probabilities[prob2] += self.q
                    probabilities[prob1] -= self.q
        self.probabilities = probabilities
        return probabilities

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



    
    
    
    
    
