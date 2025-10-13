import streamlit as st
import pandas as pd
import numpy as np
import heapq, time
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
from collections import deque, defaultdict
from typing import List, Tuple, Dict, Optional, Set
import networkx as nx  # NEW: for CSP graph visualization

# =========================
# Types & Costs
# =========================
Grid = List[List[str]]
Pos = Tuple[int, int]
COST = {'.': 1, 't': 3, 'c': 5}  # road, traffic, construction

CELL_OPTIONS = ['.', 't', 'c', '#', 'S', 'D']
CELL_LABELS = {
    '.': 'Road (1)',
    't': 'Traffic (3)',
    'c': 'Construction (5)',
    '#': 'Wall',
    'S': 'Start',
    'D': 'Destination'
}

# =========================
# Helpers
# =========================
def parse_df_to_grid(df: pd.DataFrame) -> Tuple[Grid, Pos, Pos]:
    grid = df.astype(str).values.tolist()
    start = goal = (-1, -1)
    for r, row in enumerate(grid):
        for c, ch in enumerate(row):
            if ch == 'S':
                start = (r, c)
                grid[r][c] = '.'
            elif ch == 'D':
                goal = (r, c)
                grid[r][c] = '.'
    if start == (-1, -1) or goal == (-1, -1):
        raise ValueError("Please place exactly one 'S' (start) and one 'D' (destination) on the grid.")
    return grid, start, goal

def in_bounds(grid: Grid, p: Pos) -> bool:
    r, c = p
    return 0 <= r < len(grid) and 0 <= c < len(grid[0])

def neighbors4(p: Pos) -> List[Pos]:
    r, c = p
    return [(r-1, c), (r+1, c), (r, c-1), (r, c+1)]

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

def path_cost(grid: Grid, path: Optional[List[Pos]]) -> Optional[float]:
    if not path:
        return None
    return sum(cell_cost(grid[r][c]) for (r, c) in (path[1:] if path else []))

# Encodings for a fast image render
def encode_grid(grid: Grid) -> np.ndarray:
    enc = {'.':0, 't':1, 'c':2, '#':3}
    H, W = len(grid), len(grid[0])
    img = np.zeros((H, W), dtype=int)
    for r in range(H):
        for c in range(W):
            img[r, c] = enc.get(grid[r][c], 0)
    return img

# =========================
# Searches (BFS/DFS/UCS/A*)
# =========================
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
    stck = [start]
    prev = {start: start}
    while stck:
        u = stck.pop()
        if u == goal:
            return reconstruct_path(prev, start, goal)
        for v in neighbors4(u):
            if in_bounds(grid, v) and v not in prev and cell_cost(grid[v[0]][v[1]]) < float('inf'):
                prev[v] = u
                stck.append(v)
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

def manhattan(a: Pos, b: Pos) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def astar_with_trace(grid: Grid, start: Pos, goal: Pos):
    """A* that yields snapshots of (explored, frontier, current) for animation."""
    pq = [(manhattan(start, goal), 0.0, start)]
    prev = {start: start}
    g = {start: 0.0}
    explored = set()
    frontier = {start}
    snaps = []  # list of (explored_copy, frontier_copy, current)
    while pq:
        f, gcost, u = heapq.heappop(pq)
        if gcost != g[u]:
            continue
        frontier.discard(u)
        explored.add(u)
        snaps.append((set(explored), set(frontier), u))
        if u == goal:
            path = reconstruct_path(prev, start, goal)
            return path, snaps
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
                heapq.heappush(pq, (ng + manhattan(v, goal), ng, v))
                if v not in explored:
                    frontier.add(v)
    return None, snaps

