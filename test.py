import time
import numpy as np
import tensorflow as tf
from tensorflow import keras
from collections import deque
import random
import os
import statistics

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

class TestAgent:
    INPUT_SIZE = 12
    OUTPUT_SIZE = 3

    def __init__(self, memory_size=4096):
        self.model = self._create_model()
        self.target_model = self._create_model()
        self.memory = deque(maxlen=memory_size)
        self.epsilon = 0.1
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.998
        self.update_target_counter = 0

    def _create_model(self):
        model = keras.Sequential([
            keras.layers.Dense(32, input_shape=(self.INPUT_SIZE,), activation='relu'),
            keras.layers.Dense(16, activation='relu'),
            keras.layers.Dense(self.OUTPUT_SIZE, activation='linear')
        ])
        model.compile(optimizer='adam', loss='mse')
        return model

    def replay_v1(self, batch_size):
        """Original implementation"""
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

        self.update_target_counter += 1
        if self.update_target_counter > 700:
            self.target_model.set_weights(self.model.get_weights())
            self.update_target_counter = 0

    def replay_v2(self, batch_size):
        """Optimized implementation"""
        if len(self.memory) < batch_size:
            return

        # Use numpy's random choice
        indices = np.random.choice(len(self.memory), batch_size, replace=False)

        # Pre-allocate arrays
        states = np.zeros((batch_size, self.INPUT_SIZE), dtype=np.float32)
        actions = np.zeros(batch_size, dtype=np.int32)
        rewards = np.zeros(batch_size, dtype=np.float32)
        next_states = np.zeros((batch_size, self.INPUT_SIZE), dtype=np.float32)
        dones = np.zeros(batch_size, dtype=np.bool_)

        # Fill arrays efficiently
        for i, idx in enumerate(indices):
            experience = self.memory[idx]
            states[i] = experience[0]
            actions[i] = experience[1]
            rewards[i] = experience[2]
            next_states[i] = experience[3]
            dones[i] = experience[4]

        # Batch predictions
        current_q_values = self.model.predict(states, verbose=0)
        next_q_values = self.target_model.predict(next_states, verbose=0)

        # Vectorized operations
        max_next_q = np.max(next_q_values, axis=1)
        targets = np.where(dones, rewards, rewards + 0.95 * max_next_q)

        # Update Q-values
        for i in range(batch_size):
            current_q_values[i, actions[i]] = targets[i]

        # Batch training
        self.model.fit(states, current_q_values, epochs=1, verbose=0, batch_size=batch_size)

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

        self.update_target_counter += 1
        if self.update_target_counter > 700:
            self.target_model.set_weights(self.model.get_weights())
            self.update_target_counter = 0


def fill_memory(agent, num_samples=10000):
    """Fill agent's memory with random experiences"""
    for _ in range(num_samples):
        state = np.random.random(agent.INPUT_SIZE).astype(np.float32)
        action = np.random.randint(0, agent.OUTPUT_SIZE)
        reward = np.random.random() * 2 - 1  # Range from -1 to 1
        next_state = np.random.random(agent.INPUT_SIZE).astype(np.float32)
        done = np.random.random() < 0.1  # 10% chance of being done

        agent.memory.append((state, action, reward, next_state, done))

def test_performance(num_tests=10, batch_size=128):
    # Create agent
    agent = TestAgent(memory_size=10000)

    # Fill memory with random data
    print("Filling memory buffer with test data...")
    fill_memory(agent)
    print(f"Memory buffer size: {len(agent.memory)}")

    # Initialize results
    times_v1 = []
    times_v2 = []

    # Run tests multiple times
    print(f"\nRunning {num_tests} tests with batch size {batch_size}...")

    # First test - warmup (JIT compilation, etc.)
    print("Warmup run...")
    _ = agent.replay_v1(batch_size)
    _ = agent.replay_v2(batch_size)

    # Main tests
    for i in range(num_tests):
        # Test V1
        start_time = time.time()
        agent.replay_v1(batch_size)
        end_time = time.time()
        times_v1.append(end_time - start_time)

        # Test V2
        start_time = time.time()
        agent.replay_v2(batch_size)
        end_time = time.time()
        times_v2.append(end_time - start_time)

        print(f"Test {i+1}/{num_tests} completed")

    # Calculate statistics
    avg_v1 = statistics.mean(times_v1)
    avg_v2 = statistics.mean(times_v2)

    # Print results
    print("\n===== PERFORMANCE TEST RESULTS =====")
    print(f"Original implementation (V1): {avg_v1:.6f} seconds per call")
    print(f"Optimized implementation (V2): {avg_v2:.6f} seconds per call")
    print(f"Speedup: {avg_v1/avg_v2:.2f}x")
    print(f"Improvement: {(1 - avg_v2/avg_v1) * 100:.2f}%")

    # Compare fastest runs
    fastest_v1 = min(times_v1)
    fastest_v2 = min(times_v2)
    print(f"\nFastest run V1: {fastest_v1:.6f} seconds")
    print(f"Fastest run V2: {fastest_v2:.6f} seconds")

    # Compare slowest runs
    slowest_v1 = max(times_v1)
    slowest_v2 = max(times_v2)
    print(f"\nSlowest run V1: {slowest_v1:.6f} seconds")
    print(f"Slowest run V2: {slowest_v2:.6f} seconds")

    # Print standard deviation
    std_v1 = statistics.stdev(times_v1) if len(times_v1) > 1 else 0
    std_v2 = statistics.stdev(times_v2) if len(times_v2) > 1 else 0
    print(f"\nStandard deviation V1: {std_v1:.6f} seconds")
    print(f"Standard deviation V2: {std_v2:.6f} seconds")

if __name__ == "__main__":
    test_performance(num_tests=10, batch_size=128)