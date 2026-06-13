from __future__ import annotations

import random
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from jinja2 import Environment, FileSystemLoader, select_autoescape

from todo_tree.models import ScanResult, Task

EMOJI_BY_TAG: Dict[str, str] = {
    "FIXME": "🔴",
    "HACK": "🟠",
    "TODO": "🟡",
    "NOTE": "🔵",
}

TAG_LABELS: Dict[str, str] = {
    "FIXME": "FIXME",
    "HACK": "HACK",
    "TODO": "TODO",
    "NOTE": "NOTE",
}

COLORS: Dict[str, str] = {
    "FIXME": "#e74c3c",
    "HACK": "#e67e22",
    "TODO": "#f1c40f",
    "NOTE": "#3498db",
}

PRIORITY_ORDER = ["FIXME", "HACK", "TODO", "NOTE"]

MOTIVATIONAL_QUOTES = [
    "☕️ Un café, un TODO menos. Sigue así.",
    "🐓 Depurando bugs desde el amanecer.",
    "🌅 Cada FIXME resuelto es un amanecer más tranquilo.",
    "💪 Las notas (NOTE) son el mapa del tesoro. Los FIXME, los dragones.",
    "🧹 Código limpio, mente limpia, café lleno.",
    "📋 Tu árbol de tareas está listo. Ahora, ¡a picar código!",
]


def _group_tasks_by_tag(tasks: List[Task]) -> Dict[str, List[Task]]:
    grouped: Dict[str, List[Task]] = {tag: [] for tag in EMOJI_BY_TAG}
    for task in tasks:
        grouped.setdefault(task.tag, []).append(task)
    return grouped


def _top_files(tasks: List[Task], limit: int = 5) -> List[Dict[str, object]]:
    from collections import Counter

    counter = Counter(task.file_path for task in tasks)
    return [
        {"file_path": file_path, "count": count}
        for file_path, count in counter.most_common(limit)
    ]


def generate_html(result: ScanResult, output_path: str = "TODO_TREE.html") -> str:
    template_dir = Path(__file__).resolve().parent.parent / "templates"
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=select_autoescape(["html", "xml"]),
    )
    template = env.get_template("dashboard.html")
    summary = result.summary()
    all_tags = sorted(set(["FIXME", "HACK", "TODO", "NOTE"] + [tag for tag in summary.keys() if tag != "total"]))
    stats = {tag: summary.get(tag, 0) for tag in all_tags}
    stats["total"] = summary.get("total", 0)
    grouped_tasks = _group_tasks_by_tag(result.tasks)
    top_files = _top_files(result.tasks)
    generated_at = datetime.now().strftime("%Y-%m-%d %I:%M %p")
    motivational_quote = random.choice(MOTIVATIONAL_QUOTES)
    tag_order = sorted(
        grouped_tasks.keys(),
        key=lambda tag: (
            min((task.weight for task in result.tasks if task.tag == tag), default=len(PRIORITY_ORDER)),
            tag,
        ),
    )
    request_colors = COLORS.copy()
    for tag in all_tags:
        request_colors.setdefault(tag, "#6a5b40")
    request_emoji = EMOJI_BY_TAG.copy()
    for tag in all_tags:
        request_emoji.setdefault(tag, "🔹")

    content = template.render(
        result=result,
        stats=stats,
        generated_at=generated_at,
        motivational_quote=motivational_quote,
        grouped_tasks=grouped_tasks,
        top_files=top_files,
        emoji_by_tag=request_emoji,
        colors=request_colors,
        tag_order=tag_order,
    )
    output_file = Path(output_path)
    output_file.write_text(content, encoding="utf-8")
    return str(output_file.resolve())
