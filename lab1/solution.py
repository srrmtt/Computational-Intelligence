import random
import logging
import itertools
from queue import PriorityQueue

logging.basicConfig(format="%(message)s", level=logging.INFO)
def problem(N, seed=None):
    random.seed(seed)
    return [
        list(set(random.randint(0, N - 1) for n in range(random.randint(N // 5, N // 2))))
        for n in range(random.randint(N, N * 5))
    ]

def remove_duplicates(P):
    set_list = []
    for p in P:
        if p not in set_list and len(p) != 0:
            set_list.append(p)
    return set_list


def goal_test(state):
    return set(itertools.chain(*state)) == set(range(0,N))

def possible_actions(state, P):
    return (tuple(p) for p in P if tuple(p) not in state)

def path_cost(state):
    return sum(len(p) for p in state)

def priority_function(state):
    pass
def search(P : list, 
           goal_test,
           path_cost,
           priority_function ):
    
    frontier = PriorityQueue()
    explored_nodes = 0
    state = list()
    cost = dict()
    while state is not None and not goal_test(state): 
        explored_nodes+=1
        
        for action in possible_actions(state, P):
            
            new_state = tuple([*state, action])
            
            #logging.info(f"found state: [new_state],:")    
            if new_state not in cost and new_state not in frontier.queue:
                #logging.info(f"\t\t-- Added to the frontier")
                cost[new_state] = path_cost(new_state)     
                #logging.info(f"\t\t-- with cost: {cost[new_state]}")
                frontier.put(( path_cost(new_state) , new_state ))
            elif new_state in frontier.queue and cost[new_state] > path_cost(new_state):
                cost[new_state] = path_cost(new_state)
                #logging.info(f"\t\t-- updated cost: {cost[new_state]}")
        state = frontier.get()[1]
    
    logging.info(f"visited {explored_nodes} nodes.")
    return state, cost[state]
N = 6
P = problem(N, seed=42)
# P = [[1, 2],
#  [2, 3, 4, 5],
#  [6, 7, 8, 9, 10, 11, 12, 13],
#  [1, 3, 5, 7, 9, 11, 13],
#  [2, 4, 6, 8, 10, 12, 13]]
P = remove_duplicates(P)
logging.info(f"P set: {P}.")
search(P, goal_test, path_cost, priority_function)

