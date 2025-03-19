import numpy as np
import tensorflow as tf
from tensorflow import keras
import os

class SnakeAgent:
    def __init__(self, board):
        self.board = board
        self.input_size = 16  # 4 walls + 4 obstacles + 4 foods + 4 peppers
        self.output_size = 4  # LEFT, UP, RIGHT, DOWN
        self.model = self._create_model()
        self.model_dir = "models"
        if not os.path.exists(self.model_dir):
            os.makedirs(self.model_dir)

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

        state.append(head_x + 1)
        state.append(head_y + 1)
        state.append(self.board.size_x - head_x)
        state.append(self.board.size_y - head_y)

        for dy, dx in self.board.DIRECTIONS:
            dist = self._find_closest_obstacle(head_y, head_x, dy, dx)
            state.append(dist)

        for dy, dx in self.board.DIRECTIONS:
            dist = self._find_closest_food(head_y, head_x, dy, dx, self.board.APPLE)
            state.append(dist)

        for dy, dx in self.board.DIRECTIONS:
            dist = self._find_closest_food(head_y, head_x, dy, dx, self.board.PEPPER)
            state.append(dist)

        return np.array(state)

    def _find_closest_obstacle(self, y, x, dy, dx):
        distance = 0
        while True:
            y += dy
            x += dx
            distance += 1

            if not self.board.is_in_table(y, x):
                return distance

            cell = self.board.get_cell(y, x)
            if cell == self.board.TAIL and (y != self.board.tail_y and x != self.board.tail_x): # it can move on tail's end
                return distance

    def _find_closest_food(self, y, x, dy, dx, target):
        """Find distance to closest target in given direction"""
        distance = 0
        while True:
            y += dy
            x += dx
            distance += 1

            if not self.board.is_in_table(y, x):
                return 0

            cell = self.board.get_cell(y, x)
            if cell == target:
                return distance

