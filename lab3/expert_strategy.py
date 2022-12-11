from nim import Nim
from utility import *
import random
from math import inf

class System:
    @classmethod
    def random_move(cls, nim:Nim):
        #select a random valid row (!= 0) and select a random number of element to remove
        rand_row = random.randint(0,len(nim._rows)-1)
        while nim._rows[rand_row] == 0:
            rand_row = random.randint(0,len(nim._rows)-1)
        #if the nim is without k the limit is the value of the row
        k = nim._k if nim._k else nim._rows[rand_row]
        if k < nim._rows[rand_row]:
            rand_numObj = random.randint(1,k)
        else:
            rand_numObj = random.randint(1,nim._rows[rand_row])
        return rand_row,rand_numObj
    
    @classmethod
    def worst_move(cls, nim:Nim):
        n_one = nim._rows.count(1)
        n_zero = nim._rows.count(0)
        if len(nim._rows) - n_zero - n_one == 1:
            e = max(nim._rows)
            if n_one % 2 == 0:
                if e > 1:
                    return nim._rows.index(e), e - 1
            else:
                return nim._rows.index(e), e

        for row,k in nim.possible_actions():
            new_state = nim._rows[:row] + [nim._rows[row] - k] + nim._rows[row+1:]
            if nim_sum(new_state):
                    return row,k
        return System.random_move(nim)
    



class ExpertSystem(System):
    def subtractive_version(nim:Nim): 
        #invert_strategy = [n > 1 for n in nim._rows].count(True) == 1 and max(nim._rows) <= nim._k
        invert_strategy = False    
        mod_rows = [row % (nim._k+1) for row in nim._rows ]
        safe= nim_sum(mod_rows) == 0
        if all([n == 1 or n == 0 for n in nim._rows]):
            return super().random_move(nim)
        else:
            if invert_strategy:
                #not used anymore because now who take the last win
                #when the number of rows whith one remain element will be odd, remove n elements to have all rows with one
                max_elem = max(nim._rows)  
                if nim.get_count_non_zero_rows() % 2 == 0 :
                    return nim._rows.index(max_elem),max_elem-1
                else:
                    return nim._rows.index(max_elem),max_elem
            else:
                if safe:
                    #search for the best move to do, for witch the opponent can't bring us back to safe, if not found do a random move
                    for i,n in enumerate(nim._rows):
                        for k in range(1,nim._k+1):
                            if n<k:
                                continue
                            temp_nim = nim._rows[:]
                            temp_nim[i] -= k
                            if min_cost(temp_nim)[1] > nim._k:
                                #print("trovata")
                                return i,k
                    return super().random_move(nim)
                else:
                    #best move to do
                    return min_cost(mod_rows)
    @classmethod
    def next_move(cls, nim: Nim) -> (int, int):
        #expert system basted on nimsum
        if nim._k:
            return subtractive_version(nim)
        else:
            #if no k is used
            safe= nim_sum(nim._rows) == 0
            if all([n == 1 or n == 0 for n in nim._rows]):
                return super().random_move(nim)
            else:
                if safe:
                    return super().random_move(nim)
                else:
                    # comeback to safe
                    return min_cost(nim._rows)
