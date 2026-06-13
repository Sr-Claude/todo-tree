from todo_tree.parser import extract_tasks_from_line, parse_file


def test_extract_tasks_from_python_line():
    line = "# TODO: fix this"
    tasks = extract_tasks_from_line(line, "file.py", 1, "#", ["TODO", "FIXME", "HACK", "NOTE"])
    assert len(tasks) == 1
    assert tasks[0].tag == "TODO"
    assert "fix this" in tasks[0].message


def test_extract_tasks_from_javascript_line():
    line = "// FIXME: broken"
    tasks = extract_tasks_from_line(line, "file.js", 2, "//", ["TODO", "FIXME", "HACK", "NOTE"])
    assert len(tasks) == 1
    assert tasks[0].tag == "FIXME"


def test_extract_tasks_from_hack_line():
    line = "# HACK: temporal fix"
    tasks = extract_tasks_from_line(line, "file.py", 3, "#", ["TODO", "FIXME", "HACK", "NOTE"])
    assert len(tasks) == 1
    assert tasks[0].tag == "HACK"


def test_extract_tasks_from_note_line():
    line = "# NOTE: important context"
    tasks = extract_tasks_from_line(line, "file.py", 4, "#", ["TODO", "FIXME", "HACK", "NOTE"])
    assert len(tasks) == 1
    assert tasks[0].tag == "NOTE"


def test_extract_tasks_from_line_without_tag():
    line = "# This is a comment without special tags"
    tasks = extract_tasks_from_line(line, "file.py", 5, "#", ["TODO", "FIXME", "HACK", "NOTE"])
    assert tasks == []


def test_extract_tasks_from_line_without_comment_prefix():
    line = "TODO: missing comment prefix"
    tasks = extract_tasks_from_line(line, "file.py", 6, "#", ["TODO", "FIXME", "HACK", "NOTE"])
    assert tasks == []


def test_extract_tasks_with_multiple_tags():
    line = "// TODO: fix this HACK: temporal"
    tasks = extract_tasks_from_line(line, "file.js", 7, "//", ["TODO", "FIXME", "HACK", "NOTE"])
    assert len(tasks) == 2
    assert tasks[0].tag == "TODO"
    assert tasks[1].tag == "HACK"


def test_parse_file_handles_supported_extension(tmp_path):
    file_path = tmp_path / "example.py"
    file_path.write_text("# TODO: hello\n# FIXME: stop\n", encoding="utf-8")
    tasks = parse_file(str(file_path))
    assert len(tasks) == 2
    assert {task.tag for task in tasks} == {"TODO", "FIXME"}
