"""Parser de .gitignore e .codemap-ignore."""

from __future__ import annotations

import fnmatch
from pathlib import Path


def parse_ignore_file(path: Path) -> list[str]:
    """Lê um arquivo de ignore e retorna lista de padrões."""
    if not path.exists():
        return []
    patterns: list[str] = []
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.rstrip("\n\r")
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            patterns.append(stripped)
    return patterns


def load_ignore_patterns(
    root: Path,
    ignore_files: list[str],
    extra_dirs: list[str],
) -> list[str]:
    """Carrega padrões de todos os arquivos de ignore + extra_dirs."""
    patterns: list[str] = []
    for filename in ignore_files:
        patterns.extend(parse_ignore_file(root / filename))
    for d in extra_dirs:
        patterns.append(d)
        patterns.append(d + "/")
        patterns.append(d + "\\")
    return patterns


def is_ignored(relative_path: str | Path, patterns: list[str]) -> bool:
    """Verifica se um caminho relativo corresponde a algum padrão de ignore."""
    path_str = str(relative_path).replace("\\", "/")
    name = Path(path_str).name
    for pattern in patterns:
        if not pattern or pattern.startswith("#"):
            continue
        # Negation
        if pattern.startswith("!"):
            continue
        # Directory pattern ending with /
        if pattern.endswith("/"):
            dir_pat = pattern[:-1]
            if path_str == dir_pat or path_str.startswith(dir_pat + "/"):
                return True
            continue
        # Wildcard match
        if fnmatch.fnmatch(path_str, pattern) or fnmatch.fnmatch(path_str + "/", pattern):
            return True
        if fnmatch.fnmatch(name, pattern):
            return True
    return False
