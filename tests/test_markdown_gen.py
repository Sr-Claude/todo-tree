from pathlib import Path

from todo_tree.generators.markdown_gen import generate_markdown
from todo_tree.models import ScanResult, Task


def make_scan_result() -> ScanResult:
    tasks = [
        Task("TODO", "migrar a async/await", "src/utils.py", 67),
        Task("FIXME", "validar token JWT correctamente", "src/auth.py", 42),
        Task("HACK", "parche temporal para el rate limiting", "src/api.py", 23),
        Task("NOTE", "variables de entorno documentadas en Notion", "src/config.py", 5),
    ]
    return ScanResult(tasks=tasks, files_scanned=4, extensions_checked=[".py"], timestamp="2026-06-13")


def test_generate_markdown_creates_file(tmp_path):
    result = make_scan_result()
    output = tmp_path / "TODO_TREE.md"
    path = generate_markdown(result, str(output), sort_by="priority")

    assert Path(path).exists()
    content = Path(path).read_text(encoding="utf-8")
    assert "# 🌳 TODO Tree Report" in content
    assert "## 📊 Resumen" in content
    assert "🔴 FIXME" in content
    assert "🟡 TODO" in content
    assert "🟠 HACK" in content
    assert "🔵 NOTE" in content


def test_generate_markdown_sort_by_file(tmp_path):
    result = make_scan_result()
    output = tmp_path / "TODO_TREE_BY_FILE.md"
    content = Path(generate_markdown(result, str(output), sort_by="file")).read_text(encoding="utf-8")

    assert "### src/auth.py" in content
    assert "### src/utils.py" in content
    assert "L42" in content


def test_generate_markdown_sort_by_tag(tmp_path):
    result = make_scan_result()
    output = tmp_path / "TODO_TREE_BY_TAG.md"
    content = Path(generate_markdown(result, str(output), sort_by="tag")).read_text(encoding="utf-8")

    assert "## 🔴 FIXME" in content
    assert "## 🟠 HACK" in content
    assert "## 🟡 TODO" in content
    assert "## 🔵 NOTE" in content
