from __future__ import annotations

from pathlib import Path
from typing import Dict, List
import tomllib

EXTENSION_MAP: Dict[str, str] = {
    ".py": "#",
    ".js": "//",
    ".ts": "//",
    ".jsx": "//",
    ".tsx": "//",
    ".java": "//",
    ".c": "//",
    ".cpp": "//",
    ".h": "//",
    ".go": "//",
    ".rs": "//",
    ".swift": "//",
    ".kt": "//",
    ".rb": "#",
    ".sh": "#",
    ".yaml": "#",
    ".yml": "#",
    ".toml": "#",
    ".css": "/*",
    ".html": "<!--",
    ".md": "<!--",
}

DEFAULT_TAGS: List[str] = ["TODO", "FIXME", "HACK", "NOTE"]
DEFAULT_IGNORE_DIRS: List[str] = [
    ".git",
    "__pycache__",
    "node_modules",
    "venv",
    ".venv",
    "dist",
    "build",
    ".tox",
    ".eggs",
]
DEFAULT_EXTENSIONS: List[str] = list(EXTENSION_MAP.keys())


def is_text_file(file_path: str) -> bool:
    path = Path(file_path)
    try:
        with path.open("rb") as handle:
            sample = handle.read(4096)
    except OSError:
        return False

    if b"\x00" in sample:
        return False

    try:
        sample.decode("utf-8")
        return True
    except UnicodeDecodeError:
        return False


def get_comment_prefix(extension: str) -> str | None:
    return EXTENSION_MAP.get(extension.lower())


def _merge_config(raw: dict) -> dict:
    scan = raw.get("scan", {}) if isinstance(raw, dict) else {}
    output = raw.get("output", {}) if isinstance(raw, dict) else {}
    custom_tags = raw.get("custom_tags", {}) if isinstance(raw, dict) else {}

    return {
        "scan": {
            "tags": scan.get("tags", DEFAULT_TAGS),
            "extensions": scan.get("extensions", [ext.lstrip(".") for ext in DEFAULT_EXTENSIONS]),
            "ignore_dirs": scan.get("ignore_dirs", DEFAULT_IGNORE_DIRS),
            "recursive": bool(scan.get("recursive", True)),
        },
        "output": {
            "format": output.get("format", "both"),
            "sort_by": output.get("sort_by", "priority"),
            "output_dir": output.get("output_dir", "./docs"),
        },
        "custom_tags": {str(key).upper(): str(value) for key, value in custom_tags.items()},
    }


def load_config(directory: str) -> dict:
    root = Path(directory).resolve()
    local_config = root / ".todo-tree.toml"
    home_config = Path.home() / ".config" / "todo-tree" / "config.toml"
    raw: dict = {}

    if local_config.exists():
        raw = _read_toml(local_config)
    elif home_config.exists():
        raw = _read_toml(home_config)

    return _merge_config(raw)


def _read_toml(path: Path) -> dict:
    try:
        with path.open("rb") as handle:
            return tomllib.load(handle)
    except OSError:
        return {}
