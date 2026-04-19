"""CLI tests for note commands."""

import pytest
from studykit.cli import main
from studykit.store import Store


def test_note_add(runner, data_path):
    result = runner.invoke(main, [
        "--data", data_path, "note", "add", "Lambda functions",
        "--course", "CS101", "--tags", "python,functional"
    ])
    assert result.exit_code == 0
    assert "Added note" in result.output


def test_note_list_empty(runner, data_path):
    result = runner.invoke(main, ["--data", data_path, "note", "list"])
    assert result.exit_code == 0
    assert "No notes" in result.output


def test_note_list_shows_entries(runner, data_path):
    runner.invoke(main, [
        "--data", data_path, "note", "add", "Lambda functions",
        "--course", "CS101"
    ])
    result = runner.invoke(main, ["--data", data_path, "note", "list"])
    assert result.exit_code == 0
    assert "CS101" in result.output
    assert "Lambda" in result.output


def test_note_list_filter_course(runner, data_path):
    runner.invoke(main, ["--data", data_path, "note", "add", "CS note", "--course", "CS101"])
    runner.invoke(main, ["--data", data_path, "note", "add", "Math note", "--course", "MATH201"])
    result = runner.invoke(main, ["--data", data_path, "note", "list", "--course", "CS101"])
    assert result.exit_code == 0
    assert "CS101" in result.output
    assert "Math note" not in result.output


def test_note_list_filter_tag(runner, data_path):
    runner.invoke(main, ["--data", data_path, "note", "add", "Tagged note", "--course", "CS101", "--tags", "important"])
    runner.invoke(main, ["--data", data_path, "note", "add", "Untagged note", "--course", "CS101"])
    result = runner.invoke(main, ["--data", data_path, "note", "list", "--tag", "important"])
    assert result.exit_code == 0
    assert "Tagged note" in result.output
    assert "Untagged note" not in result.output


def test_note_search(runner, data_path):
    runner.invoke(main, ["--data", data_path, "note", "add", "Pointers are tricky", "--course", "CS101"])
    runner.invoke(main, ["--data", data_path, "note", "add", "Integration by parts", "--course", "MATH201"])
    result = runner.invoke(main, ["--data", data_path, "note", "search", "pointer"])
    assert result.exit_code == 0
    assert "Pointers" in result.output
    assert "Integration" not in result.output


def test_note_search_no_match(runner, data_path):
    result = runner.invoke(main, ["--data", data_path, "note", "search", "quantum"])
    assert result.exit_code == 0
    assert "No notes" in result.output


def test_note_delete(runner, data_path):
    runner.invoke(main, ["--data", data_path, "note", "add", "Some note", "--course", "CS101"])
    store = Store(path=data_path)
    notes = store.get_notes()
    id_prefix = notes[0]["id"][:4]

    result = runner.invoke(main, ["--data", data_path, "note", "delete", id_prefix])
    assert result.exit_code == 0
    assert "Deleted" in result.output


def test_note_export_stdout(runner, data_path):
    runner.invoke(main, ["--data", data_path, "note", "add", "Test note", "--course", "CS101"])
    result = runner.invoke(main, ["--data", data_path, "note", "export"])
    assert result.exit_code == 0
    assert "# All Notes" in result.output
    assert "Test note" in result.output


def test_note_export_to_file(runner, data_path, tmp_path):
    runner.invoke(main, ["--data", data_path, "note", "add", "Test note", "--course", "CS101"])
    out_file = str(tmp_path / "notes.md")
    result = runner.invoke(main, ["--data", data_path, "note", "export", "--out", out_file])
    assert result.exit_code == 0
    from pathlib import Path
    content = Path(out_file).read_text()
    assert "Test note" in content
