import pygame

def handle_ui_events(graphics, step_by_step_mode, wait_for_step, fps):
    running = True

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_x:
                graphics.show_vision = not graphics.show_vision
            elif event.key >= pygame.K_0 and event.key <= pygame.K_9:
                key_num = event.key - pygame.K_0
                if key_num == 0:
                    step_by_step_mode = True
                    wait_for_step = True
                    print("Step-by-step mode enabled. Press SPACE to advance.")
                elif key_num == 9:
                    step_by_step_mode = False
                    fps = 0  # 0 means unlimited FPS (no delay)
                    print("Unlimited speed mode enabled")
                else:
                    step_by_step_mode = False
                    fps = 2 + (key_num - 1) * 3
                    print(f"Speed set to {fps} fps")
            elif event.key == pygame.K_SPACE and step_by_step_mode:
                wait_for_step = False

    return running, step_by_step_mode, wait_for_step, fps