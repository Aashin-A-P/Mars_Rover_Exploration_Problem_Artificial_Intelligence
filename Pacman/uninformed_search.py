import pygame, heapq, time, os
from collections import deque
from PIL import Image

# --- SETTINGS ---
CELL_SIZE = 40
GRID_ROWS, GRID_COLS = 10, 15
WIDTH, HEIGHT = GRID_COLS * CELL_SIZE, GRID_ROWS * CELL_SIZE

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pac-Man Uninformed Search (Run All Once)")
clock = pygame.time.Clock()

# --- GRID ---
grid = [[0 for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
start = None
goal = None

# --- ASSETS ---
def load_scaled(path):
    img = pygame.image.load(path).convert_alpha()
    return pygame.transform.scale(img, (CELL_SIZE, CELL_SIZE))

floor_img   = load_scaled("assets/floor.png")
wall_img    = load_scaled("assets/wall.png")
pacman_img  = load_scaled("assets/pacman.png")
pellet_img  = load_scaled("assets/pellet.png")
path_img    = load_scaled("assets/path.png")
explore_img = load_scaled("assets/explore.png")

# --- DRAW ---
def draw_grid():
    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            screen.blit(floor_img, (c*CELL_SIZE, r*CELL_SIZE))
            v = grid[r][c]
            if v == 1: screen.blit(wall_img, (c*CELL_SIZE, r*CELL_SIZE))
            elif v == 2: screen.blit(pacman_img, (c*CELL_SIZE, r*CELL_SIZE))
            elif v == 3: screen.blit(pellet_img, (c*CELL_SIZE, r*CELL_SIZE))
            elif v == 4: screen.blit(path_img, (c*CELL_SIZE, r*CELL_SIZE))
            elif v == 5: screen.blit(explore_img, (c*CELL_SIZE, r*CELL_SIZE))
    pygame.display.flip()

# --- HELPERS ---
def get_neighbors(node):
    r, c = node
    dirs = [(1,0),(-1,0),(0,1),(0,-1)]
    res = []
    for dr, dc in dirs:
        nr, nc = r+dr, c+dc
        if 0 <= nr < GRID_ROWS and 0 <= nc < GRID_COLS and grid[nr][nc] != 1:
            res.append((nr, nc))
    return res

def save_frame(frames):
    tmp = "frame_temp.png"
    if os.path.exists(tmp): os.remove(tmp)
    pygame.image.save(screen, tmp)
    while not os.path.exists(tmp):
        pygame.time.wait(10)
    try:
        img = Image.open(tmp).convert("RGB")
        frames.append(img.copy())
        img.close()
    except: pass

def reconstruct_path(came_from, current, elapsed, frames):
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    path.reverse()
    for r, c in path:
        if grid[r][c] not in (2,3):
            grid[r][c] = 4
        draw_grid(); save_frame(frames)
    return path, elapsed

# --- SEARCHES ---
def bfs(start, goal):
    frames=[]
    t1=time.time()
    queue=deque([start]); came_from={}; visited={start}
    while queue:
        current=queue.popleft()
        if current==goal:
            return reconstruct_path(came_from,current,time.time()-t1,frames),frames
        if grid[current[0]][current[1]] not in (2,3):
            grid[current[0]][current[1]]=5
        draw_grid(); save_frame(frames)
        for n in get_neighbors(current):
            if n not in visited:
                visited.add(n); came_from[n]=current; queue.append(n)
    return (None,None),frames

def dfs(start, goal):
    frames=[]
    t1=time.time()
    stack=[start]; came_from={}; visited=set()
    while stack:
        current=stack.pop()
        if current==goal:
            return reconstruct_path(came_from,current,time.time()-t1,frames),frames
        if current not in visited:
            visited.add(current)
            if grid[current[0]][current[1]] not in (2,3):
                grid[current[0]][current[1]]=5
            draw_grid(); save_frame(frames)
            for n in get_neighbors(current):
                if n not in visited:
                    came_from[n]=current; stack.append(n)
    return (None,None),frames

def ucs(start, goal):
    frames=[]
    t1=time.time()
    pq=[(0,start)]; came_from={}; cost={start:0}
    while pq:
        g,current=heapq.heappop(pq)
        if current==goal:
            return reconstruct_path(came_from,current,time.time()-t1,frames),frames
        if grid[current[0]][current[1]] not in (2,3):
            grid[current[0]][current[1]]=5
        draw_grid(); save_frame(frames)
        for n in get_neighbors(current):
            new_cost=g+1
            if n not in cost or new_cost<cost[n]:
                cost[n]=new_cost; came_from[n]=current
                heapq.heappush(pq,(new_cost,n))
    return (None,None),frames

# --- UI ---
font = pygame.font.SysFont("arial",20)
def msg(txt):
    pygame.draw.rect(screen,(0,0,0),(0,HEIGHT-25,WIDTH,25))
    text=font.render(txt,True,(255,255,0))
    screen.blit(text,(10,HEIGHT-22))
    pygame.display.flip()

msg("Left-click: Wall | S: Start | G: Goal | ENTER: Run All | ESC: Quit")
draw_grid()
running=True

while running:
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            running=False
        elif pygame.mouse.get_pressed()[0]:
            x,y=pygame.mouse.get_pos(); r,c=y//CELL_SIZE,x//CELL_SIZE
            if not start or (r,c)!=start and (r,c)!=goal:
                grid[r][c]=1
        elif event.type==pygame.KEYDOWN:
            if event.key==pygame.K_s:
                x,y=pygame.mouse.get_pos(); r,c=y//CELL_SIZE,x//CELL_SIZE
                if start: grid[start[0]][start[1]]=0
                start=(r,c); grid[r][c]=2
            elif event.key==pygame.K_g:
                x,y=pygame.mouse.get_pos(); r,c=y//CELL_SIZE,x//CELL_SIZE
                if goal: grid[goal[0]][goal[1]]=0
                goal=(r,c); grid[r][c]=3
            elif event.key==pygame.K_RETURN and start and goal:
                print("🏁 Running BFS, DFS, UCS on same grid...\n")
                base_grid=[row[:] for row in grid]

                # BFS
                grid=[row[:] for row in base_grid]
                (path,elapsed),frames=bfs(start,goal)
                if path:
                    print(f"✅ BFS Path found! Steps:{len(path)} Time:{elapsed:.4f}s")
                    frames[0].save("BFS_Pacman.gif",save_all=True,append_images=frames[1:],duration=200,loop=0)
                    print("🎞️ Saved BFS_Pacman.gif\n")

                # DFS
                grid=[row[:] for row in base_grid]
                (path,elapsed),frames=dfs(start,goal)
                if path:
                    print(f"✅ DFS Path found! Steps:{len(path)} Time:{elapsed:.4f}s")
                    frames[0].save("DFS_Pacman.gif",save_all=True,append_images=frames[1:],duration=200,loop=0)
                    print("🎞️ Saved DFS_Pacman.gif\n")

                # UCS
                grid=[row[:] for row in base_grid]
                (path,elapsed),frames=ucs(start,goal)
                if path:
                    print(f"✅ UCS Path found! Steps:{len(path)} Time:{elapsed:.4f}s")
                    frames[0].save("UCS_Pacman.gif",save_all=True,append_images=frames[1:],duration=200,loop=0)
                    print("🎞️ Saved UCS_Pacman.gif\n")

                if os.path.exists("frame_temp.png"):
                    os.remove("frame_temp.png")
                running=False
            elif event.key==pygame.K_ESCAPE:
                running=False

    draw_grid()
    clock.tick(60)

pygame.quit()
