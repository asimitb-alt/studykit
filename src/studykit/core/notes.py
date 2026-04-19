"""Notes logic for studykit."""


def search_notes(notes, query):
    """Search notes for query string (case-insensitive) in text, course, or tags."""
    query_lower = query.lower()
    result = []
    for note in notes:
        if query_lower in note["text"].lower():
            result.append(note)
        elif query_lower in note["course"].lower():
            result.append(note)
        elif any(query_lower in tag.lower() for tag in note.get("tags", [])):
            result.append(note)
    return result


def filter_notes(notes, course=None, tag=None):
    """Filter notes by course and/or tag, sorted by created date descending."""
    result = list(notes)

    if course:
        result = [n for n in result if n["course"].lower() == course.lower()]

    if tag:
        result = [n for n in result if any(tag.lower() == t.lower() for t in n.get("tags", []))]

    result.sort(key=lambda n: n.get("created", ""), reverse=True)
    return result


def export_markdown(notes, course=None):
    """Export notes as a Markdown string, optionally filtered by course."""
    if course:
        filtered = [n for n in notes if n["course"].lower() == course.lower()]
        title = f"# Notes: {course}"
    else:
        filtered = list(notes)
        title = "# All Notes"

    filtered.sort(key=lambda n: n.get("created", ""))

    lines = [title, ""]
    for note in filtered:
        lines.append(f"## [{note['course']}] {note.get('created', '')[:10]}")
        lines.append("")
        lines.append(note["text"])
        tags = note.get("tags", [])
        if tags:
            lines.append("")
            lines.append(f"*Tags: {', '.join(tags)}*")
        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)
