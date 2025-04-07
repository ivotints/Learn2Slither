import numpy as np
import random

class init_board:
    EMPTY = 0
    TAIL = 1
    HEAD = 2
    APPLE = 3
    PEPPER = 4
    DIRECTIONS = [(0, -1), (-1, 0), (0, 1), (1, 0)]  #LEFT, UP, RIGHT, DOWN

    def __init__(self, map_height, map_width):
        self.size_y = map_height
        self.size_x = map_width
        self.table = np.full((self.size_y, self.size_x),self.EMPTY, dtype='int8')
        self.head_y = 0
        self.head_x = 0
        self.tail_y = 0
        self.tail_x = 0
        self.moving_dir = 0
        self.length = 3
        self.snake_segments = [] # whole snake will be stored here from tail to head in tuple (y, x)
        self.last_move_random = False


        self._init_snake()
        self.apple_1 = self.set_cell_to_random_empty(self.APPLE)
        self.apple_2 = self.set_cell_to_random_empty(self.APPLE)
        self.set_cell_to_random_empty(self.PEPPER)

    def reset(self):
        """Reset the board to initial state"""
        self.table = np.full((self.size_y, self.size_x), self.EMPTY, dtype='int8')
        self.head_y = 0
        self.head_x = 0
        self.tail_y = 0
        self.tail_x = 0
        self.moving_dir = 0
        self.length = 3
        self.snake_segments = []

        self._init_snake()

        # Place new food
        self.apple_1 = self.set_cell_to_random_empty(self.APPLE)
        self.apple_2 = self.set_cell_to_random_empty(self.APPLE)
        self.set_cell_to_random_empty(self.PEPPER)

        return self

    def _place_adjacent_segment(self, y, x):
        """Find and return coordinates for a new segment adjacent to given position"""
        empty_cells = []
        size_y = self.size_y
        size_x = self.size_x

        for dir_y, dir_x in self.DIRECTIONS:
            new_y = y + dir_y
            new_x = x + dir_x

            if (0 <= new_y < size_y and 0 <= new_x < size_x and
                    self.table[new_y][new_x] == self.EMPTY):

                if (y == self.head_y and x == self.head_x):
                    self.moving_dir = self.DIRECTIONS.index((y - new_y, x - new_x))
                    return (new_y, new_x)

                empty_cells.append((new_y, new_x))

        if not empty_cells:
            raise RuntimeError("No empty adjacent cells found")

        return empty_cells[random.randint(0, len(empty_cells) - 1)]

    def _init_snake(self):
        """Initialize snake with head and two tail segments"""
        self.head_y, self.head_x = self.set_cell_to_random_empty(self.HEAD)

        self.second_tail_y, self.second_tail_x = self._place_adjacent_segment(
            self.head_y, self.head_x)
        self.table[self.second_tail_y][self.second_tail_x] = self.TAIL

        self.tail_y, self.tail_x = self._place_adjacent_segment(
            self.second_tail_y, self.second_tail_x)
        self.table[self.tail_y][self.tail_x] = self.TAIL

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
        for _ in range(100):
            y = random.randint(0, self.size_y - 1)
            x = random.randint(0, self.size_x - 1)

            if 0 <= y < self.size_y and 0 <= x < self.size_x and self.table[y][x] == self.EMPTY:
                self.table[y][x] = value
                return (y, x)

        for y in range(self.size_y):
            for x in range(self.size_x):
                if self.table[y][x] == self.EMPTY:
                    self.table[y][x] = value
                    return (y, x)
        return None

    def make_move(self, action):
        dy = self.DIRECTIONS[action][0]
        dx = self.DIRECTIONS[action][1]

        new_y = dy + self.head_y
        new_x = dx + self.head_x
        if not (0 <= new_y < self.size_y and 0 <= new_x < self.size_x):
            # print("Death from wall")
            return True

        cell = self.table[new_y][new_x]
        if cell == self.TAIL:
            if not (new_y == self.tail_y and new_x == self.tail_x) or self.length == 2:
                # print("Death from canibalism")
                return True
            else:
                self.snake_segments.append((new_y, new_x))
                self.table[self.head_y][self.head_x] = self.TAIL

                self.table[self.tail_y][self.tail_x] = self.EMPTY
                self.snake_segments = self.snake_segments[1:]
                self.tail_y, self.tail_x = self.snake_segments[0]

                self.head_y = new_y
                self.head_x = new_x
                self.table[new_y][new_x] = self.HEAD

        elif cell == self.APPLE:
            self.length += 1
            self.snake_segments.append((new_y, new_x))
            self.table[self.head_y][self.head_x] = self.TAIL
            self.head_y = new_y
            self.head_x = new_x
            self.table[new_y][new_x] = self.HEAD

            if self.apple_1 == (new_y, new_x):
                self.apple_1 = self.set_cell_to_random_empty(self.APPLE)
            else:
                self.apple_2 = self.set_cell_to_random_empty(self.APPLE)

        elif cell == self.PEPPER:
            self.length -= 1
            if self.length < 1:
                # print("Death from PEPPER")
                return True
            self.snake_segments.append((new_y, new_x))

            tmp_y, tmp_x = self.snake_segments[0]
            self.table[tmp_y][tmp_x] = self.EMPTY
            self.snake_segments = self.snake_segments[1:]
            tmp_y, tmp_x = self.snake_segments[0]
            self.table[tmp_y][tmp_x] = self.EMPTY
            self.snake_segments = self.snake_segments[1:]
            self.tail_y, self.tail_x = self.snake_segments[0]


            if (self.length > 1):
                self.table[self.head_y][self.head_x] = self.TAIL
            self.head_y = new_y
            self.head_x = new_x
            self.table[new_y][new_x] = self.HEAD
            self.set_cell_to_random_empty(self.PEPPER)

        elif cell == self.EMPTY:
            self.snake_segments.append((new_y, new_x))
            self.table[self.head_y][self.head_x] = self.TAIL
            self.table[self.tail_y][self.tail_x] = self.EMPTY
            self.snake_segments = self.snake_segments[1:]
            self.tail_y, self.tail_x = self.snake_segments[0]

            self.head_y = new_y
            self.head_x = new_x
            self.table[new_y][new_x] = self.HEAD

        self.moving_dir = action

        return False
