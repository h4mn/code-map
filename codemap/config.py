"""Config centralizada — merge de 4 camadas."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class DirmapConfig:
    ignore_files: list[str] = field(default_factory=lambda: [".gitignore"])
    extra_dirs: list[str] = field(default_factory=lambda: ["__pycache__", ".pytest_cache", "node_modules", ".git", ".svn", "*.dcu"])
    format: str = "json"
    indent: int = 2
    follow_symlinks: bool = False
    max_depth: int | None = None
    custom_extensions: dict[str, str] = field(default_factory=dict)
    metrics_enabled: bool = True
    metrics_languages: list[str] = field(default_factory=list)
    duplicates_min_group_size: int = 2
    orphans_heuristic: bool = True
    delphi_search_paths: list[str] = field(default_factory=list)
    python_paths: list[str] = field(default_factory=list)
    js_aliases: dict[str, str] = field(default_factory=dict)

    @classmethod
    def load(cls, cli_overrides: dict[str, Any] | None = None) -> DirmapConfig:
        """Merge: defaults → global → projeto → CLI flags."""
        config = cls()

        global_path = Path.home() / ".codemap" / "config.yml"
        if global_path.exists():
            config = cls._merge(config, cls._read_yaml(global_path))

        project_path = Path.cwd() / ".codemap.yml"
        if project_path.exists():
            config = cls._merge(config, cls._read_yaml(project_path))

        if cli_overrides:
            config = cls._merge(config, cli_overrides)

        return config

    @classmethod
    def _read_yaml(cls, path: Path) -> dict:
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                return data if isinstance(data, dict) else {}
        except (yaml.YAMLError, OSError):
            return {}

    @classmethod
    def _merge(cls, base: DirmapConfig, override: dict) -> DirmapConfig:
        """Merge override em base. Ignora chaves desconhecidas."""
        dirmap = override.get("dirmap", override)

        # ignore
        ignore = dirmap.get("ignore", {})
        if isinstance(ignore, dict):
            if "files" in ignore:
                base.ignore_files = ignore["files"]
            if "extra_dirs" in ignore:
                base.extra_dirs = ignore["extra_dirs"]

        # output
        output = dirmap.get("output", {})
        if isinstance(output, dict):
            if "format" in output:
                base.format = output["format"]
            if "indent" in output:
                base.indent = output["indent"]

        # walker
        walker = dirmap.get("walker", {})
        if isinstance(walker, dict):
            if "follow_symlinks" in walker:
                base.follow_symlinks = walker["follow_symlinks"]
            if "max_depth" in walker:
                base.max_depth = walker["max_depth"]

        # classifier
        classifier = dirmap.get("classifier", {})
        if isinstance(classifier, dict):
            if "custom_extensions" in classifier:
                base.custom_extensions = classifier["custom_extensions"]

        # CLI-level overrides (top-level keys that match fields)
        for key in ("follow_symlinks", "max_depth", "indent", "format"):
            if key in override:
                setattr(base, key, override[key])

        # metrics
        metrics = dirmap.get("metrics", {})
        if isinstance(metrics, dict):
            if "enabled" in metrics:
                base.metrics_enabled = metrics["enabled"]
            if "loc" in metrics and isinstance(metrics["loc"], dict):
                langs = metrics["loc"].get("languages")
                if langs:
                    base.metrics_languages = langs
            if "duplicates" in metrics and isinstance(metrics["duplicates"], dict):
                if "min_group_size" in metrics["duplicates"]:
                    base.duplicates_min_group_size = metrics["duplicates"]["min_group_size"]
            if "orphans" in metrics and isinstance(metrics["orphans"], dict):
                if "heuristic" in metrics["orphans"]:
                    base.orphans_heuristic = metrics["orphans"]["heuristic"]

        # uses
        uses = dirmap.get("uses", {})
        if isinstance(uses, dict):
            if "delphi_search_paths" in uses:
                base.delphi_search_paths = uses["delphi_search_paths"]
            if "python_paths" in uses:
                base.python_paths = uses["python_paths"]
            if "js_aliases" in uses:
                base.js_aliases = uses["js_aliases"]

        return base
