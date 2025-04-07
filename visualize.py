import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import argparse
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline

parser = argparse.ArgumentParser(
    description='Visualize training metrics from logs.txt'
)
parser.add_argument(
    '--model',
    type=str,
    required=True,
    help='Name of the model folder'
)
parser.add_argument(
    '--degree',
    type=int,
    default=3,
    help='Degree of polynomial for non-linear regression'
)
args = parser.parse_args()

NAME = args.model
POLY_DEGREE = args.degree

data = []
log_path = f'models/{NAME}/logs.txt'
with open(log_path, 'r') as file:
    for line in file:
        parts = line.strip().split()
        epoch = int(parts[0])
        reward = float(parts[2])
        length = int(parts[4])
        data.append([epoch, reward, length])

df = pd.DataFrame(data, columns=['epoch', 'reward', 'length'])

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

ax1.plot(df['epoch'], df['length'], color='blue', alpha=0.5, label='Actual')
ax1.set_title('Snake Length Over Training Episodes')
ax1.set_xlabel('Episode')
ax1.set_ylabel('Snake Length')
ax1.grid(True, alpha=0.3)

z1 = np.polyfit(df['epoch'], df['length'], 1)
p1 = np.poly1d(z1)
ax1.plot(
    df['epoch'],
    p1(df['epoch']),
    "r--",
    alpha=0.8,
    label='Linear Trend'
)

X = df['epoch'].values.reshape(-1, 1)
polyreg1 = make_pipeline(
    PolynomialFeatures(POLY_DEGREE),
    LinearRegression()
)
polyreg1.fit(X, df['length'])
ax1.plot(
    df['epoch'],
    polyreg1.predict(X),
    'g-',
    alpha=0.8,
    label=f'Polynomial (degree={POLY_DEGREE})'
)
ax1.legend()

ax2.plot(df['epoch'], df['reward'], color='green', alpha=0.5, label='Actual')
ax2.set_title('Reward Over Training Episodes')
ax2.set_xlabel('Episode')
ax2.set_ylabel('Reward')
ax2.grid(True, alpha=0.3)

z2 = np.polyfit(df['epoch'], df['reward'], 1)
p2 = np.poly1d(z2)
ax2.plot(
    df['epoch'],
    p2(df['epoch']),
    "r--",
    alpha=0.8,
    label='Linear Trend'
)

polyreg2 = make_pipeline(
    PolynomialFeatures(POLY_DEGREE),
    LinearRegression()
)
polyreg2.fit(X, df['reward'])
ax2.plot(
    df['epoch'],
    polyreg2.predict(X),
    'b-',
    alpha=0.8,
    label=f'Polynomial (degree={POLY_DEGREE})'
)
ax2.legend()

plt.tight_layout()

plt.savefig(f'{NAME}.png')
plt.close()
