"""
AI Assignment Starter Kit (Python)
Unique unified example: "Campus Courier"

Scenario
--------
You are building an autonomous courier bot for a university campus represented as a grid map.
- Cells may be: road (.), grass (g, higher cost), stairs (s, higher cost), obstacle (#), start (A), goal (B).
- The bot must find paths (Uninformed: BFS/DFS/UCS; Informed: A*).
- The campus is split into named zones forming an adjacency graph; we must assign Wi‑Fi channels (colors) to each zone so that adjacent zones differ (CSP: Map Coloring with Backtracking + MRV + Forward Checking).
- Adversarial Search: a guard (G) patrols the grid. The bot and guard move turn‑by‑turn. Use Minimax with Alpha‑Beta to choose the bot’s next move under a depth limit.

Run guide
---------
python campus_courier.py  # runs a small demo of all parts

You can tweak the MAP_STR, ZONES, and GAME parameters at the bottom.
"""
from __future__ import annotations
from collections import deque, defaultdict
import heapq
from typing import Tuple, List, Dict, Optional, Set

Grid = List[List[str]]
Pos = Tuple[int, int]

# -----------------------------
# Utilities
# -----------------------------

def parse_grid(map_str: str) -> Tuple[Grid, Pos, Pos]:
    grid = [list(row) for row in map_str.strip().splitlines()]
    start = goal = (-1, -1)
    for r, row in enumerate(grid):
        for c, ch in enumerate(row):
            if ch == 'A':
                start = (r, c)
                grid[r][c] = '.'
            elif ch == 'B':
                goal = (r, c)
                grid[r][c] = '.'
    if start == (-1, -1) or goal == (-1, -1):
        raise ValueError("Map must include 'A' (start) and 'B' (goal)")
    return grid, start, goal


def in_bounds(grid: Grid, p: Pos) -> bool:
    r, c = p
    return 0 <= r < len(grid) and 0 <= c < len(grid[0])


def neighbors4(p: Pos) -> List[Pos]:
    r, c = p
    return [(r-1, c), (r+1, c), (r, c-1), (r, c+1)]


# Terrain costs: road=1, grass=3, stairs=5, obstacle=inf
COST = {'.': 1, 'g': 3, 's': 5}


def cell_cost(ch: str) -> float:
    if ch == '#':
        return float('inf')
    return COST.get(ch, 1)


def reconstruct_path(prev: Dict[Pos, Pos], s: Pos, t: Pos) -> List[Pos]:
    path = []
    cur = t
    while cur != s:
        path.append(cur)
        cur = prev[cur]
    path.append(s)
    path.reverse()
    return path


# -----------------------------
# Uninformed Search
# -----------------------------

def bfs(grid: Grid, start: Pos, goal: Pos) -> Optional[List[Pos]]:
    q = deque([start])
    prev = {start: start}
    while q:
        u = q.popleft()
        if u == goal:
            return reconstruct_path(prev, start, goal)
        for v in neighbors4(u):
            if in_bounds(grid, v) and v not in prev and cell_cost(grid[v[0]][v[1]]) < float('inf'):
                prev[v] = u
                q.append(v)
    return None


def dfs(grid: Grid, start: Pos, goal: Pos) -> Optional[List[Pos]]:
    st = [start]
    prev = {start: start}
    while st:
        u = st.pop()
        if u == goal:
            return reconstruct_path(prev, start, goal)
        for v in neighbors4(u):
            if in_bounds(grid, v) and v not in prev and cell_cost(grid[v[0]][v[1]]) < float('inf'):
                prev[v] = u
                st.append(v)
    return None


def ucs(grid: Grid, start: Pos, goal: Pos) -> Optional[List[Pos]]:
    pq = [(0.0, start)]
    prev = {start: start}
    dist = {start: 0.0}
    while pq:
        d, u = heapq.heappop(pq)
        if u == goal:
            return reconstruct_path(prev, start, goal)
        if d != dist[u]:
            continue
        for v in neighbors4(u):
            if not in_bounds(grid, v):
                continue
            w = cell_cost(grid[v[0]][v[1]])
            if w == float('inf'):
                continue
            nd = d + w
            if nd < dist.get(v, float('inf')):
                dist[v] = nd
                prev[v] = u
                heapq.heappush(pq, (nd, v))
    return None


