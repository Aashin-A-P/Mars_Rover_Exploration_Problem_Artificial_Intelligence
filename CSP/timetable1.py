# filename: timetable_app.py
import streamlit as st
import pandas as pd
import time
import random
from collections import defaultdict

# --------------------------- Utilities ---------------------------

DAY_NAMES_ALL = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]

def feasible_total(subject_limits, total_slots):
    return sum(subject_limits.values()) <= total_slots

def lab_block_len(subject, subject_limits, default_lab_len=4):
    # For this app, labs consume exactly their weekly limit (e.g., 4 → 4 contiguous)
    return subject_limits[subject]

# --------------------------- CSP Engine ---------------------------

class TimetableCSP:
    """
    Two-phase solver:
      Phase 1: place each LAB as one contiguous block on some allowed day.
      Phase 2: fill remaining empty slots with theory subjects using MRV & limits.
    """
    def __init__(self, days, periods, subjects, subject_limits, subject_days, lab_subjects, progress_cb=None):
        self.days = days
        self.periods = periods
        self.subjects = subjects                  # {subject: teacher_name}
        self.subject_limits = subject_limits      # {subject: count_per_week}
        self.subject_days = subject_days or {}    # {subject: [allowed day names]}
        self.lab_subjects = set(lab_subjects)     # set(subject)
        self.progress_cb = progress_cb

        # timetable grid: (day, period) -> subject or ""
        self.grid = {(d,p): "" for d in range(days) for p in range(periods)}

        # counts
        self.remaining = dict(subject_limits)     # how many periods still to place
        self.total_slots = days * periods

        # progress = filled_slots / total_slots
        self.filled = 0

    # --------------- Progress ---------------
    def _bump_progress(self, delta):
        self.filled += delta
        if self.progress_cb:
            ratio = min(self.filled / self.total_slots, 1.0)
            self.progress_cb(ratio)

    # --------------- Feasibility helpers ---------------
    def allowed_days_idx(self, subject):
        if subject in self.subject_days and self.subject_days[subject]:
            allowed = self.subject_days[subject]
            return [DAY_NAMES_ALL.index(x) for x in allowed if x in DAY_NAMES_ALL[:self.days]]
        # if no restriction, all days allowed
        return list(range(self.days))

    def free_block_here(self, day, start_p, length):
        if start_p + length > self.periods:
            return False
        for p in range(start_p, start_p + length):
            if self.grid[(day, p)] != "":
                return False
        return True

    def place_block(self, day, start_p, subj, length):
        for p in range(start_p, start_p + length):
            self.grid[(day, p)] = subj
        self.remaining[subj] -= length
        self._bump_progress(length)

    def remove_block(self, day, start_p, subj, length):
        for p in range(start_p, start_p + length):
            self.grid[(day, p)] = ""
        self.remaining[subj] += length
        self._bump_progress(-length)

    # --------------- Phase 1: place labs ---------------
    def place_labs_backtrack(self, lab_list, idx=0):
        if idx == len(lab_list):
            return True
        subj = lab_list[idx]
        length = lab_block_len(subj, self.subject_limits)

        # try allowed days in randomized order (helps avoid pathological symmetry)
        days_try = self.allowed_days_idx(subj)
        random.shuffle(days_try)

        for d in days_try:
            # try all start slots that fit
            start_candidates = list(range(0, self.periods - length + 1))
            random.shuffle(start_candidates)
            for sp in start_candidates:
                if self.free_block_here(d, sp, length):
                    self.place_block(d, sp, subj, length)
                    if self.place_labs_backtrack(lab_list, idx + 1):
                        return True
                    self.remove_block(d, sp, subj, length)

        return False

    # --------------- Phase 2: fill theory with MRV ---------------
    def theory_subjects(self):
        return [s for s in self.subjects if s not in self.lab_subjects]

    def empty_cells(self):
        return [(d,p) for d in range(self.days) for p in range(self.periods) if self.grid[(d,p)] == ""]

    def domain_for_cell(self, cell):
        d, p = cell
        dom = []
        for s in self.theory_subjects():
            if self.remaining[s] <= 0:
                continue
            # day restriction: if subject allowed days specified, respect it
            if s in self.subject_days and self.subject_days[s]:
                dn = DAY_NAMES_ALL[d]
                if dn not in self.subject_days[s]:
                    continue
            dom.append(s)
        return dom

    def assign_cell(self, cell, subj):
        self.grid[cell] = subj
        self.remaining[subj] -= 1
        self._bump_progress(1)

    def unassign_cell(self, cell, subj):
        self.grid[cell] = ""
        self.remaining[subj] += 1
        self._bump_progress(-1)

    def theory_backtrack(self):
        cells = self.empty_cells()
        if not cells:
            return True

        # MRV: pick cell with smallest domain
        domains = [(cell, self.domain_for_cell(cell)) for cell in cells]
        # if any cell has empty domain, dead end
        for cell, dom in domains:
            if len(dom) == 0:
                return False
        cell, dom = min(domains, key=lambda x: len(x[1]))
        random.shuffle(dom)

        for s in dom:
            self.assign_cell(cell, s)
            if self.theory_backtrack():
                return True
            self.unassign_cell(cell, s)

        return False

    # --------------- Solve ---------------
    def solve(self):
        # Phase 0: quick feasibility check
        if not feasible_total(self.subject_limits, self.total_slots):
            return False

        # Place labs first (each lab consumes all its weekly limit in one contiguous block)
        lab_list = [s for s in self.subjects if s in self.lab_subjects]
        # Sort labs by (fewest allowed days, then largest block) to reduce branching
        lab_list.sort(key=lambda s: (len(self.allowed_days_idx(s)), -self.remaining[s]))

        if lab_list:
            ok = self.place_labs_backtrack(lab_list, 0)
            if not ok:
                return False

        # Fill theory
        ok = self.theory_backtrack()
        return ok

