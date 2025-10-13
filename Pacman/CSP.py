import pygame, time, os
from PIL import Image

# ===== SETTINGS =====
CELL_SIZE = 40
GRID_ROWS, GRID_COLS = 10, 15
WIDTH, HEIGHT = GRID_COLS * CELL_SIZE, GRID_ROWS * CELL_SIZE
DELAY_MS = 40
GIF_NAME = "CSP_FinalFilled.gif"

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("CSP Grid Coloring (White Start, Fully Filled End, 8-Neighbour)")
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 20)

# ===== LOAD TILE IMAGES =====
def load_scaled(path):
    img = pygame.image.load(path).convert_alpha()
    return pygame.transform.scale(img, (CELL_SIZE, CELL_SIZE))

# 4 tile textures act as 4 colors
TILE_IMAGES = [
    load_scaled("assets/wall.png"),
    load_scaled("assets/path.png"),
    load_scaled("assets/explore.png"),
    load_scaled("assets/black.png")
]
wall_img = load_scaled("assets/wall.png")

# ===== GRID =====
grid = [[0 for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]  # 0 = free, 1 = wall
frames = []

# ===== DRAWING =====
def draw_grid(assignment=None, highlight=None, backtrack=None, finalized=False):
    # Fill entire screen white first
    screen.fill((255, 255, 255))

    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            if grid[r][c] == 1:
                screen.blit(wall_img, (c * CELL_SIZE, r * CELL_SIZE))
            elif assignment and (r, c) in assignment:
                idx = assignment[(r, c)] % len(TILE_IMAGES)
                screen.blit(TILE_IMAGES[idx], (c * CELL_SIZE, r * CELL_SIZE))
            else:
                # keep white for unassigned cells during solving
                pygame.draw.rect(screen, (255, 255, 255),
                                 (c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    # highlight and backtrack outlines
    if highlight and grid[highlight[0]][highlight[1]] == 0:
        hr, hc = highlight
        pygame.draw.rect(screen, (255, 255, 0),
                         (hc * CELL_SIZE, hr * CELL_SIZE, CELL_SIZE, CELL_SIZE), 3)
    if backtrack and grid[backtrack[0]][backtrack[1]] == 0:
        br, bc = backtrack
        pygame.draw.rect(screen, (255, 0, 0),
                         (bc * CELL_SIZE, br * CELL_SIZE, CELL_SIZE, CELL_SIZE), 3)
    pygame.display.flip()

def msg(text):
    pygame.draw.rect(screen, (0,0,0), (0, HEIGHT-26, WIDTH, 26))
    surf = font.render(text, True, (255,255,0))
    screen.blit(surf, (10, HEIGHT-24))
    pygame.display.flip()

def save_frame():
    tmp = "frame_temp.png"
    if os.path.exists(tmp):
        os.remove(tmp)
    pygame.image.save(screen, tmp)
    while not os.path.exists(tmp):
        pygame.time.wait(5)
    im = Image.open(tmp).convert("RGB")
    frames.append(im.copy())
    im.close()

def pause():
    pygame.time.wait(DELAY_MS)

# ===== CSP HELPERS =====
def neighbors(r, c):
    # 8-connected adjacency
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            nr, nc = r + dr, c + dc
            if 0 <= nr < GRID_ROWS and 0 <= nc < GRID_COLS and grid[nr][nc] == 0:
                yield nr, nc

def variables():
    return [(r, c) for r in range(GRID_ROWS) for c in range(GRID_COLS) if grid[r][c] == 0]

def adjacency(vars_):
    adj = {v: set() for v in vars_}
    for v in vars_:
        r, c = v
        for n in neighbors(r, c):
            if n in adj:
                adj[v].add(n)
                adj[n].add(v)
    return adj

def is_consistent(var, val, assign, adj):
    return all(assign.get(n) != val for n in adj[var])

def select_var(assign, dom, adj):
    unassigned = [v for v in dom if v not in assign]
    if not unassigned:
        return None
    # MRV + Degree
    return min(unassigned, key=lambda v: (len(dom[v]), -len(adj[v])))

def order_vals(var, assign, dom, adj):
    def conflicts(val):
        return sum(val in dom[n] for n in adj[var] if n not in assign)
    return sorted(dom[var], key=conflicts)

def forward_check(var, val, assign, dom, adj):
    pruned = []
    for n in adj[var]:
        if n not in assign and val in dom[n]:
            dom[n].remove(val)
            pruned.append((n, val))
            if not dom[n]:
                return False, pruned
    return True, pruned

def backtrack(assign, dom, adj):
    if len(assign) == len(dom):
        return assign
    var = select_var(assign, dom, adj)
    draw_grid(assign, highlight=var)
    save_frame(); pause()

    for val in order_vals(var, assign, dom, adj):
        if is_consistent(var, val, assign, adj):
            assign[var] = val
            ok, pruned = forward_check(var, val, assign, dom, adj)
            draw_grid(assign, highlight=var)
            save_frame(); pause()
            if ok:
                res = backtrack(assign, dom, adj)
                if res:
                    return res
            for n, v in pruned:
                dom[n].add(v)
            del assign[var]
            draw_grid(assign, backtrack=var)
            save_frame(); pause()
    return None

def solve_csp():
    global frames
    frames = []
    vars_ = variables()
    if not vars_:
        return None, 0
    adj = adjacency(vars_)
    dom = {v: set(range(len(TILE_IMAGES))) for v in vars_}
    assign = {}

    draw_grid()
    save_frame()
    t1 = time.time()
    sol = backtrack(assign, dom, adj)
    t2 = time.time()

    if sol:
        draw_grid(sol, finalized=True)
        save_frame()
    return sol, (t2 - t1)

# ===== UI LOOP =====
def reset():
    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            grid[r][c] = 0

msg("Left-click: toggle wall | SPACE: solve | C: clear | ESC: quit")
draw_grid()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif pygame.mouse.get_pressed()[0]:
            x, y = pygame.mouse.get_pos()
            r, c = y // CELL_SIZE, x // CELL_SIZE
            grid[r][c] = 1 if grid[r][c] == 0 else 0
            draw_grid()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                msg("Solving CSP (8-connected)...")
                sol, elapsed = solve_csp()
                if sol:
                    print(f"✅ CSP solved in {elapsed:.3f}s, {len(sol)} tiles colored.")
                    frames[0].save(
                        GIF_NAME,
                        save_all=True,
                        append_images=frames[1:],
                        duration=DELAY_MS,
                        loop=0
                    )
                    msg(f"Done {elapsed:.2f}s — saved {GIF_NAME}")
                else:
                    print("❌ No solution.")
                    msg("No solution found.")
            elif event.key == pygame.K_c:
                reset(); draw_grid(); msg("Cleared.")
            elif event.key == pygame.K_ESCAPE:
                running = False
    clock.tick(60)

if os.path.exists("frame_temp.png"):
    os.remove("frame_temp.png")
pygame.quit()
