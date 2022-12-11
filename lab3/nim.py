from functools import reduce
import logging

class Nim:
    def __init__(self, num_rows: int, k: int = None) -> None:
        self._rows = [i * 2 + 1 for i in range(num_rows)]
        self._k = k
        self.safe = self.evaluate()
        self.winner = None
        self.player = 0
    
    
    def niming(self, row: int, num_objects: int) -> None:
        assert self._rows[row] >= num_objects
        if self._k:
            #print(f"k:{self._k},num_obj:{num_objects}")
            assert num_objects <= self._k
        self._rows[row] -= num_objects
        self.switch_player()

        # Check for a winner
        if all(pile == 0 for pile in self._rows):
            self.winner = self.player

    def evaluate(self) -> bool:
        safe = reduce((lambda x,y: x ^ y), self._rows)
        self._safe = safe == 0
        return self._safe
    
    def is_finished(self) -> bool:
        return all(map(lambda x: x == 0, self._rows))
    
    def __hash__(self):
        return tuple(self._rows).__hash__()
    
    def __eq__(self, o):
        return self._rows == o._rows
    def get_count_non_zero_rows(self):
        #count the number of rows != 0
        return len(self._rows) - [n == 0 for n in self._rows].count(True)
    
    def possible_actions(self):
        actions = []
        for i,row in enumerate(self._rows):
            for k in range(1,row+1):
                actions.append((i,k))
        return actions

    @classmethod
    def other_player(cls, player):
        """
        Nim.other_player(player) returns the player that is not
        `player`. Assumes `player` is either 0 or 1.
        """
        return 0 if player == 1 else 1
    
    def switch_player(self):
        """
        Switch the current player to the other player.
        """
        self.player = Nim.other_player(self.player)

    @classmethod
    def available_actions(cls, piles):
        """
        Nim.available_actions(piles) takes a `piles` list as input
        and returns all of the available actions `(i, j)` in that state.

        Action `(i, j)` represents the action of removing `j` items
        from pile `i` (where piles are 0-indexed).
        """
        actions = set()
        for i, pile in enumerate(piles):
            for j in range(1, pile + 1):
                actions.add((i, j))
        return actions