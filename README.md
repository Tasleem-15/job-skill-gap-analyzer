# Job Skill-Gap Analyzer

A Python tool that reads job descriptions, counts which skills appear most, and shows which in-demand skills you are still missing.

## How it works
1. Save job descriptions as `job1.txt`, `job2.txt`... in the `jobs` folder.
2. List your skills in `my_skills.txt`, one per line.
3. Run `python main.py`.

The program checks each skill as a whole word (so `java` does not match `javascript`), calculates the share of jobs that mention it, and compares it with your skills.

## Example output
(paste your screenshot here)

## Tech
Python 3, `os`, `re` (regular expressions)

## Possible improvements
- Add a bar chart with matplotlib
- Read skills from a CSV file
- Build a web version with React and Node.js