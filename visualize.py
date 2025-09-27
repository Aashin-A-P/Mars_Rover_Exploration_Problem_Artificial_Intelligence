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


def animate_csp(screen, grid, rovers, assignment, search_fn):
    """
    Animate multiple rovers moving to their assigned sites using a search function (e.g., BFS).
    rovers: list of starting rover positions
    assignment: dict {rover_idx: [sites]}
    """
    for rover_idx, sites in assignment.items():
        start = rovers[rover_idx]
        for site in sites:
            path = search_fn(grid, start, site)
            if path:
                for step in path:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit(); sys.exit()
                    screen.fill((255, 255, 255))
                    draw_grid(screen, grid, [step] + [r for i, r in enumerate(rovers) if i != rover_idx])
                    pygame.display.flip()
                    time.sleep(0.3)
                start = site  # update rover position after reaching site


def animate_adversarial(screen, grid, rover1, rover2, sites, search_depth=3):
    """
    Animate two rovers (NASA vs ISRO) competing for sites using minimax.
    """
    from adversarial_search import minimax
    positions = (rover1, rover2)
    collected = {0: set(), 1: set()}

    while sites:
        for player in [0, 1]:  # alternating turns
            score, move = minimax(grid, sites, positions, depth=search_depth,
                                  alpha=-math.inf, beta=math.inf, maximizing_player=player)
            if move:
                new_positions = list(positions)
                new_positions[player] = move
                positions = tuple(new_positions)
                if move in sites:
                    collected[player].add(move)
                    sites.remove(move)

                # animate move
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit(); sys.exit()
                screen.fill((255, 255, 255))
                draw_grid(screen, grid, [positions[0], positions[1]])
                pygame.display.flip()
                time.sleep(0.5)

            if not sites:  # stop when all sites are collected
                break

    print("Final Scores: NASA =", len(collected[0]), "ISRO =", len(collected[1]))

