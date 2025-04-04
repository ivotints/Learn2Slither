import os
import pandas as pd
import numpy as np

def analyze_model(model_path):
    try:
        with open(os.path.join(model_path, 'logs.txt'), 'r') as file:
            data = []
            for line in file:
                parts = line.strip().split()
                epoch = int(parts[0])
                length = int(parts[4])
                data.append([epoch, length])

            df = pd.DataFrame(data, columns=['epoch', 'length'])

            last_300 = df.tail(100)

            avg_length = last_300['length'].mean()

            return avg_length
    except:
        return None

def main():
    models_dir = 'models'
    results = []

    for model_name in os.listdir(models_dir):
        model_path = os.path.join(models_dir, model_name)
        if os.path.isdir(model_path):
            avg_length = analyze_model(model_path)
            if avg_length is not None:
                results.append((model_name, avg_length))

    results.sort(key=lambda x: x[1], reverse=True)

    print("\nModel Performance Analysis (Last 300 iterations)")
    print("=" * 50)
    print(f"{'Model Name':<20} {'Average Length':>15}")
    print("-" * 50)
    for model_name, avg_length in results:
        print(f"{model_name:<20} {avg_length:>15.2f}")

if __name__ == "__main__":
    main()