import streamlit as st
import pandas as pd
import time

from utils import parse_df_to_grid, CELL_OPTIONS, CELL_LABELS, path_cost
from search_algos import bfs, dfs, ucs, astar_with_trace
from csp_solver import CSP
from adversial_module import simulate_pursuit
from visualization import render_plot, render_csp_state

# -----------------------------
# STREAMLIT CONFIG & HEADER
# -----------------------------
st.set_page_config(page_title="Smart City AI", layout="wide")
st.title("🚚 Smart City AI — Autonomous Delivery Robot")
st.caption("Explore pathfinding, CSP, and adversarial AI on an editable grid.")

# Session flags
for key in ["play_astar", "play_game", "play_csp"]:
    if key not in st.session_state:
        st.session_state[key] = False

# -----------------------------
# GRID SETUP
# -----------------------------
with st.sidebar:
    st.header("Grid Settings")
    H = st.number_input("Rows", min_value=4, max_value=25, value=8)
    W = st.number_input("Cols", min_value=4, max_value=25, value=12)
    if "grid_df" not in st.session_state or st.button("Reset Grid"):
        base = [['.' for _ in range(W)] for _ in range(H)]
        for r in range(H):
            if r != H // 2 and W > 5:
                base[r][5] = '#'
        base[min(2, H - 1)][0] = 'S'
        base[min(2, H - 1)][W - 1] = 'D'
        st.session_state.grid_df = pd.DataFrame(base)

st.subheader("🧩 Edit the City Grid")
st.write("Use the table to edit cells. " + ", ".join([f"`{k}` = {v}" for k, v in CELL_LABELS.items()]))

col_config = {
    c: st.column_config.SelectboxColumn("Cell", options=CELL_OPTIONS, required=True)
    for c in st.session_state.grid_df.columns
}

grid_df = st.data_editor(st.session_state.grid_df, key="grid_editor",
                         height=min(600, 32 * H + 60), column_config=col_config)

try:
    grid, start, goal = parse_df_to_grid(grid_df)
except Exception as e:
    st.error(str(e))
    st.stop()

# -----------------------------
# MAIN TABS
# -----------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔎 Search (BFS/DFS/UCS/A*)",
    "✨ A* Explorer",
    "🗺️ CSP (Solve Once)",
    "🎬 CSP (Simulation)",
    "⚔️ Adversarial (Robot vs Drone)"
])

# ---------- TAB 1: Search ----------
with tab1:
    algo = st.selectbox("Algorithm", ["BFS", "DFS", "UCS", "A*"])
    if st.button("Run Search"):
        if algo == "BFS":
            path = bfs(grid, start, goal)
        elif algo == "DFS":
            path = dfs(grid, start, goal)
        elif algo == "UCS":
            path = ucs(grid, start, goal)
        else:
            path, _ = astar_with_trace(grid, start, goal)
        st.write(f"**Steps:** {len(path) if path else 'No path'}")
        st.write(f"**Cost:** {path_cost(grid, path) if path else '—'}")
        render_plot(grid, path, start, goal, title=f"{algo} Result")

# ---------- TAB 2: A* Animation ----------
with tab2:
    path, snaps = astar_with_trace(grid, start, goal)
    total_frames = len(snaps) + (len(path) if path else 0)
    fps = st.slider("FPS", 1, 10, 3)
    colA, colB = st.columns(2)
    with colA:
        if st.button("▶️ Play A*"): st.session_state.play_astar = True
    with colB:
        if st.button("⏹ Stop A*"): st.session_state.play_astar = False

    holder = st.empty()
    if not st.session_state.play_astar:
        frame = st.slider("Frame", 0, max(0, total_frames - 1), 0)
        if frame < len(snaps):
            explored, frontier, _ = snaps[frame]
            render_plot(grid, None, start, goal, explored=explored, frontier=frontier, title=f"A* Step {frame}")
        else:
            k = frame - len(snaps) + 1
            render_plot(grid, path[:k], start, goal, title="A* Path")
    else:
        for frame in range(total_frames):
            if not st.session_state.play_astar: break
            if frame < len(snaps):
                explored, frontier, _ = snaps[frame]
                render_plot(grid, None, start, goal, explored=explored, frontier=frontier, title=f"A* Step {frame}")
            else:
                k = frame - len(snaps) + 1
                render_plot(grid, path[:k], start, goal, title="A* Path")
            time.sleep(1 / fps)
        st.session_state.play_astar = False

