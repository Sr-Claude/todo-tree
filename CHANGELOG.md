# Changelog

## [Unreleased]

- Añadidos comandos de Git hook `hook install` y `hook uninstall`.
- Implementado `ci-check` con soporte para `--max-todos`, `--max-fixmes`, `--max-hacks` y salida `--json`.
- Añadida salida JSON rica con conteos globales, archivos y tareas, incluyendo `priority` y `weight`.
- Hooks `pre-push` y `post-commit` ahora registran resultados en `.git/hooks/todo-tree-ci.json`.
- Añadidas pruebas de integración para los hooks git.
- Documentación de uso, hooks y CI mejorada en `README.md`.

## [v0.1.0] - 2026-06-13

- Lanzamiento: `v0.1.0` (Sprint 7, Fecha de publicación: 2026-06-13).
- Características principales:
	- Instalación y desinstalación de Git hooks con `hook install` / `hook uninstall`.
	- Comando `ci-check` con soporte para `--max-todos`, `--max-fixmes`, `--max-hacks` y salida `--json`.
	- Salida JSON estructurada con conteos globales, archivos y tareas (incluye `priority` y `weight`).
	- Los hooks (`pre-push`, `post-commit`) registran resultados en `.git/hooks/todo-tree-ci.json`.
	- Compatibilidad mejorada con Windows/Git for Windows: los scripts de hook incorporan la ruta de Python convertida a formato POSIX para ejecutarse bajo `sh.exe`/MSYS.
	- Pruebas de integración para hooks añadidas y validadas en entorno local.
	- Empaquetado y validación: wheel creado y comprobado en un virtualenv limpio; instalación limpia verificada; CLI disponible vía `python -m todo_tree.cli` y muestra la versión.

- Estado de pruebas: suite completa verificada localmente (32 passed).

