import os
import contextlib
with open(os.devnull, 'w') as f, contextlib.redirect_stdout(f):
    import pygame
from board import init_board
from graphics import init_graphics

def main():
    display_grapics = True
    board = init_board()

    if display_grapics:
        graphics = init_graphics(board)

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        board.make_move(board.DIRECTIONS[0])
                    elif event.key == pygame.K_UP or event.key == pygame.K_w:
                        board.make_move(board.DIRECTIONS[1])
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        board.make_move(board.DIRECTIONS[2])
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        board.make_move(board.DIRECTIONS[3])

            # for graphics i will have to update segment list and direction of movement.
            graphics.draw_board()

            # then I need to listen for the input

            graphics.clock.tick(60) # 60 fps
        pygame.quit()

if __name__ == "__main__":
    main()
