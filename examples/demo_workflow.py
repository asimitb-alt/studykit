"""
Demo workflow for studykit.

Demonstrates:
1. Creating a Store in a temp dir
2. Adding courses, deadlines, grades, and notes
3. Calling core logic functions
4. Printing results with labels
"""

import tempfile
from pathlib import Path

from studykit.store import Store
from studykit.core.deadlines import filter_deadlines, days_remaining
from studykit.core.grades import compute_gpa, course_average, letter_grade, predict_needed
from studykit.core.notes import search_notes, export_markdown
from studykit.core.files import find_duplicates, directory_stats


def main():
    print("=" * 60)
    print("  StudyKit Demo Workflow")
    print("=" * 60)
    print()

    with tempfile.TemporaryDirectory() as tmpdir:
        data_file = Path(tmpdir) / "data.json"
        store = Store(path=data_file)

        # -------------------------------------------------------
        # 1. Add courses
        # -------------------------------------------------------
        print("[STEP 1] Adding courses...")
        cs = store.add_course("CS101", credits=3, semester="Fall 2025")
        math = store.add_course("MATH201", credits=4, semester="Fall 2025")
        print(f"  + {cs['name']} ({cs['credits']} credits, {cs['semester']})")
        print(f"  + {math['name']} ({math['credits']} credits, {math['semester']})")
        print()

        # -------------------------------------------------------
        # 2. Add deadlines
        # -------------------------------------------------------
        print("[STEP 2] Adding deadlines...")
        d1 = store.add_deadline("Programming HW1", "CS101", "2099-11-01", "high")
        d2 = store.add_deadline("Calculus Exam", "MATH201", "2099-11-15", "high")
        d3 = store.add_deadline("Project Proposal", "CS101", "2099-12-01", "medium")
        print(f"  + [{d1['id']}] {d1['name']} due {d1['due']} (priority: {d1['priority']})")
        print(f"  + [{d2['id']}] {d2['name']} due {d2['due']} (priority: {d2['priority']})")
        print(f"  + [{d3['id']}] {d3['name']} due {d3['due']} (priority: {d3['priority']})")
        print()

        # -------------------------------------------------------
        # 3. Add grades
        # -------------------------------------------------------
        print("[STEP 3] Adding grades...")
        g1 = store.add_grade("CS101", "Lab 1", 92, 100, weight=1.0, category="lab")
        g2 = store.add_grade("CS101", "Midterm", 88, 100, weight=2.0, category="exam")
        g3 = store.add_grade("MATH201", "Problem Set 1", 75, 100, weight=1.0, category="homework")
        g4 = store.add_grade("MATH201", "Quiz 1", 82, 100, weight=0.5, category="quiz")
        print(f"  + {g1['course']}/{g1['assignment']}: {g1['score']}/{g1['max_score']}")
        print(f"  + {g2['course']}/{g2['assignment']}: {g2['score']}/{g2['max_score']}")
        print(f"  + {g3['course']}/{g3['assignment']}: {g3['score']}/{g3['max_score']}")
        print(f"  + {g4['course']}/{g4['assignment']}: {g4['score']}/{g4['max_score']}")
        print()

        # -------------------------------------------------------
        # 4. Add notes
        # -------------------------------------------------------
        print("[STEP 4] Adding notes...")
        n1 = store.add_note(
            "Stack overflow occurs when recursion depth exceeds system limits.",
            "CS101", ["stack", "recursion", "memory"]
        )
        n2 = store.add_note(
            "Integration by parts: integral(u dv) = uv - integral(v du)",
            "MATH201", ["integration", "calculus"]
        )
        n3 = store.add_note(
            "Big O notation describes worst-case time complexity.",
            "CS101", ["algorithms", "complexity", "big-o"]
        )
        print(f"  + [{n1['id']}] CS101: {n1['text'][:50]}...")
        print(f"  + [{n2['id']}] MATH201: {n2['text'][:50]}...")
        print(f"  + [{n3['id']}] CS101: {n3['text'][:50]}...")
        print()

        # -------------------------------------------------------
        # 5. filter_deadlines
        # -------------------------------------------------------
        print("[STEP 5] Filtering deadlines (all upcoming)...")
        all_deadlines = store.get_deadlines()
        filtered = filter_deadlines(all_deadlines)
        print(f"  Total non-done deadlines: {len(filtered)}")
        for d in filtered:
            dr = days_remaining(d["due"])
            print(f"  [{d['priority'].upper():6}] {d['name']} - due in {dr} days")
        print()

        # -------------------------------------------------------
        # 6. compute_gpa
        # -------------------------------------------------------
        print("[STEP 6] Computing GPA...")
        grades = store.get_grades()
        courses = store.get_courses()

        for course in courses:
            avg = course_average(grades, course["name"])
            if avg is not None:
                letter = letter_grade(avg)
                print(f"  {course['name']}: {avg:.1f}% ({letter})")

        gpa = compute_gpa(grades, courses)
        print(f"  Overall GPA: {gpa:.2f}" if gpa else "  Overall GPA: N/A")
        print()

        # -------------------------------------------------------
        # 7. predict_needed
        # -------------------------------------------------------
        print("[STEP 7] Predicting needed score for CS101...")
        needed = predict_needed(grades, "CS101", target_pct=90, remaining_weight=1.0)
        if needed is not None:
            print(f"  To achieve 90% overall in CS101 with 1.0 weight remaining:")
            print(f"  You need: {needed:.1f}% on remaining work")
        print()

        # -------------------------------------------------------
        # 8. search_notes
        # -------------------------------------------------------
        print("[STEP 8] Searching notes for 'calculus'...")
        notes = store.get_notes()
        results = search_notes(notes, "calculus")
        print(f"  Found {len(results)} note(s) matching 'calculus':")
        for n in results:
            print(f"  [{n['course']}] {n['text'][:60]}")
        print()

        # -------------------------------------------------------
        # 9. find_duplicates on a temp dir
        # -------------------------------------------------------
        print("[STEP 9] Finding duplicate files in a temp directory...")
        files_dir = Path(tmpdir) / "test_files"
        files_dir.mkdir()
        (files_dir / "original.txt").write_text("same content")
        (files_dir / "copy.txt").write_text("same content")
        (files_dir / "unique.txt").write_text("different content")

        dupes = find_duplicates(files_dir)
        print(f"  Duplicate groups found: {len(dupes)}")
        for h, paths in dupes.items():
            print(f"  Hash {h[:12]}...: {[str(p.name) for p in paths]}")
        print()

        # -------------------------------------------------------
        # 10. directory_stats
        # -------------------------------------------------------
        print("[STEP 10] Directory stats for files_dir...")
        stats_dir = Path(tmpdir) / "stats_files"
        stats_dir.mkdir()
        (stats_dir / "report.pdf").write_bytes(b"pdf content")
        (stats_dir / "analysis.py").write_text("# analysis")
        (stats_dir / "notes.md").write_text("# notes")
        (stats_dir / "data.json").write_text("{}")

        stats = directory_stats(stats_dir)
        print(f"  Stats for {stats_dir.name}/:")
        for category, info in sorted(stats.items()):
            print(f"    {category}: {info['count']} file(s), {info['size']} bytes")
        print()

    print("=" * 60)
    print("  Demo complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
