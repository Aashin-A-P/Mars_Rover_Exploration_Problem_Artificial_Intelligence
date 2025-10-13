import pygame, time, os
from PIL import Image

# ===== INITIAL SETUP =====
CELL_SIZE = 60
DELAY_MS = 100
GIF_NAME = "CSP_N_Pacman.gif"

pygame.init()
font = pygame.font.SysFont("arial", 22)

def run_n_pacman(N):
    WIDTH, HEIGHT = N * CELL_SIZE, N * CELL_SIZE
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(f"CSP N-Pacman Problem (N={N})")
    clock = pygame.time.Clock()

    pacman_img = pygame.image.load("assets/pacman.png").convert_alpha()
    pacman_img = pygame.transform.scale(pacman_img, (CELL_SIZE, CELL_SIZE))
    floor_img = pygame.image.load("assets/floor.png").convert_alpha()
    floor_img = pygame.transform.scale(floor_img, (CELL_SIZE, CELL_SIZE))
    black_img = pygame.image.load("assets/black.png").convert_alpha()
    black_img = pygame.transform.scale(black_img, (CELL_SIZE, CELL_SIZE))

    frames = []

    def draw_grid(assignment=None, highlight=None, backtrack=None, final=False):
        screen.fill((255, 255, 255))
        for r in range(N):
            for c in range(N):
                screen.blit(floor_img, (c * CELL_SIZE, r * CELL_SIZE))
        if assignment:
            for r, c in assignment.items():
                screen.blit(pacman_img, (c * CELL_SIZE, r * CELL_SIZE))
        if highlight:
            pygame.draw.rect(screen, (255, 255, 0),
                             (highlight[1]*CELL_SIZE, highlight[0]*CELL_SIZE,
                              CELL_SIZE, CELL_SIZE), 3)
        if backtrack:
            pygame.draw.rect(screen, (255, 0, 0),
                             (backtrack[1]*CELL_SIZE, backtrack[0]*CELL_SIZE,
                              CELL_SIZE, CELL_SIZE), 3)
        pygame.display.flip()

    def save_frame():
        tmp = "frame_temp.png"
        if os.path.exists(tmp): os.remove(tmp)
        pygame.image.save(screen, tmp)
        while not os.path.exists(tmp):
            pygame.time.wait(5)
        im = Image.open(tmp).convert("RGB")
        frames.append(im.copy())
        im.close()

    def pause(): pygame.time.wait(DELAY_MS)

    # ===== CSP LOGIC =====
    # Variables: rows 0..N-1
    # Domain: all columns 0..N-1
    def is_consistent(row, col, assignment):
        for r, c in assignment.items():
            if c == col or abs(r - row) == abs(c - col):
                return False
        return True

    def select_unassigned_var(assignment, domains):
        unassigned = [r for r in range(N) if r not in assignment]
        return min(unassigned, key=lambda r: len(domains[r]))

    def order_domain_values(row, assignment, domains):
        return sorted(domains[row])

    def forward_check(row, col, assignment, domains):
        pruned = []
        for r in range(row+1, N):
            if col in domains[r]:
                domains[r].remove(col)
                pruned.append((r, col))
            diag1 = col + (r - row)
            diag2 = col - (r - row)
            if diag1 in domains[r]:
                domains[r].remove(diag1)
                pruned.append((r, diag1))
            if diag2 in domains[r]:
                domains[r].remove(diag2)
                pruned.append((r, diag2))
            if not domains[r]:
                return False, pruned
        return True, pruned

    def backtrack(assignment, domains):
        if len(assignment) == N:
            return assignment
        row = select_unassigned_var(assignment, domains)
        draw_grid(assignment, highlight=(row, 0))
        save_frame(); pause()

        for col in order_domain_values(row, assignment, domains):
            if is_consistent(row, col, assignment):
                assignment[row] = col
                ok, pruned = forward_check(row, col, assignment, domains)
                draw_grid(assignment, highlight=(row, col))
                save_frame(); pause()
                if ok:
                    result = backtrack(assignment, domains)
                    if result:
                        return result
                # backtrack
                for r, v in pruned:
                    domains[r].add(v)
                del assignment[row]
                draw_grid(assignment, backtrack=(row, col))
                save_frame(); pause()
        return None

    def solve_csp():
        assignment = {}
        domains = {r: set(range(N)) for r in range(N)}
        draw_grid()
        save_frame()
        t1 = time.time()
        result = backtrack(assignment, domains)
        t2 = time.time()
        if result:
            draw_grid(result)
            save_frame()
        return result, (t2 - t1)

    # ===== RUN =====
    msg = font.render(f"Solving N-Pacman for N={N}...", True, (255, 255, 0))
    screen.blit(msg, (10, HEIGHT - 25))
    pygame.display.flip()
    result, elapsed = solve_csp()
    if result:
        print(f"✅ Solved N={N} in {elapsed:.3f}s")
        frames[0].save(
            GIF_NAME,
            save_all=True,
            append_images=frames[1:],
            duration=DELAY_MS,
            loop=0
        )
        print(f"🎞️ Saved animation as {GIF_NAME}")
    else:
        print("❌ No solution found.")
    pygame.time.wait(1000)
    pygame.quit()

# ===== MAIN =====
if __name__ == "__main__":
    N = 0
    while N < 4 or N > 16:
        try:
            N = int(input("Enter number of Pac-Men (4–16): "))
        except:
            N = 0
    run_n_pacman(N)
