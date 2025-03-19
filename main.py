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
    return parser

def main():
    parser = setup_argparser()
    args = parser.parse_args()
    board = init_board()
    agent = SnakeAgent(board)
    display_grapics = not args.no_graphics

    if display_grapics:
        graphics = init_graphics(board)
        episodes = 10000
        save_frequency = 100

        for episode in range (episodes):
            state = agent.get_state()
            total_reward = 0
            running = True
            done = False
            max_length = 3

            while running and not done:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            running = False
                direction = agent.get_direction(state)

                old_length = board.length
                done = board.make_move(direction)

                if done:
                    total_reward += -20.0
                elif board.length == old_length:
                    total_reward += -0.1
                elif board.length > old_length:
                    total_reward += 2.0
                    max_length = max(board.length, max_length)
                else:
                    total_reward += -2.0

                # i dont know how to continue training

                if not done:
                    graphics.draw_board()
                    graphics.clock.tick(600)

            print(f"Episode {episode} finished with reward {total_reward} and max length {max_length}")
            if (episode + 1) % save_frequency == 0:
                agent.save_model(episode + 1)

            board = init_board()
            agent.board = board
            graphics.board = board

        agent.save_model(episodes)
        pygame.quit()
    else:
        episodes = 10000
        save_frequency = 100

        for episode in range (episodes):
            state = agent.get_state()
            total_reward = 0
            done = False
            max_length = 3

            while not done:
                direction = agent.get_direction(state)

                old_length = board.length
                done = board.make_move(direction)

                if done:
                    total_reward += -20.0
                elif board.length == old_length:
                    total_reward += -0.1
                elif board.length > old_length:
                    total_reward += 2.0
                    max_length = max(board.length, max_length)
                else:
                    total_reward += -2.0

                # i dont know how to continue training

            print(f"Episode {episode} finished with reward {total_reward} and max length {max_length}")
            if (episode + 1) % save_frequency == 0:
                agent.save_model(episode + 1)

            board = init_board()
            agent.board = board

        agent.save_model(episodes)

if __name__ == "__main__":
    main()
