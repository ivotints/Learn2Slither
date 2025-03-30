import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf
from tensorflow import keras
from collections import deque
import numpy as np
from datetime import datetime
import random

class SnakeAgent:
    INPUT_SIZE = 12
    OUTPUT_SIZE = 3
    def __init__(self, board):
        self.board = board
        self.model = self._create_model()
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.998876
        self.memory = deque(maxlen = 4096)
        self.target_model = self._create_model()
        self.update_target_counter = 0
        self.evaluation_mode = False
        self.folder_name = 'models'

    def _create_model(self):
            model = keras.Sequential([
                keras.layers.Dense(32, input_shape=(self.INPUT_SIZE,), activation='relu', use_bias=True),
                keras.layers.Dense(16, activation='relu'),
                keras.layers.Dense(self.OUTPUT_SIZE, activation='linear')
            ])
            model.compile(optimizer='adam', loss='mse')
            return model

    # now i will write new get_state, which will have
    # 3 bits of what does snake see from the left,
    # normalized distance (0 - 1) to nearest object
    # same to all 3 othrs.

    # output of the network will be LEFT, STRAIGHT and RIGHT.

    def get_state(self):
        state = np.zeros(self.INPUT_SIZE, dtype=np.float32)

        head_y = self.board.head_y
        head_x = self.board.head_x
        table = self.board.table
        tail_y = self.board.tail_y
        tail_x = self.board.tail_x
        SIZE = 10
        SIZE_INV = 0.111111111  #  1/(SIZE-1) = 1/9

        directions = self.board.DIRECTIONS
        dir_idx = self.board.moving_dir

        direction_indices = [(dir_idx-1)%4, dir_idx, (dir_idx+1)%4]
        direction_vectors = [directions[idx] for idx in direction_indices]

        for i, (dy, dx) in enumerate(direction_vectors):
            y, x = head_y, head_x
            dist = 0
            base_idx = i << 2

            while True:
                y += dy
                x += dx
                if not (0 <= y < SIZE and 0 <= x < SIZE):
                    state[base_idx] = 1
                    break

                cell = table[y][x]
                if cell == self.board.TAIL and (y != tail_y or x != tail_x):
                    state[base_idx] = 1
                    break
                if cell == self.board.APPLE:
                    state[base_idx + 1] = 1
                    break
                if cell == self.board.PEPPER:
                    state[base_idx + 2] = 1
                    break
                dist += 1

            state[base_idx + 3] = dist * SIZE_INV

        return state

    def get_action(self, state):
        """AI will choose his action"""
        # 0 = LEFT, 1 = STRAIGHT, 2 = RIGHT
        if np.random.rand() <= self.epsilon and not self.evaluation_mode:
            action = random.randint(0, self.OUTPUT_SIZE - 1)
        else:
            state_tensor = np.expand_dims(state, axis=0)
            q_values = self.model(state_tensor)[0]
            action = np.argmax(q_values)

        return action # 0 = LEFT, 1 = STRAIGHT, 2 = RIGHT

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

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

    def train(self, state, action, reward, next_state, done):
        self.remember(state, action, reward, next_state, done)
        self.replay(128)

    def replay(self, batch_size):
        if len(self.memory) < batch_size:
            return

        indices = np.random.choice(len(self.memory), batch_size, replace=False)

        states = np.zeros((batch_size, self.INPUT_SIZE), dtype=np.float32)
        actions = np.zeros(batch_size, dtype=np.int32)
        rewards = np.zeros(batch_size, dtype=np.float32)
        next_states = np.zeros((batch_size, self.INPUT_SIZE), dtype=np.float32)
        dones = np.zeros(batch_size, dtype=np.bool_)

        for i, idx in enumerate(indices):
            experience = self.memory[idx]
            states[i] = experience[0]
            actions[i] = experience[1]
            rewards[i] = experience[2]
            next_states[i] = experience[3]
            dones[i] = experience[4]

        current_q_values = self.model.predict(states, verbose=0)
        next_q_values = self.target_model.predict(next_states, verbose=0)

        max_next_q = np.max(next_q_values, axis=1)
        targets = np.where(dones, rewards, rewards + 0.95 * max_next_q)

        for i in range(batch_size):
            current_q_values[i, actions[i]] = targets[i]

        self.model.fit(states, current_q_values, epochs=1, verbose=0, batch_size=batch_size)

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

        self.update_target_counter += 1
        if self.update_target_counter > 700:
            self.target_model.set_weights(self.model.get_weights())
            self.update_target_counter = 0

        # TRY soft update
        # new_weights = []
        # target_weights = self.target_model.get_weights()
        # for i, model_weights in enumerate(self.model.get_weights()):
        #     new_weights.append(0.01 * model_weights + 0.99 * target_weights[i])
        # self.target_model.set_weights(new_weights)
