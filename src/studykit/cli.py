"""CLI entry point for studykit."""

import sys
from datetime import date, timedelta

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box

from studykit.store import Store
from studykit.core.deadlines import (
    filter_deadlines, days_remaining, urgency_score, is_overdue
)
from studykit.core.grades import (
    course_average, compute_gpa, letter_grade, pct, predict_needed
)
from studykit.core.notes import search_notes, filter_notes, export_markdown
from studykit.core.files import (
    organize_by_type, organize_by_date, find_duplicates, directory_stats, classify_file
)

console = Console()
err_console = Console(stderr=True)


def _error(msg):
    err_console.print(f"[bold red]Error:[/bold red] {msg}")
    sys.exit(1)


def _get_store(ctx):
    return ctx.obj["store"]


@click.group()
@click.option("--data", "data_path", default=None, help="Path to data JSON file.")
@click.pass_context
def main(ctx, data_path):
    """studykit - Student productivity and file management CLI."""
    ctx.ensure_object(dict)
    ctx.obj["store"] = Store(path=data_path)


# ===========================================================================
# DASHBOARD
# ===========================================================================

@main.command()
@click.pass_context
def dashboard(ctx):
    """Show a dashboard with upcoming deadlines, GPA, and notes summary."""
    store = _get_store(ctx)

    deadlines = store.get_deadlines()
    grades = store.get_grades()
    courses = store.get_courses()
    notes = store.get_notes()

    # Upcoming deadlines (next 7 days)
    upcoming = filter_deadlines(deadlines, week=True)

    console.print(Panel("[bold cyan]StudyKit Dashboard[/bold cyan]", expand=False))
    console.print()

    # Deadlines panel
    dl_table = Table(title="Upcoming Deadlines (7 days)", box=box.ROUNDED, expand=False)
    dl_table.add_column("ID", style="dim", width=10)
    dl_table.add_column("Name", style="bold")
    dl_table.add_column("Course")
    dl_table.add_column("Due")
    dl_table.add_column("Priority")
    dl_table.add_column("Days")

    for d in upcoming:
        dr = days_remaining(d["due"])
        style = "yellow" if dr <= 2 else "green"
        dl_table.add_row(
            d["id"],
            d["name"],
            d["course"],
            d["due"],
            d["priority"],
            str(dr),
            style=style,
        )

    if not upcoming:
        console.print("[dim]No upcoming deadlines in the next 7 days.[/dim]")
    else:
        console.print(dl_table)

    console.print()

    # GPA
    gpa = compute_gpa(grades, courses)
    gpa_str = f"{gpa:.2f}" if gpa is not None else "N/A"
    console.print(Panel(f"[bold]Overall GPA:[/bold] {gpa_str}", expand=False))
    console.print()

    # Per-course grade summary
    if courses:
        grade_table = Table(title="Course Grade Summary", box=box.ROUNDED, expand=False)
        grade_table.add_column("Course", style="bold")
        grade_table.add_column("Average")
        grade_table.add_column("Letter")
        grade_table.add_column("Credits")

        for course in courses:
            avg = course_average(grades, course["name"])
            if avg is not None:
                letter = letter_grade(avg)
                grade_table.add_row(
                    course["name"],
                    f"{avg:.1f}%",
                    letter,
                    str(course.get("credits", 3)),
                )
            else:
                grade_table.add_row(
                    course["name"],
                    "N/A",
                    "N/A",
                    str(course.get("credits", 3)),
                )

        console.print(grade_table)
        console.print()

    # Notes summary
    console.print(f"[bold]Total Notes:[/bold] {len(notes)}")


# ===========================================================================
# COURSE COMMANDS
# ===========================================================================

@main.group()
@click.pass_context
def course(ctx):
    """Manage courses."""
    pass


