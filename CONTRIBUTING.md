# Contribuyendo a todo-tree-cli

¡Gracias por querer contribuir! Este proyecto usa Python 3.10+, Typer, Jinja2 y Rich.

## Configurar el entorno de desarrollo

```bash
# 1. Clona el repositorio
git clone https://github.com/your/repo todo-tree
cd todo-tree

# 2. Crea un entorno virtual
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
.venv\Scripts\activate           # Windows

# 3. Instala el paquete en modo desarrollo con dependencias de test
pip install -e ".[test]"

# 4. Verifica que todo funciona
todo-tree --help
```

## Ejecutar los tests

```bash
# Todos los tests
pytest tests/ -v

# Con cobertura
pip install pytest-cov
pytest tests/ --cov=src/todo_tree --cov-report=term-missing

# Un módulo específico
pytest tests/test_parser.py -v
```

La cobertura mínima aceptada es **85%**. Los PRs que la bajen serán rechazados.

## Estructura del proyecto

```
src/todo_tree/
├── cli.py           # Comandos Typer: scan, init, version, hook, ci-check
├── scanner.py       # Recorre el árbol de directorios
├── parser.py        # Extrae TODOs línea por línea
├── models.py        # Dataclasses Task y ScanResult
├── utils.py         # Constantes, carga de config TOML
├── hooks.py         # Genera scripts de git hook
└── generators/
    ├── markdown_gen.py  # Reporte .md
    └── html_gen.py      # Dashboard .html con Jinja2
```

## Flujo para contribuir

1. **Abre un issue** describiendo el bug o la feature antes de ponerte a codear.
2. **Crea una rama** desde `master`: `git checkout -b feat/nombre-descriptivo`.
3. **Escribe tests** antes o junto al código (no después).
4. Asegúrate de que `pytest tests/ -v` pasa al 100%.
5. Abre un **Pull Request** apuntando a `master` con una descripción clara del cambio.

## Estándares de código

- **Sin comentarios obvios** — el nombre de la función ya explica el qué; comenta solo el *por qué* cuando no es evidente.
- **Sin abstracciones prematuras** — tres líneas similares no justifican un helper. Cuatro quizás.
- **Mensajes en español** — la CLI y los reportes hablan en español; mantén ese tono.
- **Tono café/mañanero** — el proyecto tiene personalidad. Los mensajes de error y éxito deben seguir el estilo del resto: ☕ motivador y ligeramente humorístico.
- Formatea con cualquier linter que tengas, pero no rompas el 100% de tests.

## Añadir soporte para un nuevo lenguaje

1. Agrega la extensión y su prefijo de comentario en `utils.py` → `EXTENSION_MAP`.
2. Si el lenguaje usa comentarios de bloque (como CSS o HTML), verifica que `parser.py` lo maneje.
3. Añade un test en `tests/test_parser.py` con una línea de ejemplo del nuevo lenguaje.

## Añadir un nuevo tag personalizado por defecto

Los tags de usuario van en `.todo-tree.toml` bajo `[custom_tags]`. Si quieres proponer uno como predeterminado, discútelo en un issue primero.

## Publicación (solo mantenedores)

La publicación a PyPI se dispara automáticamente al crear un **GitHub Release**. El workflow `.github/workflows/publish.yml` se encarga de construir y subir el paquete. Asegúrate de actualizar `__version__` en `src/todo_tree/__init__.py` y `version` en `pyproject.toml` antes del release.
