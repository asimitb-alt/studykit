"""CLI tests for grade commands."""

import pytest
from studykit.cli import main


def _add_course(runner, data_path, name="CS101"):
    runner.invoke(main, ["--data", data_path, "course", "add", name])


# ---------------------------------------------------------------------------
# grade add
# ---------------------------------------------------------------------------

def test_grade_add(runner, data_path):
    _add_course(runner, data_path)
    result = runner.invoke(main, [
        "--data", data_path, "grade", "add", "CS101", "HW1", "90", "100",
        "--weight", "1.0", "--category", "homework"
    ])
    assert result.exit_code == 0
    assert "Added grade" in result.output
    assert "HW1" in result.output


def test_grade_add_shows_letter(runner, data_path):
    _add_course(runner, data_path)
    result = runner.invoke(main, [
        "--data", data_path, "grade", "add", "CS101", "Midterm", "95", "100"
    ])
    assert result.exit_code == 0
    assert "A" in result.output


def test_grade_add_unknown_course(runner, data_path):
    result = runner.invoke(main, [
        "--data", data_path, "grade", "add", "UNKNOWN999", "HW1", "90", "100"
    ])
    assert result.exit_code == 1


def test_grade_add_duplicate(runner, data_path):
    _add_course(runner, data_path)
    runner.invoke(main, ["--data", data_path, "grade", "add", "CS101", "Midterm", "85", "100"])
    result = runner.invoke(main, ["--data", data_path, "grade", "add", "CS101", "Midterm", "90", "100"])
    assert result.exit_code == 1


def test_grade_same_assignment_different_course_allowed(runner, data_path):
    _add_course(runner, data_path, "CS101")
    _add_course(runner, data_path, "MATH201")
    runner.invoke(main, ["--data", data_path, "grade", "add", "CS101", "Midterm", "85", "100"])
    result = runner.invoke(main, ["--data", data_path, "grade", "add", "MATH201", "Midterm", "78", "100"])
    assert result.exit_code == 0


def test_grade_add_score_exceeds_max(runner, data_path):
    _add_course(runner, data_path)
    result = runner.invoke(main, [
        "--data", data_path, "grade", "add", "CS101", "HW1", "110", "100"
    ])
    assert result.exit_code != 0


def test_grade_predict_target_over_100(runner, data_path):
    _add_course(runner, data_path)
    runner.invoke(main, ["--data", data_path, "grade", "add", "CS101", "HW1", "80", "100"])
    result = runner.invoke(main, [
        "--data", data_path, "grade", "predict", "CS101",
        "--target", "150", "--remaining", "1.0"
    ])
    assert result.exit_code != 0


def test_grade_add_invalid_max(runner, data_path):
    _add_course(runner, data_path)
    result = runner.invoke(main, [
        "--data", data_path, "grade", "add", "CS101", "HW1", "90", "0"
    ])
    assert result.exit_code != 0


# ---------------------------------------------------------------------------
# grade summary
# ---------------------------------------------------------------------------

def test_grade_summary_empty(runner, data_path):
    result = runner.invoke(main, ["--data", data_path, "grade", "summary"])
    assert result.exit_code == 0
    assert "No grades" in result.output


def test_grade_summary_with_grades(runner, data_path):
    _add_course(runner, data_path)
    runner.invoke(main, ["--data", data_path, "grade", "add", "CS101", "HW1", "90", "100"])
    runner.invoke(main, ["--data", data_path, "grade", "add", "CS101", "Midterm", "85", "100"])
    result = runner.invoke(main, ["--data", data_path, "grade", "summary"])
    assert result.exit_code == 0
    assert "CS101" in result.output


def test_grade_summary_filter_course(runner, data_path):
    _add_course(runner, data_path, "CS101")
    _add_course(runner, data_path, "MATH201")
    runner.invoke(main, ["--data", data_path, "grade", "add", "CS101", "HW1", "90", "100"])
    runner.invoke(main, ["--data", data_path, "grade", "add", "MATH201", "Quiz", "80", "100"])
    result = runner.invoke(main, ["--data", data_path, "grade", "summary", "--course", "CS101"])
    assert result.exit_code == 0
    assert "CS101" in result.output


# ---------------------------------------------------------------------------
# grade gpa
# ---------------------------------------------------------------------------

def test_grade_gpa_no_grades(runner, data_path):
    result = runner.invoke(main, ["--data", data_path, "grade", "gpa"])
    assert result.exit_code == 0
    assert "No grades" in result.output


def test_grade_gpa_with_grades(runner, data_path):
    _add_course(runner, data_path)
    runner.invoke(main, ["--data", data_path, "grade", "add", "CS101", "HW1", "95", "100"])
    result = runner.invoke(main, ["--data", data_path, "grade", "gpa"])
    assert result.exit_code == 0
    assert "GPA" in result.output


# ---------------------------------------------------------------------------
# grade predict
# ---------------------------------------------------------------------------

def test_grade_predict(runner, data_path):
    _add_course(runner, data_path)
    runner.invoke(main, ["--data", data_path, "grade", "add", "CS101", "HW1", "80", "100"])
    result = runner.invoke(main, [
        "--data", data_path, "grade", "predict", "CS101",
        "--target", "90", "--remaining", "1.0"
    ])
    assert result.exit_code == 0
    assert "needed" in result.output.lower() or "Score needed" in result.output


def test_grade_predict_warns_over_100(runner, data_path):
    _add_course(runner, data_path)
    runner.invoke(main, ["--data", data_path, "grade", "add", "CS101", "HW1", "50", "100"])
    result = runner.invoke(main, [
        "--data", data_path, "grade", "predict", "CS101",
        "--target", "95", "--remaining", "1.0"
    ])
    assert result.exit_code == 0
    assert "Warning" in result.output or "exceed" in result.output.lower()


def test_grade_predict_zero_remaining(runner, data_path):
    result = runner.invoke(main, [
        "--data", data_path, "grade", "predict", "CS101",
        "--target", "90", "--remaining", "0"
    ])
    assert result.exit_code != 0
