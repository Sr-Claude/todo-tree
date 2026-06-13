from __future__ import annotations

from pathlib import Path
from typing import List

from todo_tree.models import ScanResult
from todo_tree.parser import parse_file
from todo_tree.utils import DEFAULT_EXTENSIONS, DEFAULT_IGNORE_DIRS, is_text_file


def scan_directory(
    path: str = ".",
    tags: list[str] | None = None,
    extensions: list[str] | None = None,
    ignore_dirs: list[str] | None = None,
    recursive: bool = True,
    custom_priorities: dict[str, str] | None = None,
) -> ScanResult:
    root = Path(path).resolve()
    tags = tags or []
    extensions = [f".{ext.lower().lstrip('.')}" for ext in (extensions or DEFAULT_EXTENSIONS)]
    ignore_dirs = set(ignore_dirs or DEFAULT_IGNORE_DIRS)
    tasks = []
    scanned_files = 0

    if recursive:
        walker = root.rglob("*")
    else:
        walker = root.iterdir()

    for item in walker:
        if item.is_dir():
            if item.name in ignore_dirs:
                continue
            continue

        if item.suffix.lower() not in extensions:
            continue

        if any(parent.name in ignore_dirs for parent in item.parents):
            continue

        if not is_text_file(str(item)):
            continue

        scanned_files += 1
        file_tasks = parse_file(
            str(item),
            tags=tags,
            custom_priorities=custom_priorities,
        )
        if file_tasks:
            relative_path = str(item.relative_to(root))
            for task in file_tasks:
                task.file_path = relative_path
            tasks.extend(file_tasks)

    result = ScanResult(
        tasks=tasks,
        files_scanned=scanned_files,
        extensions_checked=extensions,
        timestamp="",
    )
    return result