@course.command("add")
@click.argument("name")
@click.option("--credits", "credits_val", default=3, type=int, show_default=True, help="Credit hours.")
@click.option("--semester", default="", help="Semester (e.g. 'Fall 2025').")
@click.pass_context
def course_add(ctx, name, credits_val, semester):
    """Add a new course."""
    store = _get_store(ctx)
    try:
        c = store.add_course(name, credits=credits_val, semester=semester)
        console.print(f"[green]Added course:[/green] {c['name']} ({credits_val} credits, {semester})")
    except ValueError as e:
        _error(str(e))


@course.command("list")
@click.pass_context
def course_list(ctx):
    """List all courses."""
    store = _get_store(ctx)
    courses = store.get_courses()
    if not courses:
        console.print("[dim]No courses found. Add one with 'studykit course add NAME'.[/dim]")
        return

    table = Table(title="Courses", box=box.ROUNDED)
    table.add_column("Name", style="bold")
    table.add_column("Credits", justify="right")
    table.add_column("Semester")

    for c in courses:
        table.add_row(c["name"], str(c.get("credits", 3)), c.get("semester", ""))

    console.print(table)


@course.command("remove")
@click.argument("name")
@click.pass_context
def course_remove(ctx, name):
    """Remove a course by name."""
    store = _get_store(ctx)
    try:
        store.remove_course(name)
        console.print(f"[green]Removed course:[/green] {name}")
    except ValueError as e:
        _error(str(e))


@course.command("summary")
@click.argument("name")
@click.pass_context
def course_summary(ctx, name):
    """Show summary for a specific course."""
    store = _get_store(ctx)
    c = store.get_course(name)
    if c is None:
        _error(f"Course '{name}' not found.")

    grades = store.get_grades()
    deadlines = store.get_deadlines()
    notes = store.get_notes()

    course_grades = [g for g in grades if g["course"].lower() == name.lower()]
    course_deadlines = [d for d in deadlines if d["course"].lower() == name.lower()]
    course_notes = [n for n in notes if n["course"].lower() == name.lower()]

    avg = course_average(grades, name)
    letter = letter_grade(avg) if avg is not None else "N/A"
    avg_str = f"{avg:.1f}%" if avg is not None else "N/A"

    console.print(Panel(f"[bold cyan]{c['name']}[/bold cyan] — {c.get('semester', '')} ({c.get('credits', 3)} credits)", expand=False))
    console.print(f"  [bold]Average:[/bold] {avg_str} ({letter})")
    console.print(f"  [bold]Assignments:[/bold] {len(course_grades)}")
    console.print(f"  [bold]Deadlines:[/bold] {len(course_deadlines)}")
    console.print(f"  [bold]Notes:[/bold] {len(course_notes)}")

    if course_grades:
        console.print()
        g_table = Table(title="Grades", box=box.SIMPLE)
        g_table.add_column("Assignment")
        g_table.add_column("Score", justify="right")
        g_table.add_column("Max", justify="right")
        g_table.add_column("Pct", justify="right")
        g_table.add_column("Weight", justify="right")
        g_table.add_column("Category")

        for g in course_grades:
            p = pct(g["score"], g["max_score"])
            g_table.add_row(
                g["assignment"],
                str(g["score"]),
                str(g["max_score"]),
                f"{p:.1f}%",
                str(g["weight"]),
                g.get("category", ""),
            )
        console.print(g_table)


# ===========================================================================
# DEADLINE COMMANDS
# ===========================================================================

@main.group()
@click.pass_context
def deadline(ctx):
    """Manage deadlines."""
    pass


@deadline.command("add")
@click.argument("name")
@click.option("--course", "-c", required=True, help="Course name.")
@click.option("--due", required=True, help="Due date (YYYY-MM-DD).")
@click.option("--priority", type=click.Choice(["high", "medium", "low"]), default="medium", show_default=True)
@click.pass_context
def deadline_add(ctx, name, course, due, priority):
    """Add a new deadline."""
    store = _get_store(ctx)
    try:
        date.fromisoformat(due)
    except ValueError:
        _error("Invalid date format. Use YYYY-MM-DD.")
    d = store.add_deadline(name, course, due, priority)
    console.print(f"[green]Added deadline:[/green] [{d['id']}] {name} for {course}, due {due} ({priority})")


