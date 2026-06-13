import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest
from typer.testing import CliRunner

from todo_tree.cli import app

runner = CliRunner()


def _has_command(command: str) -> bool:
    return shutil.which(command) is not None


def _find_shell() -> str | None:
    # Prefer POSIX-compatible shells available on Windows via Git/MSYS or native sh.
    for candidate in ["sh.exe", "sh", "bash.exe", "bash"]:
        path = shutil.which(candidate)
        if path:
            try:
                subprocess.run([path, "-lc", "echo ok"], check=True, capture_output=True, text=True)
                return path
            except Exception:
                continue
    return None


def _msys_path(path: Path) -> str:
    if os.name == "nt" and len(path.drive) == 2 and path.drive[1] == ":":
        drive = path.drive[0].lower()
        return "/" + drive + path.as_posix()[2:]
    return path.as_posix()


@pytest.mark.skipif(not _has_command("git"), reason="Git is required for integration hook tests")
@pytest.mark.skipif(_find_shell() is None, reason="A working POSIX shell is required to execute hook scripts")
def test_pre_push_hook_blocks_and_creates_json(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    (repo / "main.py").write_text("# FIXME: integration test\n", encoding="utf-8")

    result = runner.invoke(app, ["hook", "install", str(repo), "--pre-push", "--block-on-fixme"])
    assert result.exit_code == 0

    hook_path = repo / ".git" / "hooks" / "pre-push"
    assert hook_path.exists()

    shell_path = _find_shell()
    assert shell_path is not None
    repo_path = _msys_path(repo)
    hook_path_msys = _msys_path(hook_path)
    execution = subprocess.run([shell_path, "-lc", f'cd "{repo_path}" && "{hook_path_msys}"'], cwd=repo, capture_output=True, text=True)
    assert execution.returncode != 0

    json_log = repo / ".git" / "hooks" / "todo-tree-ci.json"
    assert json_log.exists()
    data = json.loads(json_log.read_text(encoding="utf-8"))
    assert data["failed"] is True
    assert data["fixmes"] == 1
    assert "reason" not in data or isinstance(data["reasons"], list)
    assert "files" in data
    assert "main.py" in data["files"]
    assert data["files"]["main.py"]["fixmes"] == 1


def test_post_commit_hook_runs_and_logs_json(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    (repo / "main.py").write_text("# TODO: integration test\n", encoding="utf-8")
    subprocess.run(["git", "add", "main.py"], cwd=repo, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    subprocess.run(["git", "commit", "-m", "init", "--author", "test <test@example.com>"], cwd=repo, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    result = runner.invoke(app, ["hook", "install", str(repo)])
    assert result.exit_code == 0

    hook_path = repo / ".git" / "hooks" / "post-commit"
    assert hook_path.exists()

    shell_path = _find_shell()
    assert shell_path is not None
    repo_path = _msys_path(repo)
    hook_path_msys = _msys_path(hook_path)
    execution = subprocess.run([
        shell_path,
        "-lc",
        f'cd "{repo_path}" && "{hook_path_msys}"',
    ], cwd=repo, capture_output=True, text=True)
    assert execution.returncode == 0

    json_log = repo / ".git" / "hooks" / "todo-tree-ci.json"
    assert json_log.exists()
    data = json.loads(json_log.read_text(encoding="utf-8"))
    assert data["failed"] is False
    assert data["todos"] == 1
    assert "main.py" in data["files"]
