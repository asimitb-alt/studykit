"""Tests for studykit.core.files."""

import pytest
from pathlib import Path
from studykit.core.files import (
    classify_file, file_hash, find_duplicates,
    organize_by_type, organize_by_date, directory_stats, TYPE_MAP
)


def test_classify_pdf():
    assert classify_file("report.pdf") == "pdf"


def test_classify_image():
    assert classify_file("photo.jpg") == "images"
    assert classify_file("icon.png") == "images"


def test_classify_code():
    assert classify_file("script.py") == "code"
    assert classify_file("Main.java") == "code"
    assert classify_file("notebook.ipynb") == "code"


def test_classify_docs():
    assert classify_file("essay.docx") == "docs"
    assert classify_file("readme.md") == "docs"
    assert classify_file("slides.pptx") == "docs"


def test_classify_data():
    assert classify_file("config.json") == "data"
    assert classify_file("data.csv") == "docs"  # csv is in docs


def test_classify_other():
    assert classify_file("something.xyz") == "other"
    assert classify_file("noextension") == "other"


def test_classify_case_insensitive():
    assert classify_file("PHOTO.JPG") == "images"
    assert classify_file("SCRIPT.PY") == "code"


def test_file_hash(tmp_path):
    f = tmp_path / "test.txt"
    f.write_text("hello world")
    h = file_hash(f)
    assert isinstance(h, str)
    assert len(h) == 64  # SHA-256 hex digest


def test_file_hash_same_content(tmp_path):
    f1 = tmp_path / "a.txt"
    f2 = tmp_path / "b.txt"
    f1.write_text("same content")
    f2.write_text("same content")
    assert file_hash(f1) == file_hash(f2)


def test_file_hash_different_content(tmp_path):
    f1 = tmp_path / "a.txt"
    f2 = tmp_path / "b.txt"
    f1.write_text("content a")
    f2.write_text("content b")
    assert file_hash(f1) != file_hash(f2)


def test_find_duplicates_found(tmp_path):
    f1 = tmp_path / "a.txt"
    f2 = tmp_path / "b.txt"
    f1.write_text("duplicate content")
    f2.write_text("duplicate content")
    dupes = find_duplicates(tmp_path)
    assert len(dupes) == 1
    # Each group should have 2 paths
    group = list(dupes.values())[0]
    assert len(group) == 2


def test_find_duplicates_none(tmp_path):
    (tmp_path / "a.txt").write_text("unique content a")
    (tmp_path / "b.txt").write_text("unique content b")
    dupes = find_duplicates(tmp_path)
    assert dupes == {}


def test_organize_by_type_dry_run(tmp_path):
    (tmp_path / "doc.pdf").write_bytes(b"pdf content")
    (tmp_path / "script.py").write_text("print('hello')")
    moves = organize_by_type(tmp_path, dry_run=True)
    assert len(moves) == 2
    # Files should not have moved
    assert (tmp_path / "doc.pdf").exists()
    assert (tmp_path / "script.py").exists()


def test_organize_by_type_actual(tmp_path):
    (tmp_path / "doc.pdf").write_bytes(b"pdf content")
    moves = organize_by_type(tmp_path, dry_run=False)
    assert len(moves) == 1
    src, dst = moves[0]
    assert dst.exists()
    assert dst.parent.name == "pdf"


def test_organize_by_date_dry_run(tmp_path):
    (tmp_path / "file.txt").write_text("content")
    moves = organize_by_date(tmp_path, dry_run=True)
    assert len(moves) == 1
    # File should still be in place
    assert (tmp_path / "file.txt").exists()


def test_organize_by_date_actual(tmp_path):
    (tmp_path / "file.txt").write_text("content")
    moves = organize_by_date(tmp_path, dry_run=False)
    assert len(moves) == 1
    src, dst = moves[0]
    assert dst.exists()
    # Destination folder should be YYYY-MM format
    import re
    assert re.match(r"\d{4}-\d{2}", dst.parent.name)


def test_directory_stats(tmp_path):
    (tmp_path / "a.pdf").write_bytes(b"pdf")
    (tmp_path / "b.py").write_text("code")
    (tmp_path / "c.py").write_text("more code")
    stats = directory_stats(tmp_path)
    assert "pdf" in stats
    assert "code" in stats
    assert stats["code"]["count"] == 2
    assert stats["pdf"]["count"] == 1


def test_directory_stats_empty(tmp_path):
    stats = directory_stats(tmp_path)
    assert stats == {}
