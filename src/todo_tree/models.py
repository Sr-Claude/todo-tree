from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List

DEFAULT_PRIORITY_MAP = {
    "FIXME": "Crítica",
    "HACK": "Alta",
    "TODO": "Media",
    "NOTE": "Baja",
}

DEFAULT_PRIORITY_WEIGHT = {
    "FIXME": 1,
    "HACK": 2,
    "TODO": 3,
    "NOTE": 4,
}

PRIORITY_NAME_MAP = {
    "critica": ("Crítica", 1),
    "alta": ("Alta", 2),
    "media": ("Media", 3),
    "baja": ("Baja", 4),
}


def resolve_priority(tag: str, custom_priorities: dict[str, str] | None = None) -> str:
    tag_upper = tag.upper()
    if custom_priorities and tag_upper in custom_priorities:
        value = custom_priorities[tag_upper].strip().lower()
        return PRIORITY_NAME_MAP.get(value, ("Media", 3))[0]
    return DEFAULT_PRIORITY_MAP.get(tag_upper, "Media")


def resolve_priority_weight(tag: str, custom_priorities: dict[str, str] | None = None) -> int:
    tag_upper = tag.upper()
    if custom_priorities and tag_upper in custom_priorities:
        value = custom_priorities[tag_upper].strip().lower()
        return PRIORITY_NAME_MAP.get(value, ("Media", 3))[1]
    return DEFAULT_PRIORITY_WEIGHT.get(tag_upper, 3)


@dataclass
class Task:
    tag: str
    message: str
    file_path: str
    line_number: int
    custom_priorities: dict[str, str] | None = field(default=None, repr=False, compare=False)
    priority: str = field(init=False)
    weight: int = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self.tag = self.tag.upper()
        self.priority = resolve_priority(self.tag, self.custom_priorities)
        self.weight = resolve_priority_weight(self.tag, self.custom_priorities)

    def __str__(self) -> str:
        return f"[{self.tag}] {self.message} ({self.file_path}:{self.line_number})"


@dataclass
class ScanResult:
    tasks: List[Task]
    files_scanned: int
    extensions_checked: List[str]
    timestamp: str

    def summary(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for task in self.tasks:
            counts[task.tag] = counts.get(task.tag, 0) + 1
        counts["total"] = len(self.tasks)
        return counts

    def files_with_most_tasks(self) -> List[tuple[str, int]]:
        from collections import Counter

        counter = Counter(task.file_path for task in self.tasks)
        return counter.most_common()
