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
    DIRECTIONS = {(0, -1), (-1, 0), (0, 1), (1, 0)}  #LEFT, UP, RIGHT, DOWN

    def __init__(self):
        self.size_y = 10
        self.size_x = 10
        self.table = np.full((self.size_y, self.size_x),self.EMPTY, dtype='int8')
        self.head_y = 0
        self.head_x = 0
        self.tail_y = 0
        self.tail_x = 0

        self._init_snake()

        self.set_cell_to_random_empty(self.APPLE)
        self.set_cell_to_random_empty(self.APPLE)
        self.set_cell_to_random_empty(self.PEPPER)

    def _place_adjacent_segment(self, y, x):
        """Find and return coordinates for a new segment adjacent to given position"""
        empty_cells = []
        for dir_y, dir_x in self.DIRECTIONS:
            new_y = y + dir_y
            new_x = x + dir_x
            if self.is_in_table(new_y, new_x) and self.is_empty(new_y, new_x):
                empty_cells.append((new_y, new_x))

        if not empty_cells:
            raise RuntimeError("No empty adjacent cells found")

        if (y, x) == (self.head_y, self.head_x):
            tmp = random.randint(0, len(empty_cells) - 1)
            a, b = empty_cells[tmp]
            self.initial_direction = a - y, b - x
            return empty_cells[tmp]

        return empty_cells[random.randint(0, len(empty_cells) - 1)]


    def _init_snake(self):
        """Initialize snake with head and two tail segments"""
        self.head_y, self.head_x = self.set_cell_to_random_empty(self.HEAD)

        self.second_tail_y, self.second_tail_x = self._place_adjacent_segment(
            self.head_y, self.head_x)
        self.set_cell(self.second_tail_y, self.second_tail_x, self.TAIL)

        self.tail_y, self.tail_x = self._place_adjacent_segment(
            self.second_tail_y, self.second_tail_x)
        self.set_cell(self.tail_y, self.tail_x, self.TAIL)


    def is_in_table(self, y, x):
        if (x < 0 or x >= self.size_x or y < 0 or y >= self.size_y):
            return False
        return True

    def is_empty(self, y, x):
        if self.table[y][x] == self.EMPTY:
            return True
        return False

    def set_to_empty(self, y, x, value):
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