@deadline.command("list")
@click.option("--course", "-c", default=None, help="Filter by course.")
@click.option("--overdue", is_flag=True, help="Show only overdue deadlines.")
@click.option("--today", is_flag=True, help="Show only deadlines due today.")
@click.option("--week", is_flag=True, help="Show deadlines due within 7 days.")
@click.pass_context
def deadline_list(ctx, course, overdue, today, week):
    """List deadlines."""
    store = _get_store(ctx)
    deadlines = store.get_deadlines()
    filtered = filter_deadlines(deadlines, course=course, overdue=overdue, today=today, week=week)

    if not filtered:
        console.print("[dim]No deadlines found.[/dim]")
        return

    table = Table(title="Deadlines", box=box.ROUNDED)
    table.add_column("ID", style="dim", width=10)
    table.add_column("Name", style="bold")
    table.add_column("Course")
    table.add_column("Due")
    table.add_column("Priority")
    table.add_column("Days Left", justify="right")
    table.add_column("Status")

    for d in filtered:
        dr = days_remaining(d["due"])
        done = d.get("done", False)

        if done:
            row_style = "green"
            status = "Done"
        elif dr < 0:
            row_style = "red"
            status = "Overdue"
        elif dr <= 2:
            row_style = "yellow"
            status = "Soon"
        else:
            row_style = ""
            status = "Pending"

        table.add_row(
            d["id"],
            d["name"],
            d["course"],
            d["due"],
            d["priority"],
            str(dr),
            status,
            style=row_style,
        )

    console.print(table)


@deadline.command("done")
@click.argument("id_prefix")
@click.pass_context
def deadline_done(ctx, id_prefix):
    """Mark a deadline as done."""
    store = _get_store(ctx)
    try:
        d = store.mark_done(id_prefix)
        console.print(f"[green]Marked done:[/green] [{d['id']}] {d['name']}")
    except ValueError as e:
        _error(str(e))


@deadline.command("delete")
@click.argument("id_prefix")
@click.pass_context
def deadline_delete(ctx, id_prefix):
    """Delete a deadline."""
    store = _get_store(ctx)
    try:
        d = store.delete_deadline(id_prefix)
        console.print(f"[green]Deleted deadline:[/green] [{d['id']}] {d['name']}")
    except ValueError as e:
        _error(str(e))


# ===========================================================================
# GRADE COMMANDS
# ===========================================================================

@main.group()
@click.pass_context
def grade(ctx):
    """Manage grades."""
    pass


@grade.command("add")
@click.argument("course_name")
@click.argument("assignment")
@click.argument("score", type=float)
@click.argument("max_score", type=float)
@click.option("--weight", "-w", default=1.0, type=float, show_default=True, help="Assignment weight.")
@click.option("--category", "-cat", default="", help="Category (e.g. homework, exam).")
@click.pass_context
def grade_add(ctx, course_name, assignment, score, max_score, category, weight):
    """Add a grade entry."""
    store = _get_store(ctx)
    if max_score <= 0:
        _error("max_score must be positive.")
    g = store.add_grade(course_name, assignment, score, max_score, weight=weight, category=category)
    p = pct(score, max_score)
    letter = letter_grade(p)
    console.print(f"[green]Added grade:[/green] {assignment} for {course_name}: {score}/{max_score} = {p:.1f}% ({letter})")


