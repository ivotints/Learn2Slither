import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
from tensorflow import keras
from collections import deque
import numpy as np
from datetime import datetime
from get_state import *
from get_action import *

class SnakeAgent:
    INPUT_SIZE = 16
    OUTPUT_SIZE = 4
    BATCH_SIZE = 128
    def __init__(self, board, first_layer=32, second_layer=16):
        self.board = board
        self.first_layer = first_layer
        self.second_layer = second_layer
        self.model = self._create_model()
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.9998
        self.memory = deque(maxlen = 10000)
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
        layers = []
        first_layer_size = max(1, self.first_layer)
        layers.append(keras.layers.Dense(first_layer_size, input_shape=(self.INPUT_SIZE,), activation='relu'))
        if self.second_layer > 0:
            layers.append(keras.layers.Dense(self.second_layer, activation='relu'))
        layers.append(keras.layers.Dense(self.OUTPUT_SIZE, activation='linear'))
        model = keras.Sequential(layers)
        model.compile(optimizer='adam', loss='mse', jit_compile=True)
        return model

    def get_state(self):
        directions = np.array(self.board.DIRECTIONS, dtype=np.int8)
        return get_state_16_normalized_numba(
            self.board.head_y, self.board.head_x, self.board.table,
            self.board.tail_y, self.board.tail_x, directions,
            self.board.TAIL, self.board.APPLE, self.board.PEPPER,  self.board.size_y, self.board.size_x
        )

    def get_action(self, state):
        return(get_action_safe(self, state))
        return(get_action_dangerous(self, state))

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