# =========================
# CSP (Map Coloring) + traced solver
# =========================
class CSP:
    def __init__(self, variables: List[str], domains: Dict[str, Set[str]], adj: Dict[str, Set[str]]):
        self.vars = variables
        self.domains = {v: set(domains[v]) for v in variables}
        self.adj = {v: set(adj.get(v, set())) for v in variables}

    def select_unassigned_var(self, assignment: Dict[str, str]) -> str:
        un = [v for v in self.vars if v not in assignment]
        return min(un, key=lambda v: len(self.domains[v]))  # MRV

    def is_consistent(self, v: str, val: str, assignment: Dict[str, str]) -> bool:
        return all(assignment.get(n) != val for n in self.adj[v])

    def forward_check(self, v: str, val: str, assignment: Dict[str, str]) -> Dict[str, Set[str]]:
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
            res = self.backtrack(assignment)
            if res is not None:
                return res
            self.restore(pruned)
            del assignment[v]
        return None

    # NEW: traced backtracking that records steps for animation
    def backtrack_trace(self, assignment: Dict[str, str]):
        trace = []  # list of snapshots dicts: event, assignment, selected, tried, pruned
        def rec():
            if len(assignment) == len(self.vars):
                trace.append({"event":"solution", "assignment":assignment.copy(), "selected":None, "tried":None, "pruned":{}})
                return True
            v = self.select_unassigned_var(assignment)
            trace.append({"event":"choose", "assignment":assignment.copy(), "selected":v, "tried":None, "pruned":{}})
            for val in list(self.domains[v]):
                if not self.is_consistent(v, val, assignment):
                    trace.append({"event":"inconsistent", "assignment":assignment.copy(), "selected":v, "tried":val, "pruned":{}})
                    continue
                assignment[v] = val
                pruned = self.forward_check(v, val, assignment)
                trace.append({"event":"assign", "assignment":assignment.copy(), "selected":v, "tried":val, "pruned":{k:list(vs) for k,vs in pruned.items()}})
                if rec():
                    return True
                self.restore(pruned)
                assignment.pop(v, None)
                trace.append({"event":"backtrack", "assignment":assignment.copy(), "selected":v, "tried":val, "pruned":{k:list(vs) for k,vs in pruned.items()}})
            return False
        rec()
        return trace

# =========================
# Adversarial: Minimax + Alpha-Beta
# =========================
GamePos = Tuple[Pos, Pos, bool]

def legal_moves(grid: Grid, p: Pos) -> List[Pos]:
    moves = []
    for v in neighbors4(p):
        if in_bounds(grid, v) and cell_cost(grid[v[0]][v[1]]) < float('inf'):
            moves.append(v)
    return moves or [p]  # allow wait

