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
        self.input_size = 12 # 4 obstacles + 4 foods + 4 peppers
        self.output_size = 4  # LEFT, UP, RIGHT, DOWN
        self.model = self._create_model()
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.999719
        self.memory = deque(maxlen = 16384)
        self.target_model = self._create_model()
        self.update_target_counter = 0
        self.evaluation_mode = False
        self.folder_name = 'models'

    def _create_model(self):
        model = keras.Sequential([
            keras.layers.Dense(32, input_shape=(self.input_size,), activation='relu'),
            keras.layers.Dense(16, activation='relu'),
            keras.layers.Dense(self.output_size, activation='linear')
        ])
        model.compile(optimizer='adam', loss='mse')
        return model

    def get_state(self):
        state = []
        head_y = self.board.head_y
        head_x = self.board.head_x
        table = self.board.table
        tail_y = self.board.tail_y
        tail_x = self.board.tail_x
        TAIL = self.board.TAIL
        APPLE = self.board.APPLE
        PEPPER = self.board.PEPPER

        for dy, dx in self.board.DIRECTIONS:
            y = head_y
            x = head_x
            dist = 0
            while True:
                y += dy
                x += dx
                if y >= 10 or x >= 10 or y < 0 or x < 0:
                    break
                if table[y][x] == TAIL and (y != tail_y or x != tail_x):
                    break
                dist += 1
            state.append(dist)

            y = head_y
            x = head_x
            dist = 1
            while True:
                y += dy
                x += dx
                if y >= 10 or x >= 10 or y < 0 or x < 0:
                    break
                if table[y][x] == APPLE:
                    break
                dist += 1
            state.append(dist)

            y = head_y
            x = head_x
            dist = 1
            while True:
                y += dy
                x += dx
                if y >= 10 or x >= 10 or y < 0 or x < 0:
                    break
                if table[y][x] == PEPPER:
                    break
                dist += 1
            state.append(dist)

        return np.array(state)

    def get_direction(self, state):
        if np.random.rand() <= self.epsilon and not self.evaluation_mode:
            action = random.randint(0, self.output_size - 1)
        else:
            state_tensor = np.expand_dims(state, axis=0)
            q_values = self.model.predict(state_tensor, verbose=0)[0]
            action = np.argmax(q_values)
            # print("q_values: ", q_values)

        return self.board.DIRECTIONS[action]

    def remember(self, state, action, reward, next_state, done):
        action_idx = self.board.DIRECTIONS.index(action)
        self.memory.append((state, action_idx, reward, next_state, done))

    def set_folder_name(self, name):
        base_path = os.path.join("models", name)
        if os.path.exists(base_path) and os.path.isdir(base_path):
            i = 2
            while os.path.exists(f"{base_path}{i}") and os.path.isdir(f"{base_path}{i}"):
                i += 1
            self.folder_name = f"{name}{i}"
        else:
            self.folder_name = name
        os.makedirs("models", exist_ok=True)
        os.makedirs(os.path.join("models", self.folder_name), exist_ok=True)

    def save_model(self, episode):
        timestamp = datetime.now().strftime("%Y%m%d_%H:%M")
        model_path = os.path.join("models", self.folder_name, f"snake_model_{episode}_{timestamp}.keras")
        self.model.save(model_path)
        print(f"Model saved to {model_path}")

    def load_model(self, model_path):
        if os.path.exists(model_path):
            try:
                self.model = keras.models.load_model(model_path)
                self.target_model = keras.models.load_model(model_path)
                self.epsilon = 1 # self.epsilon_min
            except Exception as e:
                import sys
                print("\033[91mFailed to load model\033[0m")
                sys.exit(1)
        else:
            import sys
            print("\033[91mFailed to load model\033[0m")
            sys.exit(1)

    def train(self, state, direction, reward, next_state, done):
        self.remember(state, direction, reward, next_state, done)
        self.replay(512)
        return next_state

    def replay(self, batch_size):
        if len(self.memory) < batch_size:
            return

        minibatch = random.sample(self.memory, batch_size)

        states = np.array([experience[0] for experience in minibatch])
        next_states = np.array([experience[3] for experience in minibatch])

        current_q_values = self.model.predict(states, verbose=0)
        next_q_values = self.target_model.predict(next_states, verbose=0)

        for i, (state, action_idx, reward, next_state, done) in enumerate(minibatch):
            if done:
                target = reward
            else:
                target = reward + 0.95 * np.max(next_q_values[i])

            current_q_values[i][action_idx] = target

        self.model.fit(states, current_q_values, epochs=1, verbose=0)

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

        # TRY soft update

        # new_weights = []
        # target_weights = self.target_model.get_weights()
        # for i, model_weights in enumerate(self.model.get_weights()):
        #     new_weights.append(0.01 * model_weights + 0.99 * target_weights[i])
        # self.target_model.set_weights(new_weights)

        # hard update every 1000 iterations.

        self.update_target_counter += 1
        if self.update_target_counter > 700:
            self.target_model.set_weights(self.model.get_weights())
            self.update_target_counter = 0
