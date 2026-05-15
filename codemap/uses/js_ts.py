"""Parser JS/TS — extração de imports via regex."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, eq=True)
class JsImportRef:
    source: str
    section: str  # "import", "require", "dynamic"
    line: int = 0


# ES module: import ... from 'source' ou import 'source'
_ES_IMPORT_RE = re.compile(
    r"""(?:import|export)\s+.*?\s+from\s+['"]([^'"]+)['"]"""
    r"""|"""
    r"""(?:import|export)\s+['"]([^'"]+)['"]""",
)

# CommonJS: require('source') ou require("source")
_REQUIRE_RE = re.compile(
    r"""require\s*\(\s*['"]([^'"]+)['"]\s*\)""",
)

# Dynamic import: import('source')
_DYNAMIC_RE = re.compile(
    r"""import\s*\(\s*['"]([^'"]+)['"]\s*\)""",
)


def parse_js_ts_imports(filepath: Path) -> list[JsImportRef]:
    """Extrai imports de um arquivo JS/TS (.js, .jsx, .ts, .tsx)."""
    try:
        content = filepath.read_text(encoding="utf-8", errors="replace")
    except (OSError, IOError):
        return []

    if not content.strip():
        return []

    refs: list[JsImportRef] = []
    lines = content.split("\n")

    # Acompanhar fontes já registradas por linha para evitar duplicatas
    # (ex: import React, { useState } from 'react' gera 1 ref, nao 2)
    seen: set[tuple[str, int]] = set()

    for line_no, line in enumerate(lines, start=1):
        # Strip line comments for cleaner matching
        stripped = line.split("//")[0] if "//" in line else line

        # Dynamic import (check first, before ES import)
        for m in _DYNAMIC_RE.finditer(stripped):
            source = m.group(1)
            key = (source, line_no)
            if key not in seen:
                seen.add(key)
                refs.append(JsImportRef(source=source, section="dynamic", line=line_no))

        # ES module import / export from
        for m in _ES_IMPORT_RE.finditer(stripped):
            source = m.group(1) or m.group(2)
            if source is None:
                continue
            key = (source, line_no)
            if key not in seen:
                seen.add(key)
                refs.append(JsImportRef(source=source, section="import", line=line_no))

        # CommonJS require
        for m in _REQUIRE_RE.finditer(stripped):
            source = m.group(1)
            key = (source, line_no)
            if key not in seen:
                seen.add(key)
                refs.append(JsImportRef(source=source, section="require", line=line_no))

    return refs
