"""Aggregator — agrega métricas por diretório."""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Any

from codemap.metrics.counter import LocResult


@dataclass
class DirMetrics:
    loc_total: int = 0
    loc_code: int = 0
    loc_comment: int = 0
    loc_blank: int = 0
    file_count: dict[str, int] = field(default_factory=lambda: {})
    language_diversity: int = 0
    code_comment_ratio: float | None = None


def aggregate(
    file_metrics: list[dict[str, Any]],
) -> dict[str, DirMetrics]:
    """Agrega métricas por diretório.

    file_metrics: lista de dicts com keys 'path', 'language', 'loc_result' (LocResult|None).
    Retorna dict path -> DirMetrics.
    """
    dir_data: dict[str, dict] = defaultdict(lambda: {
        "loc_total": 0, "loc_code": 0, "loc_comment": 0, "loc_blank": 0,
        "file_count": Counter(),
    })

    for item in file_metrics:
        path = item["path"]
        lang = item.get("language", "unknown")
        loc: LocResult | None = item.get("loc_result")

        parts = path.replace("\\", "/").split("/")
        for i in range(1, len(parts)):
            dir_path = "/".join(parts[:i])
            dir_data[dir_path]["file_count"][lang] += 1
            if loc:
                dir_data[dir_path]["loc_total"] += loc.loc_total
                dir_data[dir_path]["loc_code"] += loc.loc_code
                dir_data[dir_path]["loc_comment"] += loc.loc_comment
                dir_data[dir_path]["loc_blank"] += loc.loc_blank

    result: dict[str, DirMetrics] = {}
    for dir_path, data in dir_data.items():
        dm = DirMetrics(
            loc_total=data["loc_total"],
            loc_code=data["loc_code"],
            loc_comment=data["loc_comment"],
            loc_blank=data["loc_blank"],
            file_count=dict(data["file_count"]),
            language_diversity=len(data["file_count"]),
        )
        if dm.loc_comment > 0:
            dm.code_comment_ratio = round(dm.loc_code / dm.loc_comment, 2)
        result[dir_path] = dm

    return result