# -----------------------------
# Informed Search (A*)
# -----------------------------

def manhattan(a: Pos, b: Pos) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar(grid: Grid, start: Pos, goal: Pos) -> Optional[List[Pos]]:
    pq = [(manhattan(start, goal), 0.0, start)]  # (f, g, node)
    prev = {start: start}
    g = {start: 0.0}
    while pq:
        f, gcost, u = heapq.heappop(pq)
        if u == goal:
            return reconstruct_path(prev, start, goal)
        if gcost != g[u]:
            continue
        for v in neighbors4(u):
            if not in_bounds(grid, v):
                continue
            w = cell_cost(grid[v[0]][v[1]])
            if w == float('inf'):
                continue
            ng = gcost + w
            if ng < g.get(v, float('inf')):
                g[v] = ng
                prev[v] = u
                h = manhattan(v, goal)
                heapq.heappush(pq, (ng + h, ng, v))
    return None


# -----------------------------
# CSP: Map Coloring with MRV + Forward Checking
# -----------------------------
class CSP:
    def __init__(self, variables: List[str], domains: Dict[str, Set[str]], adj: Dict[str, Set[str]]):
        self.vars = variables
        self.domains = {v: set(domains[v]) for v in variables}
        self.adj = {v: set(adj.get(v, set())) for v in variables}

    def select_unassigned_var(self, assignment: Dict[str, str]) -> str:
        # MRV: choose var with smallest remaining domain
        unassigned = [v for v in self.vars if v not in assignment]
        return min(unassigned, key=lambda v: len(self.domains[v]))

    def is_consistent(self, v: str, val: str, assignment: Dict[str, str]) -> bool:
        for n in self.adj[v]:
            if n in assignment and assignment[n] == val:
                return False
        return True

    def forward_check(self, v: str, val: str, assignment: Dict[str, str]) -> Dict[str, Set[str]]:
        # reduce neighbor domains; return pruned dict for backtracking
        pruned: Dict[str, Set[str]] = defaultdict(set)
        for n in self.adj[v]:
            if n in assignment:
                continue
            for x in list(self.domains[n]):
                if x == val:
                    self.domains[n].remove(x)
                    pruned[n].add(x)
        return pruned

    def restore(self, pruned: Dict[str, Set[str]]):
        for var, vals in pruned.items():
            self.domains[var] |= vals

    def backtrack(self, assignment: Dict[str, str]) -> Optional[Dict[str, str]]:
        if len(assignment) == len(self.vars):
            return assignment
        v = self.select_unassigned_var(assignment)
        for val in list(self.domains[v]):
            if not self.is_consistent(v, val, assignment):
                continue
            assignment[v] = val
            pruned = self.forward_check(v, val, assignment)
            result = self.backtrack(assignment)
            if result is not None:
                return result
            self.restore(pruned)
            del assignment[v]
        return None


# -----------------------------
# Adversarial Search: Minimax with Alpha-Beta (Pursuit-Evasion)
# -----------------------------
# State: (bot_pos, guard_pos, bot_turn: bool)

GamePos = Tuple[Pos, Pos, bool]


def legal_moves(grid: Grid, p: Pos) -> List[Pos]:
    moves = []
    for v in neighbors4(p):
        if in_bounds(grid, v) and cell_cost(grid[v[0]][v[1]]) < float('inf'):
            moves.append(v)
    return moves or [p]  # allow wait if stuck


