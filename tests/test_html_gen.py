from pathlib import Path

from todo_tree.generators.html_gen import generate_html
from todo_tree.models import ScanResult, Task


def make_scan_result() -> ScanResult:
    tasks = [
        Task("TODO", "migrar a async/await", "src/utils.py", 67),
        Task("FIXME", "validar token JWT correctamente", "src/auth.py", 42),
        Task("HACK", "parche temporal para el rate limiting", "src/api.py", 23),
        Task("NOTE", "variables de entorno documentadas en Notion", "src/config.py", 5),
    ]
    return ScanResult(tasks=tasks, files_scanned=4, extensions_checked=[".py"], timestamp="2026-06-13")


def test_generate_html_creates_file(tmp_path):
    result = make_scan_result()
    output = tmp_path / "TODO_TREE.html"
    path = generate_html(result, str(output))

    assert Path(path).exists()
    content = Path(path).read_text(encoding="utf-8")
    assert "TODO Tree Dashboard" in content
    assert "Archivos escaneados" in content
    assert "FIXME" in content
    assert "HACK" in content
    assert "TODO" in content
    assert "NOTE" in content


def test_generate_html_counts_match(tmp_path):
    result = make_scan_result()
    output = tmp_path / "TODO_TREE.html"
    content = Path(generate_html(result, str(output))).read_text(encoding="utf-8")

    assert content.count("<tr>") >= 4
    assert "src/utils.py" in content
    assert "src/auth.py" in content
