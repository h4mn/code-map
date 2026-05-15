"""Dispatcher de parsers — roteia para o parser correto por linguagem."""

from __future__ import annotations

from pathlib import Path


def parse_imports(filepath: Path, language: str) -> list[dict]:
    """Extrai imports de um arquivo usando o parser adequado.

    Retorna lista de dicts normalizados:
        {"name": str, "section": str, "line": int, "unresolved": False}

    Linguagens suportadas:
        - delphi
        - python
        - javascript, typescript (ambos usam js_ts parser)
    """
    if not isinstance(filepath, Path):
        filepath = Path(filepath)

    lang = language.lower()

    if lang == "delphi":
        from codemap.uses.delphi import parse_delphi_uses
        refs = parse_delphi_uses(filepath)
        return [
            {"name": r.name, "section": r.section, "line": r.line, "unresolved": False}
            for r in refs
        ]

    if lang == "python":
        from codemap.uses.python import parse_python_imports
        refs = parse_python_imports(filepath)
        return [
            {"name": r.module, "section": r.section, "line": r.line, "unresolved": False}
            for r in refs
        ]

    if lang in ("javascript", "typescript", "js", "ts"):
        from codemap.uses.js_ts import parse_js_ts_imports
        refs = parse_js_ts_imports(filepath)
        return [
            {"name": r.source, "section": r.section, "line": r.line, "unresolved": False}
            for r in refs
        ]

    # Linguagem sem suporte — retorna vazio
    return []
