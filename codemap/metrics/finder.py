"""Finder — detecta duplicatas por nome e órfãos candidatos."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any


@dataclass
class DuplicateGroup:
    name: str
    paths: list[str] = field(default_factory=list)
    count: int = 0


@dataclass
class FinderResult:
    duplicates: list[DuplicateGroup] = field(default_factory=list)
    orphans: list[str] = field(default_factory=list)
    duplicate_map: dict[str, str] = field(default_factory=dict)
    orphan_set: set = field(default_factory=set)


def find_duplicates(entries: list[dict[str, Any]], min_group_size: int = 2) -> list[DuplicateGroup]:
    """Detecta arquivos com mesmo basename em diretórios diferentes."""
    by_name: dict[str, list[str]] = defaultdict(list)

    for entry in entries:
        if entry.get("type") != "file":
            continue
        name = entry.get("name", "")
        path = entry.get("path", "")
        if name and path:
            by_name[name].append(path)

    groups = []
    for name, paths in by_name.items():
        if len(paths) >= min_group_size:
            groups.append(DuplicateGroup(name=name, paths=paths, count=len(paths)))

    return sorted(groups, key=lambda g: g.count, reverse=True)


def find_orphans(
    entries: list[dict[str, Any]],
    min_group_size: int = 2,
) -> tuple[set[str], list[DuplicateGroup]]:
    """Marca órfãos candidatos e detecta duplicatas."""
    by_name: dict[str, list[str]] = defaultdict(list)
    for entry in entries:
        if entry.get("type") != "file":
            continue
        name = entry.get("name", "")
        path = entry.get("path", "")
        if name and path:
            by_name[name].append(path)

    dup_groups = []
    dup_map: dict[str, str] = {}
    orphan_set: set[str] = set()

    for name, paths in by_name.items():
        if len(paths) >= min_group_size:
            group = DuplicateGroup(name=name, paths=paths, count=len(paths))
            dup_groups.append(group)
            for p in paths:
                dup_map[p] = name
        else:
            for p in paths:
                orphan_set.add(p)

    return orphan_set, dup_groups


def run_finder(
    entries: list[dict[str, Any]],
    min_group_size: int = 2,
) -> FinderResult:
    """Executa finder completo — duplicatas + órfãos."""
    orphan_set, dup_groups = find_orphans(entries, min_group_size)

    duplicate_map = {}
    for g in dup_groups:
        for p in g.paths:
            duplicate_map[p] = g.name

    return FinderResult(
        duplicates=dup_groups,
        orphans=sorted(orphan_set),
        duplicate_map=duplicate_map,
        orphan_set=orphan_set,
    )
