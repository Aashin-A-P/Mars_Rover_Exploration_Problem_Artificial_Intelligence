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

# =========================
# Streamlit UI
# =========================
st.set_page_config(page_title="Smart City AI (Search)", layout="wide")
st.title("🚚 Smart City AI — Autonomous Delivery Robot")
st.caption("Edit the grid, then run BFS/DFS/UCS/A*")

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
tab1, = st.tabs(
    ["🔎 Search (BFS/DFS/UCS/A*)"]
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

st.divider()
st.markdown("**Tips**")
st.markdown("- Set exactly **one** `S` and **one** `D` on the grid.")
st.markdown("- `#` cells are impassable. `t` and `c` increase the **cost** (UCS/A* will prefer cheaper routes).")
st.markdown("- Use **Play** to watch animations. Use **Stop** to halt.")
st.markdown("- CSP Simulation shows `choose`, `assign`, `inconsistent`, `backtrack`, and `solution` steps.")
