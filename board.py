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
    DIRECTIONS = [(0, -1), (-1, 0), (0, 1), (1, 0)]  #LEFT, UP, RIGHT, DOWN

    def __init__(self):
        self.size_y = 10
        self.size_x = 10
        self.table = np.full((self.size_y, self.size_x),self.EMPTY, dtype='int8')
        self.head_y = 0
        self.head_x = 0
        self.tail_y = 0
        self.tail_x = 0
        self.moving_dir = (0, -1)
        self.length = 3
        self.snake_segments = [] # whole snake will be stored here from tail to head in tuple (y, x)

        self._init_snake()
        self.apple_1 = self.set_cell_to_random_empty(self.APPLE)
        self.apple_2 = self.set_cell_to_random_empty(self.APPLE)
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
            self.moving_dir = y - a, x - b
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

        self.snake_segments.append((self.tail_y, self.tail_x))
        self.snake_segments.append((self.second_tail_y, self.second_tail_x))
        self.snake_segments.append((self.head_y, self.head_x))


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

    def make_move(self, dir):
        new_y = dir[0] + self.head_y
        new_x = dir[1] + self.head_x
        if not self.is_in_table(new_y, new_x):
            # print("death from wall")
            return True
        cell = self.get_cell(new_y, new_x)
        if cell == self.TAIL:
            if not (new_y == self.tail_y and new_x == self.tail_x) or self.length == 2:
                # print("death from canibalism")
                return True
            else:
                self.snake_segments.append((new_y, new_x))
                self.set_cell(self.head_y, self.head_x, self.TAIL)

                self.set_cell(self.tail_y, self.tail_x, self.EMPTY)
                self.snake_segments = self.snake_segments[1:]
                self.tail_y, self.tail_x = self.snake_segments[0]

                self.head_y = new_y
                self.head_x = new_x
                self.set_cell(new_y, new_x, self.HEAD)
                self.moving_dir = dir

        elif cell == self.APPLE:
            self.length += 1
            self.snake_segments.append((new_y, new_x))
            self.set_cell(self.head_y, self.head_x, self.TAIL)
            self.head_y = new_y
            self.head_x = new_x
            self.set_cell(new_y, new_x, self.HEAD)
            self.moving_dir = dir

            if self.apple_1 == (new_y, new_x):
                self.apple_1 = self.set_cell_to_random_empty(self.APPLE)
            else:
                self.apple_2 = self.set_cell_to_random_empty(self.APPLE)

        elif cell == self.PEPPER:
            self.length -= 1
            if self.length < 1:
                # print("death from PEPPER")
                return True
            self.snake_segments.append((new_y, new_x))

            tmp_y, tmp_x = self.snake_segments[0]
            self.set_cell(tmp_y, tmp_x, self.EMPTY)
            self.snake_segments = self.snake_segments[1:]
            tmp_y, tmp_x = self.snake_segments[0]
            self.set_cell(tmp_y, tmp_x, self.EMPTY)
            self.snake_segments = self.snake_segments[1:]
            self.tail_y, self.tail_x = self.snake_segments[0]


            if (self.length > 1):
                self.set_cell(self.head_y, self.head_x, self.TAIL)
            self.head_y = new_y
            self.head_x = new_x
            self.set_cell(new_y, new_x, self.HEAD)
            self.moving_dir = dir
            self.set_cell_to_random_empty(self.PEPPER)

        elif cell == self.EMPTY:
            self.snake_segments.append((new_y, new_x))
            self.set_cell(self.head_y, self.head_x, self.TAIL)

            self.set_cell(self.tail_y, self.tail_x, self.EMPTY)
            self.snake_segments = self.snake_segments[1:]
            self.tail_y, self.tail_x = self.snake_segments[0]

            self.head_y = new_y
            self.head_x = new_x
            self.set_cell(new_y, new_x, self.HEAD)
            self.moving_dir = dir
        return False
