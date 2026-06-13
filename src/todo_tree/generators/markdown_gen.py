from __future__ import annotations

from datetime import datetime
from pathlib import Path
import random
from typing import Dict, List

from todo_tree.models import ScanResult, Task

EMOJI_BY_TAG: Dict[str, str] = {
    "FIXME": "🔴",
    "HACK": "🟠",
    "TODO": "🟡",
    "NOTE": "🔵",
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

TAG_LABELS = {
    "FIXME": "Crítico",
    "HACK": "Alta prioridad",
    "TODO": "Media prioridad",
    "NOTE": "Informativo",
}


def _format_task_line(task: Task) -> str:
    link = f"{task.file_path}#L{task.line_number}"
    emoji = EMOJI_BY_TAG.get(task.tag, "🔹")
    return f"- **[{link}]** — {task.message}"


def _group_by_file(tasks: List[Task]) -> Dict[str, List[Task]]:
    grouped: Dict[str, List[Task]] = {}
    for task in sorted(tasks, key=lambda item: (item.file_path, item.line_number)):
        grouped.setdefault(task.file_path, []).append(task)
    return grouped


def _group_by_tag(tasks: List[Task]) -> Dict[str, List[Task]]:
    grouped: Dict[str, List[Task]] = {}
    for task in sorted(tasks, key=lambda item: (PRIORITY_ORDER.index(item.tag) if item.tag in PRIORITY_ORDER else len(PRIORITY_ORDER), item.file_path, item.line_number)):
        grouped.setdefault(task.tag, []).append(task)
    return grouped


def _render_summary(summary: Dict[str, int]) -> str:
    lines = ["| Tag | Cantidad |", "|-------|----------|"]
    for tag in PRIORITY_ORDER:
        emoji = EMOJI_BY_TAG.get(tag, "🔹")
        lines.append(f"| {emoji} {tag} | {summary.get(tag, 0)} |")
    extra_tags = [tag for tag in summary.keys() if tag not in PRIORITY_ORDER and tag != "total"]
    for tag in sorted(extra_tags):
        emoji = EMOJI_BY_TAG.get(tag, "🔹")
        lines.append(f"| {emoji} {tag} | {summary.get(tag, 0)} |")
    return "\n".join(lines)


def _render_by_priority(tasks: List[Task]) -> str:
    grouped = _group_by_tag(tasks)
    ordered_tags = sorted(
        grouped.keys(),
        key=lambda tag: (PRIORITY_ORDER.index(tag) if tag in PRIORITY_ORDER else len(PRIORITY_ORDER), tag),
    )
    sections: List[str] = []
    for tag in ordered_tags:
        tag_tasks = grouped.get(tag, [])
        if not tag_tasks:
            continue
        emoji = EMOJI_BY_TAG.get(tag, "🔹")
        label = TAG_LABELS.get(tag, tag)
        sections.append(f"## {emoji} {tag} — {label} ({len(tag_tasks)})\n")
        for task in tag_tasks:
            sections.append(_format_task_line(task))
        sections.append("")
    return "\n".join(sections).strip()


def _render_by_file(tasks: List[Task]) -> str:
    grouped = _group_by_file(tasks)
    sections: List[str] = []
    for file_path, file_tasks in grouped.items():
        sections.append(f"### {file_path}")
        for task in file_tasks:
            sections.append(f"- **L{task.line_number}** — {EMOJI_BY_TAG.get(task.tag, '🔹')} {task.tag}: {task.message}")
        sections.append("")
    return "\n".join(sections).strip()


def _render_by_tag(tasks: List[Task]) -> str:
    grouped = _group_by_tag(tasks)
    ordered_tags = sorted(
        grouped.keys(),
        key=lambda tag: (PRIORITY_ORDER.index(tag) if tag in PRIORITY_ORDER else len(PRIORITY_ORDER), tag),
    )
    sections: List[str] = []
    for tag in ordered_tags:
        tag_tasks = grouped.get(tag, [])
        if not tag_tasks:
            continue
        emoji = EMOJI_BY_TAG.get(tag, "🔹")
        label = TAG_LABELS.get(tag, tag)
        sections.append(f"## {emoji} {tag} — {label} ({len(tag_tasks)})\n")
        for task in tag_tasks:
            sections.append(_format_task_line(task))
        sections.append("")
    return "\n".join(sections).strip()


def generate_markdown(
    result: ScanResult,
    output_path: str = "TODO_TREE.md",
    sort_by: str = "priority",
) -> str:
    output_file = Path(output_path)
    now = datetime.now().strftime("%Y-%m-%d %I:%M %p")
    summary = result.summary()
    quote = random.choice(MOTIVATIONAL_QUOTES)

    header = [
        "# 🌳 TODO Tree Report",
        "",
        f"**Generado:** {now}",
        f"**Archivos escaneados:** {result.files_scanned}",
        f"**Tareas encontradas:** {summary.get('total', 0)}",
        "",
        "---",
        "",
        "## 📊 Resumen",
        "",
        _render_summary(summary),
        "",
        "---",
        "",
    ]

    if sort_by == "file":
        body = _render_by_file(result.tasks)
    elif sort_by == "tag":
        body = _render_by_tag(result.tasks)
    else:
        body = _render_by_priority(result.tasks)

    footer = [
        "---",
        "",
        f"> {quote}",
    ]

    content = "\n".join([*header, body, *footer]).strip() + "\n"
    output_file.write_text(content, encoding="utf-8")
    return str(output_file.resolve())
