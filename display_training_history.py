import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
import os


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

        df = pd.DataFrame(data, columns=['epoch', 'length'])

        plt.figure(figsize=(8, 5))
        plt.plot(df['epoch'], df['length'], color='blue',
                 marker='.', linestyle='-', label='Snake Length')
        plt.title('Snake Length Over Training Episodes')
        plt.xlabel('Episode')
        plt.ylabel('Snake Length')
        plt.grid(True, alpha=0.3)
        plt.legend()

        time = datetime.now().strftime('%Y%m%d_%H%M')
        plot_path = os.path.join("models",
                                 agent.folder_name,
                                 f"training_history_"
                                 f"{time}.png")
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
