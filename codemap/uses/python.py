"""Parser Python — extração de imports via módulo ast."""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True, eq=True)
class PythonImportRef:
    module: str
    names: list[str] = field(default_factory=list)
    level: int = 0
    section: str = ""  # "import" ou "from"
    line: int = 0


def parse_python_imports(filepath: Path) -> list[PythonImportRef]:
    """Extrai imports de um arquivo Python (.py) usando AST."""
    try:
        content = filepath.read_text(encoding="utf-8", errors="replace")
    except (OSError, IOError):
        return []

    if not content.strip():
        return []

    try:
        tree = ast.parse(content, filename=str(filepath))
    except SyntaxError:
        return []

    refs: list[PythonImportRef] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                refs.append(PythonImportRef(
                    module=alias.name,
                    names=[],
                    level=0,
                    section="import",
                    line=node.lineno,
                ))
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            names = [alias.name for alias in node.names]
            refs.append(PythonImportRef(
                module=module,
                names=names,
                level=node.level or 0,
                section="from",
                line=node.lineno,
            ))

    return refs
