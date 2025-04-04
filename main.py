import os
import contextlib
import argparse
import signal
import sys
import statistics
with open(os.devnull, 'w') as f, contextlib.redirect_stdout(f):
    import pygame
from board import init_board
from graphics import init_graphics
from agent import SnakeAgent
from display_training_history import display_training_history

try:
    from lobby import run_lobby
except ImportError:
    run_lobby = None


def setup_argparser():
    """Set up and return the argument parser for command-line arguments."""
    parser = argparse.ArgumentParser(description="Snake game with Reinforcement Learning")
    parser.add_argument('--no_graphics', '-ng', action='store_true', help='Turn off graphics')
    parser.add_argument('--evaluation_mode', '-e', action='store_true', help='Run in evaluation mode (no training)')
    parser.add_argument('--load_model', '-lm', type=str, help='Path to model to load')
    parser.add_argument('--name', '-n', type=str, default='model', help='Name of model folder')
    parser.add_argument('--first_layer', '-fl', type=int, default=32, help='Number of neurons in the first layer')
    parser.add_argument('--second_layer', '-sl', type=int, default=16, help='Number of neurons in the second layer')
    parser.add_argument('--episodes', '-ep', type=int, default=10000, help='Number of training episodes')
    parser.add_argument('--show_vision', '-sv', action='store_true', help='Show agent vision in terminal')
    parser.add_argument('--use_lobby', '-ul', action='store_true', help='Show configuration lobby')
    return parser


def evaluate_model(agent, board, evaluation_episodes):
    agent.evaluation_mode = True
    lengths = []

    for _ in range(evaluation_episodes):
        state = agent.get_state()
        done = False
        max_length = 3
        steps_no_food = 0
        max_steps = 100

        while not done and steps_no_food < max_steps:
            action = agent.get_action(state)
            old_length = board.length
            done = board.make_move(action)

            if board.length > old_length:
                steps_no_food = 0
                max_length = max(board.length, max_length)

            steps_no_food += 1
            state = agent.get_state()

        lengths.append(max_length)
        board.reset()

    agent.evaluation_mode = False
    return statistics.mean(lengths)

def periodic_evaluation(episode, agent, board, eval_frequency, eval_file, best_avg_length, poor_performance_count):
    print(f"Evaluating model at episode {episode}...")
    avg_length = evaluate_model(agent, board, eval_frequency)

    record = "" if best_avg_length > avg_length else " - record!"
    evaluation_result = f"Episode {episode}: Average length = {avg_length:.2f}{record}\n"
    print(evaluation_result, end="")
    eval_file.write(evaluation_result)
    eval_file.flush()

    if avg_length > best_avg_length:
        best_avg_length = avg_length
        poor_performance_count = 0
        print(f"New best average length: {best_avg_length:.2f}!")
    else:
        poor_performance_count += 1
        print(f"No improvement. Poor performance count: {poor_performance_count}/10")

    stop_training = poor_performance_count >= 10
    if stop_training:
        print("No improvement for 10 consecutive evaluations. Stopping training.")

    board.reset()
    return stop_training, best_avg_length, poor_performance_count

def print_evaluation_summary(evaluation_lengths):
    if not evaluation_lengths:
        return

    avg_length = statistics.mean(evaluation_lengths)
    print(f"\n\nEvaluation Results:")
    print(f"Total games played: {len(evaluation_lengths)}")
    print(f"Average snake length: {avg_length:.2f}")
    print(f"Maximum length achieved: {max(evaluation_lengths)}")

def run_training(agent, board, graphics, args):
    agent.set_folder_name(args.name)
    log_file = open(os.path.join("models", agent.folder_name, 'logs.txt'), 'a')
    eval_file = open(os.path.join("models", agent.folder_name, 'evaluation.txt'), 'a')

    fps = 24
    step_by_step_mode = False
    wait_for_step = False
    episodes = args.episodes
    show_visison = args.show_vision
    save_frequency = 50
    running = True

    best_avg_length = 0
    poor_performance_count = 0

    try:
        for episode in range(1, episodes):
            if not running:
                break

            state = agent.get_state()

            total_reward = 0
            done = False
            max_length = 3
            steps = 0
            steps_no_food = 0
            max_steps = 100

            while running and not done and steps_no_food < max_steps:
                if show_visison:
                    print("Obstacle|Apple|Pepper|Distance to obstacle")
                    print(f"{state[0]:.0f} {state[1]:.0f} {state[2]:.0f} {state[3]:.03f} - left")
                    print(f"{state[4]:.0f} {state[5]:.0f} {state[6]:.0f} {state[7]:.03f} - up")
                    print(f"{state[8]:.0f} {state[9]:.0f} {state[10]:.0f} {state[11]:.03f} - right")
                    print(f"{state[12]:.0f} {state[13]:.0f} {state[14]:.0f} {state[15]:.03f} - down")
                    print()

                if graphics:
                    running, step_by_step_mode, wait_for_step, fps = handle_ui_events(
                        graphics, step_by_step_mode, wait_for_step, fps
                    )

                if step_by_step_mode and wait_for_step:
                    pygame.time.wait(10)
                    continue

                if not running:
                    break

                action = agent.get_action(state)
                old_length = board.length
                done = board.make_move(action)

                reward = calculate_reward(board, old_length, done)
                total_reward += reward

                if board.length > old_length:
                    steps_no_food = 0
                    max_length = max(board.length, max_length)

                next_state = agent.get_state()
                agent.train(state, action, reward, next_state, done)
                state = next_state

                steps += 1
                steps_no_food += 1

                if graphics:
                    graphics.draw_board()
                    graphics.clock.tick(fps)
                    if step_by_step_mode:
                        wait_for_step = True

            log_msg = f"{episode} rwrd {total_reward:.1f} len {max_length} steps {steps} mem {len(agent.memory)}\n"
            print(log_msg, end="")
            log_file.write(log_msg)

            board.reset()

            if episode % save_frequency == 0:
                agent.save_model(episode)
                log_file.flush()
                stop, best_avg_length, poor_performance_count = periodic_evaluation(
                    episode, agent, board, 100, eval_file, best_avg_length, poor_performance_count
                )
                print()
                if stop:
                    break
    finally:
        log_file.close()
        eval_file.close()
        agent.save_model(episode)

