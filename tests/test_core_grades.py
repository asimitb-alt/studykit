"""Tests for studykit.core.grades."""

import pytest
from studykit.core.grades import (
    pct, letter_grade, course_average, compute_gpa, predict_needed,
    LETTER_GRADES, GRADE_POINTS
)


def make_grade(course, score, max_score, weight=1.0, category=""):
    return {
        "id": "abc12345",
        "course": course,
        "assignment": "Test",
        "score": score,
        "max_score": max_score,
        "weight": weight,
        "category": category,
    }


def test_pct_basic():
    assert pct(90, 100) == pytest.approx(90.0)


def test_pct_zero_max():
    assert pct(0, 0) == 0.0


def test_pct_partial():
    assert pct(45, 60) == pytest.approx(75.0)


def test_letter_grade_A():
    assert letter_grade(95) == "A"


def test_letter_grade_B():
    assert letter_grade(85) == "B"


def test_letter_grade_F():
    assert letter_grade(40) == "F"


def test_letter_grade_boundaries():
    assert letter_grade(93) == "A"
    assert letter_grade(90) == "A-"
    assert letter_grade(87) == "B+"
    assert letter_grade(83) == "B"
    assert letter_grade(80) == "B-"


def test_course_average_single():
    grades = [make_grade("CS101", 90, 100, weight=1.0)]
    avg = course_average(grades, "CS101")
    assert avg == pytest.approx(90.0)


def test_course_average_weighted():
    grades = [
        make_grade("CS101", 90, 100, weight=1.0),
        make_grade("CS101", 85, 100, weight=2.0),
    ]
    avg = course_average(grades, "CS101")
    # (90*1 + 85*2) / (1+2) = (90+170)/3 = 260/3 ~ 86.67
    assert avg == pytest.approx(260 / 3)


def test_course_average_no_grades():
    grades = [make_grade("MATH201", 90, 100)]
    avg = course_average(grades, "CS101")
    assert avg is None


def test_course_average_case_insensitive():
    grades = [make_grade("cs101", 80, 100)]
    avg = course_average(grades, "CS101")
    assert avg == pytest.approx(80.0)


def test_compute_gpa_basic():
    grades = [
        make_grade("CS101", 95, 100, weight=1.0),   # A -> 4.0
        make_grade("MATH201", 83, 100, weight=1.0),  # B -> 3.0
    ]
    courses = [
        {"name": "CS101", "credits": 3},
        {"name": "MATH201", "credits": 3},
    ]
    gpa = compute_gpa(grades, courses)
    # Both are 3 credits: (4.0*3 + 3.0*3) / 6 = 3.5
    assert gpa == pytest.approx(3.5)


def test_compute_gpa_no_grades():
    courses = [{"name": "CS101", "credits": 3}]
    assert compute_gpa([], courses) is None


def test_compute_gpa_credit_weighted():
    grades = [
        make_grade("CS101", 95, 100, weight=1.0),   # A -> 4.0
        make_grade("MATH201", 83, 100, weight=1.0),  # B -> 3.0
    ]
    courses = [
        {"name": "CS101", "credits": 4},
        {"name": "MATH201", "credits": 2},
    ]
    gpa = compute_gpa(grades, courses)
    # (4.0*4 + 3.0*2) / 6 = (16+6)/6 = 22/6 ~ 3.667
    assert gpa == pytest.approx(22 / 6)


def test_predict_needed_basic():
    grades = [make_grade("CS101", 80, 100, weight=1.0)]
    # current: 80%, remaining: 1.0 weight, target: 90%
    # needed = (90 * (1+1) - 80*1) / 1 = (180 - 80) / 1 = 100
    needed = predict_needed(grades, "CS101", 90, 1.0)
    assert needed == pytest.approx(100.0)


def test_predict_needed_over_100():
    grades = [make_grade("CS101", 50, 100, weight=1.0)]
    # needed = (90 * 2 - 50) / 1 = 130
    needed = predict_needed(grades, "CS101", 90, 1.0)
    assert needed > 100


def test_predict_needed_already_achieved():
    grades = [make_grade("CS101", 98, 100, weight=1.0)]
    # needed = (90 * 2 - 98) / 1 = 82
    needed = predict_needed(grades, "CS101", 90, 1.0)
    assert needed is not None
    assert needed < 90


def test_predict_needed_zero_remaining():
    grades = [make_grade("CS101", 80, 100, weight=1.0)]
    result = predict_needed(grades, "CS101", 90, 0)
    assert result is None


def test_grade_points_dict():
    assert GRADE_POINTS["A"] == 4.0
    assert GRADE_POINTS["B"] == 3.0
    assert GRADE_POINTS["F"] == 0.0
