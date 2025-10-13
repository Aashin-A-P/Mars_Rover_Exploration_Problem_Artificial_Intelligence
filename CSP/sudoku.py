import streamlit as st
from collections import deque, defaultdict
import time
import copy


# ============================================================
# Sudoku CSP with AC-3 + MRV + Forward Checking
# Step-by-step generator to visualize assignments & backtracks
# ============================================================

ROWS = COLS = range(9)

def box_index(r, c):
    return (r // 3) * 3 + (c // 3)

def make_peers():
    """Precompute peer cells (same row, column, or 3x3 box) for each cell."""
    peers = {}
    for r in ROWS:
        for c in COLS:
            p = set()
            # row and col
            for cc in COLS:
                if cc != c: p.add((r, cc))
            for rr in ROWS:
                if rr != r: p.add((rr, c))
            # box
            br, bc = 3*(r//3), 3*(c//3)
            for rr in range(br, br+3):
                for cc in range(bc, bc+3):
                    if (rr, cc) != (r, c):
                        p.add((rr, cc))
            peers[(r, c)] = p
    return peers

PEERS = make_peers()

def parse_puzzle(lines_or_string):
    """
    Accepts:
      - 9 lines with digits/0/. for blanks
      - or a single 81-char string with digits/0/. for blanks
    Returns:
      grid: 9x9 list of ints (0 for blank)
      givens: set of (r,c) that are pre-filled
    """
    if isinstance(lines_or_string, str):
        s = lines_or_string.replace("\n", "").replace(" ", "")
        if len(s) != 81:
            raise ValueError("Puzzle must be 81 chars (digits or . / 0).")
        grid = [[0]*9 for _ in range(9)]
        k = 0
        for r in ROWS:
            for c in COLS:
                ch = s[k]
                k += 1
                grid[r][c] = int(ch) if ch.isdigit() else 0
    else:
        raise ValueError("Provide puzzle as a single 81-char string")

    givens = set()
    for r in ROWS:
        for c in COLS:
            if grid[r][c] != 0:
                givens.add((r, c))
    return grid, givens

# ---------- CSP Core ----------
class SudokuCSP:
    def __init__(self, grid):
        """
        grid: 9x9 list of ints (0 for blank).
        domains: dict[(r,c)] -> set of possible digits 1..9
        """
        self.grid = copy.deepcopy(grid)
        self.domains = {(r, c): set(range(1, 10)) for r in ROWS for c in COLS}
        # set initial domains from givens
        for r in ROWS:
            for c in COLS:
                v = self.grid[r][c]
                if v != 0:
                    self.domains[(r, c)] = {v}

    def is_consistent_cell(self, r, c, val):
        """Check if placing val at (r,c) violates row/col/box wrt current grid."""
        # row
        for cc in COLS:
            if cc != c and self.grid[r][cc] == val:
                return False
        # col
        for rr in ROWS:
            if rr != r and self.grid[rr][c] == val:
                return False
        # box
        br, bc = 3*(r//3), 3*(c//3)
        for rr in range(br, br+3):
            for cc in range(bc, bc+3):
                if not (rr == r and cc == c) and self.grid[rr][cc] == val:
                    return False
        return True

    def ac3(self):
        """Enforce arc consistency (AC-3). Reduce domains before search.
           Returns (reduced, steps) where 'steps' are UI events to visualize domain removals.
        """
        steps = []
        queue = deque()
        for Xi in self.domains:
            for Xj in PEERS[Xi]:
                queue.append((Xi, Xj))

        def revise(Xi, Xj):
            revised = False
            remove_vals = set()
            for x in self.domains[Xi]:
                # there must exist some y in domain(Xj) such that x != y (since neighbors)
                # if Xj domain is singleton {x}, then x at Xi is impossible
                if len(self.domains[Xj]) == 1 and x in self.domains[Xj]:
                    remove_vals.add(x)
            if remove_vals:
                for v in remove_vals:
                    self.domains[Xi].remove(v)
                    steps.append(("prune", Xi, v, Xj))
                revised = True
            return revised

        while queue:
            Xi, Xj = queue.popleft()
            if revise(Xi, Xj):
                if len(self.domains[Xi]) == 0:
                    return False, steps
                for Xk in PEERS[Xi]:
                    if Xk != Xj:
                        queue.append((Xk, Xi))
        return True, steps

    def is_solved(self):
        return all(self.grid[r][c] != 0 for r in ROWS for c in COLS)

    def select_unassigned_var_MRV(self):
        """Minimum Remaining Values (smallest domain size > 1)."""
        best = None
        best_size = 10
        for r in ROWS:
            for c in COLS:
                if self.grid[r][c] == 0:
                    dsize = len(self.domains[(r, c)])
                    if dsize < best_size:
                        best_size = dsize
                        best = (r, c)
        return best

    def forward_check(self, cell, val):
        """Remove val from peers' domains; if any domain becomes empty -> fail.
           Returns (ok, removed) where removed is list of (peer, removed_val)
        """
        removed = []
        r, c = cell
        for pr, pc in PEERS[(r, c)]:
            d = self.domains[(pr, pc)]
            if self.grid[pr][pc] == 0 and val in d:
                d.remove(val)
                removed.append(((pr, pc), val))
                if len(d) == 0:
                    return False, removed
        return True, removed

    def restore(self, removed):
        for cell, v in removed:
            self.domains[cell].add(v)

    def assign(self, cell, val):
        r, c = cell
        self.grid[r][c] = val
        self.domains[cell] = {val}

    def unassign(self, cell, old_domain):
        r, c = cell
        self.grid[r][c] = 0
        self.domains[cell] = set(old_domain)

    def solve_steps(self):
        """
        Generator yielding step-by-step actions:
          - ("prune", (r,c), val, (pr,pc)) domain value removed during AC-3
          - ("assign", (r,c), val)
          - ("unassign", (r,c), val)
        Then final ("done", None, None) when solved.
        """
        # 1) AC-3 preprocessing
        ok, prune_steps = self.ac3()
        for step in prune_steps:
            yield step
        if not ok:
            yield ("fail", None, None)
            return

        # 2) Backtracking with MRV + Forward Checking
        yield from self._backtrack_steps()

        if self.is_solved():
            yield ("done", None, None)
        else:
            yield ("fail", None, None)

    def _backtrack_steps(self):
        if self.is_solved():
            return
        cell = self.select_unassigned_var_MRV()
        if cell is None:
            return


        original_domain = set(self.domains[cell])
        for val in sorted(original_domain):
            if self.is_consistent_cell(cell[0], cell[1], val):
                old_domain = set(self.domains[cell])
                self.assign(cell, val)
                yield ("assign", cell, val)

                ok, removed = self.forward_check(cell, val)
                if ok:
                    yield from self._backtrack_steps()
                    if self.is_solved():
                        return

                self.restore(removed)
                self.unassign(cell, old_domain)
                yield ("unassign", cell, val)

# ---------- Default Puzzles (string of 81 chars; 0 or . = blank) ----------
PUZZLES = {
    "Easy":
    "530070000"
    "600195000"
    "098000060"
    "800060003"
    "400803001"
    "700020006"
    "060000280"
    "000419005"
    "000080079",

    "Medium":
    "009000000"
    "080605020"
    "501078000"
    "000000705"
    "090000010"
    "208000000"
    "000720304"
    "040301060"
    "000000900",

    "Hard":
    "000000907"
    "000420180"
    "000705026"
    "100904000"
    "050000040"
    "000507009"
    "920108000"
    "034059000"
    "507000000",
}

# ---------- Streamlit UI ----------
st.set_page_config(page_title="Sudoku CSP", layout="wide")
st.title("🧩 Sudoku Solver — CSP")

# Session state init
if "csp" not in st.session_state:
    st.session_state.csp = None
if "steps" not in st.session_state:
    st.session_state.steps = None
if "givens" not in st.session_state:
    st.session_state.givens = set()
if "last_action" not in st.session_state:
    st.session_state.last_action = None
if "log" not in st.session_state:
    st.session_state.log = []
if "auto" not in st.session_state:
    st.session_state.auto = False

colA, colB = st.columns([1.2, 1])

with colA:
    st.subheader("Choose a puzzle or paste your own")
    choice = st.selectbox("Preset:",
                          options=list(PUZZLES.keys()) + ["Custom"],
                          index=0)
    if choice == "Custom":
        puzzle_str = st.text_area(
            "Paste 81 characters (digits 1-9, 0 or . for blanks):",
            value=PUZZLES["Easy"]
        ).strip()
    else:
        puzzle_str = PUZZLES[choice]

    cols = st.columns(3)
    with cols[0]:
        if st.button("Initialize / Reset"):
            grid, givens = parse_puzzle(puzzle_str)
            st.session_state.csp = SudokuCSP(grid)
            st.session_state.steps = st.session_state.csp.solve_steps()
            st.session_state.givens = givens
            st.session_state.last_action = None
            st.session_state.log = []
            st.session_state.auto = False
            st.success("Initialized. Click step buttons to watch the solver.")
    with cols[1]:
        step_k = st.number_input("Steps per click", min_value=1, max_value=500, value=25, step=1)
    with cols[2]:
        st.session_state.auto = st.toggle("Auto-play", value=st.session_state.auto, help="Run continuously (fast).")

    run_cols = st.columns(3)
    with run_cols[0]:
        step_once = st.button("▶ Step", use_container_width=True)
    with run_cols[1]:
        step_many = st.button(f"⏭ Step x{step_k}", use_container_width=True)
    with run_cols[2]:
        solve_all = st.button("🏁 Solve to End", use_container_width=True)

def draw_grid(grid, givens, last_action):
    def cell_style(r, c):
        base = "width:40px;height:40px;text-align:center;font-weight:600;font-size:18px;border:1px solid #666;"
        if c in (2,5): base += "border-right:3px solid #000;"
        if c == 0: base += "border-left:3px solid #000;"
        if r in (2,5): base += "border-bottom:3px solid #000;"
        if r == 0: base += "border-top:3px solid #000;"

        if (r,c) in givens:
            base += "background:#000000;color:white;"  
        else:
            base += "background:#ffffff;color:black;" 
        if last_action and last_action.get("cell") == (r,c):
            if last_action["type"] == "assign":
                base += "background:#d4edda;"  # light green
            elif last_action["type"] == "unassign":
                base += "background:#f8d7da;"  # light red
            elif last_action["type"] == "prune":
                base += "background:#ffeeba;"  # light yellow
        return base

    html = "<table style='border-collapse:collapse;margin-top:8px;'>"
    for r in ROWS:
        html += "<tr>"
        for c in COLS:
            v = grid[r][c]
            disp = str(v) if v != 0 else "&nbsp;"
            html += f"<td style='{cell_style(r,c)}'>{disp}</td>"
        html += "</tr>"
    html += "</table>"
    st.markdown(html, unsafe_allow_html=True)

with colA:
    st.subheader("Board")
    if st.session_state.csp is None:
        st.info("Click **Initialize / Reset** to load the puzzle.")
    else:
        draw_grid(st.session_state.csp.grid, st.session_state.givens, st.session_state.last_action)

with colB:
    st.subheader("Step Log")
    log_box = st.empty()
    def push_log(msg):
        st.session_state.log.append(msg)
        if len(st.session_state.log) > 200:
            st.session_state.log = st.session_state.log[-200:]
        log_box.code("\n".join(st.session_state.log), language="text")

    if st.session_state.csp is None:
        st.write("No log yet.")
    else:
        def do_n_steps(n):
            csp = st.session_state.csp
            steps = st.session_state.steps
            if steps is None: return
            try:
                for _ in range(n):
                    action = next(steps)
                    if action[0] == "prune":
                        _, cell, val, peer = action
                        st.session_state.last_action = {"type": "prune", "cell": cell}
                        push_log(f"PRUNE: remove {val} from {cell} due to peer {peer}")
                    elif action[0] == "assign":
                        _, cell, val = action
                        st.session_state.last_action = {"type": "assign", "cell": cell}
                        push_log(f"ASSIGN: {val} at {cell}")
                    elif action[0] == "unassign":
                        _, cell, val = action
                        st.session_state.last_action = {"type": "unassign", "cell": cell}
                        push_log(f"BACKTRACK: remove {val} from {cell}")
                    elif action[0] == "done":
                        st.session_state.last_action = None
                        push_log("✅ DONE: Puzzle solved.")
                        return "done"
                    elif action[0] == "fail":
                        st.session_state.last_action = None
                        push_log("❌ FAIL: No solution under constraints.")
                        return "fail"
                return "more"
            except StopIteration:
                if st.session_state.csp.is_solved():
                    push_log("✅ DONE: Puzzle solved.")
                    return "done"
                else:
                    push_log("❌ FAIL: No more steps.")
                    return "fail"

        if solve_all:
            status = "more"
            while status == "more":
                status = do_n_steps(500)
            draw_grid(st.session_state.csp.grid, st.session_state.givens, st.session_state.last_action)

        if step_once:
            do_n_steps(1)
            draw_grid(st.session_state.csp.grid, st.session_state.givens, st.session_state.last_action)

        if step_many:
            do_n_steps(step_k)
            draw_grid(st.session_state.csp.grid, st.session_state.givens, st.session_state.last_action)

        if st.session_state.auto:
            status = do_n_steps(50)
            draw_grid(st.session_state.csp.grid, st.session_state.givens, st.session_state.last_action)
            if status == "more":
                time.sleep(0.2)
                st.rerun()
            else:
                st.session_state.auto = False 
                push_log("Auto-play stopped.")

        if not st.session_state.log:
            push_log("Ready. Use Step/Step xN or Solve to End.")
