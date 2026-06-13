# todo-tree

🐓 **todo-tree** es un generador de árbol de tareas pendientes que ayuda a los desarrolladores a encontrar TODOs, FIXMEs, HACKs y NOTEs escondidos en un proyecto.

## ¿Qué hace?

- Escanea tu proyecto recursivamente.
- Extrae comentarios especiales como `TODO`, `FIXME`, `HACK` y `NOTE`.
- Genera reportes en Markdown y un dashboard HTML.
- Ideal para equipos que quieren visualizar deuda técnica al despertar con una buena taza de café.

## Instalación en modo desarrollo

```bash
pip install -e .
```

## Uso rápido

```bash
todo-tree scan .
```

## Ejemplo de configuración

Crea un archivo `.todo-tree.toml` en el raíz de tu proyecto:

```toml
[scan]
tags = ["TODO", "FIXME", "HACK", "NOTE"]
extensions = ["py", "js", "ts"]
ignore_dirs = [".git", "node_modules", "venv"]
recursive = true

[output]
format = "both"
sort_by = "priority"
output_dir = "./docs"

[custom_tags]
OPTIMIZE = "media"
DOCS = "baja"
```

Este archivo controla el escaneo y la generación de reportes en cada proyecto.

## Hooks de Git y CI

Instala un hook de Git con:

```bash
todo-tree hook install .
```

Para instalar un hook `pre-push` que bloquee si hay `FIXME`:

```bash
todo-tree hook install . --pre-push --block-on-fixme
```

El hook crea un log JSON en:

```bash
.git/hooks/todo-tree-ci.json
```

Esto permite inspeccionar el resultado del chequeo CI incluso cuando falla.

El hook usa `ci-check --json` para evaluar si el repositorio puede continuar.

### GitHub Actions

El workflow de ejemplo en `.github/workflows/example.yml` ejecuta:

```bash
todo-tree ci-check --max-fixmes 0 --json
```

Si `ci-check` falla, el job también falla y el pipeline detiene la ejecución.

### Comando CI

```bash
todo-tree ci-check . --max-fixmes 0 --max-hacks 0 --json
```

Esta salida JSON incluye conteos globales y detalles por archivo, como `priority` y `weight` por tarea.

Cuando se usa desde un hook, el resultado se escribe en:

```bash
.git/hooks/todo-tree-ci.json
```

Esto facilita la depuración posterior al fallo.

Ejemplo de salida JSON:

```json
{
  "todos": 3,
  "fixmes": 1,
  "hacks": 2,
  "failed": true,
  "reasons": ["fixmes>0"],
  "files": {
    "src/app.py": {
      "todos": 1,
      "fixmes": 1,
      "hacks": 0,
      "tasks": [
        {
          "tag": "FIXME",
          "message": "arreglar esto",
          "line": 42,
          "priority": "Crítica",
          "weight": 1
        }
      ]
    }
  }
}
```

```bash
python -c "from todo_tree.models import Task, ScanResult; t = Task('TODO', 'test', 'file.py', 1); print(t)"
```

## Estructura del proyecto

```text
todo-tree/
├── src/
│   └── todo_tree/
│       ├── __init__.py
│       ├── models.py
│       ├── generators/
│       │   ├── __init__.py
│       └── templates/
│           └── dashboard.html
├── tests/
│   └── __init__.py
├── pyproject.toml
├── README.md
├── LICENSE
└── .gitignore
```
