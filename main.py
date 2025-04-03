import os
import contextlib
with open(os.devnull, 'w') as f, contextlib.redirect_stdout(f):
    import pygame
from board import init_board
from graphics import init_graphics
import argparse
from agent import SnakeAgent
import statistics

def setup_argparser():
    parser = argparse.ArgumentParser(description="Snake game with RL")
    parser.add_argument('--no_graphics', '-ng', action='store_true',  help='Turn off graphics')
    parser.add_argument('--evaluation_mode', '-e', action='store_true', help='Turn off training')
    parser.add_argument('--load_model', '-lm', type=str, help='Path to model to load')
    parser.add_argument('--name', '-n', type=str, default='model', help='Name of model folder')
    return parser

def evaluate_model(agent, board, evaluation_episodes):
    agent.evaluation_mode = True
    lengths = []
    for _ in range(evaluation_episodes):
        state = agent.get_state()
        done = False
        max_length = 3
        steps_no_food = 0
        max_steps = 100  # to prevent loops

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

def evaluation(episode, agent, board, eval_frequency, eval_file, best_avg_length, poor_performance_count):
    print(f"Evaluating model at episode {episode}...")
    avg_length = evaluate_model(agent, board, eval_frequency)

    evaluation_result = f"Episode {episode}: Average length = {avg_length:.2f}\n"
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

def main():
    args = setup_argparser().parse_args()
    board = init_board()
    agent = SnakeAgent(board)
    display_graphics = not args.no_graphics
    evaluation_mode = args.evaluation_mode
    agent.evaluation_mode = evaluation_mode
    agent.set_folder_name(args.name)
    log_file = open(os.path.join("models", agent.folder_name, 'logs.txt'), 'a')
    eval_file = open(os.path.join("models", agent.folder_name, 'evaluation.txt'), 'a')

    fps = 18
    step_by_step_mode = False
    wait_for_step = False

    if args.load_model:
        agent.load_model(args.load_model)

    if display_graphics:
        graphics = init_graphics(board)
    else:
        graphics = None

    episodes = 10000
    save_frequency = 50
    running = True

    best_avg_length = 0
    poor_performance_count = 0

    for episode in range(1, episodes):
        state = agent.get_state()
        total_reward = 0
        reward = 0
        done = False
        max_length = 3
        steps = 0
        steps_no_food = 0
        max_steps = 100  # to prevent loops
        if not running:
            break

        while running and not done and steps_no_food < max_steps:
            if display_graphics:
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
                            else:
                                step_by_step_mode = False
                                fps = 2 + (key_num - 1) * 2
                                print(f"Speed set to {fps} fps")
                        elif event.key == pygame.K_SPACE and step_by_step_mode:
                            wait_for_step = False

            if step_by_step_mode and wait_for_step:
                pygame.time.wait(10)
                continue

            if not running:
                break

            action = agent.get_action(state)
            old_length = board.length
            done = board.make_move(action)

            reward = 0
            if board.length > old_length:
                reward = 1.0
                steps_no_food = 0
                max_length = max(board.length,  max_length)
            elif board.length < old_length:
                reward = -1.0
            if done:
                reward = -5.0

            total_reward += reward

            next_state = agent.get_state()
            if not evaluation_mode:
                agent.train(state, action, reward, next_state, done)
            state = next_state

            steps += 1
            steps_no_food += 1

            if display_graphics:
                graphics.draw_board()
                graphics.clock.tick(fps)
                if step_by_step_mode:
                    wait_for_step = True

        log_msg = f"{episode} rwrd {total_reward:.1f} len {max_length} steps {steps} mem {len(agent.memory)}\n"
        print(log_msg, end="")
        log_file.write(log_msg)
        board.reset()

        if not evaluation_mode and (episode) % save_frequency == 0:
            agent.save_model(episode)
            log_file.flush()
            stop, best_avg_length, poor_performance_count = evaluation(
                episode, agent, board, 100, eval_file, best_avg_length, poor_performance_count
            )
            print()
            if stop:
                break

    if not evaluation_mode and running:
        agent.save_model(episodes)
    if display_graphics:
        pygame.quit()

    log_file.close()
    eval_file.close()

if __name__ == "__main__":
    main()