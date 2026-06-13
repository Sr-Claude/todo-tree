# Release notes — v0.1.0 (2026-06-13)

Resumen: Lanzamiento inicial `v0.1.0` que completa Sprint 7. Enfocado en hooks Git, comprobaciones CI y compatibilidad con entornos Windows (Git for Windows / MSYS).

Cambios principales

- Añadido soporte para instalar/desinstalar hooks de Git con `hook install` / `hook uninstall`.
- Nuevo comando `ci-check` con opciones `--max-todos`, `--max-fixmes`, `--max-hacks` y salida `--json` para integraciones CI.
- Los hooks (`pre-push`, `post-commit`) generan un registro JSON en `.git/hooks/todo-tree-ci.json` con conteos y detalles por archivo.
- Mejorada la compatibilidad con Windows/Git for Windows: los scripts de hook incluyen la ruta a Python convertida a formato POSIX para ejecutarse bajo `sh.exe`/MSYS.
- Añadidas pruebas de integración que verifican la ejecución de hooks y la creación del JSON de salida.
- Empaquetado: generados `sdist` y `wheel` y verificada una instalación limpia en un virtualenv.

Notas de publicación

- Versión: `v0.1.0`
- Fecha: 2026-06-13
- Autor: Tu Nombre <tu.email@example.com>

Instrucciones rápidas

1. Construir artefactos:

```bash
python -m build --sdist --wheel
```

2. Instalar desde la rueda para verificar:

```bash
python -m pip install dist/todo_tree-0.1.0-py3-none-any.whl
```

3. (Opcional) Crear release en GitHub y subir artefactos o publicar en PyPI con `twine`.
