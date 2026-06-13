from pathlib import Path

from typer.testing import CliRunner

from todo_tree.cli import app

runner = CliRunner()


def test_ci_check_fails_on_fixme(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    (project / "a.py").write_text("# FIXME: broken\n", encoding="utf-8")
    result = runner.invoke(app, ["ci-check", str(project), "--max-fixmes", "0"])
    assert result.exit_code == 1


def test_ci_check_passes_when_clean(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    (project / "a.py").write_text("# TODO: note\n", encoding="utf-8")
    result = runner.invoke(app, ["ci-check", str(project), "--max-fixmes", "0"])
    assert result.exit_code == 0


def test_ci_check_hack_threshold_and_json(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    (project / "a.py").write_text("# HACK: stuff\n# HACK: more\n", encoding="utf-8")
    # should fail if max_hacks=1
    result = runner.invoke(app, ["ci-check", str(project), "--max-hacks", "1"])
    assert result.exit_code == 1

    # JSON output when passing
    result2 = runner.invoke(app, ["ci-check", str(project), "--max-hacks", "2", "--json"])
    assert result2.exit_code == 0
    assert '{"todos":' in result2.output
    import json

    payload = json.loads(result2.output)
    assert "files" in payload
    file_entry = payload["files"].get("a.py")
    assert file_entry is not None
    assert file_entry["hacks"] == 2
    assert len(file_entry["tasks"]) == 2
    assert file_entry["tasks"][0]["priority"] == "Alta"
    assert file_entry["tasks"][0]["weight"] == 2
