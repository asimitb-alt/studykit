"""CLI tests for course commands."""

import pytest
from studykit.cli import main


def test_course_add(runner, data_path):
    result = runner.invoke(main, ["--data", data_path, "course", "add", "CS101", "--credits", "3", "--semester", "Fall 2025"])
    assert result.exit_code == 0
    assert "Added course" in result.output
    assert "CS101" in result.output


def test_course_add_duplicate(runner, data_path):
    runner.invoke(main, ["--data", data_path, "course", "add", "CS101"])
    result = runner.invoke(main, ["--data", data_path, "course", "add", "CS101"])
    assert result.exit_code == 1


def test_course_list_empty(runner, data_path):
    result = runner.invoke(main, ["--data", data_path, "course", "list"])
    assert result.exit_code == 0
    assert "No courses" in result.output


def test_course_list_with_courses(runner, data_path):
    runner.invoke(main, ["--data", data_path, "course", "add", "CS101", "--credits", "3"])
    runner.invoke(main, ["--data", data_path, "course", "add", "MATH201", "--credits", "4"])
    result = runner.invoke(main, ["--data", data_path, "course", "list"])
    assert result.exit_code == 0
    assert "CS101" in result.output
    assert "MATH201" in result.output


def test_course_remove(runner, data_path):
    runner.invoke(main, ["--data", data_path, "course", "add", "CS101"])
    result = runner.invoke(main, ["--data", data_path, "course", "remove", "CS101"])
    assert result.exit_code == 0
    assert "Removed" in result.output


def test_course_remove_nonexistent(runner, data_path):
    result = runner.invoke(main, ["--data", data_path, "course", "remove", "NONEXISTENT"])
    assert result.exit_code == 1


def test_course_summary(runner, data_path):
    runner.invoke(main, ["--data", data_path, "course", "add", "CS101", "--credits", "3"])
    runner.invoke(main, ["--data", data_path, "grade", "add", "CS101", "HW1", "90", "100"])
    result = runner.invoke(main, ["--data", data_path, "course", "summary", "CS101"])
    assert result.exit_code == 0
    assert "CS101" in result.output


def test_course_summary_nonexistent(runner, data_path):
    result = runner.invoke(main, ["--data", data_path, "course", "summary", "NONEXISTENT"])
    assert result.exit_code == 1
