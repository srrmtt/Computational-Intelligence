from functools import cache
from nim import Nim
from math import inf
from copy import deepcopy


def possible_actions(nim: Nim):
    """
    Return the possible actions from a state, trying to remove the max quantity of element first.

    """
    for i, r in enumerate(nim._rows):
        _max = r if nim._k == None else nim._k
        for e in range(_max, 0, -1):
            if r >= e:

                ret = deepcopy(nim)
                ret.niming(i, e)
                #print(f"{ret._rows} from move: ({i}, {e})")
                yield ret, (i, e)
            else:
                break


class MinMaxAgent:
    def __init__(self):
        """
        Instanciate the minmax cache.
        """
        self._cache = dict()

    @cache
    def minmax(self, state: Nim, max_player=True, alpha=-1, beta=1, max_depth=None):
        """
        A cached recursive method that simulate the minmax algorithm for the nim game.
        @params
            - state: a nim game stage
            - max_player: bool, maximizing fase if true
            - alpha: current alpha for the node parent
            - beta: current beta for the node parent
        @return
            - a tuple with the best move to play according to the algorithm (row, k)

        """
        # contains all the moves to reach the final state
        current_depth = 0

        # terminal leaf
        if state.is_finished() or max_depth == 0:
            state.winner = -1 if max_player else 1
            return state.winner, None

        # if the state has already been visited return the cached value
        if (tuple(state._rows), max_player) in self._cache:
            return self._cache[(tuple((state._rows)), max_player)]

        if max_player:
            # print("maximizing")
            best = -inf
            # iterate over possible actions
            for child, move in possible_actions(state):
                # recur with the selected move
                max_depth = max_depth -1 if max_depth else None
                value, best_move = self.minmax(
                    child, False, alpha, beta, max_depth)
                # print(f"{moves}")
                if value > best:
                    best_move = move
                # update best and alphaS
                best = max(best, value)
                alpha = max(alpha, best)
                # pruning
                if beta <= alpha:
                    break
            self._cache[(tuple((state._rows)),
                            max_player)] = value, best_move
            return best, best_move
        else:
            best = +inf
            for child, move in possible_actions(state):
                max_depth = max_depth -1 if max_depth else None
                value, best_move = self.minmax(
                    child, True, alpha, beta, max_depth)
                if value < best:
                    best_move = move
                # update best and beta
                best = min(best, value)
                beta = min(beta, best)

                if beta <= alpha:
                    break
            self._cache[(tuple((state._rows)),
                            max_player)] = value, best_move
            return best, best_move
    def next_move(self, nim: Nim):
       return self.minmax(nim)[1]