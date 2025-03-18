import numpy as np
import tensorflow as tf
from tensorflow import keras

class SnakeAgent:
    def __init__(self, board):
        self.board = board
        self.input_size = 16  # 4 walls + 4 obstacles + 4 foods + 4 peppers
        self.output_size = 4  # LEFT, UP, RIGHT, DOWN
        self.model = self._create_model()

    def _create_model(self):
        model = keras.Sequential([
            keras.layers.Dense(32, input_shape=(self.input_size,), activation='relu'),
            keras.layers.Dense(16, activation='relu'),
            keras.layers.Dense(self.output_size, activation='softmax')
        ])
        model.compile(optimizer='adam', loss='categorical_crossentropy')
        return model

    def get_state(self):
        """Get all distances as neural network input"""
        state = []
        head_y, head_x = self.board.head_y, self.board.head_x

        # Distances to walls
        state.append(head_x)  # left wall
        state.append(self.board.size_x - 1 - head_x)  # right wall
        state.append(head_y)  # top wall
        state.append(self.board.size_y - 1 - head_y)  # bottom wall

        # Find closest obstacles in each direction
        for dy, dx in [(0, -1), (0, 1), (-1, 0), (1, 0)]:  # LEFT, RIGHT, UP, DOWN
            dist = self._find_closest(head_y, head_x, dy, dx, [self.board.TAIL])
            state.append(dist)

        # Find closest foods
        for dy, dx in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            dist = self._find_closest(head_y, head_x, dy, dx, [self.board.APPLE])
            state.append(dist)

        # Find closest peppers
        for dy, dx in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            dist = self._find_closest(head_y, head_x, dy, dx, [self.board.PEPPER])
            state.append(dist)

        return np.array(state)

    def _find_closest(self, y, x, dy, dx, target_types):
        """Find distance to closest target in given direction"""
        distance = 0
        while True:
            y += dy
            x += dx
            distance += 1

            if not self.board.is_in_table(y, x):
                return distance

            cell = self.board.get_cell(y, x)
            if cell in target_types:
                return distance

    def get_action(self, state, epsilon=0.1):
        """Get next action using epsilon-greedy policy"""
        if np.random.random() < epsilon:
            return np.random.randint(0, 4)

        state = np.array([state])
        q_values = self.model.predict(state, verbose=0)[0]
        return np.argmax(q_values)

    def train(self, state, action, reward, next_state, done):
        """Train the model using Q-learning"""
        state = np.array([state])
        next_state = np.array([next_state])

        target = reward
        if not done:
            target += 0.95 * np.max(self.model.predict(next_state, verbose=0)[0])

        target_f = self.model.predict(state, verbose=0)
        target_f[0][action] = target

        self.model.fit(state, target_f, epochs=1, verbose=0)