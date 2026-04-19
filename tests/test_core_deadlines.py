"""Tests for studykit.core.deadlines."""

import pytest
from datetime import date, timedelta
from studykit.core.deadlines import (
    days_remaining, urgency_score, is_overdue, filter_deadlines, PRIORITY_WEIGHTS
)


def make_deadline(name="HW1", course="CS101", due_offset=7, priority="medium", done=False):
    due = (date.today() + timedelta(days=due_offset)).isoformat()
    return {
        "id": "abcd1234",
        "name": name,
        "course": course,
        "due": due,
        "priority": priority,
        "done": done,
    }


def test_days_remaining_future():
    future = (date.today() + timedelta(days=5)).isoformat()
    assert days_remaining(future) == 5


def test_days_remaining_past():
    past = (date.today() - timedelta(days=3)).isoformat()
    assert days_remaining(past) == -3


def test_days_remaining_today():
    today = date.today().isoformat()
    assert days_remaining(today) == 0


def test_urgency_score_high_priority_lower():
    d_high = make_deadline(due_offset=6, priority="high")
    d_low = make_deadline(due_offset=6, priority="low")
    assert urgency_score(d_high) < urgency_score(d_low)


def test_urgency_score_sooner_lower():
    d_soon = make_deadline(due_offset=2, priority="medium")
    d_later = make_deadline(due_offset=10, priority="medium")
    assert urgency_score(d_soon) < urgency_score(d_later)


def test_is_overdue_true():
    d = make_deadline(due_offset=-1, priority="medium", done=False)
    assert is_overdue(d) is True


def test_is_overdue_false_future():
    d = make_deadline(due_offset=5, priority="medium", done=False)
    assert is_overdue(d) is False


def test_is_overdue_false_done():
    d = make_deadline(due_offset=-3, priority="high", done=True)
    assert is_overdue(d) is False


def test_filter_deadlines_excludes_done():
    deadlines = [
        make_deadline("D1", done=False),
        make_deadline("D2", done=True),
    ]
    result = filter_deadlines(deadlines)
    assert len(result) == 1
    assert result[0]["name"] == "D1"


def test_filter_deadlines_by_course():
    deadlines = [
        make_deadline("D1", course="CS101"),
        make_deadline("D2", course="MATH201"),
    ]
    result = filter_deadlines(deadlines, course="CS101")
    assert len(result) == 1
    assert result[0]["name"] == "D1"


def test_filter_deadlines_overdue():
    deadlines = [
        make_deadline("D1", due_offset=-2),
        make_deadline("D2", due_offset=5),
    ]
    result = filter_deadlines(deadlines, overdue=True)
    assert len(result) == 1
    assert result[0]["name"] == "D1"


def test_filter_deadlines_today():
    deadlines = [
        make_deadline("D1", due_offset=0),
        make_deadline("D2", due_offset=3),
    ]
    result = filter_deadlines(deadlines, today=True)
    assert len(result) == 1
    assert result[0]["name"] == "D1"


def test_filter_deadlines_week():
    deadlines = [
        make_deadline("D1", due_offset=3),
        make_deadline("D2", due_offset=10),
        make_deadline("D3", due_offset=-1),
    ]
    result = filter_deadlines(deadlines, week=True)
    # D1 is in 3 days (within 7), D2 is 10 days out, D3 is overdue
    names = [d["name"] for d in result]
    assert "D1" in names
    assert "D2" not in names
    assert "D3" not in names


def test_filter_deadlines_sorted_by_urgency():
    d1 = make_deadline("D1", due_offset=10, priority="low")
    d2 = make_deadline("D2", due_offset=4, priority="high")
    d3 = make_deadline("D3", due_offset=6, priority="medium")
    result = filter_deadlines([d1, d2, d3])
    # D2 has urgency 4/3 ~1.33, D3 has 6/2=3, D1 has 10/1=10
    assert result[0]["name"] == "D2"


def test_priority_weights():
    assert PRIORITY_WEIGHTS["high"] == 3
    assert PRIORITY_WEIGHTS["medium"] == 2
    assert PRIORITY_WEIGHTS["low"] == 1
