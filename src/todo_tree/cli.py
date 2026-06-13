from __future__ import annotations

from pathlib import Path
from typing import List

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from todo_tree.generators.html_gen import generate_html
from todo_tree.generators.markdown_gen import generate_markdown
from todo_tree.hooks import generate_hook_script
from todo_tree.scanner import scan_directory
from todo_tree.utils import DEFAULT_EXTENSIONS, DEFAULT_IGNORE_DIRS, DEFAULT_TAGS, load_config
from todo_tree import __version__

app = typer.Typer(rich_markup_mode="rich")
console = Console()

# Sub-app for git hooks
hooks_app = typer.Typer()
app.add_typer(hooks_app, name="hook")

import sys


def _normalize_extensions(extensions: list[str] | None) -> list[str]:
    if not extensions:
        return [ext.lstrip(".") for ext in DEFAULT_EXTENSIONS]
    return [ext.lower().lstrip(".") for ext in extensions]


def _normalize_tags(tags: list[str] | None) -> list[str]:
    return [tag.upper() for tag in (tags or DEFAULT_TAGS)]


def _coalesce_list(cli_value: list[str] | None, config_value: list[str] | None, default: list[str]) -> list[str]:
    if cli_value is not None:
        return cli_value
    if config_value is not None:
        return config_value
    return default


def _coalesce_str(cli_value: str | None, config_value: str | None, default: str) -> str:
    if cli_value is not None:
        return cli_value
    if config_value is not None:
        return config_value
    return default


def _merge_settings(
    path: str,
    tags: list[str] | None,
    extensions: list[str] | None,
    ignore_dirs: list[str] | None,
    output_dir: Path | None,
    format: str | None,
    sort_by: str | None,
    recursive: bool | None,
) -> tuple[list[str], list[str], list[str], Path, str, str, bool, dict[str, str]]:
    config = load_config(path)
    scan_config = config.get("scan", {})
    output_config = config.get("output", {})
    custom_tags = config.get("custom_tags", {})

    effective_tags = _normalize_tags(_coalesce_list(tags, scan_config.get("tags"), DEFAULT_TAGS))
    effective_extensions = _normalize_extensions(_coalesce_list(extensions, scan_config.get("extensions"), [ext.lstrip(".") for ext in DEFAULT_EXTENSIONS]))
    effective_ignore_dirs = _coalesce_list(ignore_dirs, scan_config.get("ignore_dirs"), DEFAULT_IGNORE_DIRS)
    if output_dir is not None:
        effective_output_dir = output_dir
    else:
        config_output_dir = output_config.get("output_dir", "./docs")
        config_path = Path(config_output_dir)
        if config_path.is_absolute():
            effective_output_dir = config_path
        else:
            effective_output_dir = Path(path) / config_path
    effective_format = _coalesce_str(format, output_config.get("format"), "both")
    effective_sort_by = _coalesce_str(sort_by, output_config.get("sort_by"), "priority")
    effective_recursive = recursive if recursive is not None else bool(scan_config.get("recursive", True))

    return (
        effective_tags,
        effective_extensions,
        effective_ignore_dirs,
        effective_output_dir,
        effective_format,
        effective_sort_by,
        effective_recursive,
        custom_tags,
    )


def _render_summary(result):
    summary = result.summary()
    table = Table.grid(padding=(0, 2))
    table.add_column()
    table.add_column()
    table.add_column()
    table.add_row("Archivos escaneados:", str(result.files_scanned), "")
    table.add_row("Tareas encontradas:", str(summary.get("total", 0)), "")
    counts = [
        f"🔴 FIXME: {summary.get('FIXME', 0)}",
        f"🟠 HACK: {summary.get('HACK', 0)}",
        f"🟡 TODO: {summary.get('TODO', 0)}",
        f"🔵 NOTE: {summary.get('NOTE', 0)}",
    ]
    table.add_row("", "", " | ".join(counts))
    return table


# Helper to write git hook files
def _write_hook(repo_path: Path, hook_name: str, content: str) -> Path:
    git_hooks = Path(repo_path) / ".git" / "hooks"
    git_hooks.mkdir(parents=True, exist_ok=True)
    hook_path = git_hooks / hook_name
    hook_path.write_text(content, encoding="utf-8")
    try:
        hook_path.chmod(0o755)
    except OSError:
        pass
    return hook_path


