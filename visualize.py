import pygame
import sys
import time

CELL_SIZE = 60
COLORS = {
    0: (210, 180, 140),  # empty - sand
    1: (70, 70, 70),     # crater
    2: (0, 200, 0),      # site
}

def draw_grid(screen, grid, rovers, path=None):
    rows, cols = len(grid), len(grid[0])
    for x in range(rows):
        for y in range(cols):
            rect = pygame.Rect(y * CELL_SIZE, x * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, COLORS[grid[x][y]], rect)
            pygame.draw.rect(screen, (0, 0, 0), rect, 1)

    # draw rovers
    for idx, r in enumerate(rovers):
        pygame.draw.circle(screen, (0, 0, 255) if idx == 0 else (255, 100, 0),
                           (r[1] * CELL_SIZE + CELL_SIZE // 2, r[0] * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 3)

    # draw path
    if path:
        for (px, py) in path:
            pygame.draw.rect(screen, (255, 255, 0), (py * CELL_SIZE, px * CELL_SIZE, CELL_SIZE, CELL_SIZE))

def animate_path(screen, grid, rover, path):
    for step in path:
        screen.fill((255, 255, 255))
        draw_grid(screen, grid, [step])
        pygame.display.flip()
        time.sleep(0.3)

def run_visualization(grid, rovers, path=None):
    pygame.init()
    rows, cols = len(grid), len(grid[0])
    screen = pygame.display.set_mode((cols * CELL_SIZE, rows * CELL_SIZE))
    pygame.display.set_caption("Mars Rover Exploration")

    running = True
    while running:
        screen.fill((255, 255, 255))
        draw_grid(screen, grid, rovers, path)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
