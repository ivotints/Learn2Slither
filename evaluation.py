import sys
import signal
import pygame

def run_evaluation(agent, board, graphics, args):
    from training import print_evaluation_summary
    from ui import handle_ui_events

    fps = 24
    step_by_step_mode = False
    wait_for_step = False
    episodes = args.episodes

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