@app.command()
def scan(
    path: str = typer.Argument(".", help="Directorio raíz para escanear."),
    tags: List[str] | None = typer.Option(
        None,
        "--tags",
        help="Tags a buscar. Ej: --tags TODO FIXME HACK NOTE",
    ),
    extensions: List[str] | None = typer.Option(
        None,
        "--extensions",
        help="Extensiones de archivos a escanear sin el punto. Ej: --extensions py js ts",
    ),
    ignore_dirs: List[str] | None = typer.Option(
        None,
        "--ignore-dirs",
        help="Directorios a ignorar durante el escaneo.",
    ),
    output_dir: Path | None = typer.Option(
        None,
        "--output-dir",
        help="Directorio de salida para los reportes.",
    ),
    format: str | None = typer.Option(
        None,
        "--format",
        help="Formato de salida: markdown, html, both.",
        show_choices=True,
    ),
    sort_by: str | None = typer.Option(
        None,
        "--sort-by",
        help="Orden de las tareas: priority, file, tag.",
        show_choices=True,
    ),
    recursive: bool | None = typer.Option(
        None,
        "--recursive/--no-recursive",
        help="Activa o desactiva la recursividad.",
    ),
    verbose: bool = typer.Option(False, "--verbose", help="Muestra progreso y detalles.")
) -> None:
    (
        normalized_tags,
        normalized_extensions,
        normalized_ignore_dirs,
        effective_output_dir,
        effective_format,
        effective_sort_by,
        effective_recursive,
        custom_tags,
    ) = _merge_settings(
        path,
        tags,
        extensions,
        ignore_dirs,
        output_dir,
        format,
        sort_by,
        recursive,
    )

    effective_output_dir.mkdir(parents=True, exist_ok=True)
    console.print("🐓 [bold green]todo-tree escaneando...[/bold green]\n")
    with console.status("Escaneando archivos..."):
        result = scan_directory(
            path=path,
            tags=normalized_tags,
            extensions=normalized_extensions,
            ignore_dirs=normalized_ignore_dirs,
            recursive=effective_recursive,
            custom_priorities=custom_tags,
        )

    if not result.tasks:
        console.print(
            "✅ [bold green]¡No hay tareas pendientes![/bold green] Tu código está más limpio que una taza recién lavada. ☕️✨"
        )
        raise typer.Exit()

    markdown_path = None
    html_path = None
    if effective_format in {"markdown", "both"}:
        markdown_path = generate_markdown(result, str(effective_output_dir / "TODO_TREE.md"), sort_by=effective_sort_by)
    if effective_format in {"html", "both"}:
        html_path = generate_html(result, str(effective_output_dir / "TODO_TREE.html"))

    panel = Panel.fit(
        _render_summary(result),
        title="🌳 TODO Tree — Reporte generado",
        border_style="green",
    )
    console.print(panel)

    if markdown_path:
        console.print(f"📄 Markdown: {markdown_path}")
    if html_path:
        console.print(f"🌐 HTML:     {html_path}")

    fixer_count = result.summary().get("FIXME", 0)
    console.print(f"\n☕️ Prepara tu café. Hay {fixer_count} bugs críticos esperándote.")


@app.command()
def init(
    directory: Path = typer.Argument(Path("."), help="Directorio donde crear .todo-tree.toml."),
    force: bool = typer.Option(False, "--force", help="Sobrescribe el archivo si ya existe."),
) -> None:
    config_path = directory / ".todo-tree.toml"
    if config_path.exists() and not force:
        console.print(
            f"⚠️ El archivo {config_path} ya existe. Usa --force para sobrescribir."
        )
        raise typer.Exit(code=1)

    config_path.write_text(
        """# Configuración de todo-tree
[scan]
# Tags especiales a buscar en los comentarios.
tags = ["TODO", "FIXME", "HACK", "NOTE"]
# Extensiones de archivo a escanear.
extensions = ["py", "js", "ts", "java"]
ignore_dirs = [".git", "node_modules", "venv"]
recursive = true

[output]
format = "both" # markdown, html, both
sort_by = "priority" # priority, file, tag
output_dir = "./docs"

[custom_tags]
# OPTIMIZE = "media"
# DOCS = "baja"
# SECURITY = "critica"
""",
        encoding="utf-8",
    )
    console.print(f"✅ Archivo de configuración creado en {config_path}")


