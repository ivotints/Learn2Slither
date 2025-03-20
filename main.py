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
    display_grapics = not args.no_graphics
    evaluation_mode = args.evaluation_mode

    if args.load_model:
        agent.load_model(args.load_model)

    if display_grapics:
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
            max_steps = 300

            while running and not done and steps < max_steps:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            running = False

                direction = agent.get_direction(state)

                old_length = board.length
                done = board.make_move(direction)
                next_state = agent.get_state()

                if done:
                    reward = -20.0
                elif board.length == old_length:
                    reward = -0.1
                elif board.length > old_length:
                    reward = 2.0
                    max_length = max(board.length, max_length)
                else:
                    reward = -2.0

                total_reward += reward

                if not evaluation_mode:
                    state = agent.train(state, direction, reward, next_state, done)
                else:
                    state = next_state

                steps += 1

                if not done:
                    graphics.draw_board()
                    graphics.clock.tick(600)

            print(f"Episode {episode} finished with reward {total_reward:.2f}, max length {max_length}, steps {steps}")
            if not evaluation_mode and (episode + 1) % save_frequency == 0:
                agent.save_model(episode + 1)

            board = init_board()
            agent.board = board
            graphics.board = board

        if not evaluation_mode:
            agent.save_model(episodes)
        pygame.quit()
    else:
        episodes = 1000000
        save_frequency = 100

        for episode in range (episodes):
            state = agent.get_state()
            total_reward = 0
            done = False
            max_length = 3
            steps = 0
            max_steps = 300
            reward = 0

            while not done and steps < max_steps:
                direction = agent.get_direction(state)

                old_length = board.length
                done = board.make_move(direction)
                next_state = agent.get_state() # what if move was deadly? state will not be updated.

                if done:
                    reward = -20.0
                elif board.length == old_length:
                    reward = -0.1
                elif board.length > old_length:
                    reward = 2.0
                    max_length = max(board.length, max_length)
                else:
                    reward = -2.0

                total_reward += reward

                if not evaluation_mode:
                    state = agent.train(state, direction, reward, next_state, done)
                else:
                    state = next_state
                steps += 1
            print(f"Episode {episode} finished with reward {total_reward:.2f}, max length {max_length}, steps {steps}")
            if not evaluation_mode and (episode + 1) % save_frequency == 0:
                agent.save_model(episode + 1)

            board = init_board()
            agent.board = board

        if not evaluation_mode:
            agent.save_model(episodes)

if __name__ == "__main__":
    main()


# fix : WARNING:absl:You are saving your model as an HDF5 file via `model.save()` or `keras.saving.save_model(model)`. This file format is considered legacy. We recommend using instead the native Keras format, e.g. `model.save('my_model.keras')` or `keras.saving.save_model(model, 'my_model.keras')`.
# Model saved to models/snake_model_1900.h5