"""CLI tests for deadline commands."""

import pytest
from studykit.cli import main
from studykit.store import Store


def test_deadline_add(runner, data_path):
    result = runner.invoke(main, [
        "--data", data_path, "deadline", "add", "HW1",
        "--course", "CS101", "--due", "2099-12-01", "--priority", "high"
    ])
    assert result.exit_code == 0
    assert "Added deadline" in result.output
    assert "HW1" in result.output


def test_deadline_add_invalid_date(runner, data_path):
    result = runner.invoke(main, [
        "--data", data_path, "deadline", "add", "HW1",
        "--course", "CS101", "--due", "not-a-date"
    ])
    assert result.exit_code == 1


def test_deadline_list_empty(runner, data_path):
    result = runner.invoke(main, ["--data", data_path, "deadline", "list"])
    assert result.exit_code == 0
    assert "No deadlines" in result.output


def test_deadline_list_shows_entries(runner, data_path):
    runner.invoke(main, [
        "--data", data_path, "deadline", "add", "HW1",
        "--course", "CS101", "--due", "2099-12-01"
    ])
    result = runner.invoke(main, ["--data", data_path, "deadline", "list"])
    assert result.exit_code == 0
    assert "HW1" in result.output


def test_deadline_list_filter_course(runner, data_path):
    runner.invoke(main, ["--data", data_path, "deadline", "add", "HW1", "--course", "CS101", "--due", "2099-12-01"])
    runner.invoke(main, ["--data", data_path, "deadline", "add", "HW2", "--course", "MATH201", "--due", "2099-12-05"])
    result = runner.invoke(main, ["--data", data_path, "deadline", "list", "--course", "CS101"])
    assert result.exit_code == 0
    assert "HW1" in result.output
    assert "HW2" not in result.output


def test_deadline_done(runner, data_path):
    add_result = runner.invoke(main, [
        "--data", data_path, "deadline", "add", "HW1",
        "--course", "CS101", "--due", "2099-12-01"
    ])
    # Extract ID from output
    store = Store(path=data_path)
    deadlines = store.get_deadlines()
    id_prefix = deadlines[0]["id"][:4]

    result = runner.invoke(main, ["--data", data_path, "deadline", "done", id_prefix])
    assert result.exit_code == 0
    assert "Marked done" in result.output


def test_deadline_done_invalid_id(runner, data_path):
    result = runner.invoke(main, ["--data", data_path, "deadline", "done", "zzzzzzzz"])
    assert result.exit_code == 1


def test_deadline_delete(runner, data_path):
    runner.invoke(main, [
        "--data", data_path, "deadline", "add", "HW1",
        "--course", "CS101", "--due", "2099-12-01"
    ])
    store = Store(path=data_path)
    deadlines = store.get_deadlines()
    id_prefix = deadlines[0]["id"][:4]

    result = runner.invoke(main, ["--data", data_path, "deadline", "delete", id_prefix])
    assert result.exit_code == 0
    assert "Deleted" in result.output


def test_deadline_delete_invalid_id(runner, data_path):
    result = runner.invoke(main, ["--data", data_path, "deadline", "delete", "zzzzzzzz"])
    assert result.exit_code == 1


def test_deadline_list_overdue(runner, data_path):
    runner.invoke(main, [
        "--data", data_path, "deadline", "add", "OldHW",
        "--course", "CS101", "--due", "2020-01-01"
    ])
    runner.invoke(main, [
        "--data", data_path, "deadline", "add", "FutureHW",
        "--course", "CS101", "--due", "2099-12-01"
    ])
    result = runner.invoke(main, ["--data", data_path, "deadline", "list", "--overdue"])
    assert result.exit_code == 0
    assert "OldHW" in result.output
    assert "FutureHW" not in result.output


def test_deadline_list_week(runner, data_path):
    from datetime import date, timedelta
    soon = (date.today() + timedelta(days=3)).isoformat()
    runner.invoke(main, [
        "--data", data_path, "deadline", "add", "SoonHW",
        "--course", "CS101", "--due", soon
    ])
    runner.invoke(main, [
        "--data", data_path, "deadline", "add", "FarHW",
        "--course", "CS101", "--due", "2099-12-01"
    ])
    result = runner.invoke(main, ["--data", data_path, "deadline", "list", "--week"])
    assert result.exit_code == 0
    assert "SoonHW" in result.output
    assert "FarHW" not in result.output
