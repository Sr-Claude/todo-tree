from __future__ import annotations

import re
from pathlib import Path
from typing import List

from todo_tree.models import Task
from todo_tree.utils import DEFAULT_TAGS, get_comment_prefix


def _build_tag_pattern(tags: list[str]) -> re.Pattern:
    escaped_tags = [re.escape(tag) for tag in tags]
    tags_pattern = "|".join(escaped_tags)
    return re.compile(
        rf"\b(?P<tag>{tags_pattern})\b[:\s]*(?P<message>.*?)(?=(\b(?:{tags_pattern})\b|$))",
        re.IGNORECASE,
    )


def extract_tasks_from_line(
    line: str,
    file_path: str,
    line_number: int,
    comment_prefix: str,
    tags: list[str],
    custom_priorities: dict[str, str] | None = None,
) -> list[Task]:
    if not comment_prefix or comment_prefix not in line:
        return []

    start = line.find(comment_prefix)
    if start == -1:
        return []

    comment_text = line[start + len(comment_prefix) :]
    if comment_prefix == "/*" and "*/" in comment_text:
        comment_text = comment_text[: comment_text.index("*/")]
    if comment_prefix == "<!--" and "-->" in comment_text:
        comment_text = comment_text[: comment_text.index("-->")]

    comment_text = comment_text.strip()
    if not comment_text:
        return []

    pattern = _build_tag_pattern(tags)
    tasks: list[Task] = []
    for match in pattern.finditer(comment_text):
        tag = match.group("tag").upper()
        message = match.group("message").strip(" :\t")
        tasks.append(Task(tag, message, file_path, line_number, custom_priorities=custom_priorities))

    return tasks


def parse_file(
    file_path: str,
    tags: list[str] | None = None,
    custom_priorities: dict[str, str] | None = None,
) -> list[Task]:
    tags = tags or DEFAULT_TAGS
    path = Path(file_path)
    extension = path.suffix.lower()
    prefix = get_comment_prefix(extension)
    if not prefix:
        return []

    tasks: list[Task] = []
    try:
        with path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                extracted = extract_tasks_from_line(
                    line,
                    str(file_path),
                    line_number,
                    prefix,
                    tags,
                    custom_priorities=custom_priorities,
                )
                tasks.extend(extracted)
    except (OSError, UnicodeDecodeError):
        return []

    return tasks