# ---------- TAB 3: CSP Solve ----------
with tab3:
    st.write("Assign delivery windows to zones so adjacent ones differ.")
    default_adj = {
        'Hospital': {'Market', 'ITPark'},
        'Market': {'Hospital', 'OldTown', 'ITPark'},
        'OldTown': {'Market', 'Stadium'},
        'ITPark': {'Hospital', 'Market', 'Stadium'},
        'Stadium': {'OldTown', 'ITPark'},
    }
    zones_txt = st.text_area("Zone adjacency (Python dict)", value=str(default_adj), height=160)
    windows = st.multiselect("Available windows", ['M1', 'M2', 'M3', 'M4'], default=['M1', 'M2', 'M3'])
    if st.button("Solve CSP"):
        try:
            adj = eval(zones_txt, {"__builtins__": {}})
            csp = CSP(list(adj.keys()), {v: set(windows) for v in adj}, adj)
            trace = csp.backtrack_trace({})
            solution = next((snap["assignment"] for snap in reversed(trace) if snap["event"] == "solution"), None)
            if solution:
                st.success(f"Solution: {solution}")
            else:
                st.error("No valid assignment.")
        except Exception as e:
            st.error(f"Invalid adjacency: {e}")

# ---------- TAB 4: CSP Simulation ----------
with tab4:
    zones_txt2 = st.text_area("Zone adjacency (sim)", value=str(default_adj), height=160, key="zones_sim")
    windows2 = st.multiselect("Windows", ['M1','M2','M3','M4'], default=['M1','M2','M3'], key="wins_sim")
    if st.button("Plan CSP Simulation"):
        try:
            adj2 = eval(zones_txt2, {"__builtins__": {}})
            csp2 = CSP(list(adj2.keys()), {v:set(windows2) for v in adj2}, adj2)
            st.session_state.csp_trace = csp2.backtrack_trace({})
            st.session_state.csp_adj = adj2
            st.session_state.csp_windows = windows2
            st.success(f"{len(st.session_state.csp_trace)} steps planned.")
        except Exception as e:
            st.error(f"Invalid input: {e}")

    fps_csp = st.slider("FPS (CSP)", 1, 10, 3)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("▶️ Play CSP"): st.session_state.play_csp = True
    with c2:
        if st.button("⏹ Stop CSP"): st.session_state.play_csp = False

    holder_csp = st.empty()
    trace = st.session_state.get("csp_trace", [])
    if not trace:
        st.info("Click 'Plan CSP Simulation' first.")
    else:
        if not st.session_state.play_csp:
            i = st.slider("Step", 0, len(trace) - 1, 0)
            render_csp_state(st.session_state.csp_adj, trace[i], st.session_state.csp_windows)
        else:
            for i in range(len(trace)):
                if not st.session_state.play_csp: break
                render_csp_state(st.session_state.csp_adj, trace[i], st.session_state.csp_windows)
                time.sleep(1 / fps_csp)
            st.session_state.play_csp = False

# ---------- TAB 5: Adversarial ----------
with tab5:
    dr_r = st.number_input("Drone Start Row", 0, grid_df.shape[0] - 1, 0)
    dr_c = st.number_input("Drone Start Col", 0, grid_df.shape[1] - 1, 0)
    depth = st.slider("Search Depth", 2, 6, 4)
    max_steps = st.slider("Max Steps", 6, 60, 24)
    if st.button("Plan Simulation"):
        st.session_state.sim_frames = simulate_pursuit(grid, start, goal, (int(dr_r), int(dr_c)), depth, max_steps)
    fps2 = st.slider("FPS (Adversarial)", 1, 10, 2)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("▶️ Play Simulation"): st.session_state.play_game = True
    with c2:
        if st.button("⏹ Stop Simulation"): st.session_state.play_game = False

    holder2 = st.empty()
    frames = st.session_state.get("sim_frames", [])
    if not frames:
        st.info("Click 'Plan Simulation' first.")
    else:
        if not st.session_state.play_game:
            k = st.slider("Frame", 0, len(frames)-1, 0)
            bot, drone = frames[k]
            render_plot(grid, None, start, goal, bot=bot, drone=drone, title=f"Frame {k}")
        else:
            for k in range(len(frames)):
                if not st.session_state.play_game: break
                bot, drone = frames[k]
                render_plot(grid, None, start, goal, bot=bot, drone=drone, title=f"Frame {k}")
                if bot == drone:
                    st.error("Drone caught the robot!")
                    break
                elif bot == goal:
                    st.success("Delivered!")
                    break
                time.sleep(1 / fps2)
            st.session_state.play_game = False

st.divider()
st.markdown("✅ **Tips:**")
st.markdown("- Place exactly one `S` and one `D`.")
st.markdown("- `#` = walls, `t` and `c` = high-cost routes.")
st.markdown("- Use Play/Stop to animate.")
st.markdown("- CSP sim shows `choose`, `assign`, `inconsistent`, `backtrack`, and `solution` steps.")
