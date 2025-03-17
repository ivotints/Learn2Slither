import pygame
import numpy as np
import math

def create_bokeh_surface(outer_radius, inner_radius, green):
    bokeh_surface = pygame.Surface((outer_radius * 2, outer_radius * 2), pygame.SRCALPHA)

    for x in range(outer_radius * 2):
        for y in range(outer_radius * 2):
            distance = math.sqrt((x - outer_radius)**2 + (y - outer_radius)**2)
            if distance <= outer_radius:
                # Calculate intensity based on distance
                if distance <= inner_radius:
                    intensity = 1.0
                else:
                    intensity = 1.0 - (distance - inner_radius) / (outer_radius - inner_radius)

                # Calculate bokeh color (green with alpha)
                color = (green[0], green[1], green[2], int(intensity * 255))  # Alpha value

                # Draw the pixel on the bokeh surface
                bokeh_surface.set_at((x, y), color)
    return bokeh_surface






pygame.init()

width, height = 800, 800
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Bokeh Effect")

green = (0, 255, 0)
white = (255, 255, 255)
gray = (128, 128, 128)

inner_radius = 30
outer_radius = 60

# Создаем боке
bokeh_surface = create_bokeh_surface(outer_radius, inner_radius, green)
bokeh_surface_white = create_bokeh_surface(inner_radius, 1, white)

# Главный цикл
clock = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False

    screen.fill(gray)

    # Отрисовка боке по центру
    screen.blit(bokeh_surface, (width // 2 - outer_radius, height // 2 - outer_radius))
    screen.blit(bokeh_surface_white, (width // 2 + 30 - inner_radius, height // 2 + 30 - inner_radius))

    pygame.display.flip()
    clock.tick(60)  # Ограничение FPS до 60

pygame.quit()
