"""Serializer — converte resultado do walker em JSON."""

from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from codemap import __version__
from codemap.config import DirmapConfig
from codemap.dirmap.classifier import classify
from codemap.dirmap.walker import WalkResult, walk


def serialize(
    result: WalkResult,
    root: str,
    config: DirmapConfig | None = None,
) -> dict:
    """Monta o dict completo do dirmap JSON."""
    if config is None:
        config = DirmapConfig()

    root_path = Path(root)
    root_name = root_path.name

    # Classifica e enriquece as entries
    tree = []
    by_ext: Counter = Counter()
    by_lang: Counter = Counter()
    total_size = 0
    file_count = 0

    for entry in result.entries:
        if entry.type == "file":
            lang = classify(entry.extension, config.custom_extensions)
            tree.append({
                "path": entry.path,
                "type": "file",
                "extension": entry.extension,
                "language": lang,
                "size_bytes": entry.size_bytes,
            })
            by_ext[entry.extension] += 1
            by_lang[lang] += 1
            total_size += entry.size_bytes
            file_count += 1
        else:
            tree.append({
                "path": entry.path,
                "type": "dir",
            })

    return {
        "meta": {
            "tool": "codemap",
            "command": "dirmap",
            "version": __version__,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "root": str(root),
            "root_name": root_name,
        },
        "errors": result.errors,
        "summary": {
            "total_files": file_count,
            "total_dirs": result.total_dirs,
            "total_size_bytes": total_size,
            "by_extension": dict(by_ext),
            "by_language": dict(by_lang),
        },
        "tree": tree,
    }


def run_dirmap(
    root: str,
    output: str = "dirmap.json",
    stdout: bool = False,
    with_metrics: bool = False,
    with_uses: bool = False,
    **cli_overrides,
):
    """Ponto de entrada do comando dirmap."""
    config = DirmapConfig.load(cli_overrides=cli_overrides or None)
    result = walk(root, config)
    data = serialize(result, root, config)

    if with_metrics:
        from codemap.metrics.enricher import enrich_dirmap
        data = enrich_dirmap(data, root, config)

    if with_uses:
        print("Extraindo dependências (uses)...", file=sys.stderr)
        from codemap.uses.enricher import enrich_dirmap_with_uses
        data = enrich_dirmap_with_uses(data, root, config)

    json_str = json.dumps(data, indent=config.indent, ensure_ascii=False)

    if stdout:
        print(json_str)
    else:
        out_path = Path(output)
        out_path.write_text(json_str, encoding="utf-8")