def terminal(bot: Pos, guard: Pos, goal: Pos, 
             max_steps: int, steps: int) -> Optional[int]:
    if bot == guard:
        return -1000  # caught
    if bot == goal:
        return 1000  # success
    if steps >= max_steps:
        # score by distance to goal minus distance from guard
        return 200 - manhattan(bot, goal) + (manhattan(bot, guard) // 2)
    return None


def heuristic(bot: Pos, guard: Pos, goal: Pos) -> int:
    return 100 - manhattan(bot, goal) + (manhattan(bot, guard) // 2)


def alphabeta(grid: Grid, state: GamePos, goal: Pos, depth: int, alpha: int, beta: int, 
              steps: int, max_steps: int) -> Tuple[int, Optional[Pos]]:
    bot, guard, bot_turn = state
    term = terminal(bot, guard, goal, max_steps, steps)
    if term is not None:
        return term, None
    if depth == 0:
        return heuristic(bot, guard, goal), None

    if bot_turn:
        best = -10**9
        best_move = None
        for m in legal_moves(grid, bot):
            val, _ = alphabeta(grid, (m, guard, False), goal, depth-1, alpha, beta, steps+1, max_steps)
            if val > best:
                best, best_move = val, m
            alpha = max(alpha, best)
            if beta <= alpha:
                break
        return best, best_move
    else:
        worst = 10**9
        worst_move = None
        for m in legal_moves(grid, guard):
            val, _ = alphabeta(grid, (bot, m, True), goal, depth-1, alpha, beta, steps+1, max_steps)
            if val < worst:
                worst, worst_move = val, m
            beta = min(beta, worst)
            if beta <= alpha:
                break
        return worst, worst_move


# -----------------------------
# Pretty printers
# -----------------------------

def path_to_str(grid: Grid, path: Optional[List[Pos]]) -> str:
    if not path:
        return "<no path>"
    g2 = [row[:] for row in grid]
    for r, c in path:
        g2[r][c] = '*'
    return "\n".join("".join(row) for row in g2)


def print_board(grid: Grid, bot: Pos, guard: Pos, goal: Pos) -> str:
    g2 = [row[:] for row in grid]
    br, bc = bot
    gr, gc = guard
    g2[br][bc] = 'A'
    g2[gr][gc] = 'G'
    g2[goal[0]][goal[1]] = 'B'
    return "\n".join("".join(row) for row in g2)


# -----------------------------
# Demo data (edit me)
# -----------------------------
MAP_STR = """
..g..#....
..g..#..s.
A.g..#..sB
..ggg#..s.
..ggg#....
"""

# Zones: map coloring graph (same campus, arbitrary partition names)
ZONES = {
    'Library': {'Quad', 'CSE'},
    'CSE': {'Library', 'Admin', 'Hostel'},
    'Admin': {'CSE', 'Hostel', 'Quad'},
    'Hostel': {'CSE', 'Admin'},
    'Quad': {'Library', 'Admin'}
}
COLORS = {"Red", "Green", "Blue"}

# Adversarial game settings
GUARD_START = (0, 0)
DEPTH = 4
MAX_STEPS = 20


# -----------------------------
# Main demo
# -----------------------------
if __name__ == "__main__":
    grid, start, goal = parse_grid(MAP_STR)

    print("=== MAP (A=start, B=goal, .=road, g=grass, s=stairs, #=wall) ===")
    print_board_str = print_board(grid, start, GUARD_START, goal)
    print(print_board_str)

    # --- Uninformed ---
    print("\n--- BFS path (unweighted shortest hops) ---")
    p = bfs(grid, start, goal)
    print(path_to_str(grid, p))

    print("\n--- DFS path (a depth-first solution) ---")
    p = dfs(grid, start, goal)
    print(path_to_str(grid, p))

    print("\n--- Uniform Cost Search (true min-cost using terrain costs) ---")
    p = ucs(grid, start, goal)
    print(path_to_str(grid, p))

    # --- Informed ---
    print("\n--- A* (Manhattan heuristic) ---")
    p = astar(grid, start, goal)
    print(path_to_str(grid, p))

    # --- CSP ---
    print("\n=== CSP: Map Coloring (Wi‑Fi channel assignment) ===")
    variables = list(ZONES.keys())
    domains = {v: set(COLORS) for v in variables}
    csp = CSP(variables, domains, ZONES)
    sol = csp.backtrack({})
    print("Solution:")
    print(sol)

    # --- Adversarial ---
    print("\n=== Adversarial Search: Bot vs Guard (Alpha‑Beta) ===")
    bot = start
    guard = GUARD_START
    steps = 0
    while steps < 6:  # show a few plies
        val, move = alphabeta(grid, (bot, guard, True), goal, DEPTH, -10**9, 10**9, steps, MAX_STEPS)
        bot = move or bot
        # Guard plays optimally next move as well (best reply)
        gval, gmove = alphabeta(grid, (bot, guard, False), goal, DEPTH, -10**9, 10**9, steps, MAX_STEPS)
        guard = gmove or guard
        steps += 2
        print(f"\nAfter {steps} plies:")
        print(print_board(grid, bot, guard, goal))
        if bot == guard:
            print("Bot got caught!")
            break
        if bot == goal:
            print("Bot reached goal!")
            break
