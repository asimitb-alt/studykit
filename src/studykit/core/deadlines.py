"""Deadline logic for studykit."""

from datetime import date, timedelta

PRIORITY_WEIGHTS = {"high": 3, "medium": 2, "low": 1}


def days_remaining(due_str):
    """Return number of days from today to the due date (can be negative if overdue)."""
    due = date.fromisoformat(due_str)
    today = date.today()
    return (due - today).days


def urgency_score(deadline):
    """Compute urgency score: days_remaining / priority_weight. Lower = more urgent."""
    weight = PRIORITY_WEIGHTS.get(deadline.get("priority", "medium"), 2)
    days = days_remaining(deadline["due"])
    return days / weight


def is_overdue(deadline):
    """Return True if the deadline is past due and not marked done."""
    return days_remaining(deadline["due"]) < 0 and not deadline.get("done", False)


def filter_deadlines(deadlines, course=None, overdue=False, today=False, week=False):
    """
    Filter deadlines and sort by urgency_score.

    - Excludes done items unless overdue filter is explicitly set.
    - course: filter to specific course
    - overdue: show only overdue items
    - today: show only items due today
    - week: show items due within next 7 days
    """
    result = [d for d in deadlines if not d.get("done", False)]

    if course:
        result = [d for d in result if d["course"].lower() == course.lower()]

    if overdue:
        result = [d for d in result if is_overdue(d)]
    elif today:
        result = [d for d in result if days_remaining(d["due"]) == 0]
    elif week:
        result = [d for d in result if 0 <= days_remaining(d["due"]) <= 7]

    result.sort(key=urgency_score)
    return result
