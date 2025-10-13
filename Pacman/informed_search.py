import pygame
import heapq
import time
from PIL import Image

# --- SETTINGS ---
CELL_SIZE = 40
GRID_ROWS, GRID_COLS = 10, 15
WIDTH, HEIGHT = GRID_COLS * CELL_SIZE, GRID_ROWS * CELL_SIZE

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pac-Man A* Search (Sprite Mode)")
clock = pygame.time.Clock()

# --- GRID ---
grid = [[0 for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
start = None
goal = None
frames = []

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

# --- HEURISTIC ---
def heuristic(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

# --- DRAW GRID ---
def draw_grid():
    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            screen.blit(floor_img, (c*CELL_SIZE, r*CELL_SIZE))
            val = grid[r][c]
            if val == 1:
                screen.blit(wall_img, (c*CELL_SIZE, r*CELL_SIZE))
            elif val == 2:
                screen.blit(pacman_img, (c*CELL_SIZE, r*CELL_SIZE))
            elif val == 3:
                screen.blit(pellet_img, (c*CELL_SIZE, r*CELL_SIZE))
            elif val == 4:
                screen.blit(path_img, (c*CELL_SIZE, r*CELL_SIZE))
            elif val == 5:
                screen.blit(explore_img, (c*CELL_SIZE, r*CELL_SIZE))
    pygame.display.flip()

# --- HELPERS ---
def get_neighbors(node):
    r,c = node
    dirs = [(1,0),(-1,0),(0,1),(0,-1)]
    result=[]
    for dr,dc in dirs:
        nr,nc=r+dr,c+dc
        if 0<=nr<GRID_ROWS and 0<=nc<GRID_COLS and grid[nr][nc]!=1:
            result.append((nr,nc))
    return result

import os
from PIL import Image

def save_frame():
    temp_file = "frame_temp.png"

    if os.path.exists(temp_file):
        os.remove(temp_file)

    pygame.image.save(screen, temp_file)

    while not os.path.exists(temp_file):
        pygame.time.wait(10)

    try:
        frame_img = Image.open(temp_file).convert("RGB")
        frames.append(frame_img.copy())
        frame_img.close()
    except Exception as e:
        print(f"⚠️ Frame save error: {e}")


# --- A* ---
def a_star(start, goal):
    t1=time.time()
    open_set=[]
    heapq.heappush(open_set,(0,start))
    g_score={start:0}
    f_score={start:heuristic(start,goal)}
    came_from={}
    while open_set:
        _,current=heapq.heappop(open_set)
        if current==goal:
            return reconstruct_path(came_from,current,time.time()-t1)
        r,c=current
        if grid[r][c] not in (2,3):
            grid[r][c]=5
        draw_grid(); save_frame()
        for neighbor in get_neighbors(current):
            temp_g=g_score[current]+1
            if neighbor not in g_score or temp_g<g_score[neighbor]:
                came_from[neighbor]=current
                g_score[neighbor]=temp_g
                f_score[neighbor]=temp_g+heuristic(neighbor,goal)
                heapq.heappush(open_set,(f_score[neighbor],neighbor))
    return None, None

def reconstruct_path(came_from,current,elapsed):
    path=[current]
    while current in came_from:
        current=came_from[current]
        path.append(current)
    path.reverse()
    for r,c in path:
        if grid[r][c] not in (2,3):
            grid[r][c]=4
        draw_grid(); save_frame()
    return path, elapsed

# --- USER SETUP ---
font = pygame.font.SysFont("arial",20)
def msg(txt):
    pygame.draw.rect(screen,(0,0,0),(0,HEIGHT-25,WIDTH,25))
    text = font.render(txt,True,(255,255,0))
    screen.blit(text,(10,HEIGHT-22))
    pygame.display.flip()

instructions="Left-click: Wall | S: Start | G: Goal | SPACE: Run A* | ESC: Quit"
msg(instructions)
draw_grid()
running=True

while running:
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            running=False
        elif pygame.mouse.get_pressed()[0]:
            x,y=pygame.mouse.get_pos()
            r,c=y//CELL_SIZE,x//CELL_SIZE
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
            elif event.key==pygame.K_SPACE and start and goal:
                path,elapsed=a_star(start,goal)
                if path:
                    print(f"✅ Path found! Steps: {len(path)}  Time: {elapsed:.5f} sec")
                else:
                    print("❌ No path found.")
                frames[0].save("Astar_Pacman.gif",save_all=True,append_images=frames[1:],duration=200,loop=0)
                print("🎞️ Saved as Astar_Pacman.gif")
                running=False
            elif event.key==pygame.K_ESCAPE:
                running=False
    draw_grid()
    clock.tick(60)

pygame.quit()
