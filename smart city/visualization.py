import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
import numpy as np
import networkx as nx
from typing import List, Dict, Optional, Set, Tuple

# ========= GRID VISUALIZATION =========
TILE_CMAP = ListedColormap([
    "#d9d9d9",  # road
    "#f4b183",  # traffic
    "#b5651d",  # construction
    "#000000",  # wall
    "#9ec5fe",  # explored (blue-ish)
    "#ffe8a1",  # frontier (yellow-ish)
])
TILE_BOUNDS = [-0.5, 0.5, 1.5, 2.5, 3.5, 4.5, 5.5]
TILE_NORM = BoundaryNorm(TILE_BOUNDS, TILE_CMAP.N)

def encode_grid(grid: List[List[str]]) -> np.ndarray:
    enc = {'.': 0, 't': 1, 'c': 2, '#': 3}
    H, W = len(grid), len(grid[0])
    img = np.zeros((H, W), dtype=int)
    for r in range(H):
        for c in range(W):
            img[r, c] = enc.get(grid[r][c], 0)
    return img

def build_overlay_image(grid, explored=None, frontier=None):
    img = encode_grid(grid)
    if explored:
        for r, c in explored:
            if 0 <= r < img.shape[0] and 0 <= c < img.shape[1] and img[r, c] != 3:
                img[r, c] = 4
    if frontier:
        for r, c in frontier:
            if 0 <= r < img.shape[0] and 0 <= c < img.shape[1] and img[r, c] != 3:
                img[r, c] = 5
    return img

def render_plot(grid, path, start, goal, explored=None, frontier=None,
                bot=None, drone=None, title=""):
    img = build_overlay_image(grid, explored, frontier)
    H, W = img.shape
    fig, ax = plt.subplots(figsize=(min(10, W * 0.6), min(10, H * 0.6)))
    ax.imshow(img, cmap=TILE_CMAP, norm=TILE_NORM, interpolation="none")
    ax.set_xticks(range(W)); ax.set_yticks(range(H))
    ax.set_xticklabels([]); ax.set_yticklabels([])
    ax.set_xlim(-0.5, W - 0.5); ax.set_ylim(H - 0.5, -0.5)
    ax.grid(color="white", linewidth=0.5, alpha=0.6)

    # Start & Destination markers
    ax.scatter([start[1]], [start[0]], marker="o", s=120, edgecolors="black", facecolors="#2ecc71", zorder=4, label="Start")
    ax.scatter([goal[1]], [goal[0]], marker="X", s=160, edgecolors="black", facecolors="#e74c3c", zorder=4, label="Destination")

    # Robot/Drone markers
    if bot:
        ax.scatter([bot[1]], [bot[0]], marker="o", s=120, edgecolors="black", facecolors="#1f77b4", zorder=5, label="Robot")
    if drone:
        ax.scatter([drone[1]], [drone[0]], marker="s", s=120, edgecolors="black", facecolors="#8e44ad", zorder=5, label="Drone")

    # Draw final path
    if path and len(path) > 1:
        ys = [r for r, c in path]
        xs = [c for r, c in path]
        ax.plot(xs, ys, linewidth=3.5, color="#2ecc71", alpha=0.95, zorder=3, label="Path")

    ax.set_title(title or "Grid View")
    ax.legend(loc="upper left", fontsize=8, frameon=True)
    st.pyplot(fig, clear_figure=True)

# ========= CSP VISUALIZATION =========
CSP_COLORS = ["#1abc9c", "#3498db", "#9b59b6", "#f1c40f", "#e67e22", "#e74c3c"]

def get_window_color_map(windows: List[str]) -> Dict[str, str]:
    return {w: CSP_COLORS[i % len(CSP_COLORS)] for i, w in enumerate(windows)}

def render_csp_state(adj: Dict[str, Set[str]], snapshot: Dict, windows: List[str]):
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

    pos = nx.spring_layout(G, seed=42)
    cmap = get_window_color_map(windows)

    node_colors = [cmap.get(assign[n], "#dddddd") if n in assign else "#dddddd" for n in G.nodes()]

    fig, ax = plt.subplots(figsize=(7, 5))
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, edgecolors="black", node_size=900, ax=ax)
    nx.draw_networkx_edges(G, pos, edge_color="#444444", width=1.5, ax=ax)
    nx.draw_networkx_labels(G, pos, font_color="white", font_size=10, ax=ax)

    # Highlight selected variable
    if selected in G:
        nx.draw_networkx_nodes(G, pos, nodelist=[selected], node_color="none",
                               edgecolors="#2c3e50", linewidths=3, node_size=1000, ax=ax)

    # Title and legend
    title = f"CSP {event}"
    if selected: title += f" — var: {selected}"
    if tried is not None: title += f", val: {tried}"
    ax.set_title(title)

    # Small legend
    y = 1.02
    for w, col in cmap.items():
        ax.text(0.0, y, f" {w} ", transform=ax.transAxes, fontsize=9,
                bbox=dict(fc=col, ec="black", alpha=0.9, boxstyle="round,pad=0.2"))
        y -= 0.06

    ax.axis("off")
    st.pyplot(fig, clear_figure=True)

    if pruned:
        st.caption("Forward-check pruning at this step:")
        st.json(pruned)
