import numpy as np
import random

def get_action_dangerous(self, state):
    if np.random.rand() <= self.epsilon and not self.evaluation_mode:
        action = random.randint(0, self.OUTPUT_SIZE - 1)
        self.board.last_move_random = True
    else:
        state_tensor = np.expand_dims(state, axis=0)
        q_values = self.model(state_tensor)[0]
        action = np.argmax(q_values)
        self.board.last_move_random = False

    return action

def get_action_safe(self, state):
    """AI will choose an action that avoids immediate death when exploring"""
    if np.random.rand() <= self.epsilon and not self.evaluation_mode:
        safe_directions = []
        for i, (dy, dx) in enumerate(self.board.DIRECTIONS):
            new_y = self.board.head_y + dy
            new_x = self.board.head_x + dx
            if 0 <= new_y < self.board.size_y and 0 <= new_x < self.board.size_x:
                cell = self.board.table[new_y][new_x]
                if (cell != self.board.TAIL or
                    (new_y == self.board.tail_y and new_x == self.board.tail_x)):
                    safe_directions.append(i)
        if safe_directions:
            action = random.choice(safe_directions)
        else:
            action = random.randint(0, self.OUTPUT_SIZE - 1)
        self.board.last_move_random = True
    else:
        state_tensor = np.expand_dims(state, axis=0)
        q_values = self.model(state_tensor)[0]
        action = np.argmax(q_values)
        self.board.last_move_random = False

    return action

def get_action_half_safe(self, state):
    if np.random.rand() <= self.epsilon and not self.evaluation_mode:
        if np.random.rand() <= 0.9:
            safe_directions = []
            for i, (dy, dx) in enumerate(self.board.DIRECTIONS):
                new_y = self.board.head_y + dy
                new_x = self.board.head_x + dx
                if 0 <= new_y < self.board.size_y and 0 <= new_x < self.board.size_x:
                    cell = self.board.table[new_y][new_x]
                    if (cell != self.board.TAIL or
                        (new_y == self.board.tail_y and new_x == self.board.tail_x)):
                        safe_directions.append(i)
            if safe_directions:
                action = random.choice(safe_directions)
            else:
                action = random.randint(0, self.OUTPUT_SIZE - 1)
        else:
            action = random.randint(0, self.OUTPUT_SIZE - 1)
        self.board.last_move_random = True
    else:
        state_tensor = np.expand_dims(state, axis=0)
        q_values = self.model(state_tensor)[0]
        action = np.argmax(q_values)
        self.board.last_move_random = False

    return action