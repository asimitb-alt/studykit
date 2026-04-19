# StudyKit

**studykit** is a student productivity and file management CLI for undergraduate students. It helps you track courses, deadlines, grades, and notes — all from the terminal.

---

## Installation

```bash
cd /path/to/studykit
pip install -e ".[dev]"
```

This installs the `studykit` command and all dependencies (`click`, `rich`).

---

## Quick Start

```bash
# Add your courses
studykit course add "CS101" --credits 3 --semester "Fall 2025"
studykit course add "MATH201" --credits 4 --semester "Fall 2025"

# Track deadlines
studykit deadline add "Programming HW1" --course CS101 --due 2025-11-15 --priority high

# Record grades
studykit grade add CS101 "Midterm" 88 100 --weight 2.0 --category exam

# Add notes
studykit note add "Stack overflow: recursion depth exceeded" --course CS101 --tags "stack,memory"

# See everything at a glance
studykit dashboard
```

---

## All Commands

### Dashboard

```bash
studykit dashboard
```

Shows:
- Upcoming deadlines (next 7 days), color-coded by urgency
- Overall GPA
- Per-course grade summary
- Total notes count

---

### Course Commands

```bash
# Add a course
studykit course add NAME [--credits N] [--semester S]
studykit course add "CS101" --credits 3 --semester "Fall 2025"

# List all courses
studykit course list

# Remove a course
studykit course remove NAME
studykit course remove "CS101"

# Show detailed summary for a course
studykit course summary NAME
studykit course summary "CS101"
```

Example output for `course list`:
```
                Courses
┌──────────┬─────────┬────────────┐
│ Name     │ Credits │ Semester   │
├──────────┼─────────┼────────────┤
│ CS101    │       3 │ Fall 2025  │
│ MATH201  │       4 │ Fall 2025  │
└──────────┴─────────┴────────────┘
```

---

### Deadline Commands

```bash
# Add a deadline
studykit deadline add NAME --course COURSE --due YYYY-MM-DD [--priority high|medium|low]
studykit deadline add "Final Project" --course CS101 --due 2025-12-15 --priority high

# List deadlines (with optional filters)
studykit deadline list [--course COURSE] [--overdue] [--today] [--week]
studykit deadline list --course CS101
studykit deadline list --overdue
studykit deadline list --week

# Mark a deadline as done (use ID prefix from list)
studykit deadline done ID_PREFIX
studykit deadline done a1b2c3d4

# Delete a deadline
studykit deadline delete ID_PREFIX
studykit deadline delete a1b2c3d4
```

Row colors in deadline list:
- **Red**: overdue
- **Yellow**: due within 2 days
- **Green**: done

---

### Grade Commands

```bash
# Add a grade
studykit grade add COURSE ASSIGNMENT SCORE MAX [--weight W] [--category CAT]
studykit grade add CS101 "Midterm" 88 100 --weight 2.0 --category exam
studykit grade add MATH201 "Quiz 1" 75 100 --weight 0.5

# Show grade summary
studykit grade summary [--course COURSE]
studykit grade summary
studykit grade summary --course CS101

# Show GPA breakdown
studykit grade gpa

# Predict score needed to hit a target
studykit grade predict COURSE --target TARGET_PCT --remaining REMAINING_WEIGHT
studykit grade predict CS101 --target 90 --remaining 1.0
```

Example output for `grade predict`:
```
Course: CS101
Target: 90.0%
Remaining weight: 1.0
Score needed on remaining work: 94.5%
Achievable!
```

If target is not achievable:
```
Warning: You need 105.0%, which exceeds 100%. Target may be unachievable.
```

---

### Note Commands

```bash
# Add a note
studykit note add TEXT --course COURSE [--tags tag1,tag2]
studykit note add "Lambda functions are anonymous functions" --course CS101 --tags "python,functional"

# List notes
studykit note list [--course COURSE] [--tag TAG]
studykit note list --course CS101
studykit note list --tag algorithms

# Search notes (case-insensitive, searches text, course, and tags)
studykit note search QUERY
studykit note search "recursion"

# Delete a note
studykit note delete ID_PREFIX

# Export notes as Markdown
studykit note export [--course COURSE] [--out FILE]
studykit note export                          # prints to stdout
studykit note export --course CS101
studykit note export --out notes.md
studykit note export --course CS101 --out cs101_notes.md
```

---

### Files Commands

```bash
# Organize files into subdirectories by type or date
studykit files organize DIR [--by type|date] [--dry-run]
studykit files organize ~/Downloads --by type
studykit files organize ~/Downloads --by date
studykit files organize ~/Downloads --dry-run    # preview without moving

# Find duplicate files
studykit files dupes DIR
studykit files dupes ~/Documents

# Show file statistics with ASCII bar chart
studykit files stats DIR
studykit files stats ~/Downloads
```