def terminal(bot: Pos, drone: Pos, goal: Pos, max_steps: int, steps: int) -> Optional[int]:
    if bot == drone:
        return -1000
    if bot == goal:
        return 1000
    if steps >= max_steps:
        return 200 - manhattan(bot, goal) + (manhattan(bot, drone) // 2)
    return None

def heuristic(bot: Pos, drone: Pos, goal: Pos) -> int:
    return 100 - manhattan(bot, goal) + (manhattan(bot, drone) // 2)

def alphabeta(grid: Grid, state: GamePos, goal: Pos, depth: int, alpha: int, beta: int,
              steps: int, max_steps: int) -> Tuple[int, Optional[Pos]]:
    bot, drone, bot_turn = state
    term = terminal(bot, drone, goal, max_steps, steps)
    if term is not None:
        return term, None
    if depth == 0:
        return heuristic(bot, drone, goal), None
    if bot_turn:
        best = -10**9; best_move = None
        for m in legal_moves(grid, bot):
            val, _ = alphabeta(grid, (m, drone, False), goal, depth-1, alpha, beta, steps+1, max_steps)
            if val > best:
                best, best_move = val, m
            alpha = max(alpha, best)
            if beta <= alpha:
                break
        return best, best_move
    else:
        worst = 10**9; worst_move = None
        for m in legal_moves(grid, drone):
            val, _ = alphabeta(grid, (bot, m, True), goal, depth-1, alpha, beta, steps+1, max_steps)
            if val < worst:
                worst, worst_move = val, m
            beta = min(beta, worst)
            if beta <= alpha:
                break
        return worst, worst_move

def simulate_pursuit(grid: Grid, start: Pos, goal: Pos, drone_start: Pos, depth=4, max_steps=24):
    bot = start
    drone = drone_start
    steps = 0
    frames = [(bot, drone)]
    while steps < max_steps:
        _, move = alphabeta(grid, (bot, drone, True), goal, depth, -10**9, 10**9, steps, max_steps)
        bot = move or bot
        steps += 1
        frames.append((bot, drone))
        if bot == goal or bot == drone:
            break
        _, gmove = alphabeta(grid, (bot, drone, False), goal, depth, -10**9, 10**9, steps, max_steps)
        drone = gmove or drone
        steps += 1
        frames.append((bot, drone))
        if bot == goal or bot == drone:
            break
    return frames

# =========================
# Visualization (matplotlib)
# =========================
# Tile colormap: 0=road, 1=traffic, 2=construction, 3=wall, 4=explored, 5=frontier
TILE_CMAP = ListedColormap([
    "#d9d9d9",  # road
    "#f4b183",  # traffic
    "#b5651d",  # construction
    "#000000",  # wall
    "#9ec5fe",  # explored (blue-ish)
    "#ffe8a1",  # frontier (yellow-ish)
])
TILE_BOUNDS = [-0.5,0.5,1.5,2.5,3.5,4.5,5.5]
TILE_NORM = BoundaryNorm(TILE_BOUNDS, TILE_CMAP.N)

def build_overlay_image(grid: Grid,
                        explored: Optional[Set[Pos]]=None,
                        frontier: Optional[Set[Pos]]=None) -> np.ndarray:
    img = encode_grid(grid)
    if explored:
        for r,c in explored:
            if 0 <= r < img.shape[0] and 0 <= c < img.shape[1] and img[r,c] != 3:
                img[r,c] = 4
    if frontier:
        for r,c in frontier:
            if 0 <= r < img.shape[0] and 0 <= c < img.shape[1] and img[r,c] != 3:
                img[r,c] = 5
    return img

def render_plot(grid: Grid,
                path: Optional[List[Pos]],
                start: Pos,
                goal: Pos,
                explored: Optional[Set[Pos]]=None,
                frontier: Optional[Set[Pos]]=None,
                bot: Optional[Pos]=None,
                drone: Optional[Pos]=None,
                title: str=""):
    img = build_overlay_image(grid, explored, frontier)
    H, W = img.shape
    fig, ax = plt.subplots(figsize=(min(10, W*0.6), min(10, H*0.6)))
    ax.imshow(img, cmap=TILE_CMAP, norm=TILE_NORM, interpolation="none")
    ax.set_xticks(range(W)); ax.set_yticks(range(H))
    ax.set_xticklabels([]); ax.set_yticklabels([])
    ax.set_xlim(-0.5, W-0.5); ax.set_ylim(H-0.5, -0.5)
    ax.grid(color="white", linewidth=0.5, alpha=0.6)

    # Start / Goal markers
    ax.scatter([start[1]], [start[0]], marker="o", s=120, edgecolors="black", facecolors="#2ecc71", zorder=4, label="Start")
    ax.scatter([goal[1]],  [goal[0]],  marker="X", s=160, edgecolors="black", facecolors="#e74c3c", zorder=4, label="Destination")

    # Optional robot/drone markers
    if bot:
        ax.scatter([bot[1]], [bot[0]], marker="o", s=120, edgecolors="black", facecolors="#1f77b4", zorder=5, label="Robot")
    if drone:
        ax.scatter([drone[1]], [drone[0]], marker="s", s=120, edgecolors="black", facecolors="#8e44ad", zorder=5, label="Drone")

    # Final path as a polyline (S→…→D)
    if path and len(path) > 1:
        ys = [r for r,c in path]
        xs = [c for r,c in path]
        ax.plot(xs, ys, linewidth=3.5, color="#2ecc71", alpha=0.95, zorder=3, label="Path")

    ax.set_title(title or "Grid View")
    ax.legend(loc="upper left", fontsize=8, frameon=True)
    st.pyplot(fig, clear_figure=True)

# ---------- CSP viz helpers (graph animation) ----------
CSP_COLORS = ["#1abc9c", "#3498db", "#9b59b6", "#f1c40f", "#e67e22", "#e74c3c"]  # colors for windows

def get_window_color_map(windows: List[str]) -> Dict[str, str]:
    cmap = {}
    for i, w in enumerate(windows):
        cmap[w] = CSP_COLORS[i % len(CSP_COLORS)]
    return cmap

def render_csp_state(adj: Dict[str, Set[str]],
                     snapshot: Dict,
                     windows: List[str]):
    """
    Draw the zone graph with current partial assignment.
    snapshot fields: event, assignment, selected, tried, pruned
    """
    assign = snapshot["assignment"]
    selected, tried, event = snapshot.get("selected"), snapshot.get("tried"), snapshot.get("event")
    pruned = snapshot.get("pruned", {})

    G = nx.Graph()
    for u, nbrs in adj.items():
        for v in nbrs:
            G.add_edge(u, v)
    for u in adj:
        if u not in G:
            G.add_node(u)

    pos = nx.spring_layout(G, seed=42)  # stable-ish layout
    cmap = get_window_color_map(windows)

    # Node colors: assigned -> their color; unassigned -> light gray
    node_colors = []
    for n in G.nodes():
        if n in assign:
            node_colors.append(cmap.get(assign[n], "#cccccc"))
        else:
            node_colors.append("#dddddd")

    fig, ax = plt.subplots(figsize=(7, 5))
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, edgecolors="black", node_size=900, ax=ax)
    nx.draw_networkx_edges(G, pos, edge_color="#444444", width=1.5, ax=ax)
    nx.draw_networkx_labels(G, pos, font_color="white", font_size=10, ax=ax)

    # highlight selected variable
    if selected in G:
        nx.draw_networkx_nodes(G, pos, nodelist=[selected], node_color="none",
                               edgecolors="#2c3e50", linewidths=3, node_size=1000, ax=ax)

    # title/legend
    title = f"CSP {event}"
    if selected: title += f" — var: {selected}"
    if tried is not None: title += f", val: {tried}"
    ax.set_title(title)

    # mini legend
    y = 1.02
    for w, col in cmap.items():
        ax.text(0.0, y, f" {w} ", transform=ax.transAxes, fontsize=9,
                bbox=dict(fc=col, ec="black", alpha=0.9, boxstyle="round,pad=0.2"))
        y -= 0.06

    ax.axis("off")
    st.pyplot(fig, clear_figure=True)

    # Show pruning info for this step
    if pruned:
        st.caption("Forward-check pruning at this step:")
        st.json(pruned)

# =========================
# Streamlit UI
# =========================
st.set_page_config(page_title="Smart City AI (Search + CSP + Adversarial)", layout="wide")
st.title("🚚 Smart City AI — Autonomous Delivery Robot")
st.caption("Edit the grid, then run BFS/DFS/UCS/A*, CSP (solve & animate), and a robot-vs-drone adversarial simulation.")

# init session flags for autoplay
if "play_astar" not in st.session_state:
    st.session_state.play_astar = False
if "play_game" not in st.session_state:
    st.session_state.play_game = False
if "play_csp" not in st.session_state:  # NEW
    st.session_state.play_csp = False

with st.sidebar:
    st.header("Grid Settings")
    H = st.number_input("Rows",  min_value=4, max_value=25, value=8, step=1)
    W = st.number_input("Cols",  min_value=4, max_value=25, value=12, step=1)
    if "grid_df" not in st.session_state or st.button("Reset Grid"):
        # Initialize a sample map with a small opening
        base = [['.' for _ in range(W)] for _ in range(H)]
        for r in range(H):
            if r != H//2 and W > 5:
                base[r][5] = '#'
        base[min(2, H-1)][0] = 'S'
        base[min(2, H-1)][W-1] = 'D'
        st.session_state.grid_df = pd.DataFrame(base)

st.subheader("🧩 Edit the City Grid")
st.write("Use the table to set each cell: "
         + ", ".join([f"`{k}` = {v}" for k,v in CELL_LABELS.items()]))

# Build column configs with selectbox editors
col_config = {}
for c in st.session_state.grid_df.columns:
    col_config[c] = st.column_config.SelectboxColumn(
        "Cell",
        options=CELL_OPTIONS,
        required=True
    )

grid_df = st.data_editor(
    st.session_state.grid_df,
    key="grid_editor",
    height=min(600, 32*H+60),
    column_config=col_config
)

# Convert to grid
grid = None; start = None; goal = None
error_placeholder = st.empty()
try:
    grid, start, goal = parse_df_to_grid(grid_df)
except Exception as e:
    error_placeholder.error(str(e))

# Tabs for Search / A* Animation / CSP / Adversarial
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["🔎 Search (BFS/DFS/UCS/A*)", "✨ A* Explorer", "🗺️ CSP (Solve Once)", "🎬 CSP (Simulation)", "⚔️ Adversarial (Robot vs Drone)"]
)

