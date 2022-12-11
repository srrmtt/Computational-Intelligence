from functools import reduce
from math import inf
import random
from typing import Callable
from nim import Nim

def run_benchmark(n_games: int, n: int,p1_strategy: Callable,p2_strategy: Callable, k: int=None):
    '''
    Run n_games nim games of size n with two player p1 and p2.
    @param
    - n_games: number of games
    - n: game size
    - p1_strategy, p2_strategy: strategy of player 1 and 2, it's a callable and must return a tuple indicating the row and how many items to remove
    - k: optional parameter, indicates the maximum number of items that can be removed
    @return
    winner ratio of strategy 1
    '''
    # play a n_games number of match and count the % of victory of the first strategy
    wins = 0
    for i in range(n_games):
        nim = Nim(n,k)
        wins += play(nim,p1_strategy,p2_strategy)
    
    return wins/n_games*100

def play(nim: Nim,p1_strategy: Callable,p2_strategy: Callable):
    '''
    Play a nim game with 2 players following p1_strategy and p2_strategy.
    @params
    - nim: Nim instance
    - p1_strategy, p2_strategy: strategy of player 1 and 2, it's a callable and must return a tuple indicating the row and how many items to remove 
    @return
    - 1 if strategy 1 won 0 otherwise
    '''
    #play a match and return the winner
    random.seed()
    turn = random.randint(0,1)
    while not nim.is_finished():
        if turn:
            row,k = p2_strategy(nim)
        else:
            row,k = p1_strategy(nim)
        turn = not turn
        nim.niming(row,k)
    return int(turn)


def nim_sum(rows: list):
    """
    Compute the nim sum on the rows list. 
    @return 
    minsum of the rows
    """
    return reduce((lambda x, y: x ^ y), rows)


def min_cost(arr):
    """
    Compute the quantity to remove and on which row in order to get in a state with min_sum equals to
    zero.
    @return
    a tuple with: distance from a zero min sum, row  
    """
    cost = inf
    elem = -1
    # calculate XOR sum of array
    XOR = 0
    for e in arr:
        XOR ^= e

    # find the min cost and element
    # corresponding
    r_cost = 0
    for i, e in enumerate(arr):
        new_cost = abs((XOR ^ e) - e)

        if (cost > new_cost):
            r_cost = ((XOR ^ e) - e)
            if ((XOR ^ e) - e) > 0:
                continue
            else:
                cost = (XOR ^ e) - e
                element = e
    return arr.index(element), -r_cost


def generate_random_probabilities(n: int):
    """
    Generate a random set of ptobabilities for the strategies
    @return
        - a list of probabilities of length n
    """
    prob = []
    max_range = 1.0
    for i in range(n):
        rand_num = random.uniform(0, max_range)
        max_range -= rand_num
        prob.append(rand_num)
    return prob
