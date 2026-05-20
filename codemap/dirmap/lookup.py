"""Lookup de símbolos — tipos, constantes, enums via regex."""

from __future__ import annotations

import json
import re
from pathlib import Path

# Padrões regex por linguagem — capturam declarações de tipos/consts/enums
_PATTERNS = {
    "delphi": [
        (r"^\s*(\w[\w.]*)\s*=\s*class\b", "type"),
        (r"^\s*(\w[\w.]*)\s*=\s*record\b", "type"),
        (r"^\s*(\w[\w.]*)\s*=\s*interface\b", "type"),
        (r"^\s*(\w[\w.]*)\s*=\s*\(", "enum"),
        (r"^\s*(\w[\w.]*)\s*=\s*\d+\s*;", "const"),
        (r"^\s*(\w[\w.]*)\s*=\s*'", "const"),
        (r"^\s*(\w[\w.]*)\s*=\s*[A-Z][\w.]+\s*;", "const"),
        (r"^\s*type\s+(\w[\w.]*)\s*=", "type"),
        (r"^\s*const\s+(\w[\w.]*)\s*=", "const"),
    ],
    "python": [
        (r"^\s*class\s+(\w+)", "type"),
        (r"^\s*(\w+)\s*=\s*\d+", "const"),
        (r"^\s*(\w+)\s*=\s*['\"]", "const"),
        (r"^\s*(\w+)\s*:\s*\w+\s*=", "const"),
    ],
}


def _scan_file(filepath: Path, patterns: list[tuple[str, str]], symbol: str) -> list[dict]:
    """Escaneia um arquivo buscando símbolos que matchem o termo."""
    results = []
    symbol_lower = symbol.lower()
    try:
        text = filepath.read_text(encoding="utf-8", errors="ignore")
    except (OSError, PermissionError):
        return results

    for line_no, line in enumerate(text.splitlines(), 1):
        for pattern, kind in patterns:
            m = re.match(pattern, line, re.IGNORECASE)
            if m and symbol_lower in m.group(1).lower():
                results.append({
                    "symbol": m.group(1),
                    "kind": kind,
                    "line": line_no,
                    "context": line.strip(),
                })
    return results


def lookup(
    data: dict,
    symbol: str,
    lang: str | None = None,
) -> list[dict]:
    """Busca declarações de tipos/constantes/enums nos arquivos do dirmap."""
    root_path = data.get("meta", {}).get("root_path", ".")
    entries = data.get("tree", [])
    symbol_lower = symbol.lower()

    # Coleta arquivos candidatos
    candidates = []
    for entry in entries:
        if entry.get("type") != "file":
            continue
        entry_lang = entry.get("language")
        if lang and entry_lang != lang:
            continue
        if entry_lang not in _PATTERNS:
            continue
        candidates.append((entry, entry_lang))

    results = []
    for entry, entry_lang in candidates:
        filepath = Path(root_path) / entry["path"]
        patterns = _PATTERNS[entry_lang]
        matches = _scan_file(filepath, patterns, symbol)
        for match in matches:
            match["path"] = entry["path"]
            match["language"] = entry_lang
            results.append(match)

    # Se regex não achou, fallback pra substring no conteúdo
    if not results:
        for entry, entry_lang in candidates:
            filepath = Path(root_path) / entry["path"]
            try:
                text = filepath.read_text(encoding="utf-8", errors="ignore")
            except (OSError, PermissionError):
                continue
            for line_no, line in enumerate(text.splitlines(), 1):
                if symbol_lower in line.lower():
                    results.append({
                        "symbol": symbol,
                        "kind": "text",
                        "path": entry["path"],
                        "line": line_no,
                        "context": line.strip(),
                        "language": entry_lang,
                    })

    return results


def run_lookup_cmd(symbol: str, filepath: str, **kwargs):
    """Ponto de entrada do subcomando lookup."""
    if not filepath:
        raise FileNotFoundError("Nenhum dirmap especificado. Passe o arquivo ou configure default_dirmap em .codemap.yml")
    from codemap.dirmap.query import load_dirmap_json
    data = load_dirmap_json(filepath)
    lang = kwargs.get("lang")
    result = lookup(data, symbol, lang=lang)
    print(json.dumps(result, indent=2, ensure_ascii=False))