@grade.command("summary")
@click.option("--course", "-c", default=None, help="Filter by course.")
@click.pass_context
def grade_summary(ctx, course):
    """Show grade summary."""
    store = _get_store(ctx)
    grades = store.get_grades()
    courses = store.get_courses()

    if course:
        courses_to_show = [c for c in courses if c["name"].lower() == course.lower()]
        if not courses_to_show:
            # Still show if there are grades even without a registered course
            course_names = list({g["course"] for g in grades if g["course"].lower() == course.lower()})
            courses_to_show = [{"name": cn, "credits": 3, "semester": ""} for cn in course_names]
    else:
        # Show all courses with grades
        graded_names = {g["course"] for g in grades}
        registered_names = {c["name"] for c in courses}
        all_names = graded_names | registered_names
        courses_to_show = []
        for name in all_names:
            c = next((c for c in courses if c["name"].lower() == name.lower()), None)
            if c:
                courses_to_show.append(c)
            else:
                courses_to_show.append({"name": name, "credits": 3, "semester": ""})

    if not courses_to_show:
        console.print("[dim]No grades found.[/dim]")
        return

    table = Table(title="Grade Summary", box=box.ROUNDED)
    table.add_column("Course", style="bold")
    table.add_column("Average", justify="right")
    table.add_column("Letter")
    table.add_column("Credits", justify="right")
    table.add_column("Assignments", justify="right")

    for c in courses_to_show:
        avg = course_average(grades, c["name"])
        course_grades = [g for g in grades if g["course"].lower() == c["name"].lower()]
        if avg is not None:
            letter = letter_grade(avg)
            table.add_row(
                c["name"],
                f"{avg:.1f}%",
                letter,
                str(c.get("credits", 3)),
                str(len(course_grades)),
            )
        else:
            table.add_row(c["name"], "N/A", "N/A", str(c.get("credits", 3)), "0")

    console.print(table)


@grade.command("gpa")
@click.pass_context
def grade_gpa(ctx):
    """Show letter grade per course and overall GPA."""
    store = _get_store(ctx)
    grades = store.get_grades()
    courses = store.get_courses()

    table = Table(title="GPA Breakdown", box=box.ROUNDED)
    table.add_column("Course", style="bold")
    table.add_column("Average", justify="right")
    table.add_column("Letter")
    table.add_column("Grade Points", justify="right")
    table.add_column("Credits", justify="right")

    for c in courses:
        avg = course_average(grades, c["name"])
        if avg is not None:
            letter = letter_grade(avg)
            from studykit.core.grades import GRADE_POINTS
            points = GRADE_POINTS.get(letter, 0.0)
            table.add_row(
                c["name"],
                f"{avg:.1f}%",
                letter,
                f"{points:.1f}",
                str(c.get("credits", 3)),
            )
        else:
            table.add_row(c["name"], "N/A", "N/A", "N/A", str(c.get("credits", 3)))

    console.print(table)

    gpa = compute_gpa(grades, courses)
    if gpa is not None:
        overall_letter = letter_grade(gpa * 25)  # Convert back: 4.0 -> A (100%)
        console.print()
        console.print(f"[bold]Overall GPA:[/bold] {gpa:.2f}")
    else:
        console.print()
        console.print("[dim]No grades found to compute GPA.[/dim]")


@grade.command("predict")
@click.argument("course_name")
@click.option("--target", "-t", required=True, type=float, help="Target percentage (e.g. 90).")
@click.option("--remaining", "-r", required=True, type=float, help="Remaining weight of work.")
@click.pass_context
def grade_predict(ctx, course_name, target, remaining):
    """Predict score needed on remaining work to hit target."""
    store = _get_store(ctx)
    grades = store.get_grades()

    needed = predict_needed(grades, course_name, target, remaining)
    if needed is None:
        _error("Could not compute prediction. Check remaining weight > 0.")

    console.print(f"[bold]Course:[/bold] {course_name}")
    console.print(f"[bold]Target:[/bold] {target:.1f}%")
    console.print(f"[bold]Remaining weight:[/bold] {remaining}")
    console.print(f"[bold]Score needed on remaining work:[/bold] {needed:.1f}%")

    if needed > 100:
        console.print(f"[bold red]Warning:[/bold red] You need {needed:.1f}%, which exceeds 100%. Target may be unachievable.")
    elif needed < 0:
        console.print(f"[green]You have already achieved your target![/green]")
    else:
        console.print(f"[green]Achievable![/green]")


