import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf
from tensorflow import keras
from collections import deque
import numpy as np
from datetime import datetime
import random

class SnakeAgent:
    def __init__(self, board):
        self.board = board
        self.input_size = 16  # 4 walls + 4 obstacles + 4 foods + 4 peppers
        self.output_size = 4  # LEFT, UP, RIGHT, DOWN
        self.model = self._create_model()
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.999
        self.memory = deque(maxlen = 2000)
        self.target_model = self._create_model()
        self.gamma = 0.95
        self.update_target_counter = 0
        self.evaluation_mode = False
        self.folder_name = 'models'

    def _create_model(self):
        model = keras.Sequential([
            keras.layers.Dense(32, input_shape=(self.input_size,), activation='relu'),
            keras.layers.Dense(16, activation='relu'),
            keras.layers.Dense(self.output_size, activation='linear')
        ])
        optimizer = tf.keras.optimizers.Adam(0.001, clipvalue=1.0)
        model.compile(optimizer=optimizer, loss='mse')
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

    def get_direction(self, state):
        """Choose direction based on the current state using epsilon-greedy policy"""
        if np.random.rand() <= self.epsilon and not self.evaluation_mode:
            action = random.randint(0, self.output_size - 1)
        else:
            state_tensor = np.expand_dims(state, axis=0)
            q_values = self.model.predict(state_tensor, verbose=0)[0]
            action = np.argmax(q_values)

        return self.board.DIRECTIONS[action]


    def train(self, state, direction, reward, next_state, done):
        self.remember(state, direction, reward, next_state, done)
        self.replay(32)
        return next_state

    def remember(self, state, action, reward, next_state, done):
        action_idx = self.board.DIRECTIONS.index(action)
        self.memory.append((state, action_idx, reward, next_state, done))

    def set_folder_name(self, name):
        if os.path.exists(name) and os.path.isdir(name):
            i = 2
            while os.path.exists(f"{name}{i}") and os.path.isdir(f"{name}{i}"):
                i += 1
            self.folder_name = f"{name}{i}"
        else:
            self.folder_name = name
        os.makedirs(self.folder_name, exist_ok=True)

    def save_model(self, episode):
        timestamp = datetime.now().strftime("%Y%m%d_%H:%M")
        model_path = os.path.join(self.folder_name, f"snake_model_{episode}_{timestamp}.keras")
        self.model.save(model_path)
        print(f"Model saved to {model_path}")

    def load_model(self, model_path):
        if os.path.exists(model_path):
            try:
                self.model = keras.models.load_model(model_path)
                self.target_model = keras.models.load_model(model_path)
                self.epsilon = self.epsilon_min
            except Exception as e:
                import sys
                print("\033[91mFailed to load model\033[0m")
                sys.exit(1)
        else:
            import sys
            print("\033[91mFailed to load model\033[0m")
            sys.exit(1)


    def replay(self, batch_size):
        """Train the model on a batch of experiences from memory"""
        if len(self.memory) < batch_size:
            return

        minibatch = random.sample(self.memory, batch_size)

        states = np.array([experience[0] for experience in minibatch])
        next_states = np.array([experience[3] for experience in minibatch])

        # Predict Q-values for current states and next states
        current_q_values = self.model.predict(states, verbose=0)
        next_q_values = self.target_model.predict(next_states, verbose=0)

        # Update Q-values based on the Bellman equation
        for i, (state, action_idx, reward, next_state, done) in enumerate(minibatch):
            if done:
                target = reward
            else:
                target = reward + self.gamma * np.max(next_q_values[i])

            current_q_values[i][action_idx] = target

        # Train the model
        self.model.fit(states, current_q_values, epochs=1, verbose=0)

        # Decay epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

        # Update the target network periodically
        self.update_target_counter += 1
        if self.update_target_counter > 100:
            self.target_model.set_weights(self.model.get_weights())
            self.update_target_counter = 0
