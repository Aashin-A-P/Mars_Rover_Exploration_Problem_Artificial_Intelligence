import pygame, sys, time

CELL_SIZE = 60
COLORS = {0: (210, 180, 140), 1: (70, 70, 70), 2: (0, 200, 0)}

def draw_grid(screen, grid, rovers, path=None):
    rows, cols = len(grid), len(grid[0])
    for x in range(rows):
        for y in range(cols):
            rect = pygame.Rect(y * CELL_SIZE, x * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, COLORS[grid[x][y]], rect)
            pygame.draw.rect(screen, (0, 0, 0), rect, 1)
    for idx, r in enumerate(rovers):
        color = (0, 0, 255) if idx == 0 else (255, 100, 0)
        pygame.draw.circle(screen, color,
                           (r[1] * CELL_SIZE + CELL_SIZE // 2, r[0] * CELL_SIZE + CELL_SIZE // 2),
                           CELL_SIZE // 3)
    if path:
        for (px, py) in path:
            pygame.draw.rect(screen, (255, 255, 0),
                             (py * CELL_SIZE, px * CELL_SIZE, CELL_SIZE, CELL_SIZE))

def animate_path(screen, grid, start, path):
    rover = start
    for step in path:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
        screen.fill((255, 255, 255))
        draw_grid(screen, grid, [step])
        pygame.display.flip()
        time.sleep(0.3)
