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
    return parser

def main():
    parser = setup_argparser()
    args = parser.parse_args()
    board = init_board()
    agent = SnakeAgent(board)
    display_graphics = not args.no_graphics
    evaluation_mode = args.evaluation_mode

    if args.load_model:
        agent.load_model(args.load_model)

    if display_graphics:
        graphics = init_graphics(board)

    episodes = 10000
    save_frequency = 100

    for episode in range (episodes):
        state = agent.get_state()
        total_reward = 0
        reward = 0
        running = True
        done = False
        max_length = 3
        steps = 0
        steps_no_food = 0
        max_steps = 300 # to prevent loops

        while running and not done and steps_no_food < max_steps:
            if display_graphics:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            running = False
            if not running:
                break

            direction = agent.get_direction(state)
            old_length = board.length
            done = board.make_move(direction)
            next_state = agent.get_state() # if move was deadly state will not be updated.

            if done:
                reward = -20.0
            elif board.length == old_length:
                reward = -0.1
            elif board.length > old_length:
                reward = 2.0
                steps_no_food = 0
                max_length = max(board.length, max_length)
            else:
                reward = -2.0

            total_reward += reward

            if not evaluation_mode:
                state = agent.train(state, direction, reward, next_state, done)
            else:
                state = next_state

            steps += 1
            steps_no_food += 1

            if display_graphics and not done:
                graphics.draw_board()
                graphics.clock.tick(2)

        print(f"Episode {episode} finished with reward {total_reward:.2f}, max length {max_length}, steps {steps}")
        if not evaluation_mode and (episode + 1) % save_frequency == 0:
            agent.save_model(episode + 1)

        board = init_board()
        agent.board = board
        if display_graphics:
            graphics.board = board

    if not evaluation_mode:
        agent.save_model(episodes)
    if display_graphics:
        pygame.quit()

if __name__ == "__main__":
    main()
