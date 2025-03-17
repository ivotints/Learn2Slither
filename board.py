import numpy as np
import random

#    0 1 2 3 4 5 6 7 8 9
#    _ _ _ _ _ _ _ _ _ _
# 0 |. . . . . H S S . .|
# 1 |. . . . . . . . . .|
# 2 |. . . . . . . . . .|
# 3 |. . . A . . . . . .|
# 4 |. . . . . . . . . .|
# 5 |. . . . . . . . . .|
# 6 |. . . . . . A . . .|
# 7 |. . . . . . . . . .|
# 8 |. . . P . . . . . .|
# 9 |. . . . . . . . . .|
#    ‾ ‾ ‾ ‾ ‾ ‾ ‾ ‾ ‾ ‾

class init_board:
    EMPTY = 0
    TAIL = 1
    HEAD = 2
    APPLE = 3
    PEPPER = 4

    def __init__(self):
        self.size_y = 10  # number of vertical cells
        self.size_x = 10  # number of horisontal cells

        # fill the array (table) with EMPTY
        self.table = np.full(
            (self.size_y, self.size_x),
            self.EMPTY, dtype='int8')

        # set head to random place
        self.head_y, self.head_x = self.set_cell_to_random_empty(self.HEAD)

        # now I need to set first segment of tail for snake
        # lets count amount of empty cells around snake and get a list of empty coordinates

        empty_cells = []
        directions = {(0, -1), (-1, 0), (0, 1), (1, 0)}
        for dir in directions:
            new_y = self.head_y + dir[0]
            new_x = self.head_x + dir[1]
            if self.is_in_table(new_y, new_x) and self.is_empty(new_y, new_x):
                empty_cells.append((new_y, new_x))
        self.initial_direction = random.randint(0, len(empty_cells) - 1)
        tail_y, tail_x = empty_cells[self.initial_direction]
        self.set_cell(tail_y, tail_x, self.TAIL)
        self.second_tail_y = tail_y
        self.second_tail_x = tail_x

        # now set second tail segment

        empty_cells = []
        for dir in directions:
            new_y = tail_y + dir[0]
            new_x = tail_x + dir[1]
            if self.is_in_table(new_y, new_x) and self.is_empty(new_y, new_x):
                empty_cells.append((new_y, new_x))
        tail_y, tail_x = empty_cells[random.randint(0, len(empty_cells) - 1)]
        self.set_cell(tail_y, tail_x, self.TAIL)

        # to remember the tail position:
        self.tail_y = tail_y
        self.tail_x = tail_x

        # now we have our snake set.

        # lets set the food and pepper

        self.set_cell_to_random_empty(self.APPLE)
        self.set_cell_to_random_empty(self.APPLE)
        self.set_cell_to_random_empty(self.PEPPER)







    def is_in_table(self, y, x):
        if (x < 0 or x >= self.size_x or y < 0 or y >= self.size_y):
            return False
        return True

    def is_empty(self, y, x):
        if self.table[y][x] == self.EMPTY:
            return True
        return False

    def set_to_empty(self, y, x, value):
        """Will set only if that coordinate is empty

        ## Parameters
            y (int): row
            x (int): column
            value (int): Value to set in the cell

        ## Returns
            bool: True for success, False for fail
        """
        if (x < 0 or x >= self.size_x or y < 0 or y >= self.size_y):
            return False
        if (self.table[y][x] != self.EMPTY):
            return False
        self.table[y][x] = value
        return True

    def set_cell(self, y, x, value):
        if (x < 0 or x >= self.size_x or y < 0 or y >= self.size_y):
            return False
        self.table[y][x] = value
        return True

    def get_cell(self, y, x):
        if (x < 0 or x >= self.size_x or y < 0 or y >= self.size_y):
            return None
        return self.table[y][x]

    def set_cell_to_random_empty(self, value):
        """Set value to a random empty cell and return its coordinates.

        ## Parameters
            value (int): Value to set in the random empty cell

        ## Returns
            tuple: (y, x) coordinates of the set cell

        ## Raises
            RuntimeError: If no empty cell could be found.
        """
        y = 0
        x = 0
        i = 0
        while i < 100:
            y = random.randint(0, self.size_y - 1)
            x = random.randint(0, self.size_x - 1)
            if self.set_to_empty(y, x, value):
                return (y, x)
            i += 1

        # if we here mean that we are so unlucky to find random empty cell, I will have to assign first empty cell for that
        for y in range(self.size_y):
            for x in range(self.size_x):
                if self.set_to_empty(y, x, value):
                    return (y, x)
        raise RuntimeError("No empty cells found in the board")

