---
name: project-package-name
description: El nombre del paquete en PyPI es todo-tree-cli, no todo-tree, porque todo-tree ya estaba tomado
metadata:
  type: project
---

El paquete se llama `todo-tree-cli` en PyPI (no `todo-tree` como figura en el spec original).

**Why:** El nombre `todo-tree` ya estaba registrado en PyPI por otro autor, así que se usó `todo-tree-cli` para poder publicar.

**How to apply:** Cuando el usuario mencione el nombre del paquete o la publicación en PyPI, usar siempre `todo-tree-cli`. El comando CLI sigue siendo `todo-tree` (definido en el entry point de pyproject.toml). El módulo Python sigue siendo `todo_tree`.
