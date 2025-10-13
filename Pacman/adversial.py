import pygame, math, os
from PIL import Image

# ===== SETTINGS =====
CELL_SIZE = 40
ROWS, COLS = 10, 15
WIDTH, HEIGHT = COLS * CELL_SIZE, ROWS * CELL_SIZE + 40
DEPTH_LIMIT = 4
GIF_NAME = "Adversarial_Pacman.gif"

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Adversarial Search - Pacman vs 1 Ghost")
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 20)

# ===== LOAD SPRITES =====
def load_scaled(path):
    img = pygame.image.load(path).convert_alpha()
    return pygame.transform.scale(img, (CELL_SIZE, CELL_SIZE))

floor_img   = load_scaled("assets/floor.png")
wall_img    = load_scaled("assets/wall.png")
pacman_img  = load_scaled("assets/pacman.png")
ghost_img   = load_scaled("assets/ghost.png")
pellet_img  = load_scaled("assets/pellet.png")

# ===== PREDEFINED GRID =====
# 0 = floor, 1 = wall, 2 = pacman, 3 = pellet, 4 = ghost
grid = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,4,3,0,0,0,1,0,3,0,0,0,0,3,1],
    [1,0,1,1,1,0,1,0,1,1,1,0,1,0,1],
    [1,0,3,0,0,0,0,0,0,3,0,0,0,0,1],
    [1,0,1,1,1,1,0,1,1,1,1,1,0,1,1],
    [1,0,0,0,3,0,0,3,0,0,0,0,0,0,1],
    [1,1,1,0,1,1,0,1,1,1,1,0,1,0,1],
    [1,0,0,0,0,3,0,0,0,3,0,0,0,0,1],
    [1,0,1,0,1,0,0,1,0,0,1,0,3,0,1],
    [1,2,0,0,1,0,0,0,0,0,1,0,0,0,1],
]

frames = []
pacman = None
ghost = None
pellets = []

for r in range(ROWS):
    for c in range(COLS):
        if grid[r][c] == 2:
            pacman = (r, c)
        elif grid[r][c] == 4:
            ghost = (r, c)
        elif grid[r][c] == 3:
            pellets.append((r, c))

# ===== DRAW =====
def draw_grid():
    for r in range(ROWS):
        for c in range(COLS):
            screen.blit(floor_img, (c * CELL_SIZE, r * CELL_SIZE))
            val = grid[r][c]
            if val == 1:
                screen.blit(wall_img, (c * CELL_SIZE, r * CELL_SIZE))
            elif val == 2:
                screen.blit(pacman_img, (c * CELL_SIZE, r * CELL_SIZE))
            elif val == 3:
                screen.blit(pellet_img, (c * CELL_SIZE, r * CELL_SIZE))
            elif val == 4:
                screen.blit(ghost_img, (c * CELL_SIZE, r * CELL_SIZE))
    pygame.display.flip()

def save_frame():
    tmp = "frame_temp.png"
    pygame.image.save(screen, tmp)
    im = Image.open(tmp).convert("RGB")
    frames.append(im.copy())
    im.close()

def msg(text):
    pygame.draw.rect(screen, (0, 0, 0), (0, HEIGHT - 40, WIDTH, 40))
    surf = font.render(text, True, (255, 255, 0))
    screen.blit(surf, (10, HEIGHT - 30))
    pygame.display.flip()

# ===== HELPERS =====
def valid_moves(pos):
    r, c = pos
    moves = []
    for dr, dc in [(1,0),(-1,0),(0,1),(0,-1)]:
        nr, nc = r + dr, c + dc
        if 0 <= nr < ROWS and 0 <= nc < COLS and grid[nr][nc] != 1:
            moves.append((nr, nc))
    return moves

