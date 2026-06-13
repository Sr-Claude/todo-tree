from __future__ import annotations

import sys
from pathlib import Path


def generate_hook_script(
    pre_push: bool = False,
    block_on_fixme: bool = False,
    output_dir: Path | str | None = None,
    python_executable: str | None = None,
) -> str:
    python_executable = python_executable or sys.executable
    output_dir = output_dir or Path(".")
    output_dir = str(output_dir)
    if python_executable:
        python_path = Path(python_executable)
        if python_path.drive and len(python_path.drive) == 2 and python_path.drive[1] == ":":
            python_executable = "/" + python_path.drive[0].lower() + python_path.as_posix()[2:]
        else:
            python_executable = python_path.as_posix()
    else:
        python_executable = "python"
    header = [
        "#!/bin/sh",
        "set -e",
        "cd \"$(git rev-parse --show-toplevel)\"",
        f'PYTHON_CMD="{python_executable}"',
        "command -v python >/dev/null 2>&1 || PYTHON_CMD=python3",
    ]
    ci_check_cmd = f"$PYTHON_CMD -m todo_tree.cli ci-check . --json"
    scan_cmd = f"$PYTHON_CMD -m todo_tree.cli scan . --output-dir \"{output_dir}\" --format both"

    json_log = ".git/hooks/todo-tree-ci.json"
    if pre_push:
        if block_on_fixme:
            header.append(f"{ci_check_cmd} --max-fixmes 0 > {json_log} || exit 1")
        else:
            header.append(
                f"if ! {ci_check_cmd} --max-fixmes 0 > {json_log}; then echo 'CI check failed, continuing'; fi"
            )
        header.append(scan_cmd)
    else:
        header.append(f"{ci_check_cmd} > {json_log} || true")
        header.append(f"{scan_cmd} || true")

    return "\n".join(header) + "\n"
