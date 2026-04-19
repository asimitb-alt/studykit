"""Tests for studykit.core.notes."""

import pytest
from studykit.core.notes import search_notes, filter_notes, export_markdown


def make_note(text, course, tags=None, created="2025-09-01T10:00:00"):
    return {
        "id": "abc12345",
        "text": text,
        "course": course,
        "tags": tags or [],
        "created": created,
    }


SAMPLE_NOTES = [
    make_note("Pointers are tricky", "CS101", ["pointers", "memory"], "2025-09-01T10:00:00"),
    make_note("Integration by parts", "MATH201", ["calculus"], "2025-09-02T10:00:00"),
    make_note("Big O notation", "CS101", ["algorithms", "complexity"], "2025-09-03T10:00:00"),
    make_note("Differential equations", "MATH201", ["calculus", "ODE"], "2025-09-04T10:00:00"),
]


def test_search_notes_by_text():
    results = search_notes(SAMPLE_NOTES, "pointer")
    assert len(results) == 1
    assert results[0]["text"] == "Pointers are tricky"


def test_search_notes_by_course():
    results = search_notes(SAMPLE_NOTES, "MATH201")
    assert len(results) == 2


def test_search_notes_by_tag():
    results = search_notes(SAMPLE_NOTES, "calculus")
    assert len(results) == 2


def test_search_notes_case_insensitive():
    results = search_notes(SAMPLE_NOTES, "POINTER")
    assert len(results) == 1


def test_search_notes_no_match():
    results = search_notes(SAMPLE_NOTES, "quantum physics")
    assert results == []


def test_filter_notes_by_course():
    results = filter_notes(SAMPLE_NOTES, course="CS101")
    assert len(results) == 2
    assert all(n["course"] == "CS101" for n in results)


def test_filter_notes_by_tag():
    results = filter_notes(SAMPLE_NOTES, tag="calculus")
    assert len(results) == 2


def test_filter_notes_sorted_desc():
    results = filter_notes(SAMPLE_NOTES)
    # Should be sorted by created, descending
    assert results[0]["created"] >= results[-1]["created"]


def test_filter_notes_combined():
    results = filter_notes(SAMPLE_NOTES, course="MATH201", tag="ODE")
    assert len(results) == 1
    assert results[0]["text"] == "Differential equations"


def test_export_markdown_all():
    md = export_markdown(SAMPLE_NOTES)
    assert "# All Notes" in md
    assert "CS101" in md
    assert "MATH201" in md
    assert "Pointers are tricky" in md


def test_export_markdown_filtered_course():
    md = export_markdown(SAMPLE_NOTES, course="CS101")
    assert "# Notes: CS101" in md
    assert "Pointers are tricky" in md
    assert "Integration by parts" not in md


def test_export_markdown_has_tags():
    notes = [make_note("Test note", "CS101", ["tag1", "tag2"])]
    md = export_markdown(notes)
    assert "tag1" in md
    assert "tag2" in md
