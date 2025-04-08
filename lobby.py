import pygame
import os


class Button:
    def __init__(self, x, y, width, height, text, color=(50, 50, 50)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = (color[0]+20, color[1]+20, color[2]+20)

    def draw(self, surface, font):
        if self.is_hovered(pygame.mouse.get_pos()):
            color = self.hover_color
        else:
            color = self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        pygame.draw.rect(surface, (200, 200, 200),
                         self.rect, 2, border_radius=5)

        text_surf = font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_hovered(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

    def is_clicked(self, mouse_pos, mouse_clicked):
        return self.is_hovered(mouse_pos) and mouse_clicked


class TextInput:
    def __init__(self, x, y, width, height, label, value="", numeric=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.label = label
        self.value = str(value)
        self.active = False
        self.numeric = numeric

    def draw(self, surface, font):
        label_surf = font.render(self.label, True, (220, 220, 220))
        surface.blit(label_surf, (self.rect.x - 180, self.rect.y + 5))

        border_color = (180, 180, 180) if self.active else (100, 100, 100)
        pygame.draw.rect(surface, (40, 40, 50), self.rect, border_radius=5)
        pygame.draw.rect(surface, border_color, self.rect, 2, border_radius=5)

        text_surf = font.render(self.value, True, (255, 255, 255))
        surface.blit(text_surf, (self.rect.x + 5, self.rect.y + 5))

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

    def handle_key(self, event):
        if not self.active:
            return

        if event.key == pygame.K_BACKSPACE:
            self.value = self.value[:-1]
        elif self.numeric and event.unicode.isdigit():
            self.value += event.unicode
        elif not self.numeric and (event.unicode.isalnum()
                                   or event.unicode in "-_/.:"):
            self.value += event.unicode


class Toggle:
    def __init__(self, x, y, label, initial_state=False):
        self.rect = pygame.Rect(x, y, 40, 20)
        self.label = label
        self.state = initial_state

    def draw(self, surface, font):
        label_surf = font.render(self.label, True, (220, 220, 220))
        surface.blit(label_surf, (self.rect.x - 160, self.rect.y))

        bg_color = (60, 180, 100) if self.state else (60, 60, 60)
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=10)

        circle_x = self.rect.right - 10 if self.state else self.rect.left + 10
        pygame.draw.circle(surface, (240, 240, 240),
                           (circle_x, self.rect.centery), 8)

    def toggle(self, pos, click):
        if self.rect.collidepoint(pos) and click:
            self.state = not self.state
            return True
        return False


def run_lobby():
    pygame.init()
    screen = pygame.display.set_mode((700, 500))
    pygame.display.set_caption("Learn2Slither")

    font = pygame.font.Font(None, 28)
    title_font = pygame.font.Font(None, 36)

    train_button = Button(200, 400, 140, 40, "Train", (50, 120, 50))
    eval_button = Button(360, 400, 140, 40, "Evaluate", (50, 50, 120))

    inputs = [
        TextInput(270, 100, 200, 30, "Model Name:", "model"),
        TextInput(270, 140, 200, 30, "Episodes:", "10000", True),
        TextInput(270, 180, 200, 30, "First Layer:", "32", True),
        TextInput(270, 220, 200, 30, "Second Layer:", "16", True),
        TextInput(270, 260, 200, 30, "Map Width (3-24):", "10", True),
        TextInput(270, 300, 200, 30, "Map Height (3-13):", "10", True)
    ]
    active_input = None

    graphics_toggle = Toggle(250, 340, "Graphics:", True)
    vision_toggle = Toggle(450, 340, " Print State:", False)

    history_toggle = Toggle(250, 370, "Show History:", False)

    running = True
    clock = pygame.time.Clock()

    while running:
        screen.fill((25, 30, 40))
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN
                                             and event.key == pygame.K_ESCAPE):
                pygame.quit()
                return None, False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_clicked = True

                active_input = None
                for input_field in inputs:
                    if input_field.is_clicked(mouse_pos):
                        active_input = input_field
                        input_field.active = True
                    else:
                        input_field.active = False

                graphics_toggle.toggle(mouse_pos, mouse_clicked)
                vision_toggle.toggle(mouse_pos, mouse_clicked)
                history_toggle.toggle(mouse_pos, mouse_clicked)

                if train_button.is_clicked(mouse_pos, mouse_clicked):
                    model_name = inputs[0].value or "model"
                    episodes = inputs[1].value or "10000"
                    first_layer = inputs[2].value or "32"
                    second_layer = inputs[3].value or "16"
                    map_width = max(3, min(24, int(inputs[4].value or 10)))
                    map_height = max(3, min(13, int(inputs[5].value or 10)))

                    cmd_args = []
                    if not graphics_toggle.state:
                        cmd_args.append("--no_graphics")
                    if vision_toggle.state:
                        cmd_args.append("--show_vision")
                    if history_toggle.state:
                        cmd_args.append("--show_history")

                    cmd_args.extend([
                        f"--name={model_name}",
                        f"--episodes={episodes}",
                        f"--first_layer={first_layer}",
                        f"--second_layer={second_layer}",
                        f"--map_width={map_width}",
                        f"--map_height={map_height}"
                    ])

                    pygame.quit()
                    return cmd_args, False

                if eval_button.is_clicked(mouse_pos, mouse_clicked):
                    model_name = inputs[0].value or "model"
                    map_width = max(3, min(24, int(inputs[4].value or 10)))
                    map_height = max(3, min(13, int(inputs[5].value or 10)))
                    episodes = inputs[1].value or "10000"

                    cmd_args = ["--evaluation_mode"]
                    if not graphics_toggle.state:
                        cmd_args.append("--no_graphics")

                    model_path = os.path.join("models", model_name)
                    if os.path.exists(model_path):
                        cmd_args.append(f"--load_model={model_path}")

                    cmd_args.extend([
                        f"--name={model_name}",
                        f"--episodes={episodes}",
                        f"--map_width={map_width}",
                        f"--map_height={map_height}"
                    ])

                    pygame.quit()
                    return cmd_args, True

            elif event.type == pygame.KEYDOWN and active_input:
                active_input.handle_key(event)

        title = title_font.render("Configuration", True, (220, 220, 220))
        screen.blit(title, (screen.get_width()//2 - title.get_width()//2, 40))

        for input_field in inputs:
            input_field.draw(screen, font)

        graphics_toggle.draw(screen, font)
        vision_toggle.draw(screen, font)
        history_toggle.draw(screen, font)

        train_button.draw(screen, font)
        eval_button.draw(screen, font)

        instructions = font.render("Press ESC to exit", True, (150, 150, 150))
        screen.blit(instructions, (10, 470))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    return None, False
