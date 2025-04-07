import os
import statistics
import pygame

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
    episodes = max(2, args.episodes)
    show_vision = args.show_vision
    save_frequency = 50
    running = True

    best_avg_length = 0
    poor_performance_count = 0

    try:
        episode = 0
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
                if show_vision:
                    print("Obstacle|Apple|Pepper|Distance to obstacle")
                    for i in range(4):
                        direction_labels = ["left", "up", "right", "down"]
                        base_idx = i * 4
                        print(f"{state[base_idx]:.0f} {state[base_idx+1]:.0f} {state[base_idx+2]:.0f} {state[base_idx+3]:.03f} - {direction_labels[i]}")
                    print()

                if graphics:
                    from ui import handle_ui_events
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
        if episode > 0:
            agent.save_model(episode)

def calculate_reward(board, old_length, done):
    if board.length > old_length:
        return 1.0  # Food eaten
    elif board.length < old_length:
        return -1.0  # Lost tail
    elif done:
        return -5.0  # Game over
    return 0.0  # No change