import os
import pandas as pd
import numpy as np

def analyze_model(model_path):
    # Read the logs file
    try:
        with open(os.path.join(model_path, 'logs.txt'), 'r') as file:
            data = []
            for line in file:
                parts = line.strip().split()
                epoch = int(parts[0])
                length = int(parts[4])  # 'len' value
                data.append([epoch, length])

            # Convert to DataFrame
            df = pd.DataFrame(data, columns=['epoch', 'length'])

            # Get last 300 iterations
            last_300 = df.tail(1000)

            # Calculate average length
            avg_length = last_300['length'].mean()

            return avg_length
    except:
        return None

def main():
    models_dir = 'models'
    results = []

    # Iterate through all directories in models folder
    for model_name in os.listdir(models_dir):
        model_path = os.path.join(models_dir, model_name)
        if os.path.isdir(model_path):
            avg_length = analyze_model(model_path)
            if avg_length is not None:
                results.append((model_name, avg_length))

    # Sort results by average length in descending order
    results.sort(key=lambda x: x[1], reverse=True)

    # Print results
    print("\nModel Performance Analysis (Last 300 iterations)")
    print("=" * 50)
    print(f"{'Model Name':<20} {'Average Length':>15}")
    print("-" * 50)
    for model_name, avg_length in results:
        print(f"{model_name:<20} {avg_length:>15.2f}")

if __name__ == "__main__":
    main()