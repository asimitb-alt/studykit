"""CLI tests for files commands."""

import pytest
from pathlib import Path
from studykit.cli import main


def test_files_organize_dry_run(runner, data_path, tmp_path):
    (tmp_path / "doc.pdf").write_bytes(b"pdf content")
    (tmp_path / "script.py").write_text("print('hello')")
    result = runner.invoke(main, [
        "--data", data_path, "files", "organize", str(tmp_path),
        "--by", "type", "--dry-run"
    ])
    assert result.exit_code == 0
    assert "DRY RUN" in result.output or "dry" in result.output.lower()
    # Files should still be in place
    assert (tmp_path / "doc.pdf").exists()
    assert (tmp_path / "script.py").exists()


def test_files_organize_type(runner, data_path, tmp_path):
    (tmp_path / "doc.pdf").write_bytes(b"pdf content")
    result = runner.invoke(main, [
        "--data", data_path, "files", "organize", str(tmp_path), "--by", "type"
    ])
    assert result.exit_code == 0
    assert "Moved" in result.output
    # File should now be in pdf/ subdirectory
    assert (tmp_path / "pdf" / "doc.pdf").exists()


def test_files_organize_date(runner, data_path, tmp_path):
    (tmp_path / "file.txt").write_text("some content")
    result = runner.invoke(main, [
        "--data", data_path, "files", "organize", str(tmp_path), "--by", "date"
    ])
    assert result.exit_code == 0
    assert "Moved" in result.output


def test_files_organize_empty_dir(runner, data_path, tmp_path):
    result = runner.invoke(main, [
        "--data", data_path, "files", "organize", str(tmp_path)
    ])
    assert result.exit_code == 0
    assert "No files" in result.output


def test_files_organize_invalid_dir(runner, data_path):
    result = runner.invoke(main, [
        "--data", data_path, "files", "organize", "/nonexistent/path/xyz"
    ])
    assert result.exit_code == 1


def test_files_dupes_no_dupes(runner, data_path, tmp_path):
    (tmp_path / "a.txt").write_text("unique content a")
    (tmp_path / "b.txt").write_text("unique content b")
    result = runner.invoke(main, ["--data", data_path, "files", "dupes", str(tmp_path)])
    assert result.exit_code == 0
    assert "No duplicate" in result.output


def test_files_dupes_found(runner, data_path, tmp_path):
    (tmp_path / "a.txt").write_text("duplicate content")
    (tmp_path / "b.txt").write_text("duplicate content")
    result = runner.invoke(main, ["--data", data_path, "files", "dupes", str(tmp_path)])
    assert result.exit_code == 0
    assert "Group" in result.output or "duplicate" in result.output.lower()


def test_files_stats(runner, data_path, tmp_path):
    (tmp_path / "a.pdf").write_bytes(b"pdf")
    (tmp_path / "b.py").write_text("code")
    (tmp_path / "c.jpg").write_bytes(b"image")
    result = runner.invoke(main, ["--data", data_path, "files", "stats", str(tmp_path)])
    assert result.exit_code == 0
    assert "pdf" in result.output
    assert "code" in result.output
    assert "images" in result.output


def test_files_stats_empty_dir(runner, data_path, tmp_path):
    result = runner.invoke(main, ["--data", data_path, "files", "stats", str(tmp_path)])
    assert result.exit_code == 0
    assert "No files" in result.output


def test_dashboard_empty(runner, data_path):
    result = runner.invoke(main, ["--data", data_path, "dashboard"])
    assert result.exit_code == 0
    assert "Dashboard" in result.output or "dashboard" in result.output.lower()