def run_evaluation(agent, board, graphics, args):
    fps = 24
    step_by_step_mode = False
    wait_for_step = False
    episodes = episodes = args.episodes

    running = True

    evaluation_lengths = []

    def signal_handler(sig, frame):
        agent.save_model(episode)
        print_evaluation_summary(evaluation_lengths)
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    try:
        for episode in range(1, episodes):
            if not running:
                break

            state = agent.get_state()
            done = False
            max_length = 3
            steps = 0
            steps_no_food = 0
            max_steps = 100

            while running and not done and steps_no_food < max_steps:
                if graphics:
                    running, step_by_step_mode, wait_for_step, fps = handle_ui_events(
                        graphics, step_by_step_mode, wait_for_step, fps
                    )

                    if not running:
                        print_evaluation_summary(evaluation_lengths)
                        break

                if step_by_step_mode and wait_for_step:
                    pygame.time.wait(10)
                    continue

                action = agent.get_action(state)
                old_length = board.length
                done = board.make_move(action)

                if board.length > old_length:
                    steps_no_food = 0
                    max_length = max(board.length, max_length)

                steps_no_food += 1
                steps += 1
                state = agent.get_state()

                if graphics:
                    graphics.draw_board()
                    graphics.clock.tick(fps)
                    if step_by_step_mode:
                        wait_for_step = True

            log_msg = f"{episode} len {max_length} steps {steps}\n"
            print(log_msg, end="")

            evaluation_lengths.append(max_length)

            board.reset()

        print_evaluation_summary(evaluation_lengths)

    except KeyboardInterrupt:
        print_evaluation_summary(evaluation_lengths)

def handle_ui_events(graphics, step_by_step_mode, wait_for_step, fps):
    running = True

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_x:
                graphics.show_vision = not graphics.show_vision
            elif event.key >= pygame.K_0 and event.key <= pygame.K_9:
                key_num = event.key - pygame.K_0
                if key_num == 0:
                    step_by_step_mode = True
                    wait_for_step = True
                    print("Step-by-step mode enabled. Press SPACE to advance.")
                elif key_num == 9:
                    step_by_step_mode = False
                    fps = 0  # 0 means unlimited FPS (no delay)
                    print("Unlimited speed mode enabled")
                else:
                    step_by_step_mode = False
                    fps = 2 + (key_num - 1) * 3
                    print(f"Speed set to {fps} fps")
            elif event.key == pygame.K_SPACE and step_by_step_mode:
                wait_for_step = False

    return running, step_by_step_mode, wait_for_step, fps

def calculate_reward(board, old_length, done):
    if board.length > old_length:
        return 1.0  # Food eaten
    elif board.length < old_length:
        return -1.0  # Lost tail
    elif done:
        return -5.0  # Game over
    return 0.0  # No change

def main():
    args = setup_argparser().parse_args()

    if run_lobby is not None and (args.use_lobby or len(sys.argv) == 1):
        lobby_args, eval_mode = run_lobby()
        if lobby_args is None:
            return

        args = setup_argparser().parse_args(lobby_args)
        args.evaluation_mode = eval_mode

    board = init_board()
    agent = SnakeAgent(board, first_layer=args.first_layer, second_layer=args.second_layer)
    agent.evaluation_mode = args.evaluation_mode

    if args.load_model:
        agent.load_model(args.load_model)

    graphics = None if args.no_graphics else init_graphics(board)

    try:
        if args.evaluation_mode:
            run_evaluation(agent, board, graphics, args)
        else:
            run_training(agent, board, graphics, args)

    finally:
        if graphics:
            pygame.quit()

        if not args.evaluation_mode:
            display_training_history(agent, show_plot=(not args.no_graphics))

if __name__ == "__main__":
    main()
