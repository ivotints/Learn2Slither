import os

import contextlib
with open(os.devnull, 'w') as f, contextlib.redirect_stdout(f):
    import pygame
from board import init_board
from graphics import init_graphics
import argparse
from agent import SnakeAgent

def setup_argparser():
    parser = argparse.ArgumentParser(description="Snake game with RL")
    parser.add_argument('--no_graphics', '-ng', action='store_true',  help='Turn off graphics')
    parser.add_argument('--evaluation_mode', '-e', action='store_true', help='Turn off training')
    parser.add_argument('--load_model', '-lm', type=str, help='Path to model to load')
    parser.add_argument('--name', '-n', type=str, default='model', help='Name of model folder')
    return parser

def main():
    parser = setup_argparser()
    args = parser.parse_args()
    board = init_board()
    agent = SnakeAgent(board)
    display_graphics = not args.no_graphics
    evaluation_mode = args.evaluation_mode
    agent.evaluation_mode = evaluation_mode
    agent.set_folder_name(args.name)
    log_file = open(os.path.join("models", agent.folder_name, 'logs.txt'), 'a')

    fps = 5
    step_by_step_mode = False
    wait_for_step = False

    if args.load_model:
        agent.load_model(args.load_model)

    if display_graphics:
        graphics = init_graphics(board)

    episodes = 1000000
    save_frequency = 300
    running = True

    for episode in range (episodes):
        state = agent.get_state()
        total_reward = 0
        reward = 0
        done = False
        max_length = 3
        steps = 0
        steps_no_food = 0
        max_steps = 200 # to prevent loops
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

            action = agent.get_action(state)  # 0 = LEFT, 1 = STRAIGHT, 2 = RIGHT
            old_length = board.length

            # apple_1_distance = abs(board.head_y - board.apple_1[0]) + abs(board.head_x - board.apple_1[1])
            # apple_2_distance = abs(board.head_y - board.apple_2[0]) + abs(board.head_x - board.apple_2[1])
            # old_food_distance = min(apple_1_distance, apple_2_distance)

            done = board.make_move(action)

            # apple_1_distance = abs(board.head_y - board.apple_1[0]) + abs(board.head_x - board.apple_1[1])
            # apple_2_distance = abs(board.head_y - board.apple_2[0]) + abs(board.head_x - board.apple_2[1])
            # new_food_distance = min(apple_1_distance, apple_2_distance)

            # if done: # died
            #     reward = -20.0
            # elif board.length > old_length: # eated apple
            #     reward = 1.0 * (board.length)# add non linearity
            #     steps_no_food = 0
            #     max_length = max(board.length, max_length)
            # elif board.length < old_length: # eated pepper
            #     reward = -2.0 * (board.length)
            # elif new_food_distance < old_food_distance: # moved closer to the food
            #     reward = 0
            # elif new_food_distance == old_food_distance:
            #     reward = -0.1
            # elif new_food_distance > old_food_distance: # moved away from food
            #     reward = -0.2
            reward = 0
            if board.length > old_length:
                reward = 1.0
                steps_no_food = 0
                max_length = max(board.length,  max_length)
            elif board.length < old_length:
                reward = -1.0

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

        log_msg = f"{episode} rwrd {total_reward:.1f} len {max_length} steps {steps}\n"
        print(log_msg, end="")
        log_file.write(log_msg)

        if not evaluation_mode and (episode + 1) % save_frequency == 0:
            agent.save_model(episode + 1)

        board.reset()

    if not evaluation_mode and running:
        agent.save_model(episodes)
    if display_graphics:
        pygame.quit()

if __name__ == "__main__":
    main()
