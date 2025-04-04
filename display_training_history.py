import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import datetime
import os
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline
def display_training_history(agent, show_plot=True):
    try:
        data = []
        log_path = os.path.join("models", agent.folder_name, 'logs.txt')
        if not os.path.exists(log_path):
            print("No training logs found to display.")
            return

        with open(log_path, 'r') as file:
            for line in file:
                parts = line.strip().split()
                if len(parts) >= 5:
                    epoch = int(parts[0])
                    length = int(parts[4])
                    data.append([epoch, length])

        if not data:
            print("No training data found to display.")
            return

        if len(data) < 5:
            print("Not enough training data for visualization (minimum 5 episodes required).")
            return

        df = pd.DataFrame(data, columns=['epoch', 'length'])

        fig = plt.figure(figsize=(10, 6))
        plt.plot(df['epoch'], df['length'], color='blue', alpha=0.5, label='Snake Length')
        plt.title('Snake Length Over Training Episodes')
        plt.xlabel('Episode')
        plt.ylabel('Snake Length')
        plt.grid(True, alpha=0.3)

        if len(df) > 3:
            z = np.polyfit(df['epoch'], df['length'], 1)
            p = np.poly1d(z)
            plt.plot(df['epoch'], p(df['epoch']), "r--", alpha=0.8, label='Linear Trend')

            X = df['epoch'].values.reshape(-1, 1)
            poly_degree = 3
            polyreg = make_pipeline(PolynomialFeatures(poly_degree), LinearRegression())
            polyreg.fit(X, df['length'])
            plt.plot(df['epoch'], polyreg.predict(X), 'g-', alpha=0.8, label=f'Non-Linear Trend (degree={poly_degree})')

        plt.legend()

        plot_path = os.path.join("models", agent.folder_name, f"training_history_{datetime.now().strftime('%Y%m%d_%H%M')}.png")
        plt.savefig(plot_path)
        print(f"Training history visualization saved to: {plot_path}")

        if show_plot:
            plt.show(block=False)
            plt.pause(5)
            plt.close()
        else:
            plt.close()

    except Exception as e:
        print(f"Error displaying training history: {e}")