import heapq
from collections import deque
from typing import List, Tuple, Optional, Dict, Set
from utils import in_bounds, neighbors4, cell_cost, reconstruct_path, manhattan, Grid, Pos

def bfs(grid: Grid, start: Pos, goal: Pos):
    q = deque([start]); prev = {start: start}
    while q:
        u = q.popleft()
        if u == goal: return reconstruct_path(prev, start, goal)
        for v in neighbors4(u):
            if in_bounds(grid, v) and v not in prev and cell_cost(grid[v[0]][v[1]]) < float('inf'):
                prev[v] = u; q.append(v)
    return None

def dfs(grid: Grid, start: Pos, goal: Pos):
    stck = [start]; prev = {start: start}
    while stck:
        u = stck.pop()
        if u == goal: return reconstruct_path(prev, start, goal)
        for v in neighbors4(u):
            if in_bounds(grid, v) and v not in prev and cell_cost(grid[v[0]][v[1]]) < float('inf'):
                prev[v] = u; stck.append(v)
    return None

def ucs(grid: Grid, start: Pos, goal: Pos):
    pq = [(0.0, start)]; prev = {start: start}; dist = {start: 0.0}
    while pq:
        d, u = heapq.heappop(pq)
        if u == goal: return reconstruct_path(prev, start, goal)
        if d != dist[u]: continue
        for v in neighbors4(u):
            if not in_bounds(grid, v): continue
            w = cell_cost(grid[v[0]][v[1]])
            if w == float('inf'): continue
            nd = d + w
            if nd < dist.get(v, float('inf')):
                dist[v] = nd; prev[v] = u; heapq.heappush(pq, (nd, v))
    return None

def astar_with_trace(grid: Grid, start: Pos, goal: Pos):
    pq = [(manhattan(start, goal), 0.0, start)]
    prev = {start: start}; g = {start: 0.0}
    explored, frontier, snaps = set(), {start}, []
    while pq:
        f, gcost, u = heapq.heappop(pq)
        if gcost != g[u]: continue
        frontier.discard(u); explored.add(u)
        snaps.append((set(explored), set(frontier), u))
        if u == goal: return reconstruct_path(prev, start, goal), snaps
        for v in neighbors4(u):
            if not in_bounds(grid, v): continue
            w = cell_cost(grid[v[0]][v[1]])
            if w == float('inf'): continue
            ng = gcost + w
            if ng < g.get(v, float('inf')):
                g[v] = ng; prev[v] = u
                heapq.heappush(pq, (ng + manhattan(v, goal), ng, v))
                if v not in explored: frontier.add(v)
    return None, snaps

def manhattan(a: Pos, b: Pos) -> int:
    return abs(a[0]-b[0]) + abs(a[1]-b[1])
