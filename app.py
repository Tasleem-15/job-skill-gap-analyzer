import os
import re
import json

import streamlit as st
import matplotlib.pyplot as plt

BASE = os.path.dirname(os.path.abspath(__file__))
JOBS_FOLDER = os.path.join(BASE, "jobs")

st.set_page_config(page_title="Job Skill-Gap Dashboard", layout="wide")
st.title("Job Skill-Gap Dashboard")
st.caption("Find out which in-demand skills you are missing, using real job postings.")


def mentions(skill, text):
    """True if the skill appears as a whole word in the text."""
    pattern = r"(?<![a-z0-9])" + re.escape(skill) + r"(?![a-z0-9])"
    return re.search(pattern, text) is not None


# ---------- Load skills ----------
with open(os.path.join(BASE, "skills.json"), encoding="utf-8") as f:
    skills_to_check = json.load(f)

with open(os.path.join(BASE, "my_skills.txt"), encoding="utf-8") as f:
    saved_skills = [line.strip().lower() for line in f if line.strip()]

# ---------- Sidebar (the left panel) ----------
st.sidebar.header("Settings")

my_skills = st.sidebar.multiselect(
    "Your skills",
    options=skills_to_check,
    default=[s for s in saved_skills if s in skills_to_check],
)

use_folder = st.sidebar.checkbox("Use saved jobs from the jobs folder", value=True)
uploaded = st.sidebar.file_uploader(
    "Add job descriptions (.txt)", type="txt", accept_multiple_files=True
)
pasted = st.sidebar.text_area("Or paste one job description")

min_demand = st.sidebar.slider("Minimum demand (%)", 0, 100, 0)
view = st.sidebar.radio("Show", ["All", "Have", "Missing"])

# ---------- Collect job texts ----------
job_texts = []
if use_folder and os.path.isdir(JOBS_FOLDER):
    for name in sorted(os.listdir(JOBS_FOLDER)):
        if name.endswith(".txt"):
            with open(os.path.join(JOBS_FOLDER, name), encoding="utf-8", errors="ignore") as f:
                job_texts.append(f.read().lower())

for file in uploaded:
    job_texts.append(file.read().decode("utf-8", errors="ignore").lower())

if pasted.strip():
    job_texts.append(pasted.lower())

total = len(job_texts)
if total == 0:
    st.warning("No job descriptions yet. Add some in the sidebar.")
    st.stop()

# ---------- Count demand ----------
demand = {}
for skill in skills_to_check:
    demand[skill] = sum(1 for text in job_texts if mentions(skill, text))

# Build one row (a dictionary) per skill that was found
rows = []
for skill, count in demand.items():
    if count > 0:
        status = "HAVE" if skill in my_skills else "MISSING"
        rows.append({
            "Skill": skill,
            "Jobs": count,
            "Demand %": round(count / total * 100),
            "Status": status,
        })

# Biggest demand first
rows.sort(key=lambda row: row["Jobs"], reverse=True)

# ---------- Stat cards ----------
total_mentions = sum(demand.values())
my_mentions = sum(c for s, c in demand.items() if s in my_skills)
match = my_mentions / total_mentions * 100 if total_mentions else 0

missing = [row for row in rows if row["Status"] == "MISSING"]
top_gap = missing[0]["Skill"] if missing else "None"

col1, col2, col3 = st.columns(3)
col1.metric("Jobs analysed", total)
col2.metric("Match score", f"{match:.0f}%")
col3.metric("Top gap", top_gap)

# ---------- Apply the sidebar filters ----------
shown = [row for row in rows if row["Demand %"] >= min_demand]
if view == "Have":
    shown = [row for row in shown if row["Status"] == "HAVE"]
elif view == "Missing":
    shown = [row for row in shown if row["Status"] == "MISSING"]

# ---------- Chart and table ----------
left, right = st.columns([3, 2])

with left:
    st.subheader("Skill demand")
    top = shown[:10][::-1]  # top 10, reversed so the biggest bar is on top
    if not top:
        st.info("Nothing to show with these filters.")
    else:
        names = [row["Skill"] for row in top]
        percents = [row["Demand %"] for row in top]
        colors = ["green" if row["Status"] == "HAVE" else "red" for row in top]

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.barh(names, percents, color=colors)
        ax.set_xlabel("% of jobs asking for the skill")
        st.pyplot(fig)

with right:
    st.subheader("Table")
    st.dataframe(shown, hide_index=True)

st.subheader("Top skills to learn next")
if not missing:
    st.success("You have every skill found in these jobs.")
else:
    for row in missing[:5]:
        st.write(f"- **{row['Skill']}**: asked in {row['Jobs']} of {total} jobs")