# ===========================================================================
# NOTE COMMANDS
# ===========================================================================

@main.group()
@click.pass_context
def note(ctx):
    """Manage notes."""
    pass


@note.command("add")
@click.argument("text")
@click.option("--course", "-c", required=True, help="Course name.")
@click.option("--tags", default="", help="Comma-separated tags.")
@click.pass_context
def note_add(ctx, text, course, tags):
    """Add a note."""
    store = _get_store(ctx)
    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []
    n = store.add_note(text, course, tags=tag_list)
    console.print(f"[green]Added note:[/green] [{n['id']}] for {course}")


@note.command("list")
@click.option("--course", "-c", default=None, help="Filter by course.")
@click.option("--tag", "-t", default=None, help="Filter by tag.")
@click.pass_context
def note_list(ctx, course, tag):
    """List notes."""
    store = _get_store(ctx)
    notes = store.get_notes()
    filtered = filter_notes(notes, course=course, tag=tag)

    if not filtered:
        console.print("[dim]No notes found.[/dim]")
        return

    table = Table(title="Notes", box=box.ROUNDED)
    table.add_column("ID", style="dim", width=10)
    table.add_column("Course", style="bold")
    table.add_column("Text")
    table.add_column("Tags")
    table.add_column("Created")

    for n in filtered:
        table.add_row(
            n["id"],
            n["course"],
            n["text"][:60] + ("..." if len(n["text"]) > 60 else ""),
            ", ".join(n.get("tags", [])),
            n.get("created", "")[:10],
        )

    console.print(table)


@note.command("search")
@click.argument("query")
@click.pass_context
def note_search(ctx, query):
    """Search notes by keyword."""
    store = _get_store(ctx)
    notes = store.get_notes()
    results = search_notes(notes, query)

    if not results:
        console.print(f"[dim]No notes found matching '{query}'.[/dim]")
        return

    console.print(f"[bold]Found {len(results)} note(s) matching '{query}':[/bold]")
    table = Table(box=box.ROUNDED)
    table.add_column("ID", style="dim", width=10)
    table.add_column("Course", style="bold")
    table.add_column("Text")
    table.add_column("Tags")

    for n in results:
        table.add_row(
            n["id"],
            n["course"],
            n["text"][:80] + ("..." if len(n["text"]) > 80 else ""),
            ", ".join(n.get("tags", [])),
        )

    console.print(table)


@note.command("delete")
@click.argument("id_prefix")
@click.pass_context
def note_delete(ctx, id_prefix):
    """Delete a note by ID prefix."""
    store = _get_store(ctx)
    try:
        n = store.delete_note(id_prefix)
        console.print(f"[green]Deleted note:[/green] [{n['id']}]")
    except ValueError as e:
        _error(str(e))


@note.command("export")
@click.option("--course", "-c", default=None, help="Filter by course.")
@click.option("--out", "-o", default=None, help="Output file path (default: stdout).")
@click.pass_context
def note_export(ctx, course, out):
    """Export notes as Markdown."""
    store = _get_store(ctx)
    notes = store.get_notes()
    md = export_markdown(notes, course=course)

    if out:
        from pathlib import Path
        Path(out).write_text(md, encoding="utf-8")
        console.print(f"[green]Exported to:[/green] {out}")
    else:
        console.print(md)


# ===========================================================================
# FILES COMMANDS
# ===========================================================================

@main.group()
@click.pass_context
def files(ctx):
    """File management utilities."""
    pass


