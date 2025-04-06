import os
import re
import glob
from tabulate import tabulate

def find_best_score(eval_file_path):
    """Extract the best average length from an evaluation.txt file"""
    try:
        best_avg = 0.0
        best_episode = 0

        with open(eval_file_path, 'r') as file:
            for line in file:
                match = re.search(r'Episode (\d+): Average length = (\d+\.\d+)', line)
                if match:
                    episode = int(match.group(1))
                    avg_length = float(match.group(2))

                    if avg_length > best_avg:
                        best_avg = avg_length
                        best_episode = episode

        return best_avg, best_episode
    except Exception as e:
        print(f"Error processing {eval_file_path}: {e}")
        return 0.0, 0

def main():
    pattern = os.path.join('models', '*', 'evaluation.txt')

    results = []

    for eval_file_path in glob.glob(pattern):
        model_name = os.path.basename(os.path.dirname(eval_file_path))

        best_score, best_episode = find_best_score(eval_file_path)

        if best_score > 0:
            results.append({
                'Model Name': model_name,
                'Best Average Length': best_score,
                'At Episode': best_episode
            })

    results.sort(key=lambda x: x['Best Average Length'], reverse=True)

    if results:
        print("\n🏆 Snake AI Model Rankings 🏆")
        print("=" * 60)

        try:
            from tabulate import tabulate
            print(tabulate(results, headers='keys', tablefmt='pretty'))
        except ImportError:
            # Fallback formatting without tabulate
            print(f"{'Model Name':<30} {'Best Avg Length':>15} {'At Episode':>10}")
            print("-" * 60)
            for r in results:
                print(f"{r['Model Name']:<30} {r['Best Average Length']:>15.2f} {r['At Episode']:>10}")

        print("\nTotal models analyzed:", len(results))
    else:
        print("\nNo evaluation files found. Make sure your models are in the 'models' directory and contain evaluation.txt files.")

if __name__ == "__main__":
    main()