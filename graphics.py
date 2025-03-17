import os
import contextlib
with open(os.devnull, 'w') as f, contextlib.redirect_stdout(f):
    import pygame

class init_graphics:
    def __init__(self, board):
        self.board = board
        pygame.init()
        self.window = pygame.display.set_mode((800, 800))
        pygame.display.set_caption("Learn2Slither")
        self.clock = pygame.time.Clock()
        self.saved_board = None
        self.moving_dir = self.board.initial_direction
        self.snake_segments = self.get_initial_snake_segments() # whole snake will be stored here from tail to head
        self.cell_size = self.window.get_width() // self.board.size_x  # 80


    def get_initial_snake_segments(self):
        snake_segments = []
        snake_segments.append((self.board.tail_y, self.board.tail_x))
        snake_segments.append((self.board.second_tail_y, self.board.second_tail_x))
        snake_segments.append((self.board.head_y, self.board.head_x))
        return snake_segments

    def draw_initial_board(self):
        """Draws initial board without snake and food"""

        if self.saved_board != None:
            self.window.blit(self.saved_board, (0, 0))
            return

        floor_color = (14, 22, 31)
        edge_color = (9,13,18)
        square_color_bottom = (20, 31, 42)
        square_color_top = (28, 43, 58)

        self.window.fill(floor_color)

        cell_size = self.cell_size
        shift = 4
        border = 7

        for y in range(self.board.size_y):
            for x in range(self.board.size_x):
                rect_outer = pygame.Rect(
                    x * cell_size + shift,
                    y * cell_size + shift,
                    cell_size - 2 * shift,
                    cell_size - 2 * shift
                )
                pygame.draw.rect(self.window, edge_color, rect_outer, border)

                inner_width = cell_size - 2 * shift - 2 * border  # 58
                inner_surface = pygame.Surface((inner_width, inner_width))

                for i in range(inner_width):
                    ratio = i / inner_width
                    r = int(square_color_top[0] * (1 - ratio) + square_color_bottom[0] * ratio)
                    g = int(square_color_top[1] * (1 - ratio) + square_color_bottom[1] * ratio)
                    b = int(square_color_top[2] * (1 - ratio) + square_color_bottom[2] * ratio)
                    pygame.draw.line(inner_surface, (r, g, b), (0, i), (inner_width, i))  # x, y

                self.window.blit(inner_surface, (x * cell_size + shift + border, y * cell_size + shift + border))
        self.saved_board = self.window.copy()

    def draw_board(self):
        self.draw_initial_board()


        # snake made of bigger circle of shadow, and smaller circle of violate body with gradient.
        # bigger the length of snake - bigger the circles. We start drawing snake from tail to head, starting from middle of tail cell going to the midle of next cell having between aproximatly 10 connecting circels,
        # drawing first all the shadows and then all the gradient bodies.
        # At the end we draw an 2 eyes for the snake, made from 2 circles : 1 white and 1 smaller black, whaching in the direction of moving.

        def get_purple():
            CYCLE = 16
            if not hasattr(get_purple, 'colors'):
                get_purple.colors = []
                get_purple.counter = 0
                for i in range(CYCLE):
                    r = int(96 + (173 - 96) * (i / CYCLE))
                    g = int(1 + (78 - 1) * (i / CYCLE))
                    b = int(172 + (253 - 172) * (i / CYCLE))
                    get_purple.colors.append((r, g, b))
                for i in range(CYCLE):
                    r = int(173 - (173 - 96) * (i / CYCLE))
                    g = int(78 - (78 - 1) * (i / CYCLE))
                    b = int(253 - (253 - 172) * (i / CYCLE))
                    get_purple.colors.append((r, g, b))

            get_purple.counter += 1
            return get_purple.colors[get_purple.counter % (CYCLE * 2)]

        def get_shadow():
            return (10, 10, 10)

        def draw_segment(start_pos, end_pos, size, color_function):
            start_y, start_x = start_pos
            end_y, end_x = end_pos

            start_center_y = start_y * self.cell_size + self.cell_size // 2
            start_center_x = start_x * self.cell_size + self.cell_size // 2

            dir_y = end_y - start_y
            dir_x = end_x - start_x

            for i in range(10):
                center_y = start_center_y + 8 * i * dir_y
                center_x = start_center_x + 8 * i * dir_x
                pygame.draw.circle(self.window, color_function(), (center_y, center_x), size)

        for i in range(len(self.snake_segments) - 1):
                draw_segment(self.snake_segments[i], self.snake_segments[i + 1], min(30, 16 + len(self.snake_segments)) + 4, get_shadow)

        for i in range(len(self.snake_segments) - 1):
                draw_segment(self.snake_segments[i], self.snake_segments[i + 1], min(30, 16 + len(self.snake_segments)), get_purple)

        # now i need to dray eyes with respect to direction of movement






        pygame.display.flip()
