import os
import contextlib
import math


with open(os.devnull, 'w') as f, contextlib.redirect_stdout(f):
    import pygame


class init_graphics:
    def __init__(self, board):
        self.board = board
        pygame.init()
        self.cell_size = 80
        window_width = self.cell_size * self.board.size_x
        window_height = self.cell_size * self.board.size_y
        self.window = pygame.display.set_mode((window_width, window_height))
        pygame.display.set_caption(
            f"Learn2Slither - {self.board.size_x}x{self.board.size_y}"
        )
        self.clock = pygame.time.Clock()
        self.saved_board = None
        self.green_bokeh = None
        self.red_bokeh = None
        self.show_vision = False

    def _draw_initial_board(self):
        """Draws initial board without snake and food"""

        if self.saved_board is not None:
            self.window.blit(self.saved_board, (0, 0))
            return

        floor_color = (14, 22, 31)
        edge_color = (9, 13, 18)
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
                    r = int(square_color_top[0] * (1 - ratio) +
                            square_color_bottom[0] * ratio)
                    g = int(square_color_top[1] * (1 - ratio) +
                            square_color_bottom[1] * ratio)
                    b = int(square_color_top[2] * (1 - ratio) +
                            square_color_bottom[2] * ratio)
                    # x, y
                    pygame.draw.line(
                        inner_surface, (r, g, b), (0, i), (inner_width, i)
                    )

                self.window.blit(
                    inner_surface,
                    (x * cell_size + shift + border,
                     y * cell_size + shift + border)
                )
        self.saved_board = self.window.copy()

    def _draw_snake(self):
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

        def get_red():
            CYCLE = 16
            if not hasattr(get_red, 'colors'):
                get_red.colors = []
                get_red.counter = 0
                bright_red = (220, 60, 60)
                dark_red = (170, 40, 40)
                for i in range(CYCLE):
                    r = int(bright_red[0] -
                            (bright_red[0] - dark_red[0]) * (i / CYCLE))
                    g = int(bright_red[1] -
                            (bright_red[1] - dark_red[1]) * (i / CYCLE))
                    b = int(bright_red[2] -
                            (bright_red[2] - dark_red[2]) * (i / CYCLE))
                    get_red.colors.append((r, g, b))
                for i in range(CYCLE):
                    r = int(dark_red[0] +
                            (bright_red[0] - dark_red[0]) * (i / CYCLE))
                    g = int(dark_red[1] +
                            (bright_red[1] - dark_red[1]) * (i / CYCLE))
                    b = int(dark_red[2] +
                            (bright_red[2] - dark_red[2]) * (i / CYCLE))
                    get_red.colors.append((r, g, b))
            get_red.counter += 1
            return get_red.colors[get_red.counter % (CYCLE * 2)]

        def get_shadow():
            return (10, 10, 10)

        color_func = get_red if self.board.last_move_random else get_purple

        def draw_segment(start_pos, end_pos, size, color_function):
            start_y, start_x = start_pos
            end_y, end_x = end_pos

            start_center_x = start_x * self.cell_size + self.cell_size // 2
            start_center_y = start_y * self.cell_size + self.cell_size // 2

            dir_x = end_x - start_x
            dir_y = end_y - start_y

            for i in range(10):
                center_x = start_center_x + 8 * i * dir_x
                center_y = start_center_y + 8 * i * dir_y
                pygame.draw.circle(
                    self.window, color_function(), (center_x, center_y), size
                )

        for i in range(len(self.board.snake_segments) - 1):
            segment_size = min(30, 17 + self.board.length // 2) + 4
            draw_segment(
                self.board.snake_segments[i],
                self.board.snake_segments[i + 1],
                segment_size,
                get_shadow
            )

        for i in range(len(self.board.snake_segments) - 1):
            segment_size = min(30, 17 + self.board.length // 2)
            draw_segment(
                self.board.snake_segments[i],
                self.board.snake_segments[i + 1],
                segment_size,
                color_func
            )

        if (len(self.board.snake_segments) < 2):
            start_y, start_x = self.board.snake_segments[-1]
            start_center_x = start_x * self.cell_size + self.cell_size // 2
            start_center_y = start_y * self.cell_size + self.cell_size // 2
            size = min(30, 17 + len(self.board.snake_segments) // 2)
            pygame.draw.circle(
                self.window, get_shadow(), (start_center_x, start_center_y),
                size + 4
            )
            pygame.draw.circle(
                self.window, color_func(), (start_center_x, start_center_y),
                size
            )

        self._draw_snake_eyes()

    def _draw_snake_eyes(self):
        head_center_x = (self.board.head_x * self.cell_size +
                         self.cell_size // 2)
        head_center_y = (self.board.head_y * self.cell_size +
                         self.cell_size // 2)

        dir_y, dir_x = self.board.DIRECTIONS[self.board.moving_dir]
        if dir_x == -1:  # LEFT
            eye_offsets = [(-8, 0), (8, 0)]
            pupil_shift = (0, -3)
        elif dir_y == -1:  # UP
            eye_offsets = [(0, -8), (0, 8)]
            pupil_shift = (-3, 0)
        elif dir_x == 1:  # RIGHT
            eye_offsets = [(-8, 0), (8, 0)]
            pupil_shift = (0, 3)
        else:  # DOWN
            eye_offsets = [(0, -8), (0, 8)]
            pupil_shift = (3, 0)

        for offset_y, offset_x in eye_offsets:
            pygame.draw.circle(
                self.window,
                (255, 255, 255),
                (head_center_x + offset_x, head_center_y + offset_y),
                8
            )

            # Pupil
            shift_y, shift_x = pupil_shift
            pygame.draw.circle(
                self.window,
                (0, 0, 0),
                (head_center_x + offset_x + shift_x,
                 head_center_y + offset_y + shift_y),
                5
            )

    def _create_bokeh(self, color):
        radius = self.cell_size
        bokeh_surface = pygame.Surface((radius, radius), pygame.SRCALPHA)
        bokeh_surface_white = pygame.Surface((radius, radius),
                                             pygame.SRCALPHA)
        self._create_bokeh_surface(bokeh_surface, radius // 4,
                                   radius // 6, color)
        self._create_bokeh_surface(
            bokeh_surface_white, radius // 6, radius // 10, (255, 255, 255)
        )
        bokeh_surface.blit(bokeh_surface_white, (0, 0))
        return bokeh_surface

    def _create_bokeh_surface(self, bokeh_surface, outer_radius,
                              inner_radius, color):
        surface_size = bokeh_surface.get_width()
        center = surface_size // 2

        for x in range(surface_size):
            for y in range(surface_size):
                distance = math.sqrt((x - center)**2 + (y - center)**2)
                if distance <= outer_radius:
                    if distance <= inner_radius:
                        intensity = 1.0
                    else:
                        intensity = 1.0 - (distance - inner_radius) / (
                            outer_radius - inner_radius)
                    alpha = int(intensity * 255)
                    bokeh_surface.set_at((x, y),
                                         (color[0], color[1], color[2], alpha))
        return bokeh_surface

    def _draw_bokeh(self, y, x, food):
        center_y = y * self.cell_size
        center_x = x * self.cell_size
        surface = 0
        if food == self.board.APPLE:
            if self.green_bokeh is None:
                self.green_bokeh = self._create_bokeh((0, 255, 0))
            surface = self.green_bokeh
        else:
            if self.red_bokeh is None:
                self.red_bokeh = self._create_bokeh((255, 0, 0))
            surface = self.red_bokeh
        self.window.blit(surface, (center_x, center_y))

    def _draw_food(self):
        food_coords = []
        for y in range(self.board.size_y):
            for x in range(self.board.size_x):
                cell = self.board.table[y][x]
                if cell == self.board.APPLE or cell == self.board.PEPPER:
                    food_coords.append((y, x, cell))
        for y, x, food in food_coords:
            self._draw_bokeh(y, x, food)

    def draw_board(self):
        self._draw_initial_board()
        self._draw_snake()
        self._draw_food()

        if self.show_vision:
            self._draw_snake_vision_simple()

        pygame.display.flip()

    def _draw_snake_vision_simple(self):
        head_y = self.board.head_y
        head_x = self.board.head_x
        directions = self.board.DIRECTIONS

        visible_directions = directions

        overlay = pygame.Surface(
            (self.window.get_width(),
             self.window.get_height()), pygame.SRCALPHA
        )
        overlay.fill((0, 0, 0, 255))

        for dy, dx in visible_directions:
            y, x = head_y, head_x
            while True:
                y += dy
                x += dx
                if not (0 <= y < self.board.size_y
                        and 0 <= x < self.board.size_x):
                    break

                rect = pygame.Rect(
                    x * self.cell_size,
                    y * self.cell_size,
                    self.cell_size,
                    self.cell_size
                )
                pygame.draw.rect(overlay, (0, 0, 0, 0), rect)

        head_rect = pygame.Rect(
            head_x * self.cell_size,
            head_y * self.cell_size,
            self.cell_size,
            self.cell_size
        )
        pygame.draw.rect(overlay, (0, 0, 0, 0), head_rect)

        self.window.blit(overlay, (0, 0))
