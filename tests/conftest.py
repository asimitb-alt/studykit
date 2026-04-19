import pytest
import json
from pathlib import Path
from studykit.store import Store


@pytest.fixture()
def store(tmp_path):
    return Store(path=tmp_path / "data.json")


@pytest.fixture()
def runner():
    from click.testing import CliRunner
    return CliRunner()


@pytest.fixture()
def data_path(tmp_path):
    return str(tmp_path / "data.json")


@pytest.fixture()
def populated_store(tmp_path):
    s = Store(path=tmp_path / "data.json")
    s.add_course("CS101", credits=3, semester="Fall 2025")
    s.add_course("MATH201", credits=4, semester="Fall 2025")
    s.add_deadline("HW1", "CS101", "2099-12-01", "high")
    s.add_deadline("HW2", "MATH201", "2099-12-15", "medium")
    s.add_grade("CS101", "HW1", 90, 100, weight=1.0, category="homework")
    s.add_grade("CS101", "Midterm", 85, 100, weight=2.0, category="exam")
    s.add_grade("MATH201", "Quiz1", 78, 100, weight=1.0, category="quiz")
    s.add_note("Pointers are tricky", "CS101", ["pointers", "memory"])
    s.add_note("Integration by parts", "MATH201", ["calculus"])
    return s
