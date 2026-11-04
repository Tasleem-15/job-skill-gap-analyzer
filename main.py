import os
import re
import json
import sqlite3
from datetime import datetime

import matplotlib
matplotlib.use("Agg")  # save charts to a file, no pop-up window
import matplotlib.pyplot as plt

BASE = os.path.dirname(os.path.abspath(__file__))
JOBS_FOLDER = os.path.join(BASE, "jobs")
MY_SKILLS_FILE = os.path.join(BASE, "my_skills.txt")
SKILLS_FILE = os.path.join(BASE, "skills.json")
DB_FILE = os.path.join(BASE, "skillgap.db")
CHART_FILE = os.path.join(BASE, "chart.png")

# Skills to search for, loaded from skills.json
with open(SKILLS_FILE, encoding="utf-8") as f:
    skills_to_check = json.load(f)

# My skills (one per line)
with open(MY_SKILLS_FILE, encoding="utf-8") as f:
    my_skills = {line.strip().lower() for line in f if line.strip()}


def mentions(skill, text):
    """True if the skill appears as a whole word in the text."""
    pattern = r"(?<![a-z0-9])" + re.escape(skill) + r"(?![a-z0-9])"
    return re.search(pattern, text) is not None


# Read all job files
job_texts = []
for name in sorted(os.listdir(JOBS_FOLDER)):
    if name.endswith(".txt"):
        path = os.path.join(JOBS_FOLDER, name)
        with open(path, encoding="utf-8", errors="ignore") as f:
            job_texts.append(f.read().lower())

total = len(job_texts)
if total == 0:
    print("No job files found in the jobs folder.")
    raise SystemExit

# Count in how many jobs each skill appears
demand = {}
for skill in skills_to_check:
    demand[skill] = sum(1 for text in job_texts if mentions(skill, text))

ranked = sorted(demand.items(), key=lambda item: item[1], reverse=True)
found = [(s, c) for s, c in ranked if c > 0]

# ---------- Print the table ----------
print(f"\nJobs analysed: {total}\n")
print(f"{'SKILL':<18}{'DEMAND':>7}   {'':<20} STATUS")
for skill, count in found:
    percent = count / total * 100
    bar = "#" * int(percent / 5)
    status = "HAVE" if skill in my_skills else "MISSING"
    print(f"{skill:<18}{percent:6.0f}%   {bar:<20} {status}")

# ---------- Match score ----------
total_mentions = sum(demand.values())
my_mentions = sum(c for s, c in demand.items() if s in my_skills)
match = my_mentions / total_mentions * 100 if total_mentions else 0
print(f"\nMatch score: {match:.0f}% of the skill mentions in these jobs are skills you have.")

# ---------- Save to SQLite ----------
conn = sqlite3.connect(DB_FILE)
conn.execute(
    """CREATE TABLE IF NOT EXISTS skill_demand (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_time TEXT,
        skill TEXT,
        job_count INTEGER,
        total_jobs INTEGER,
        percent REAL,
        have_it INTEGER
    )"""
)
run_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
for skill, count in found:
    conn.execute(
        "INSERT INTO skill_demand (run_time, skill, job_count, total_jobs, percent, have_it) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (run_time, skill, count, total, count / total * 100, 1 if skill in my_skills else 0),
    )
conn.commit()

# Use SQL to get the top 5 skills I am missing in this run
rows = conn.execute(
    "SELECT skill, job_count FROM skill_demand "
    "WHERE run_time = ? AND have_it = 0 "
    "ORDER BY job_count DESC LIMIT 5",
    (run_time,),
).fetchall()
conn.close()

print("\nTop skills to learn next (from the database):")
for skill, count in rows:
    print(f"  - {skill} (asked in {count} of {total} jobs)")

# ---------- Draw the chart ----------
top = found[:10][::-1]  # reversed so the biggest bar is at the top
names = [s for s, _ in top]
percents = [c / total * 100 for _, c in top]
colors = ["green" if s in my_skills else "red" for s in names]

plt.figure(figsize=(9, 5))
plt.barh(names, percents, color=colors)
plt.xlabel("% of jobs asking for the skill")
plt.title(f"Skill demand across {total} jobs (green = you have it, red = missing)")
plt.tight_layout()
plt.savefig(CHART_FILE)
print(f"\nChart saved as {CHART_FILE}")