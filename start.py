import subprocess
import sys
import os

def main():
    args = sys.argv[1:] if len(sys.argv) > 1 else []

    command = [sys.executable, "main.py"] + args

    try:
        with open(os.devnull, 'w') as devnull:
            process = subprocess.run(
                command,
                stdout=None,
                stderr=devnull,
                check=True
            )

        return process.returncode

    except subprocess.CalledProcessError as e:
        return e.returncode
    except FileNotFoundError:
        print("Error: main.py not found in the current directory", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())