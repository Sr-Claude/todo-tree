import tempfile
from pathlib import Path

from todo_tree.scanner import scan_directory


def test_scan_directory_collects_tasks(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    (project / "main.py").write_text("# TODO: start here\n# FIXME: broken\n", encoding="utf-8")
    (project / "script.js").write_text("// HACK: workaround\n", encoding="utf-8")
    result = scan_directory(str(project))

    assert result.files_scanned == 2
    assert len(result.tasks) == 3
    assert {task.tag for task in result.tasks} == {"TODO", "FIXME", "HACK"}


def test_scan_directory_respects_ignore_dirs(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    ignore_dir = project / "node_modules"
    ignore_dir.mkdir()
    (ignore_dir / "ignored.py").write_text("# TODO: hidden\n", encoding="utf-8")
    (project / "keep.py").write_text("# TODO: visible\n", encoding="utf-8")
    result = scan_directory(str(project))

    assert result.files_scanned == 1
    assert len(result.tasks) == 1
    assert result.tasks[0].file_path == "keep.py"


def test_scan_directory_filters_extensions(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    (project / "a.py").write_text("# TODO: yes\n", encoding="utf-8")
    (project / "b.txt").write_text("# TODO: no\n", encoding="utf-8")
    result = scan_directory(str(project), extensions=["py"])

    assert result.files_scanned == 1
    assert len(result.tasks) == 1
    assert result.tasks[0].file_path == "a.py"
