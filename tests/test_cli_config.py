from pathlib import Path

from typer.testing import CliRunner

from todo_tree.cli import app

runner = CliRunner()


def test_scan_uses_config_file(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    (project / "main.py").write_text("# TODO: config test\n", encoding="utf-8")
    config_file = project / ".todo-tree.toml"
    config_file.write_text(
        """[scan]
tags = ["TODO"]
extensions = ["py"]
ignore_dirs = []
recursive = false

[output]
format = "markdown"
sort_by = "file"
output_dir = "./out"
""",
        encoding="utf-8",
    )
    result = runner.invoke(app, ["scan", str(project)])

    assert result.exit_code == 0
    assert (project / "out" / "TODO_TREE.md").exists()
    assert not (project / "out" / "TODO_TREE.html").exists()


def test_custom_tags_priority(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    (project / "main.py").write_text("# OPTIMIZE: speed up\n", encoding="utf-8")
    config_file = project / ".todo-tree.toml"
    config_file.write_text(
        """[scan]
tags = ["OPTIMIZE"]
extensions = ["py"]
ignore_dirs = []
recursive = false

[output]
format = "markdown"
sort_by = "priority"
output_dir = "./out"

[custom_tags]
OPTIMIZE = "media"
""",
        encoding="utf-8",
    )
    result = runner.invoke(app, ["scan", str(project)])

    assert result.exit_code == 0
    assert "OPTIMIZE" in (project / "out" / "TODO_TREE.md").read_text(encoding="utf-8")


def test_cli_overrides_config(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    (project / "main.py").write_text("# TODO: override\n", encoding="utf-8")
    config_file = project / ".todo-tree.toml"
    config_file.write_text(
        """[scan]
tags = ["TODO"]
extensions = ["py"]
ignore_dirs = []
recursive = true

[output]
format = "html"
sort_by = "priority"
output_dir = "./out"
""",
        encoding="utf-8",
    )
    result = runner.invoke(app, ["scan", str(project), "--format", "markdown", "--no-recursive"])

    assert result.exit_code == 0
    assert (project / "out" / "TODO_TREE.md").exists()
    assert not (project / "out" / "TODO_TREE.html").exists()
