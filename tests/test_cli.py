from pathlib import Path

from typer.testing import CliRunner

from todo_tree.cli import app

runner = CliRunner()


def test_version_shows_version():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "todo-tree v" in result.output


def test_init_creates_config(tmp_path):
    result = runner.invoke(app, ["init", str(tmp_path)])
    assert result.exit_code == 0
    config_file = tmp_path / ".todo-tree.toml"
    assert config_file.exists()
    assert "[scan]" in config_file.read_text(encoding="utf-8")


def test_scan_generates_markdown_and_html(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    (project / "main.py").write_text("# TODO: test\n# FIXME: broken\n", encoding="utf-8")
    output_dir = tmp_path / "out"
    result = runner.invoke(app, ["scan", str(project), "--output-dir", str(output_dir), "--format", "both"])

    assert result.exit_code == 0
    assert (output_dir / "TODO_TREE.md").exists()
    assert (output_dir / "TODO_TREE.html").exists()


def test_scan_format_markdown_only(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    (project / "main.py").write_text("# TODO: only markdown\n", encoding="utf-8")
    output_dir = tmp_path / "out"
    result = runner.invoke(app, ["scan", str(project), "--output-dir", str(output_dir), "--format", "markdown"])

    assert result.exit_code == 0
    assert (output_dir / "TODO_TREE.md").exists()
    assert not (output_dir / "TODO_TREE.html").exists()


def test_scan_no_recursive(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    sub = project / "sub"
    sub.mkdir()
    (sub / "nested.py").write_text("# TODO: no recursive\n", encoding="utf-8")
    (project / "root.py").write_text("# TODO: root\n", encoding="utf-8")
    output_dir = tmp_path / "out"
    result = runner.invoke(app, ["scan", str(project), "--output-dir", str(output_dir), "--no-recursive"])

    assert result.exit_code == 0
    content = (output_dir / "TODO_TREE.md").read_text(encoding="utf-8")
    assert "root.py" in content
    assert "nested.py" not in content


def test_scan_verbose(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    (project / "main.py").write_text("# TODO: verbose\n", encoding="utf-8")
    output_dir = tmp_path / "out"
    result = runner.invoke(app, ["scan", str(project), "--output-dir", str(output_dir), "--verbose"])

    assert result.exit_code == 0
    assert "todo-tree escaneando" in result.output
