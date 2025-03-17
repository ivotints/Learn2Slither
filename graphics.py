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

        window_width = self.window.get_width()
        cell_size = window_width // self.board.size_x  # 80
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

        # Calculate cell size and center offset
        window_width = self.window.get_width()
        cell_size = window_width // self.board.size_x
        center_offset = cell_size // 2

        # Shadow and body colors
        shadow_color = (25, 25, 40)
        body_color_outer = (120, 80, 200)
        body_color_inner = (160, 100, 230)

        # Draw shadows first (from tail to head)
        for segment in self.snake_segments:
            y, x = segment
            center_x = x * cell_size + center_offset
            center_y = y * cell_size + center_offset

            # Shadow circle (slightly larger than body)
            shadow_radius = int(cell_size * 0.45)
            pygame.draw.circle(self.window, shadow_color, (center_x, center_y), shadow_radius)

        # Draw body circles (from tail to head)
        for i, segment in enumerate(self.snake_segments):
            y, x = segment
            center_x = x * cell_size + center_offset
            center_y = y * cell_size + center_offset

            # Make head slightly larger than body segments
            if i == len(self.snake_segments) - 1:  # Head
                body_radius = int(cell_size * 0.4)
            else:
                body_radius = int(cell_size * 0.35)

            # Draw gradient body (simplified as a solid color for now)
            pygame.draw.circle(self.window, body_color_outer, (center_x, center_y), body_radius)

        # Draw eyes on the head
        head_y, head_x = self.snake_segments[-1]
        head_center_x = head_x * cell_size + center_offset
        head_center_y = head_y * cell_size + center_offset

        # Determine eye positions based on movement direction
        # 0: left, 1: up, 2: right, 3: down
        eye_offsets = [
            [(0, -0.15), (0, 0.15)],  # left
            [(-0.15, 0), (0.15, 0)],  # up
            [(0, -0.15), (0, 0.15)],  # right
            [(-0.15, 0), (0.15, 0)]   # down
        ]

        dir_idx = self.moving_dir
        for offset in eye_offsets[dir_idx]:
            eye_x = int(head_center_x + offset[1] * cell_size)
            eye_y = int(head_center_y + offset[0] * cell_size)

            # White part of eye
            pygame.draw.circle(self.window, (255, 255, 255), (eye_x, eye_y), cell_size // 10)

            # Pupil (black part)
            pupil_offset_x = 2 if dir_idx == 2 else (-2 if dir_idx == 0 else 0)
            pupil_offset_y = 2 if dir_idx == 3 else (-2 if dir_idx == 1 else 0)
            pygame.draw.circle(self.window, (0, 0, 0),
                            (eye_x + pupil_offset_x, eye_y + pupil_offset_y),
                            cell_size // 20)

        # Draw food items (apples and peppers)
        for y in range(self.board.size_y):
            for x in range(self.board.size_x):
                cell_value = self.board.get_cell(y, x)
                if cell_value == self.board.APPLE:
                    center_x = x * cell_size + center_offset
                    center_y = y * cell_size + center_offset
                    pygame.draw.circle(self.window, (0, 200, 0), (center_x, center_y), int(cell_size * 0.3))
                elif cell_value == self.board.PEPPER:
                    center_x = x * cell_size + center_offset
                    center_y = y * cell_size + center_offset
                    pygame.draw.circle(self.window, (200, 0, 0), (center_x, center_y), int(cell_size * 0.3))

        pygame.display.flip() # call after wrote something to the screen to update it