@files.command("organize")
@click.argument("directory")
@click.option("--by", "by_mode", type=click.Choice(["type", "date"]), default="type", show_default=True)
@click.option("--dry-run", is_flag=True, help="Show what would happen without moving files.")
@click.pass_context
def files_organize(ctx, directory, by_mode, dry_run):
    """Organize files in a directory by type or date."""
    from pathlib import Path
    d = Path(directory)
    if not d.exists() or not d.is_dir():
        _error(f"Directory not found: {directory}")

    if by_mode == "type":
        moves = organize_by_type(d, dry_run=dry_run)
    else:
        moves = organize_by_date(d, dry_run=dry_run)

    if not moves:
        console.print("[dim]No files to organize.[/dim]")
        return

    table = Table(
        title=f"{'[DRY RUN] ' if dry_run else ''}File Organization ({by_mode})",
        box=box.ROUNDED,
    )
    table.add_column("Source", style="dim")
    table.add_column("Destination", style="bold")

    for src, dst in moves:
        table.add_row(str(src.name), str(dst))

    console.print(table)
    action = "Would move" if dry_run else "Moved"
    console.print(f"[green]{action} {len(moves)} file(s).[/green]")


@files.command("dupes")
@click.argument("directory")
@click.pass_context
def files_dupes(ctx, directory):
    """Find duplicate files in a directory."""
    from pathlib import Path
    d = Path(directory)
    if not d.exists() or not d.is_dir():
        _error(f"Directory not found: {directory}")

    console.print(f"[dim]Scanning for duplicates in {directory}...[/dim]")
    dupes = find_duplicates(d)

    if not dupes:
        console.print("[green]No duplicate files found.[/green]")
        return

    console.print(f"[bold red]Found {len(dupes)} group(s) of duplicate files:[/bold red]")
    console.print()

    for i, (h, paths) in enumerate(dupes.items(), 1):
        total_size = sum(p.stat().st_size for p in paths if p.exists())
        console.print(f"[bold]Group {i}[/bold] (hash: {h[:12]}..., total: {total_size:,} bytes)")
        for p in paths:
            size = p.stat().st_size if p.exists() else 0
            console.print(f"  {p}  [dim]({size:,} bytes)[/dim]")
        console.print()


@files.command("stats")
@click.argument("directory")
@click.pass_context
def files_stats(ctx, directory):
    """Show file statistics for a directory."""
    from pathlib import Path
    d = Path(directory)
    if not d.exists() or not d.is_dir():
        _error(f"Directory not found: {directory}")

    stats = directory_stats(d)

    if not stats:
        console.print("[dim]No files found.[/dim]")
        return

    table = Table(title=f"File Statistics: {directory}", box=box.ROUNDED)
    table.add_column("Category", style="bold")
    table.add_column("Count", justify="right")
    table.add_column("Size (bytes)", justify="right")
    table.add_column("Size", justify="right")

    total_count = sum(v["count"] for v in stats.values())
    max_count = max(v["count"] for v in stats.values()) if stats else 1

    sorted_stats = sorted(stats.items(), key=lambda x: x[1]["count"], reverse=True)

    for category, info in sorted_stats:
        size_bytes = info["size"]
        if size_bytes >= 1024 * 1024:
            size_str = f"{size_bytes / 1024 / 1024:.1f} MB"
        elif size_bytes >= 1024:
            size_str = f"{size_bytes / 1024:.1f} KB"
        else:
            size_str = f"{size_bytes} B"
        table.add_row(category, str(info["count"]), f"{size_bytes:,}", size_str)

    console.print(table)

    # ASCII bar chart by count
    console.print()
    console.print("[bold]File Count Distribution:[/bold]")
    bar_width = 30
    for category, info in sorted_stats:
        count = info["count"]
        bar_len = int((count / max_count) * bar_width) if max_count > 0 else 0
        bar = "#" * bar_len
        console.print(f"  {category:<12} {bar:<{bar_width}} {count}")

    console.print()
    console.print(f"[bold]Total files:[/bold] {total_count}")