@app.command()
def version() -> None:
    console.print(f"🐓 todo-tree v{__version__}")
    console.print(r"[bold yellow]  _  _   _   _  _   _   _   _  \n | |/ / | | | || | | | | \ | | \n | ' /  | | | || | | | |  \| |  \n | . \  | |_| || |_| | | |\  |  \n |_||_\  \___/  \___/  |_| \_|  \n[/bold yellow]")


@hooks_app.command("install")
def hook_install(
    repo: Path = typer.Argument(Path("."), help="Repositorio Git donde instalar el hook."),
    pre_push: bool = typer.Option(False, "--pre-push", help="Instalar como pre-push en lugar de post-commit."),
    block_on_fixme: bool = typer.Option(False, "--block-on-fixme", help="Bloquear push si hay FIXMEs."),
    output_dir: Path | None = typer.Option(None, "--output-dir", help="Directorio de salida del reporte."),
) -> None:
    repo = Path(repo).resolve()
    if not (repo / ".git").exists():
        console.print(f"⚠️ {repo} no parece ser un repositorio git (no encuentra .git).")
        raise typer.Exit(code=1)

    out_dir = output_dir or Path(".")
    hook_name = "pre-push" if pre_push else "post-commit"
    content = generate_hook_script(
        pre_push=pre_push,
        block_on_fixme=block_on_fixme,
        output_dir=out_dir,
        python_executable=sys.executable,
    )

    path = _write_hook(repo, hook_name, content)
    console.print(f"✅ Hook instalado: {path}")


@hooks_app.command("uninstall")
def hook_uninstall(repo: Path = typer.Argument(Path("."), help="Repositorio Git donde desinstalar el hook."), pre_push: bool = typer.Option(False, "--pre-push", help="Desinstala el pre-push en lugar del post-commit.")) -> None:
    repo = Path(repo).resolve()
    hook_name = "pre-push" if pre_push else "post-commit"
    hook_path = repo / ".git" / "hooks" / hook_name
    if hook_path.exists():
        hook_path.unlink()
        console.print(f"✅ Hook eliminado: {hook_path}")
    else:
        console.print(f"ℹ️ No se encontró hook {hook_name} en {repo}")


@app.command("ci-check")
def ci_check(
    path: str = typer.Argument(".", help="Directorio raíz para escanear."),
    max_todos: int | None = typer.Option(None, "--max-todos", help="Fallará si hay más de N TODOs."),
    max_fixmes: int | None = typer.Option(None, "--max-fixmes", help="Fallará si hay más de N FIXMEs."),
    max_hacks: int | None = typer.Option(None, "--max-hacks", help="Fallará si hay más de N HACKs."),
    json_out: bool = typer.Option(False, "--json", help="Imprime salida en JSON para máquinas."),
) -> None:
    result = scan_directory(path)
    summary = result.summary()
    todos = summary.get("TODO", 0)
    fixmes = summary.get("FIXME", 0)
    hacks = summary.get("HACK", 0)

    failed = False
    reasons: list[str] = []
    if max_todos is not None and todos > max_todos:
        failed = True
        reasons.append(f"todos>{max_todos}")
    if max_fixmes is not None and fixmes > max_fixmes:
        failed = True
        reasons.append(f"fixmes>{max_fixmes}")
    if max_hacks is not None and hacks > max_hacks:
        failed = True
        reasons.append(f"hacks>{max_hacks}")

    # Build per-file details
    files: dict[str, dict] = {}
    for task in result.tasks:
        fp = task.file_path or "<unknown>"
        entry = files.setdefault(fp, {"todos": 0, "fixmes": 0, "hacks": 0, "tasks": []})
        if task.tag == "TODO":
            entry["todos"] += 1
        elif task.tag == "FIXME":
            entry["fixmes"] += 1
        elif task.tag == "HACK":
            entry["hacks"] += 1
        task_entry = {
            "tag": task.tag,
            "message": task.message,
            "line": task.line_number,
            "priority": task.priority,
            "weight": task.weight,
        }
        entry["tasks"].append(task_entry)

    out = {
        "todos": todos,
        "fixmes": fixmes,
        "hacks": hacks,
        "failed": failed,
        "reasons": reasons,
        "files": files,
    }

    if json_out:
        import json

        console.print(json.dumps(out))
    else:
        if failed:
            console.print(f"❌ CI check falló: TODOs={todos}, FIXMEs={fixmes}, HACKs={hacks} — {';'.join(reasons)}")
        else:
            console.print(f"✅ CI check pasó: TODOs={todos}, FIXMEs={fixmes}, HACKs={hacks}")

    if failed:
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
