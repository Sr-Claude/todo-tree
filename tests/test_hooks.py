from pathlib import Path

from typer.testing import CliRunner

from todo_tree.cli import app

runner = CliRunner()


def test_hook_install_creates_hook_with_json(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".git").mkdir()

    result = runner.invoke(app, ["hook", "install", str(repo)])
    assert result.exit_code == 0
    hook = repo / ".git" / "hooks" / "post-commit"
    assert hook.exists()
    content = hook.read_text(encoding="utf-8")
    assert "ci-check" in content and "--json" in content
    assert ".git/hooks/todo-tree-ci.json" in content


def test_hook_install_pre_push_blocking(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".git").mkdir()

    result = runner.invoke(app, ["hook", "install", str(repo), "--pre-push", "--block-on-fixme"]) 
    assert result.exit_code == 0
    hook = repo / ".git" / "hooks" / "pre-push"
    assert hook.exists()
    content = hook.read_text(encoding="utf-8")
    assert "ci-check" in content and "--json" in content and "exit 1" in content
