import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf
from tensorflow import keras
from collections import deque
import numpy as np
from datetime import datetime
import random

class SnakeAgent:
    INPUT_SIZE = 16
    OUTPUT_SIZE = 4
    BATCH_SIZE = 256
    def __init__(self, board):
        self.board = board
        self.model = self._create_model()
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.9998
        self.memory = deque(maxlen = 30000)
        self.target_model = self._create_model()
        self.update_target_counter = 0
        self.evaluation_mode = False
        self.folder_name = 'models'
        self._init_replay_buffers(self.BATCH_SIZE)

    def _init_replay_buffers(self, max_batch_size):
        """Pre-allocate memory arrays for replay buffer to improve performance"""
        self.replay_states = np.zeros((max_batch_size, self.INPUT_SIZE), dtype=np.float32)
        self.replay_actions = np.zeros(max_batch_size, dtype=np.int32)
        self.replay_rewards = np.zeros(max_batch_size, dtype=np.float32)
        self.replay_next_states = np.zeros((max_batch_size, self.INPUT_SIZE), dtype=np.float32)
        self.replay_dones = np.zeros(max_batch_size, dtype=np.bool_)
        self.max_batch_size = max_batch_size

    def _create_model(self):
            model = keras.Sequential([
                keras.layers.Dense(32, input_shape=(self.INPUT_SIZE,), activation='relu'),
                keras.layers.Dense(16, activation='relu'),
                keras.layers.Dense(self.OUTPUT_SIZE, activation='linear')
            ])
            model.compile(optimizer='adam', loss='mse', jit_compile=True)
            return model

    def get_state(self):
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
                if next_cell != self.board.TAIL or (next_y == tail_y and next_x == tail_x):
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

    def get_action(self, state):
        """AI will choose his action"""
        if np.random.rand() <= self.epsilon and not self.evaluation_mode:
            action = random.randint(0, self.OUTPUT_SIZE - 1)
            self.board.last_move_random = True
        else:
            state_tensor = np.expand_dims(state, axis=0)
            q_values = self.model(state_tensor)[0]
            action = np.argmax(q_values)
            self.board.last_move_random = False

        return action

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
                self.epsilon = 0.1 # self.epsilon_min
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
        self.replay(self.BATCH_SIZE)

    def replay(self, batch_size):
        if len(self.memory) < batch_size:
            return

        indices = np.random.choice(len(self.memory), batch_size, replace=False)

        states = self.replay_states[:batch_size]
        actions = self.replay_actions[:batch_size]
        rewards = self.replay_rewards[:batch_size]
        next_states = self.replay_next_states[:batch_size]
        dones = self.replay_dones[:batch_size]

        for i, idx in enumerate(indices):
            experience = self.memory[idx]
            states[i] = experience[0]
            actions[i] = experience[1]
            rewards[i] = experience[2]
            next_states[i] = experience[3]
            dones[i] = experience[4]

        current_q_values = self.model(states, training=False).numpy()
        next_q_values = self.target_model(next_states, training=False).numpy()

        max_next_q = np.max(next_q_values, axis=1)
        targets = np.where(dones, rewards, rewards + 0.95 * max_next_q)

        for i in range(batch_size):
            current_q_values[i, actions[i]] = targets[i]

        self.model.fit(states, current_q_values, epochs=1, verbose=0, batch_size=batch_size)

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

        new_weights = []
        target_weights = self.target_model.get_weights()
        for i, model_weights in enumerate(self.model.get_weights()):
            new_weights.append(0.01 * model_weights + 0.99 * target_weights[i])  # adjastable
        self.target_model.set_weights(new_weights)
