"""Enricher — enriquece dirmap.json com métricas."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from codemap.config import DirmapConfig
from codemap.metrics.aggregator import aggregate
from codemap.metrics.counter import count_loc
from codemap.metrics.finder import run_finder


def enrich_dirmap(
    data: dict[str, Any],
    root: str | Path | None = None,
    config: DirmapConfig | None = None,
) -> dict[str, Any]:
    """Enriquece dirmap JSON com métricas. Retorna novo dict (não muta original)."""
    if config is None:
        config = DirmapConfig()

    if not config.metrics_enabled:
        return data

    tree = data.get("tree", [])
    root_path = str(root or data.get("meta", {}).get("root", "."))

    # Conta LOC por arquivo
    file_metrics = []
    for entry in tree:
        if entry.get("type") != "file":
            continue
        ext = entry.get("extension", "")
        path = Path(root_path) / entry["path"]
        loc = count_loc(path, _language_from_entry(entry, config))
        file_metrics.append({
            "path": entry["path"],
            "language": entry.get("language", "unknown"),
            "loc_result": loc,
        })

    # Agrega por diretório
    dir_metrics = aggregate(file_metrics)

    # Finder — duplicatas e órfãos
    finder_entries = []
    for entry in tree:
        if entry.get("type") == "file":
            path = entry["path"]
            parts = path.replace("\\", "/").split("/")
            finder_entries.append({
                "type": "file",
                "name": parts[-1],
                "path": path,
            })

    finder_result = run_finder(finder_entries, config.duplicates_min_group_size)

    # Enriquece tree
    enriched_tree = []
    loc_by_path = {f["path"]: f["loc_result"] for f in file_metrics}

    for entry in tree:
        new_entry = dict(entry)
        path = entry.get("path", "")

        if entry.get("type") == "file":
            loc = loc_by_path.get(path)
            new_entry["metrics"] = {
                "loc_total": loc.loc_total,
                "loc_code": loc.loc_code,
                "loc_comment": loc.loc_comment,
                "loc_blank": loc.loc_blank,
            } if loc else None

            if path in finder_result.duplicate_map:
                new_entry["duplicate_candidate"] = True
                new_entry["duplicate_group"] = finder_result.duplicate_map[path]

            if path in finder_result.orphan_set:
                new_entry["orphan_candidate"] = True

        elif entry.get("type") == "dir":
            dm = dir_metrics.get(path)
            if dm:
                new_entry["metrics"] = {
                    "loc_total": dm.loc_total,
                    "loc_code": dm.loc_code,
                    "loc_comment": dm.loc_comment,
                    "loc_blank": dm.loc_blank,
                    "file_count": dm.file_count,
                    "language_diversity": dm.language_diversity,
                    "code_comment_ratio": dm.code_comment_ratio,
                }

        enriched_tree.append(new_entry)

    # Monta resultado
    result = dict(data)
    result["tree"] = enriched_tree
    result["metrics_summary"] = {
        "duplicate_groups": len(finder_result.duplicates),
        "orphan_count": len(finder_result.orphans),
    }

    return result


def run_enrich(
    filepath: str,
    output: str | None = None,
    stdout: bool = False,
    config: DirmapConfig | None = None,
):
    """Ponto de entrada do comando metrics."""
    if config is None:
        config = DirmapConfig()

    src = Path(filepath)
    if not src.exists():
        print(f"Arquivo não encontrado: {filepath}", file=sys.stderr)
        sys.exit(1)

    data = json.loads(src.read_text(encoding="utf-8"))
    root = data.get("meta", {}).get("root")
    enriched = enrich_dirmap(data, root, config)
    json_str = json.dumps(enriched, indent=config.indent, ensure_ascii=False)

    if stdout:
        print(json_str)
    elif output:
        Path(output).write_text(json_str, encoding="utf-8")
    else:
        src.write_text(json_str, encoding="utf-8")


def _language_from_entry(entry: dict, config: DirmapConfig) -> str | None:
    lang = entry.get("language", "unknown")
    if config.metrics_languages and lang not in config.metrics_languages:
        return None
    return lang if lang != "unknown" else None
