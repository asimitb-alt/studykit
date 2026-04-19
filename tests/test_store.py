"""Tests for studykit.store."""

import pytest
from studykit.store import Store


def test_store_creates_empty(store):
    assert store.get_courses() == []
    assert store.get_deadlines() == []
    assert store.get_grades() == []
    assert store.get_notes() == []


def test_add_course(store):
    c = store.add_course("CS101", credits=3, semester="Fall 2025")
    assert c["name"] == "CS101"
    assert c["credits"] == 3
    assert c["semester"] == "Fall 2025"


def test_get_courses(store):
    store.add_course("CS101")
    store.add_course("MATH201")
    courses = store.get_courses()
    assert len(courses) == 2
    names = [c["name"] for c in courses]
    assert "CS101" in names
    assert "MATH201" in names


def test_duplicate_course_raises(store):
    store.add_course("CS101")
    with pytest.raises(ValueError, match="already exists"):
        store.add_course("CS101")


def test_get_course(store):
    store.add_course("CS101", credits=4, semester="Spring 2026")
    c = store.get_course("CS101")
    assert c is not None
    assert c["credits"] == 4


def test_get_course_missing(store):
    assert store.get_course("UNKNOWN") is None


def test_remove_course(store):
    store.add_course("CS101")
    store.remove_course("CS101")
    assert store.get_course("CS101") is None


def test_remove_course_missing_raises(store):
    with pytest.raises(ValueError, match="not found"):
        store.remove_course("NONEXISTENT")


def test_add_deadline(store):
    d = store.add_deadline("HW1", "CS101", "2099-12-01", "high")
    assert d["name"] == "HW1"
    assert d["course"] == "CS101"
    assert d["due"] == "2099-12-01"
    assert d["priority"] == "high"
    assert d["done"] is False
    assert "id" in d


def test_mark_done(store):
    d = store.add_deadline("HW1", "CS101", "2099-12-01", "high")
    id_prefix = d["id"][:4]
    updated = store.mark_done(id_prefix)
    assert updated["done"] is True


def test_delete_deadline(store):
    d = store.add_deadline("HW1", "CS101", "2099-12-01", "high")
    store.delete_deadline(d["id"][:4])
    assert store.get_deadlines() == []


def test_add_grade(store):
    g = store.add_grade("CS101", "Midterm", 85, 100, weight=2.0, category="exam")
    assert g["course"] == "CS101"
    assert g["assignment"] == "Midterm"
    assert g["score"] == 85
    assert g["max_score"] == 100
    assert g["weight"] == 2.0
    assert g["category"] == "exam"


def test_get_grades(store):
    store.add_grade("CS101", "HW1", 90, 100)
    store.add_grade("MATH201", "Quiz", 70, 100)
    grades = store.get_grades()
    assert len(grades) == 2


def test_add_note(store):
    n = store.add_note("Lambda functions in Python", "CS101", ["lambda", "functional"])
    assert n["text"] == "Lambda functions in Python"
    assert n["course"] == "CS101"
    assert "lambda" in n["tags"]
    assert "id" in n


def test_delete_note(store):
    n = store.add_note("Some note", "CS101", [])
    store.delete_note(n["id"][:4])
    assert store.get_notes() == []


def test_new_id_length(store):
    id1 = store.new_id()
    id2 = store.new_id()
    assert len(id1) == 8
    assert len(id2) == 8
    assert id1 != id2


def test_store_persistence(tmp_path):
    path = tmp_path / "data.json"
    s1 = Store(path=path)
    s1.add_course("CS101", credits=3, semester="Fall 2025")
    s2 = Store(path=path)
    courses = s2.get_courses()
    assert len(courses) == 1
    assert courses[0]["name"] == "CS101"


def test_mark_done_invalid_prefix(store):
    with pytest.raises(ValueError):
        store.mark_done("zzzzzzzz")


def test_delete_note_invalid_prefix(store):
    with pytest.raises(ValueError):
        store.delete_note("zzzzzzzz")
