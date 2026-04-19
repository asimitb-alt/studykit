"""File management logic for studykit."""

import hashlib
from pathlib import Path
from datetime import datetime

TYPE_MAP = {
    "pdf": {".pdf"},
    "images": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".tif", ".svg", ".webp"},
    "code": {".py", ".js", ".ts", ".java", ".c", ".cpp", ".h", ".cs", ".go", ".rs", ".r", ".m", ".ipynb"},
    "docs": {".doc", ".docx", ".odt", ".txt", ".md", ".rst", ".tex", ".pptx", ".ppt", ".xlsx", ".xls", ".csv"},
    "data": {".json", ".xml", ".yaml", ".yml", ".sql", ".db", ".h5", ".npy", ".npz", ".mat"},
    "archives": {".zip", ".tar", ".gz", ".7z", ".rar", ".bz2"},
    "videos": {".mp4", ".avi", ".mov", ".mkv", ".wmv"},
    "audio": {".mp3", ".wav", ".flac", ".aac", ".ogg"},
}


def classify_file(path):
    """Return the category name for a file or 'other'."""
    suffix = Path(path).suffix.lower()
    for category, extensions in TYPE_MAP.items():
        if suffix in extensions:
            return category
    return "other"


def file_hash(path, chunk=65536):
    """Return SHA-256 hex digest of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        data = f.read(chunk)
        while data:
            h.update(data)
            data = f.read(chunk)
    return h.hexdigest()


def find_duplicates(directory):
    """
    Find duplicate files in directory (recursive).

    Returns dict of hash -> [list of Path] where len > 1.
    """
    directory = Path(directory)
    hash_map = {}

    for filepath in directory.rglob("*"):
        if filepath.is_file():
            try:
                h = file_hash(filepath)
                if h not in hash_map:
                    hash_map[h] = []
                hash_map[h].append(filepath)
            except (OSError, PermissionError):
                pass

    return {h: paths for h, paths in hash_map.items() if len(paths) > 1}


def organize_by_type(directory, dry_run=False):
    """
    Organize files by type into subdirectories.

    Returns list of (src_Path, dst_Path) tuples.
    If dry_run=False, actually moves the files.
    """
    directory = Path(directory)
    moves = []

    for filepath in list(directory.iterdir()):
        if filepath.is_file():
            category = classify_file(filepath)
            dst = directory / category / filepath.name
            moves.append((filepath, dst))

            if not dry_run:
                dst.parent.mkdir(parents=True, exist_ok=True)
                if dst.exists():
                    # Avoid overwriting: add numeric suffix
                    stem = filepath.stem
                    suffix = filepath.suffix
                    counter = 1
                    while dst.exists():
                        dst = directory / category / f"{stem}_{counter}{suffix}"
                        counter += 1
                filepath.rename(dst)

    return moves


def organize_by_date(directory, dry_run=False):
    """
    Organize files into YYYY-MM/ subdirectories based on modification time.

    Returns list of (src_Path, dst_Path) tuples.
    """
    directory = Path(directory)
    moves = []

    for filepath in list(directory.iterdir()):
        if filepath.is_file():
            mtime = filepath.stat().st_mtime
            dt = datetime.fromtimestamp(mtime)
            folder_name = dt.strftime("%Y-%m")
            dst = directory / folder_name / filepath.name
            moves.append((filepath, dst))

            if not dry_run:
                dst.parent.mkdir(parents=True, exist_ok=True)
                if dst.exists():
                    stem = filepath.stem
                    suffix = filepath.suffix
                    counter = 1
                    while dst.exists():
                        dst = directory / folder_name / f"{stem}_{counter}{suffix}"
                        counter += 1
                filepath.rename(dst)

    return moves


def directory_stats(directory):
    """
    Return stats about files in directory (recursive).

    Returns dict: {category: {"count": N, "size": bytes}}
    """
    directory = Path(directory)
    stats = {}

    for filepath in directory.rglob("*"):
        if filepath.is_file():
            category = classify_file(filepath)
            try:
                size = filepath.stat().st_size
            except OSError:
                size = 0

            if category not in stats:
                stats[category] = {"count": 0, "size": 0}
            stats[category]["count"] += 1
            stats[category]["size"] += size

    return stats