with tab1:
    st.subheader("Run a Search Algorithm")
    algo = st.selectbox("Algorithm", ["BFS", "DFS", "UCS", "A*"])
    run = st.button("Run Search")
    if run and grid:
        if algo == "BFS":
            path = bfs(grid, start, goal)
        elif algo == "DFS":
            path = dfs(grid, start, goal)
        elif algo == "UCS":
            path = ucs(grid, start, goal)
        else:
            path, _ = astar_with_trace(grid, start, goal)

        st.write(f"**Path length (steps):** {len(path) if path else 'No path'}")
        st.write(f"**Path cost:** {path_cost(grid, path) if path else '—'}")

        # Visual plot (with line connecting S->D along the path)
        render_plot(grid, path, start, goal, title=f"{algo} Result")

with tab2:
    st.subheader("A* Frontier & Explored — Auto Play")
    if grid:
        path, snaps = astar_with_trace(grid, start, goal)
        total_frames = len(snaps) + (len(path) if path else 0)

        fps = st.slider("FPS", 1, 10, 3, help="Playback speed for auto-play")
        colA, colB = st.columns(2)
        with colA:
            if st.button("▶️ Play A*", use_container_width=True):
                st.session_state.play_astar = True
        with colB:
            if st.button("⏹ Stop A*", use_container_width=True):
                st.session_state.play_astar = False

        holder = st.empty()

        # Manual scrub fallback
        if not st.session_state.play_astar:
            frame = st.slider("Frame", 0, max(0, total_frames-1), 0)
            if frame < len(snaps):
                explored, frontier, current = snaps[frame]
                with holder:
                    render_plot(grid, None, start, goal, explored=explored, frontier=frontier, title=f"A* Expansion — step {frame}")
            else:
                k = frame - len(snaps) + 1
                show_path = path[:k] if path else None
                with holder:
                    render_plot(grid, show_path, start, goal, title="A* — drawing optimal path")
            st.write(f"**Optimal cost (A*):** {path_cost(grid, path) if path else 'No path'}")

        # Auto-play
        else:
            for frame in range(total_frames):
                if not st.session_state.play_astar:
                    break
                if frame < len(snaps):
                    explored, frontier, current = snaps[frame]
                    with holder:
                        render_plot(grid, None, start, goal, explored=explored, frontier=frontier, title=f"A* Expansion — step {frame}")
                else:
                    k = frame - len(snaps) + 1
                    show_path = path[:k] if path else None
                    with holder:
                        render_plot(grid, show_path, start, goal, title="A* — drawing optimal path")
                time.sleep(1.0 / fps)
            st.session_state.play_astar = False  # reset when finished

