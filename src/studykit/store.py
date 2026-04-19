"""JSON persistence layer for studykit."""

import json
import uuid
from pathlib import Path
from datetime import datetime


class Store:
    """Persistent JSON store for studykit data."""

    DEFAULT_PATH = Path.home() / ".studykit" / "data.json"

    def __init__(self, path=None):
        if path is None:
            self.path = self.DEFAULT_PATH
        else:
            self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._data = self._load()

    def _load(self):
        if self.path.exists():
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                pass
        return {
            "courses": [],
            "deadlines": [],
            "grades": [],
            "notes": [],
        }

    def _save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2, default=str)

    def new_id(self):
        return str(uuid.uuid4())[:8]

    # ------------------------------------------------------------------
    # Courses
    # ------------------------------------------------------------------

    def add_course(self, name, credits=3, semester=""):
        for c in self._data["courses"]:
            if c["name"].lower() == name.lower():
                raise ValueError(f"Course '{name}' already exists.")
        course = {
            "name": name,
            "credits": credits,
            "semester": semester,
        }
        self._data["courses"].append(course)
        self._save()
        return course

    def get_courses(self):
        return list(self._data["courses"])

    def get_course(self, name):
        for c in self._data["courses"]:
            if c["name"].lower() == name.lower():
                return c
        return None

    def remove_course(self, name):
        courses = self._data["courses"]
        new_courses = [c for c in courses if c["name"].lower() != name.lower()]
        if len(new_courses) == len(courses):
            raise ValueError(f"Course '{name}' not found.")
        self._data["courses"] = new_courses
        self._save()

    # ------------------------------------------------------------------
    # Deadlines
    # ------------------------------------------------------------------

    def add_deadline(self, name, course, due, priority="medium"):
        deadline = {
            "id": self.new_id(),
            "name": name,
            "course": course,
            "due": due,
            "priority": priority,
            "done": False,
            "created": datetime.now().isoformat(),
        }
        self._data["deadlines"].append(deadline)
        self._save()
        return deadline

    def get_deadlines(self):
        return list(self._data["deadlines"])

    def _find_deadline(self, id_prefix):
        matches = [d for d in self._data["deadlines"] if d["id"].startswith(id_prefix)]
        if not matches:
            raise ValueError(f"No deadline found with id prefix '{id_prefix}'.")
        if len(matches) > 1:
            raise ValueError(f"Ambiguous id prefix '{id_prefix}' matches multiple deadlines.")
        return matches[0]

    def mark_done(self, id_prefix):
        d = self._find_deadline(id_prefix)
        d["done"] = True
        self._save()
        return d

    def delete_deadline(self, id_prefix):
        d = self._find_deadline(id_prefix)
        self._data["deadlines"] = [x for x in self._data["deadlines"] if x["id"] != d["id"]]
        self._save()
        return d

    # ------------------------------------------------------------------
    # Grades
    # ------------------------------------------------------------------

    def add_grade(self, course, assignment, score, max_score, weight=1.0, category=""):
        grade = {
            "id": self.new_id(),
            "course": course,
            "assignment": assignment,
            "score": score,
            "max_score": max_score,
            "weight": weight,
            "category": category,
            "created": datetime.now().isoformat(),
        }
        self._data["grades"].append(grade)
        self._save()
        return grade

    def get_grades(self):
        return list(self._data["grades"])

    # ------------------------------------------------------------------
    # Notes
    # ------------------------------------------------------------------

    def add_note(self, text, course, tags=None):
        note = {
            "id": self.new_id(),
            "text": text,
            "course": course,
            "tags": tags or [],
            "created": datetime.now().isoformat(),
        }
        self._data["notes"].append(note)
        self._save()
        return note

    def get_notes(self):
        return list(self._data["notes"])

    def delete_note(self, id_prefix):
        matches = [n for n in self._data["notes"] if n["id"].startswith(id_prefix)]
        if not matches:
            raise ValueError(f"No note found with id prefix '{id_prefix}'.")
        if len(matches) > 1:
            raise ValueError(f"Ambiguous id prefix '{id_prefix}' matches multiple notes.")
        note = matches[0]
        self._data["notes"] = [n for n in self._data["notes"] if n["id"] != note["id"]]
        self._save()
        return note