Example output for `files stats`:
```
        File Statistics: /home/user/Downloads
┌──────────┬───────┬──────────────┬────────┐
│ Category │ Count │ Size (bytes) │ Size   │
├──────────┼───────┼──────────────┼────────┤
│ pdf      │    12 │    5,242,880 │ 5.0 MB │
│ docs     │     8 │      819,200 │ 800 KB │
│ code     │     5 │       20,480 │ 20.0 KB│
└──────────┴───────┴──────────────┴────────┘

File Count Distribution:
  pdf          ##############################  12
  docs         ####################            8
  code         ############                    5

Total files: 25
```

---

## File Type Categories

| Category | Extensions |
|----------|-----------|
| pdf | .pdf |
| images | .jpg .jpeg .png .gif .bmp .tiff .svg .webp |
| code | .py .js .ts .java .c .cpp .h .cs .go .rs .r .m .ipynb |
| docs | .doc .docx .odt .txt .md .rst .tex .pptx .ppt .xlsx .xls .csv |
| data | .json .xml .yaml .yml .sql .db .h5 .npy .npz .mat |
| archives | .zip .tar .gz .7z .rar .bz2 |
| videos | .mp4 .avi .mov .mkv .wmv |
| audio | .mp3 .wav .flac .aac .ogg |

---

## Python API

You can use studykit programmatically:

```python
from studykit.store import Store
from studykit.core.deadlines import filter_deadlines, days_remaining
from studykit.core.grades import compute_gpa, course_average, letter_grade, predict_needed
from studykit.core.notes import search_notes, filter_notes, export_markdown
from studykit.core.files import find_duplicates, directory_stats, organize_by_type

# Create or open a store
store = Store(path="/path/to/data.json")

# Courses
store.add_course("CS101", credits=3, semester="Fall 2025")
courses = store.get_courses()
course = store.get_course("CS101")
store.remove_course("CS101")

# Deadlines
d = store.add_deadline("HW1", "CS101", "2025-11-15", "high")
deadlines = store.get_deadlines()
store.mark_done(d["id"])
store.delete_deadline(d["id"])

# Filter and sort deadlines
upcoming = filter_deadlines(deadlines, week=True)
overdue = filter_deadlines(deadlines, overdue=True)

# Grades
store.add_grade("CS101", "Midterm", 88, 100, weight=2.0, category="exam")
grades = store.get_grades()

# Compute averages and GPA
avg = course_average(grades, "CS101")        # float or None
gpa = compute_gpa(grades, courses)          # float or None
grade = letter_grade(avg)                   # "A", "B+", etc.

# Predict needed score
needed = predict_needed(grades, "CS101", target_pct=90, remaining_weight=1.0)

# Notes
store.add_note("Lambda functions", "CS101", tags=["python", "functional"])
notes = store.get_notes()

results = search_notes(notes, "lambda")     # case-insensitive search
filtered = filter_notes(notes, course="CS101", tag="python")
md = export_markdown(notes, course="CS101") # returns Markdown string

# Files
from pathlib import Path
dupes = find_duplicates(Path("~/Downloads"))
stats = directory_stats(Path("~/Downloads"))
moves = organize_by_type(Path("~/Downloads"), dry_run=True)
```

---

## Global Options

All commands accept a `--data PATH` option to specify a custom data file location:

```bash
studykit --data /path/to/custom.json course list
studykit --data /path/to/custom.json dashboard
```

Default data location: `~/.studykit/data.json`

---

## Running Tests

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest tests/ -v

# Run specific test module
pytest tests/test_store.py -v
pytest tests/test_core_grades.py -v

# Run with coverage
pip install pytest-cov
pytest tests/ -v --cov=studykit
```

Expected: 60+ tests, all passing.

---

## Demo Workflow

Run the included demo script to see the Python API in action:

```bash
python examples/demo_workflow.py
```

This demonstrates:
- Creating a Store in a temporary directory
- Adding courses, deadlines, grades, and notes
- Using `filter_deadlines`, `compute_gpa`, `search_notes`, and `find_duplicates`
- Printing results with labels

---

## Data Storage

All data is stored in a single JSON file (default: `~/.studykit/data.json`). The structure is:

```json
{
  "courses": [...],
  "deadlines": [...],
  "grades": [...],
  "notes": [...]
}
```

Each item has a unique 8-character ID (UUID prefix) for referencing in commands.

---

## Grade Scale

| Percentage | Letter | GPA Points |
|-----------|--------|-----------|
| 93-100 | A | 4.0 |
| 90-92 | A- | 3.7 |
| 87-89 | B+ | 3.3 |
| 83-86 | B | 3.0 |
| 80-82 | B- | 2.7 |
| 77-79 | C+ | 2.3 |
| 73-76 | C | 2.0 |
| 70-72 | C- | 1.7 |
| 67-69 | D+ | 1.3 |
| 63-66 | D | 1.0 |
| 60-62 | D- | 0.7 |
| 0-59 | F | 0.0 |

GPA is computed as a credit-weighted average across all courses with recorded grades.