with tab3:
    st.subheader("CSP — Zone Delivery Windows (Solve Once)")
    st.write("Assign delivery windows (M1/M2/M3...) to zones so adjacent zones differ.")
    default_adj = {
        'Hospital': {'Market', 'ITPark'},
        'Market': {'Hospital', 'OldTown', 'ITPark'},
        'OldTown': {'Market', 'Stadium'},
        'ITPark': {'Hospital', 'Market', 'Stadium'},
        'Stadium': {'OldTown', 'ITPark'},
    }
    zones_txt = st.text_area("Zone adjacency (Python dict literal)", value=str(default_adj), height=160)
    windows = st.multiselect("Available windows", ['M1','M2','M3','M4'], default=['M1','M2','M3'])
    solve_csp = st.button("Solve CSP")
    if solve_csp:
        try:
            adj = eval(zones_txt, {"__builtins__": {}})  # simple for assignment context
            variables = list(adj.keys())
            domains = {v: set(windows) for v in variables}
            csp = CSP(variables, domains, adj)
            # Use traced solver; last snapshot with event 'solution' is the result
            trace = csp.backtrack_trace({})
            solution = None
            for snap in reversed(trace):
                if snap["event"] == "solution":
                    solution = snap["assignment"]; break
            if solution:
                st.success(f"Solution: {solution}")
            else:
                st.error("No solution with the given windows/adjacency.")
        except Exception as e:
            st.error(f"Invalid adjacency: {e}")

