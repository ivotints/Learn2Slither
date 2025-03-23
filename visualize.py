import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Read the data from logs.txt
data = []
with open('linear/logs.txt', 'r') as file:
    for line in file:
        parts = line.strip().split()
        epoch = int(parts[0])
        reward = float(parts[2])  # 'rwrd' value
        length = int(parts[4])    # 'len' value
        data.append([epoch, reward, length])

# Convert to DataFrame
df = pd.DataFrame(data, columns=['epoch', 'reward', 'length'])

# Create two subplots
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

# Length plot
ax1.plot(df['epoch'], df['length'], color='blue', alpha=0.5)
ax1.set_title('Snake Length Over Training Episodes')
ax1.set_xlabel('Episode')
ax1.set_ylabel('Snake Length')
ax1.grid(True, alpha=0.3)

# Add trend line for length
z1 = np.polyfit(df['epoch'], df['length'], 1)
p1 = np.poly1d(z1)
ax1.plot(df['epoch'], p1(df['epoch']), "r--", alpha=0.8)

# Reward plot
ax2.plot(df['epoch'], df['reward'], color='green', alpha=0.5)
ax2.set_title('Reward Over Training Episodes')
ax2.set_xlabel('Episode')
ax2.set_ylabel('Reward')
ax2.grid(True, alpha=0.3)

# Add trend line for reward
z2 = np.polyfit(df['epoch'], df['reward'], 1)
p2 = np.poly1d(z2)
ax2.plot(df['epoch'], p2(df['epoch']), "r--", alpha=0.8)

# Adjust layout to prevent overlap
plt.tight_layout()

# Save the plot
plt.savefig('training_progress.png')
plt.close()