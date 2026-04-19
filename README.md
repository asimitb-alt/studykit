# studykit

**studykit** is a student productivity and file management CLI for undergraduate students.  
Track courses, deadlines, grades, and notes — all from the terminal.

[![CI](https://github.com/asimitb-alt/studykit/actions/workflows/ci.yml/badge.svg)](https://github.com/asimitb-alt/studykit/actions)
![Python](https://img.shields.io/badge/python-3.8%20|%203.9%20|%203.10%20|%203.11%20|%203.12%20|%203.13-blue)
![Platform](https://img.shields.io/badge/platform-Windows%20|%20macOS%20|%20Linux-lightgrey)

---

## Install

```bash
cd studykit
pip install -e .          # basic install
pip install -e ".[dev]"   # includes pytest for running tests
```

---

## Quick Start

```bash
# 1. Register your courses first
studykit course add "CS101"   --credits 3  --semester "Fall 2025"
studykit course add "MATH201" --credits 4  --semester "Fall 2025"

# 2. Track deadlines
studykit deadline add "Programming HW1" --course "CS101" --due 2025-11-15 --priority high

# 3. Log grades
studykit grade add "CS101" "Midterm" 88 100 --weight 2.0 --category exam

# 4. Add notes
studykit note add "Stack overflow: recursion depth exceeded" --course "CS101" --tags "stack,memory"

# 5. See everything at a glance
studykit dashboard
```

> **Important:** You must add a course with `studykit course add` before you can
> attach deadlines, grades, or notes to it.

---

## All Commands

### `studykit dashboard`

Single-screen overview showing:
- Upcoming deadlines in the next 7 days (color-coded by urgency)
- Overall GPA
- Per-course grade summary
- Total note count

```
studykit dashboard
```

---

### Course commands

Courses are the foundation — register them before using any other command.

```bash
studykit course add NAME [--credits N] [--semester TEXT]
studykit course list
studykit course remove NAME
studykit course summary NAME
```

| Option | Default | Description |
|--------|---------|-------------|
| `--credits` | `3` | Credit hours (must be ≥ 0) |
| `--semester` | `""` | e.g. `"Fall 2025"` |

**Validation:**
- Name cannot be empty or whitespace-only
- Credits cannot be negative
- Duplicate course names are rejected

**Examples:**
```bash
studykit course add "CS101" --credits 3 --semester "Fall 2025"
studykit course list
studykit course summary "CS101"
studykit course remove "CS101"
```

**`course list` output:**
```
         Courses
┌─────────┬─────────┬───────────┐
│ Name    │ Credits │ Semester  │
├─────────┼─────────┼───────────┤
│ CS101   │       3 │ Fall 2025 │
│ MATH201 │       4 │ Fall 2025 │
└─────────┴─────────┴───────────┘
```

---

### Deadline commands

```bash
studykit deadline add NAME --course COURSE --due YYYY-MM-DD [--priority high|medium|low]
studykit deadline list [--course COURSE] [--overdue] [--today] [--week]
studykit deadline done ID
studykit deadline delete ID
```

| Option | Default | Description |
|--------|---------|-------------|
| `--course` | required | Must be a registered course |
| `--due` | required | Date in `YYYY-MM-DD` format |
| `--priority` | `medium` | `high`, `medium`, or `low` |

**Validation:**
- Name cannot be empty or whitespace-only
- Course must already be registered — otherwise an error with the fix is shown
- Duplicate deadline name within the same course is rejected
- Same deadline name across different courses is allowed
- Due date must be a valid `YYYY-MM-DD` date

**`deadline list` output:**

Rows are color-coded:
- **Red** — overdue
- **Yellow** — due within 2 days
- **Green** — marked as done
- White — pending, not urgent

```bash
studykit deadline list
studykit deadline list --course "CS101"
studykit deadline list --overdue
studykit deadline list --week      # due in the next 7 days
studykit deadline list --today
```

To mark done or delete, use the 8-character ID shown in `deadline list`:
```bash
studykit deadline done   a1b2c3d4
studykit deadline delete a1b2c3d4
```

---

### Grade commands

```bash
studykit grade add COURSE ASSIGNMENT SCORE MAX [--weight W] [--category CAT]
studykit grade summary [--course COURSE]
studykit grade gpa
studykit grade predict COURSE --target T --remaining R
```

| Argument / Option | Description |
|-------------------|-------------|
| `COURSE` | Must be a registered course |
| `ASSIGNMENT` | Assignment name (unique per course) |
| `SCORE` | Score received (≥ 0) |
| `MAX` | Maximum possible score (> 0) |
| `--weight` | Relative weight (default `1.0`, must be > 0) |
| `--category` | e.g. `homework`, `exam`, `quiz` |

**Validation:**
- Score cannot be negative
- Score cannot exceed max score
- Max score must be greater than 0
- Weight must be greater than 0
- Course must already be registered
- Duplicate assignment name within the same course is rejected

**`grade summary` output:**
```
          Grade Summary
┌─────────┬─────────┬────────┬─────────┬─────────────┐
│ Course  │ Average │ Letter │ Credits │ Assignments │
├─────────┼─────────┼────────┼─────────┼─────────────┤
│ CS101   │   89.3% │ B+     │       3 │           2 │
│ MATH201 │   77.3% │ C+     │       4 │           2 │
└─────────┴─────────┴────────┴─────────┴─────────────┘
```

**`grade predict` output:**
```bash
# What score do I need on the final (weight 2.0) to reach 90% overall?
studykit grade predict "CS101" --target 90 --remaining 2.0
```
```
Course:  CS101
Target:  90.0%
Remaining weight: 2.0
Score needed on remaining work: 94.5%
Achievable!
```
If the target is mathematically impossible:
```
Warning: You need 107.0%, which exceeds 100%. Target may be unachievable.
```
`--target` must be between 0 and 100. `--remaining` must be greater than 0.

---

### Note commands

```bash
studykit note add TEXT --course COURSE [--tags tag1,tag2]
studykit note list [--course COURSE] [--tag TAG]
studykit note search QUERY
studykit note delete ID
studykit note export [--course COURSE] [--out FILE]
```

**Validation:**
- Text cannot be empty or whitespace-only
- Course must already be registered
- Duplicate note text within the same course is rejected
- Same text across different courses is allowed

```bash
studykit note add "Lambda functions are anonymous" --course "CS101" --tags "python,functional"
studykit note list
studykit note list --course "CS101"
studykit note list --tag "python"
studykit note search "recursion"     # case-insensitive; searches text, course, and tags
studykit note delete a1b2c3d4
studykit note export                 # prints all notes as Markdown
studykit note export --course "CS101"
studykit note export --out notes.md
```

---

### Files commands

No course registration required — these work on any directory.

```bash
studykit files organize DIR [--by type|date] [--dry-run]
studykit files dupes DIR
studykit files stats DIR
```

**`files organize`** — moves files into subfolders:
- `--by type` (default): sorts into `pdf/`, `code/`, `images/`, `docs/`, `data/`, `archives/`, `videos/`, `audio/`, `other/`
- `--by date`: sorts into `YYYY-MM/` folders based on file modification date
- `--dry-run`: shows what *would* move without touching any files

```bash
studykit files organize ~/Downloads --by type --dry-run
studykit files organize ~/Downloads --by type
studykit files organize ~/Downloads --by date
```

**`files dupes`** — finds exact duplicate files using SHA-256 content hashing:
```bash
studykit files dupes ~/Downloads
# Found 2 group(s) of duplicate files:
# Group 1 (hash: a636bd7cd420..., total: 4,096 bytes)
#   /home/user/Downloads/report.pdf  (2,048 bytes)
#   /home/user/Downloads/report_copy.pdf  (2,048 bytes)
```

**`files stats`** — breakdown by file category with ASCII bar chart:
```bash
studykit files stats ~/Downloads
```
```
        File Statistics: /home/user/Downloads
┌──────────┬───────┬──────────────┬────────┐
│ Category │ Count │ Size (bytes) │ Size   │
├──────────┼───────┼──────────────┼────────┤
│ pdf      │    12 │    5,242,880 │ 5.0 MB │
│ images   │     8 │    2,097,152 │ 2.0 MB │
│ code     │     5 │       20,480 │ 20 KB  │
└──────────┴───────┴──────────────┴────────┘

File Count Distribution:
  pdf          ##############################  12
  images       ####################            8
  code         ############                    5

Total files: 25
```

**Supported file categories:**

| Category | Extensions |
|----------|-----------|
| pdf | `.pdf` |
| images | `.jpg` `.jpeg` `.png` `.gif` `.bmp` `.tiff` `.svg` `.webp` |
| code | `.py` `.js` `.ts` `.java` `.c` `.cpp` `.h` `.cs` `.go` `.rs` `.r` `.m` `.ipynb` |
| docs | `.doc` `.docx` `.odt` `.txt` `.md` `.rst` `.tex` `.pptx` `.ppt` `.xlsx` `.xls` `.csv` |
| data | `.json` `.xml` `.yaml` `.yml` `.sql` `.db` `.h5` `.npy` `.npz` `.mat` |
| archives | `.zip` `.tar` `.gz` `.7z` `.rar` `.bz2` |
| videos | `.mp4` `.avi` `.mov` `.mkv` `.wmv` |
| audio | `.mp3` `.wav` `.flac` `.aac` `.ogg` |

---

## Error Handling

studykit validates all inputs and gives clear, actionable error messages:

| Bad input | Error |
|-----------|-------|
| `course add ""` | `Error: Course name cannot be empty.` |
| `course add CS101 --credits -1` | `Error: -1 is not in the range x>=0.` |
| `deadline add "HW1" --course FAKE …` | `Error: Course 'FAKE' not found. Add it first with: studykit course add "FAKE"` |
| `deadline add "HW1" --course CS101 …` (duplicate) | `Error: Deadline 'HW1' already exists for course 'CS101'.` |
| `grade add CS101 HW1 110 100` | `Error: Score (110.0) cannot exceed max score (100.0).` |
| `grade add CS101 HW1 90 0` | `Error: 0 is not in the range x>=0.01.` |
| `grade predict CS101 --target 150 …` | `Error: 150 is not in the range 0<=x<=100.` |
| `grade predict CS101 --remaining 0 …` | `Error: 0 is not in the range x>=0.01.` |
| `note add "  " --course CS101` | `Error: Note text cannot be empty.` |
| `note add "Same text" --course CS101` (duplicate) | `Error: An identical note already exists for course 'CS101'.` |

---

## Data Storage

All data lives in a single JSON file — no database server needed.

**Default location:** `~/.studykit/data.json`

```json
{
  "courses":   [{ "name": "CS101", "credits": 3, "semester": "Fall 2025" }],
  "deadlines": [{ "id": "a1b2c3d4", "name": "HW1", "course": "CS101",
                  "due": "2025-11-15", "priority": "high", "done": false, "created": "…" }],
  "grades":    [{ "id": "e5f6a7b8", "course": "CS101", "assignment": "Midterm",
                  "score": 88, "max_score": 100, "weight": 2.0, "category": "exam", "created": "…" }],
  "notes":     [{ "id": "c9d0e1f2", "text": "…", "course": "CS101",
                  "tags": ["memory"], "created": "…" }]
}
```

Each item has a unique 8-character ID used for `done`, `delete`, etc.

Use `--data PATH` on any command to point to a custom file:
```bash
studykit --data ~/school/spring2026.json course list
```

---

## Grade Scale

| Percentage | Letter | GPA Points |
|------------|--------|------------|
| 93–100 | A  | 4.0 |
| 90–92  | A- | 3.7 |
| 87–89  | B+ | 3.3 |
| 83–86  | B  | 3.0 |
| 80–82  | B- | 2.7 |
| 77–79  | C+ | 2.3 |
| 73–76  | C  | 2.0 |
| 70–72  | C- | 1.7 |
| 67–69  | D+ | 1.3 |
| 63–66  | D  | 1.0 |
| 60–62  | D- | 0.7 |
| 0–59   | F  | 0.0 |

GPA is computed as a credit-weighted average across all courses that have recorded grades.

---

## Python API

Use studykit programmatically in your own scripts:

```python
from studykit.store import Store
from studykit.core.deadlines import filter_deadlines, days_remaining
from studykit.core.grades import compute_gpa, course_average, letter_grade, predict_needed
from studykit.core.notes import search_notes, filter_notes, export_markdown
from studykit.core.files import find_duplicates, directory_stats, organize_by_type

store = Store()                    # uses ~/.studykit/data.json
store = Store(path="custom.json")  # or a custom path

# Courses
store.add_course("CS101", credits=3, semester="Fall 2025")
courses = store.get_courses()

# Deadlines
d = store.add_deadline("HW1", "CS101", "2025-11-15", "high")
upcoming = filter_deadlines(store.get_deadlines(), week=True)
overdue  = filter_deadlines(store.get_deadlines(), overdue=True)

# Grades
store.add_grade("CS101", "Midterm", 88, 100, weight=2.0, category="exam")
avg    = course_average(store.get_grades(), "CS101")   # float or None
gpa    = compute_gpa(store.get_grades(), courses)       # float or None
letter = letter_grade(avg)                              # "A", "B+", …
needed = predict_needed(store.get_grades(), "CS101", target_pct=90, remaining_weight=1.0)

# Notes
store.add_note("Cache lines matter", "CS101", tags=["memory"])
results  = search_notes(store.get_notes(), "cache")
filtered = filter_notes(store.get_notes(), course="CS101", tag="memory")
md       = export_markdown(store.get_notes(), course="CS101")

# Files
from pathlib import Path
dupes = find_duplicates(Path("~/Downloads"))
stats = directory_stats(Path("~/Downloads"))
moves = organize_by_type(Path("~/Downloads"), dry_run=True)
```

See `examples/demo_workflow.py` for a full walkthrough.

---

## Running Tests

```bash
pip install -e ".[dev]"

pytest tests/ -v              # all 162 tests
pytest tests/test_store.py    # persistence layer only
pytest tests/test_core_grades.py  # grade logic only
pytest tests/ --tb=short      # compact failure output
```

Tests run on **Python 3.8 – 3.13** across **Ubuntu, Windows, and macOS** via GitHub Actions.

| Test file | Tests | What it covers |
|-----------|------:|----------------|
| `test_store.py` | 27 | JSON persistence, validation, duplicate checks |
| `test_core_deadlines.py` | 15 | Urgency scoring, overdue detection, filtering |
| `test_core_grades.py` | 17 | Weighted avg, letter grade, GPA, prediction |
| `test_core_notes.py` | 12 | Search, filter, Markdown export |
| `test_core_files.py` | 18 | SHA-256 dedup, classify, organize, stats |
| `test_cli_courses.py` | 10 | course add/list/remove/summary + validation |
| `test_cli_deadlines.py` | 15 | deadline CRUD, filters, validation |
| `test_cli_grades.py` | 15 | grade CRUD, GPA, predict, validation |
| `test_cli_notes.py` | 15 | note CRUD, search, export, validation |
| `test_cli_files.py` | 18 | files organize/dupes/stats |
| **Total** | **162** | |

---

## Demo

```bash
python examples/demo_workflow.py
```

Walks through a complete workflow using the Python API directly:
adding courses, deadlines, grades, and notes; computing GPA; searching notes; and finding duplicate files.
