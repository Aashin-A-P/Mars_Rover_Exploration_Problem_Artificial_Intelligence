from collections import deque
import heapq

MOVES = [(-1,0),(1,0),(0,-1),(0,1)]

def is_valid(grid,x,y):
    rows,cols=len(grid),len(grid[0])
    return 0<=x<rows and 0<=y<cols and grid[x][y]!=1

def reconstruct_path(visited,start,goal):
    path,node=[],goal
    while node is not None:
        path.append(node); node=visited[node]
    path.reverse(); return path

def bfs(grid,start,goal):
    q=deque([start]); visited={start:None}
    while q:
        cur=q.popleft()
        if cur==goal: return reconstruct_path(visited,start,goal)
        for dx,dy in MOVES:
            nx,ny=cur[0]+dx,cur[1]+dy
            if is_valid(grid,nx,ny) and (nx,ny) not in visited:
                visited[(nx,ny)]=cur; q.append((nx,ny))
    return None

def dfs(grid,start,goal):
    stack=[start]; visited={start:None}
    while stack:
        cur=stack.pop()
        if cur==goal: return reconstruct_path(visited,start,goal)
        for dx,dy in MOVES:
            nx,ny=cur[0]+dx,cur[1]+dy
            if is_valid(grid,nx,ny) and (nx,ny) not in visited:
                visited[(nx,ny)]=cur; stack.append((nx,ny))
    return None

def ucs(grid,start,goal,cost_fn=lambda x,y:1):
    pq=[(0,start)]; visited={start:None}; cost_so_far={start:0}
    while pq:
        cost,cur=heapq.heappop(pq)
        if cur==goal: return reconstruct_path(visited,start,goal)
        for dx,dy in MOVES:
            nx,ny=cur[0]+dx,cur[1]+dy
            if is_valid(grid,nx,ny):
                new_cost=cost_so_far[cur]+cost_fn(nx,ny)
                if (nx,ny) not in cost_so_far or new_cost<cost_so_far[(nx,ny)]:
                    cost_so_far[(nx,ny)]=new_cost; visited[(nx,ny)]=cur
                    heapq.heappush(pq,(new_cost,(nx,ny)))
    return None

def a_star(grid,start,goal,cost_fn=lambda x,y:1,
           heuristic=lambda x,y,g=None: abs(x-g[0])+abs(y-g[1])):
    pq=[(0,start)]; visited={start:None}; g_cost={start:0}
    while pq:
        f,cur=heapq.heappop(pq)
        if cur==goal: return reconstruct_path(visited,start,goal)
        for dx,dy in MOVES:
            nx,ny=cur[0]+dx,cur[1]+dy
            if is_valid(grid,nx,ny):
                new_g=g_cost[cur]+cost_fn(nx,ny)
                if (nx,ny) not in g_cost or new_g<g_cost[(nx,ny)]:
                    g_cost[(nx,ny)]=new_g; visited[(nx,ny)]=cur
                    f_val=new_g+heuristic(nx,ny,goal)
                    heapq.heappush(pq,(f_val,(nx,ny)))
    return None