with tab4:
    st.subheader("CSP — Simulation (Animated)")
    default_adj_sim = {
        'Hospital': {'Market', 'ITPark'},
        'Market': {'Hospital', 'OldTown', 'ITPark'},
        'OldTown': {'Market', 'Stadium'},
        'ITPark': {'Hospital', 'Market', 'Stadium'},
        'Stadium': {'OldTown', 'ITPark'},
    }
    zones_txt2 = st.text_area("Zone adjacency for simulation", value=str(default_adj_sim), height=160, key="zones_sim")
    windows2 = st.multiselect("Windows", ['M1','M2','M3','M4'], default=['M1','M2','M3'], key="wins_sim")

    if st.button("Plan CSP Simulation"):
        try:
            adj2 = eval(zones_txt2, {"__builtins__": {}})
            variables = list(adj2.keys())
            domains = {v: set(windows2) for v in variables}
            csp2 = CSP(variables, domains, adj2)
            st.session_state.csp_trace = csp2.backtrack_trace({})
            st.session_state.csp_adj = adj2
            st.session_state.csp_windows = windows2
            st.success(f"Planned {len(st.session_state.csp_trace)} CSP steps.")
        except Exception as e:
            st.error(f"Invalid adjacency: {e}")

    fps_csp = st.slider("FPS (CSP)", 1, 10, 3)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("▶️ Play CSP", use_container_width=True):
            st.session_state.play_csp = True
    with c2:
        if st.button("⏹ Stop CSP", use_container_width=True):
            st.session_state.play_csp = False

    holder_csp = st.empty()
    trace = st.session_state.get("csp_trace", [])
    adj_show = st.session_state.get("csp_adj", default_adj_sim)
    win_show = st.session_state.get("csp_windows", ['M1','M2','M3'])

    if not trace:
        st.info("Click **Plan CSP Simulation** to generate steps.")
    else:
        if not st.session_state.play_csp:
            i = st.slider("Step", 0, len(trace)-1, 0)
            with holder_csp:
                render_csp_state(adj_show, trace[i], win_show)
        else:
            for i in range(len(trace)):
                if not st.session_state.play_csp:
                    break
                with holder_csp:
                    render_csp_state(adj_show, trace[i], win_show)
                time.sleep(1.0 / fps_csp)
            st.session_state.play_csp = False  # reset when finished

with tab5:
    st.subheader("Robot vs Drone — Auto Play")
    dr_r = st.number_input("Drone Start Row", min_value=0, max_value=max(0, (grid_df.shape[0]-1)), value=0)
    dr_c = st.number_input("Drone Start Col", min_value=0, max_value=max(0, (grid_df.shape[1]-1)), value=0)
    depth = st.slider("Search Depth", 2, 6, 4)
    max_steps = st.slider("Max Steps", 6, 60, 24)
    frames = []
    if st.button("Plan Simulation"):
        if grid:
            frames = simulate_pursuit(grid, start, goal, (int(dr_r), int(dr_c)), depth=depth, max_steps=max_steps)
            st.session_state.sim_frames = frames

    fps2 = st.slider("FPS (Adversarial)", 1, 10, 2)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("▶️ Play Simulation", use_container_width=True):
            st.session_state.play_game = True
    with c2:
        if st.button("⏹ Stop Simulation", use_container_width=True):
            st.session_state.play_game = False

    holder2 = st.empty()
    frames = st.session_state.get("sim_frames", [])

    if not frames:
        st.info("Click **Plan Simulation** to generate frames first.")
    else:
        if not st.session_state.play_game:
            k = st.slider("Frame", 0, len(frames)-1, 0)
            bot, drone = frames[k]
            with holder2:
                render_plot(grid, None, start, goal, bot=bot, drone=drone, title=f"Adversarial — frame {k}")
            if bot == drone:
                st.error("Drone caught the robot!")
            elif bot == goal:
                st.success("Delivered!")
        else:
            for k in range(len(frames)):
                if not st.session_state.play_game:
                    break
                bot, drone = frames[k]
                with holder2:
                    render_plot(grid, None, start, goal, bot=bot, drone=drone, title=f"Adversarial — frame {k}")
                if bot == drone:
                    st.error("Drone caught the robot!")
                    break
                elif bot == goal:
                    st.success("Delivered!")
                    break
                time.sleep(1.0 / fps2)
            st.session_state.play_game = False  # reset

st.divider()
st.markdown("**Tips**")
st.markdown("- Set exactly **one** `S` and **one** `D` on the grid.")
st.markdown("- `#` cells are impassable. `t` and `c` increase the **cost** (UCS/A* will prefer cheaper routes).")
st.markdown("- Use **Play** to watch animations. Use **Stop** to halt.")
st.markdown("- CSP Simulation shows `choose`, `assign`, `inconsistent`, `backtrack`, and `solution` steps.")
