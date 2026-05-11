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
    extra_dirs: list[str] = field(default_factory=lambda: ["__pycache__", ".pytest_cache", "node_modules", ".git"])
    format: str = "json"
    indent: int = 2
    follow_symlinks: bool = False
    max_depth: int | None = None
    custom_extensions: dict[str, str] = field(default_factory=dict)

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

        return base
