import pygame, sys, time
from PIL import Image

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

def animate_path(screen, grid, start, path, save_gif=False, gif_name="rover_path.gif"):
    frames = []
    for step in path:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

        screen.fill((255, 255, 255))
        draw_grid(screen, grid, [step])
        pygame.display.flip()

        # Save frame for GIF
        if save_gif:
            data = pygame.image.tostring(screen, "RGB")
            img = Image.frombytes("RGB", screen.get_size(), data)
            frames.append(img)

        time.sleep(0.3)

    # Save GIF after path animation
    if save_gif and frames:
        frames[0].save(gif_name, save_all=True, append_images=frames[1:], duration=300, loop=0)
        print(f"GIF saved as {gif_name}")
