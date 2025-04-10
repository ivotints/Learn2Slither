# here i will have a lot of get_state functions to find out the best
import numpy as np
import numba as nb


def get_state_16bits(self):
    state = np.zeros(self.INPUT_SIZE, dtype=np.float32)

    head_y = self.board.head_y
    head_x = self.board.head_x
    table = self.board.table
    tail_y = self.board.tail_y
    tail_x = self.board.tail_x
    SIZE = 10

    for i, (dy, dx) in enumerate(self.board.DIRECTIONS):
        base_idx = i << 2  # * 4

        next_y = head_y + dy
        next_x = head_x + dx
        if 0 <= next_y < SIZE and 0 <= next_x < SIZE:
            next_cell = table[next_y][next_x]
            if next_cell != self.board.TAIL or (next_y == tail_y
                                                and next_x == tail_x):
                state[base_idx + 3] = 1  # Next cell is free to move

        y = head_y
        x = head_x
        nearest_object_found = False

        while not nearest_object_found:
            y += dy
            x += dx

            # Out of bounds check
            if not (0 <= y < SIZE and 0 <= x < SIZE):
                state[base_idx + 2] = 1  # Obstacle (wall)
                nearest_object_found = True
                continue

            cell = table[y][x]

            # Check what we found
            if cell == self.board.EMPTY:
                continue
            elif cell == self.board.TAIL and (y != tail_y or x != tail_x):
                state[base_idx + 2] = 1  # Obstacle (tail)
                nearest_object_found = True
            elif cell == self.board.APPLE:
                state[base_idx + 0] = 1  # Food
                nearest_object_found = True
            elif cell == self.board.PEPPER:
                state[base_idx + 1] = 1  # Pepper
                nearest_object_found = True

    return state


@nb.njit
def get_state_16_normalized_numba(head_y, head_x,
                                  table, tail_y, tail_x,
                                  directions, TAIL, APPLE,
                                  PEPPER, SIZE_Y, SIZE_X):
    state = np.zeros(16, dtype=np.float32)

    MAX_DISTANCE = max(SIZE_Y, SIZE_X)
    SIZE_INV = 1.0 / MAX_DISTANCE

    for i in range(4):
        dy, dx = directions[i]
        y = head_y
        x = head_x
        dist = 0
        base_idx = i * 4

        while True:
            y += dy
            x += dx
            if not (0 <= y < SIZE_Y and 0 <= x < SIZE_X):
                state[base_idx] = 1
                break

            cell = table[y][x]
            if cell == TAIL:  # and (y != tail_y or x != tail_x):
                state[base_idx] = 1
                break
            if cell == APPLE:
                state[base_idx + 1] = 1
                break
            if cell == PEPPER:
                state[base_idx + 2] = 1
                break
            dist += 1

        state[base_idx + 3] = dist * SIZE_INV

    return state


@nb.njit
def get_state_12_normalized_numba(head_y, head_x, table, directions,
                                  TAIL, APPLE, SIZE_Y, SIZE_X):
    state = np.zeros(12, dtype=np.float32)

    MAX_DISTANCE = max(SIZE_Y, SIZE_X)
    SIZE_INV = 1.0 / MAX_DISTANCE

    for i in range(4):
        dy, dx = directions[i]
        y = head_y
        x = head_x
        dist = 0
        base_idx = i * 3

        while True:
            y += dy
            x += dx
            if not (0 <= y < SIZE_Y and 0 <= x < SIZE_X):
                state[base_idx] = 1
                break

            cell = table[y][x]
            if cell == TAIL:  # and (y != tail_y or x != tail_x):
                state[base_idx] = 1  # Tail detected
                break
            if cell == APPLE:
                state[base_idx + 1] = 1  # Apple detected
                break

            dist += 1

        state[base_idx + 2] = dist * SIZE_INV

    return state
