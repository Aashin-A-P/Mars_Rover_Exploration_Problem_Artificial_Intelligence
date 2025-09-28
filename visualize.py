import pygame, sys, time
from PIL import Image

CELL_SIZE=60
COLORS={0:(210,180,140),1:(70,70,70),2:(0,200,0)}  # empty, crater, site

def draw_grid(screen,grid,rovers,path=None,goal=None):
    rows,cols=len(grid),len(grid[0])
    for x in range(rows):
        for y in range(cols):
            rect=pygame.Rect(y*CELL_SIZE,x*CELL_SIZE,CELL_SIZE,CELL_SIZE)

            # default color from grid
            color = COLORS[grid[x][y]]

            # highlight chosen goal (only for BFS/DFS/UCS/A*)
            if goal and (x,y)==goal:
                color = (200,0,0)  # red

            pygame.draw.rect(screen,color,rect)
            pygame.draw.rect(screen,(0,0,0),rect,1)

    # draw rovers
    for idx,r in enumerate(rovers):
        color=(0,0,255) if idx==0 else (255,100,0)
        pygame.draw.circle(screen,color,(r[1]*CELL_SIZE+CELL_SIZE//2,
                           r[0]*CELL_SIZE+CELL_SIZE//2),CELL_SIZE//3)

    # path highlight (yellow, final step purple)
    if path:
        for i,(px,py) in enumerate(path):
            rect = pygame.Rect(py*CELL_SIZE,px*CELL_SIZE,CELL_SIZE,CELL_SIZE)
            if i == len(path)-1:   # final step
                pygame.draw.rect(screen,(160,32,240),rect)  # purple
            else:
                pygame.draw.rect(screen,(255,255,0),rect)  # yellow

def capture_frame(screen,frames):
    data=pygame.image.tostring(screen,"RGB")
    img=Image.frombytes("RGB",screen.get_size(),data); frames.append(img)

def save_gif_file(frames,name,duration=300):
    if frames:
        frames[0].save(name,save_all=True,append_images=frames[1:],duration=duration,loop=0)
        print(f"GIF saved as {name}")

def animate_path(screen,grid,start,path,goal=None,save_gif=False,gif_name="path.gif"):
    frames=[]
    for step in path:
        for e in pygame.event.get():
            if e.type==pygame.QUIT: pygame.quit(); sys.exit()
        screen.fill((255,255,255))
        draw_grid(screen,grid,[step],path=path,goal=goal)
        pygame.display.flip()
        if save_gif: capture_frame(screen,frames)
        time.sleep(0.3)
    if save_gif: save_gif_file(frames,gif_name)

def animate_csp(screen,grid,rovers,assignment,search_fn,save_gif=False,gif_name="csp.gif"):
    frames=[]
    for rid,sites in assignment.items():
        start=rovers[rid]
        for site in sites:
            path=search_fn(grid,start,site)
            if path:
                for step in path:
                    for e in pygame.event.get():
                        if e.type==pygame.QUIT: pygame.quit(); sys.exit()
                    screen.fill((255,255,255))
                    draw_grid(screen,grid,[step]+[r for i,r in enumerate(rovers) if i!=rid])
                    pygame.display.flip()
                    if save_gif: capture_frame(screen,frames)
                    time.sleep(0.3)
                start=site
    if save_gif: save_gif_file(frames,gif_name)

def animate_adversarial(screen,grid,rover1,rover2,sites,search_depth=3,
                        save_gif=False,gif_name="adversarial.gif"):
    from adversarial_search import minimax
    positions=(rover1,rover2); collected={0:set(),1:set()}; frames=[]
    while sites:
        for player in [0,1]:
            score,move=minimax(grid,sites,positions,depth=search_depth,
                               alpha=float("-inf"),beta=float("inf"),maximizing_player=player)
            if move:
                np=list(positions); np[player]=move; positions=tuple(np)
                if move in sites: collected[player].add(move); sites.remove(move)
                for e in pygame.event.get():
                    if e.type==pygame.QUIT: pygame.quit(); sys.exit()
                screen.fill((255,255,255))
                draw_grid(screen,grid,[positions[0],positions[1]])
                pygame.display.flip()
                if save_gif: capture_frame(screen,frames)
                time.sleep(0.5)
            if not sites: break
    if save_gif: save_gif_file(frames,gif_name,duration=400)
    print("Final Scores: NASA =",len(collected[0]),"ISRO =",len(collected[1]))
