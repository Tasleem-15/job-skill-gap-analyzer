# Job Skill-Gap Analyzer

A Python tool that reads job descriptions, counts which skills companies ask for most, and shows which in-demand skills I am still missing.

## Problem
Job postings list dozens of skills, and it is hard to know what to learn first. This tool measures real demand instead of guessing.

## Features
- Reads job descriptions from text files and counts skill mentions
- Matches skills as whole words (so `java` does not match `javascript`)
- Compares demand with my own skills and shows the gap
- Gives a match score
- Stores every run in a SQLite database and queries the top missing skills with SQL
- Saves a bar chart (green = have, red = missing)

## Output
![Chart](chart.png)

*Based on 11 Software Engineer fresher postings, Nov 2026.*

## Tech
Python 3, `re` (regex), `sqlite3`, `matplotlib`, JSON

## How to run
```bash
pip install matplotlib
python main.py
```
1. Put job descriptions in the `jobs` folder as `job1.txt`, `job2.txt`...
2. List your skills in `my_skills.txt`, one per line.
3. Edit `skills.json` to change which skills are searched.

## Limitations
- Small sample size (11 jobs)
- Keyword matching cannot understand synonyms such as "ML" and "machine learning"

## Future improvements
- Synonym handling
- Larger dataset
- A web interface