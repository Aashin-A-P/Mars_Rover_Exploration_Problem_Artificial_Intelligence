from collections import deque
import heapq
import math

# Directions: Up, Down, Left, Right
MOVES = [(-1, 0), (1, 0), (0, -1), (0, 1)]

def is_valid(grid, x, y):
    """Check if a position is inside the grid and not a crater/obstacle."""
    rows, cols = len(grid), len(grid[0])
    return 0 <= x < rows and 0 <= y < cols and grid[x][y] != 1  # 1 = obstacle


# =============================
# Breadth First Search (BFS)
# =============================
def bfs(grid, start, goal):
    queue = deque([start])
    visited = {start: None}  # parent tracking

    while queue:
        current = queue.popleft()

        if current == goal:
            return reconstruct_path(visited, start, goal)

        for dx, dy in MOVES:
            nx, ny = current[0] + dx, current[1] + dy
            if is_valid(grid, nx, ny) and (nx, ny) not in visited:
                visited[(nx, ny)] = current
                queue.append((nx, ny))

    return None  # no path found


# =============================
# Depth First Search (DFS)
# =============================
def dfs(grid, start, goal):
    stack = [start]
    visited = {start: None}

    while stack:
        current = stack.pop()

        if current == goal:
            return reconstruct_path(visited, start, goal)

        for dx, dy in MOVES:
            nx, ny = current[0] + dx, current[1] + dy
            if is_valid(grid, nx, ny) and (nx, ny) not in visited:
                visited[(nx, ny)] = current
                stack.append((nx, ny))

    return None


# =============================
# Uniform Cost Search (UCS)
# =============================
def ucs(grid, start, goal, cost_fn=None):
    if cost_fn is None:
        cost_fn = lambda x, y: 1  # default: all moves cost 1

    pq = [(0, start)]
    visited = {start: None}
    cost_so_far = {start: 0}

    while pq:
        cost, current = heapq.heappop(pq)

        if current == goal:
            return reconstruct_path(visited, start, goal)

        for dx, dy in MOVES:
            nx, ny = current[0] + dx, current[1] + dy
            if is_valid(grid, nx, ny):
                new_cost = cost_so_far[current] + cost_fn(nx, ny)
                if (nx, ny) not in cost_so_far or new_cost < cost_so_far[(nx, ny)]:
                    cost_so_far[(nx, ny)] = new_cost
                    visited[(nx, ny)] = current
                    heapq.heappush(pq, (new_cost, (nx, ny)))

    return None


# =============================
# A* Search
# =============================
def a_star(grid, start, goal, cost_fn=None, heuristic=None):
    if cost_fn is None:
        cost_fn = lambda x, y: 1
    if heuristic is None:
        heuristic = lambda x, y: abs(x - goal[0]) + abs(y - goal[1])  # Manhattan

    pq = [(0, start)]
    visited = {start: None}
    g_cost = {start: 0}

    while pq:
        f, current = heapq.heappop(pq)

        if current == goal:
            return reconstruct_path(visited, start, goal)

        for dx, dy in MOVES:
            nx, ny = current[0] + dx, current[1] + dy
            if is_valid(grid, nx, ny):
                new_g = g_cost[current] + cost_fn(nx, ny)
                if (nx, ny) not in g_cost or new_g < g_cost[(nx, ny)]:
                    g_cost[(nx, ny)] = new_g
                    f_val = new_g + heuristic(nx, ny)
                    visited[(nx, ny)] = current
                    heapq.heappush(pq, (f_val, (nx, ny)))

    return None


# =============================
# Helper: Path Reconstruction
# =============================
def reconstruct_path(visited, start, goal):
    path = []
    node = goal
    while node is not None:
        path.append(node)
        node = visited[node]
    path.reverse()
    return path