def manhattan(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

def evaluate_state(pac, ghost, pellets):
    score = 0
    if pellets:
        d_pellet = min(manhattan(pac, p) for p in pellets)
        score += 10 / (1 + d_pellet)
    if ghost:
        d_ghost = manhattan(pac, ghost)
        score -= 5 / (1 + d_ghost)
    if pac in pellets:
        score += 10
    return score

# ===== MINIMAX =====
def minimax(pac, ghost, pellets, depth, alpha, beta, maximizing):
    if depth == 0 or not pellets:
        return evaluate_state(pac, ghost, pellets), None

    if maximizing:  # Pacman turn
        best_val, best_move = -math.inf, None
        for move in valid_moves(pac):
            new_pellets = [p for p in pellets if p != move]
            val, _ = minimax(move, ghost, new_pellets, depth - 1, alpha, beta, False)
            if val > best_val:
                best_val, best_move = val, move
            alpha = max(alpha, best_val)
            if beta <= alpha:
                break
        return best_val, best_move
    else:  # Ghost turn
        best_val = math.inf
        gmoves = valid_moves(ghost)
        if not gmoves:
            return evaluate_state(pac, ghost, pellets), None
        new_ghost = min(gmoves, key=lambda m: manhattan(m, pac))
        if new_ghost == pac:
            return -999, None
        val, _ = minimax(pac, new_ghost, pellets, depth - 1, alpha, beta, True)
        best_val = min(best_val, val)
        beta = min(beta, best_val)
        return best_val, None

# ===== SIMULATION =====
def simulate_game(pac, ghost, pellets):
    total_score = 0
    step = 0
    draw_grid()
    save_frame()

    while pellets and step < 80:
        _, move = minimax(pac, ghost, pellets, DEPTH_LIMIT, -math.inf, math.inf, True)
        if not move:
            break

        grid[pac[0]][pac[1]] = 0
        pac = move

        if pac in pellets:
            pellets.remove(pac)
            total_score += 10

        if pac == ghost:
            msg(f"❌ Caught! Final Score: {total_score}")
            grid[pac[0]][pac[1]] = 2
            draw_grid(); save_frame()
            return total_score

        grid[pac[0]][pac[1]] = 2

        # Ghost move
        grid[ghost[0]][ghost[1]] = 0
        gmoves = valid_moves(ghost)
        if gmoves:
            ghost = min(gmoves, key=lambda m: manhattan(m, pac))
        grid[ghost[0]][ghost[1]] = 4

        if pac == ghost:
            msg(f"❌ Caught! Final Score: {total_score}")
            draw_grid(); save_frame()
            return total_score

        draw_grid()
        save_frame()
        step += 1

    msg(f"✅ Game Over | Score: {total_score}")
    save_frame()
    return total_score

# ===== MAIN LOOP =====
msg("🟡 Edit: LeftClick=Wall | P=Pacman | G=Ghost | O=Pellet | SPACE=Run | ESC=Quit")
draw_grid()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            if y < ROWS * CELL_SIZE:
                r, c = y // CELL_SIZE, x // CELL_SIZE
                if event.button == 1:
                    grid[r][c] = 1 if grid[r][c] == 0 else 0
                    draw_grid()

        elif event.type == pygame.KEYDOWN:
            x, y = pygame.mouse.get_pos()
            if y >= ROWS * CELL_SIZE:
                continue
            r, c = y // CELL_SIZE, x // CELL_SIZE

            if event.key == pygame.K_p:
                for rr in range(ROWS):
                    for cc in range(COLS):
                        if grid[rr][cc] == 2:
                            grid[rr][cc] = 0
                pacman = (r, c)
                grid[r][c] = 2

            elif event.key == pygame.K_g:
                # Only one ghost allowed
                if ghost:
                    grid[ghost[0]][ghost[1]] = 0
                ghost = (r, c)
                grid[r][c] = 4

            elif event.key == pygame.K_o:
                pellets.append((r, c))
                grid[r][c] = 3

            elif event.key == pygame.K_SPACE and pacman and ghost and pellets:
                msg("Running Adversarial Search...")
                pygame.display.flip()
                score = simulate_game(pacman, ghost, pellets)
                frames[0].save(GIF_NAME, save_all=True, append_images=frames[1:], duration=200, loop=0)
                print(f"🎞 Simulation Done | Final Score: {score}")
                running = False

            elif event.key == pygame.K_ESCAPE:
                running = False

        draw_grid()
        msg("🟡 Edit: LeftClick=Wall | P=Pacman | G=Ghost | O=Pellet | SPACE=Run | ESC=Quit")

    clock.tick(60)

if os.path.exists("frame_temp.png"):
    os.remove("frame_temp.png")
pygame.quit()
