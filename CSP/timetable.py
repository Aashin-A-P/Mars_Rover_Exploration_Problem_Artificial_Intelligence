import streamlit as st
import pandas as pd
import random

# ===================== CSP ENGINE ===================== #
class TimetableCSP:
    def __init__(self, days, periods, subjects, subject_limits, subject_days, lab_subjects):
        self.days = days
        self.periods = periods
        self.variables = [(d, p) for d in range(days) for p in range(periods)]
        self.domains = {var: list(subjects.keys()) for var in self.variables}
        self.subject_limits = subject_limits
        self.subject_days = subject_days
        self.lab_subjects = lab_subjects
        self.assignments = {}
        self.subject_count = {s: 0 for s in subjects}
        self.teachers = subjects

    # --- constraint checking ---
    def is_valid(self, var, value):
        day, period = var
        teacher = self.teachers[value]

        # 1. No teacher clash (same period different day)
        for (d, p), v in self.assignments.items():
            if p == period and self.teachers[v] == teacher:
                return False

        # 2. Subject limit
        if self.subject_count[value] >= self.subject_limits[value]:
            return False

        # 3. Day restriction
        day_name = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][day]
        if value in self.subject_days and day_name not in self.subject_days[value]:
            return False

        # 4. Lab continuity constraint
        if value in self.lab_subjects:
            block_size = self.subject_limits[value]  # number of continuous periods for lab
            start_period = period
            end_period = period + block_size - 1

            # must fit inside same day
            if end_period >= self.periods:
                return False

            # all next slots must be free
            for p in range(start_period, end_period + 1):
                if (day, p) in self.assignments:
                    return False

        return True

    # --- assignment helpers ---
    def assign_subject(self, var, value):
        day, period = var
        if value in self.lab_subjects:
            block_size = self.subject_limits[value]
            for p in range(period, period + block_size):
                self.assignments[(day, p)] = value
                self.subject_count[value] += 1
        else:
            self.assignments[var] = value
            self.subject_count[value] += 1

    def unassign_subject(self, var, value):
        day, period = var
        if value in self.lab_subjects:
            block_size = self.subject_limits[value]
            for p in range(period, period + block_size):
                if (day, p) in self.assignments:
                    del self.assignments[(day, p)]
                    self.subject_count[value] -= 1
        else:
            if var in self.assignments:
                del self.assignments[var]
                self.subject_count[value] -= 1

    # --- backtracking search ---
    def backtrack(self):
        if len(self.assignments) == len(self.variables):
            return True

        unassigned = [v for v in self.variables if v not in self.assignments]
        if not unassigned:
            return True
        var = random.choice(unassigned)
        random.shuffle(self.domains[var])

        for value in self.domains[var]:
            if self.is_valid(var, value):
                self.assign_subject(var, value)
                if self.backtrack():
                    return True
                self.unassign_subject(var, value)
        return False

    def solve(self):
        self.backtrack()
        return self.assignments

# ===================== STREAMLIT UI ===================== #
st.set_page_config(page_title="AI Timetable Scheduler", layout="wide")
st.title("📚 AI-Based Timetable Scheduling (CSP)")

st.sidebar.header("Configuration")

days = st.sidebar.number_input("Days in a week", 1, 7, 5)
periods = st.sidebar.number_input("Periods per day", 1, 10, 8)
num_subjects = st.sidebar.number_input("Number of subjects", 1, 10, 5)

st.sidebar.markdown("---")

subjects = {}
subject_limits = {}
subject_days = {}
lab_subjects = []

st.subheader("Enter Subject Details")

for i in range(num_subjects):
    st.markdown(f"### Subject {i+1}")
    subject = st.text_input(f"Name of Subject {i+1}", key=f"sub{i}")
    teacher = st.text_input(f"Teacher for {subject if subject else 'Subject '+str(i+1)}", key=f"teach{i}")
    limit = st.number_input(f"Total periods per week for {subject if subject else 'this subject'}", 1, days*periods, 4, key=f"limit{i}")
    is_lab = st.checkbox(f"Is this a Lab (continuous periods)?", key=f"lab{i}")
    allowed_days = st.multiselect(f"Allowed days for {subject if subject else 'this subject'}",
                                  ["Mon","Tue","Wed","Thu","Fri","Sat"], key=f"days{i}")
    st.markdown("---")

    if subject:
        subjects[subject] = teacher if teacher else f"T{i+1}"
        subject_limits[subject] = limit
        if allowed_days:
            subject_days[subject] = allowed_days
        if is_lab:
            lab_subjects.append(subject)

# ===================== GENERATE BUTTON ===================== #
if st.button("🚀 Generate Timetable"):
    if not subjects:
        st.warning("Please enter at least one subject.")
    else:
        with st.spinner("Solving CSP... Please wait ⏳"):
            csp = TimetableCSP(days, periods, subjects, subject_limits, subject_days, lab_subjects)
            assignments = csp.solve()

        if assignments:
            st.success("✅ Timetable Generated Successfully!")
            day_names = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"][:days]
            table = [[assignments.get((d,p),"") for p in range(periods)] for d in range(days)]
            df = pd.DataFrame(table, index=day_names, columns=[f"Period {i+1}" for i in range(periods)])

            st.dataframe(df.style.set_properties(**{
                'background-color': '#E8F6F3',
                'color': 'black',
                'border-color': 'black'
            }), use_container_width=True)

            csv = df.to_csv().encode('utf-8')
            st.download_button("📥 Download Timetable as CSV", csv, "timetable.csv", "text/csv")
        else:
            st.error("❌ No valid timetable could be generated under given constraints. Try adjusting limits or days.")
else:
    st.info("Fill in subject details on the left and click **Generate Timetable** to start.")
