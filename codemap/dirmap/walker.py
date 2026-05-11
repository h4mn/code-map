"""Walker — caminha árvore de diretórios coletando metadados."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from codemap.config import DirmapConfig
from codemap.dirmap.ignore import is_ignored, load_ignore_patterns


@dataclass
class Entry:
    path: str
    type: str  # "file" ou "dir"
    extension: str = ""
    language: str = ""
    size_bytes: int = 0


@dataclass
class WalkResult:
    entries: list[Entry] = field(default_factory=list)
    errors: list[dict] = field(default_factory=list)
    total_dirs: int = 0


def walk(root: str | Path, config: DirmapConfig | None = None) -> WalkResult:
    """Caminha a árvore de diretórios coletando metadados."""
    if config is None:
        config = DirmapConfig()

    root_path = Path(root).resolve()
    if not root_path.exists():
        raise FileNotFoundError(f"Caminho não encontrado: '{root}'")
    if not root_path.is_dir():
        raise FileNotFoundError(f"'{root}' não é um diretório")

    patterns = load_ignore_patterns(
        root_path, config.ignore_files, config.extra_dirs
    )
    # Arquivos de ignore são sempre excluídos do resultado
    for fname in config.ignore_files:
        if fname not in patterns:
            patterns.append(fname)

    result = WalkResult()
    visited_real: set[int] = set()
    _walk_recursive(root_path, root_path, config, patterns, result, 0, visited_real)
    return result


def _walk_recursive(
    current: Path,
    root: Path,
    config: DirmapConfig,
    patterns: list[str],
    result: WalkResult,
    depth: int,
    visited_real: set[int],
):
    if config.max_depth is not None and depth > config.max_depth:
        return

    try:
        items = list(current.iterdir())
    except PermissionError:
        rel = str(current.relative_to(root)).replace("\\", "/")
        result.errors.append({"path": rel, "reason": "permission_denied"})
        return

    for item in sorted(items, key=lambda p: (not p.is_dir(), p.name)):
        try:
            rel = str(item.relative_to(root)).replace("\\", "/")
        except ValueError:
            continue

        if is_ignored(rel, patterns):
            continue

        if item.is_symlink():
            if not config.follow_symlinks:
                continue
            real = item.resolve()
            real_id = real.stat().st_ino if real.exists() else None
            if real_id is not None:
                if real_id in visited_real:
                    result.errors.append({"path": rel, "reason": "symlink_cycle"})
                    continue
                visited_real.add(real_id)
            if real.is_dir():
                _walk_recursive(item, root, config, patterns, result, depth + 1, visited_real)
            elif real.is_file():
                result.entries.append(Entry(
                    path=rel, type="file",
                    extension=item.suffix.lower(),
                    size_bytes=item.stat().st_size,
                ))
            continue

        if item.is_dir():
            result.total_dirs += 1
            result.entries.append(Entry(path=rel, type="dir"))
            _walk_recursive(item, root, config, patterns, result, depth + 1, visited_real)
        elif item.is_file():
            result.entries.append(Entry(
                path=rel, type="file",
                extension=item.suffix.lower(),
                size_bytes=item.stat().st_size,
            ))