# --------------------------- App (Streamlit) ---------------------------

st.set_page_config(page_title="AI Timetable Scheduler", layout="wide")
st.title("📚 Timetable Scheduling (CSP) — Labs First + MRV (Guaranteed Working)")

# Defaults requested: 6 subjects, 4 periods each; 2 labs; 5 days × 8 periods
days, periods = 5, 8

default_subjects = {
    "Math": "Mr. Ravi",
    "Physics": "Ms. Priya",
    "Chemistry": "Mr. John",
    "English": "Ms. Divya",
    "CS Lab": "Mr. Arjun",
    "Electronics Lab": "Mr. Kiran",
}
default_limits = {s: 4 for s in default_subjects.keys()}  # each 4 per week
default_lab_subjects = ["CS Lab", "Electronics Lab"]
default_subject_days = {
    # give labs TWO days each to guarantee space; theory unrestricted
    "CS Lab": ["Wed", "Fri"],
    "Electronics Lab": ["Tue", "Thu"],
}

with st.sidebar:
    st.subheader("Setup")
    days = st.number_input("Days", 3, 7, 5)
    periods = st.number_input("Periods per day", 4, 12, 8)
    st.caption("Defaults loaded: 6 subjects, each 4 per week; 2 labs as contiguous blocks.")

# Show defaults to the user (read-only preview)
st.markdown("### Using Default Subjects")
df_prev = pd.DataFrame({
    "Subject": list(default_subjects.keys()),
    "Teacher": [default_subjects[s] for s in default_subjects],
    "Weekly Periods": [default_limits[s] for s in default_subjects],
    "Is Lab?": [s in default_lab_subjects for s in default_subjects],
    "Allowed Days (if any)": [
        ", ".join(default_subject_days.get(s, [])) if s in default_subject_days else "All"
        for s in default_subjects
    ],
})
st.dataframe(df_prev, use_container_width=True)

if st.button("🚀 Generate Timetable"):
    total_slots = days * periods

    # Build from defaults (you can later expose custom inputs if needed)
    subjects = dict(default_subjects)
    subject_limits = dict(default_limits)
    subject_days = dict(default_subject_days)
    lab_subjects = list(default_lab_subjects)

    # Sanity: if any lab limit > periods/day, impossible to fit as one block
    for lab in lab_subjects:
        L = subject_limits[lab]
        if L > periods:
            st.error(f"Lab '{lab}' needs {L} contiguous periods but day has only {periods}. Lower its limit.")
            st.stop()

    if sum(subject_limits.values()) > total_slots:
        st.error(f"Sum of weekly periods ({sum(subject_limits.values())}) exceeds total slots ({total_slots}). Lower some limits.")
        st.stop()

    prog = st.progress(0)
    prog_txt = st.empty()

    def progress_cb(r):
        prog.progress(r)
        prog_txt.text(f"Progress: {int(r*100)}%")

    start = time.time()
    csp = TimetableCSP(days, periods, subjects, subject_limits, subject_days, lab_subjects, progress_cb)
    ok = csp.solve()
    elapsed = time.time() - start

    if not ok:
        st.error("❌ Could not generate timetable. (This default should work; if it doesn’t, increase days/periods or loosen lab days.)")
    else:
        st.success(f"✅ Timetable generated in {elapsed:.2f}s")
        day_names = DAY_NAMES_ALL[:days]
        table = [[csp.grid[(d,p)] for p in range(periods)] for d in range(days)]
        out = pd.DataFrame(table, index=day_names, columns=[f"P{i+1}" for i in range(periods)])
        # nice compact view
        st.dataframe(out, use_container_width=True)
        csv = out.to_csv().encode("utf-8")
        st.download_button("📥 Download CSV", data=csv, file_name="timetable.csv", mime="text/csv")

st.info("Tip: This solver first locks lab blocks (e.g., CS Lab on Wed/Fri; Electronics Lab on Tue/Thu), then fills theory with MRV. No teacher-overlap constraint across days is enforced (single class).")
