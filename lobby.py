import pygame
import os
import sys
import glob

class Button:
    def __init__(self, x, y, width, height, text, color=(50, 50, 50), hover_color=(70, 70, 70), text_color=(255, 255, 255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.hovered = False

    def draw(self, surface, font):
        color = self.hover_color if self.hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, (200, 200, 200), self.rect, 2, border_radius=8)

        text_surf = font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_hovered(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)
        return self.hovered

    def is_clicked(self, mouse_pos, mouse_click):
        return self.is_hovered(mouse_pos) and mouse_click

class TextInput:
    def __init__(self, x, y, width, height, label, initial_value="", numeric=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.label = label
        self.value = str(initial_value)
        self.active = False
        self.numeric = numeric
        self.cursor_visible = True
        self.cursor_timer = 0

    def draw(self, surface, font):
        label_surf = font.render(self.label, True, (220, 220, 220))
        label_rect = label_surf.get_rect(midleft=(self.rect.left - 180, self.rect.centery))
        surface.blit(label_surf, label_rect)

        pygame.draw.rect(surface, (50, 50, 60), self.rect, border_radius=5)
        pygame.draw.rect(surface, (150, 150, 150) if self.active else (100, 100, 100),
                         self.rect, 2, border_radius=5)

        text_surf = font.render(self.value, True, (255, 255, 255))
        surface.blit(text_surf, (self.rect.x + 5, self.rect.y + 5))

        if self.active:
            self.cursor_timer = (self.cursor_timer + 1) % 60
            self.cursor_visible = self.cursor_timer < 30

            if self.cursor_visible:
                cursor_x = self.rect.x + 5 + text_surf.get_width()
                pygame.draw.line(surface, (255, 255, 255),
                                (cursor_x, self.rect.y + 5),
                                (cursor_x, self.rect.y + 25), 2)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

    def handle_key(self, event):
        if not self.active:
            return

        if event.key == pygame.K_BACKSPACE:
            self.value = self.value[:-1]
        elif self.numeric:
            if event.unicode.isdigit():
                self.value += event.unicode
        else:
            if event.unicode.isalnum() or event.unicode in "-_":
                self.value += event.unicode

        if self.numeric and self.value:
            try:
                int_value = int(self.value)
            except ValueError:
                self.value = "0"

class Toggle:
    def __init__(self, x, y, width, label, initial_state=False):
        self.rect = pygame.Rect(x, y, 50, 24)
        self.label = label
        self.state = initial_state

    def draw(self, surface, font):
        label_surf = font.render(self.label, True, (220, 220, 220))
        label_rect = label_surf.get_rect(midleft=(self.rect.left - 180, self.rect.centery))
        surface.blit(label_surf, label_rect)

        bg_color = (60, 180, 100) if self.state else (60, 60, 60)
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=12)
        pygame.draw.rect(surface, (200, 200, 200), self.rect, 1, border_radius=12)

        circle_x = self.rect.right - 12 if self.state else self.rect.left + 12
        pygame.draw.circle(surface, (240, 240, 240), (circle_x, self.rect.centery), 10)

    def is_clicked(self, pos, click):
        return self.rect.collidepoint(pos) and click

    def toggle(self):
        self.state = not self.state
        return self.state

def run_lobby():
    pygame.init()
    screen = pygame.display.set_mode((900, 600))
    pygame.display.set_caption("Learn2Slither - Configuration")

    title_font = pygame.font.Font(None, 48)
    subtitle_font = pygame.font.Font(None, 32)
    regular_font = pygame.font.Font(None, 24)

    bg_color = (20, 25, 35)
    panel_color = (30, 35, 45)
    accent_color = (70, 130, 180)

    start_button = Button(350, 500, 200, 50, "Start Training", color=(50, 120, 50), hover_color=(60, 150, 60))
    eval_button = Button(600, 500, 200, 50, "Evaluate Model", color=(70, 70, 120), hover_color=(80, 80, 150))

    model_input = TextInput(330, 130, 200, 30, "Model Name:", "model")
    episodes_input = TextInput(330, 180, 200, 30, "Episodes:", "1000", numeric=True)
    first_layer_input = TextInput(330, 230, 200, 30, "First Layer Neurons:", "32", numeric=True)
    second_layer_input = TextInput(330, 280, 200, 30, "Second Layer Neurons:", "16", numeric=True)

    text_inputs = [model_input, episodes_input, first_layer_input, second_layer_input]
    active_input = None

    graphics_toggle = Toggle(330, 330, 50, "Enable Graphics", True)
    vision_toggle = Toggle(330, 380, 50, "Show Vision", False)

    clock = pygame.time.Clock()
    running = True

    while running:
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None, False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return None, False

                if active_input:
                    active_input.handle_key(event)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_clicked = True

                found_active = False
                for input_field in text_inputs:
                    if input_field.is_clicked(mouse_pos):
                        active_input = input_field
                        input_field.active = True
                        found_active = True
                    else:
                        input_field.active = False

                if not found_active:
                    active_input = None

                if graphics_toggle.is_clicked(mouse_pos, mouse_clicked):
                    graphics_toggle.toggle()

                if vision_toggle.is_clicked(mouse_pos, mouse_clicked):
                    vision_toggle.toggle()

                if start_button.is_clicked(mouse_pos, mouse_clicked):
                    model_name = model_input.value if model_input.value else "model"
                    episodes = episodes_input.value if episodes_input.value else "1000"
                    first_layer = first_layer_input.value if first_layer_input.value else "32"
                    second_layer = second_layer_input.value if second_layer_input.value else "16"

                    cmd_args = []
                    if not graphics_toggle.state:
                        cmd_args.append("--no_graphics")
                    if vision_toggle.state:
                        cmd_args.append("--show_vision")
                    cmd_args.extend([
                        f"--episodes={episodes}",
                        f"--first_layer={first_layer}",
                        f"--second_layer={second_layer}",
                        f"--name={model_name}"
                    ])

                    pygame.quit()
                    return cmd_args, False

                if eval_button.is_clicked(mouse_pos, mouse_clicked):
                    cmd_args = ["--evaluation_mode"]
                    if not graphics_toggle.state:
                        cmd_args.append("--no_graphics")

                    model_name = model_input.value if model_input.value else "model"
                    cmd_args.append(f"--name={model_name}")

                    model_path = os.path.join("models", model_name, "best_model.keras")
                    if os.path.exists(model_path):
                        cmd_args.append(f"--load_model={model_path}")

                    pygame.quit()
                    return cmd_args, True

        start_button.is_hovered(mouse_pos)
        eval_button.is_hovered(mouse_pos)

        screen.fill(bg_color)

        title_surf = title_font.render("Learn2Slither", True, (255, 255, 255))
        screen.blit(title_surf, (screen.get_width()//2 - title_surf.get_width()//2, 30))

        subtitle_surf = subtitle_font.render("Configuration Panel", True, accent_color)
        screen.blit(subtitle_surf, (screen.get_width()//2 - subtitle_surf.get_width()//2, 70))

        panel_rect = pygame.Rect(150, 110, 600, 370)
        pygame.draw.rect(screen, panel_color, panel_rect, border_radius=15)
        pygame.draw.rect(screen, accent_color, panel_rect, 2, border_radius=15)

        for text_input in text_inputs:
            text_input.draw(screen, regular_font)

        graphics_toggle.draw(screen, regular_font)
        vision_toggle.draw(screen, regular_font)

        start_button.draw(screen, regular_font)
        eval_button.draw(screen, regular_font)

        footer_text = regular_font.render("Press ESC to quit", True, (150, 150, 150))
        screen.blit(footer_text, (20, screen.get_height() - 30))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    return None, False

if __name__ == "__main__":
    run_lobby()