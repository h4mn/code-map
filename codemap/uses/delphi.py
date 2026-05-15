"""Parser Delphi — extração de cláusulas uses."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, eq=True)
class ImportRef:
    name: str
    section: str  # "interface", "implementation", "program"
    line: int = 0


# Regex: captura conteúdo entre "uses" e ";", lidando com multi-linha
_USES_RE = re.compile(
    r"\buses\b\s+(.*?)\s*;",
    re.DOTALL | re.IGNORECASE,
)

# Regex: captura "in 'path'" para remover
_IN_PATH_RE = re.compile(
    r"\s+in\s+'[^']*'",
    re.IGNORECASE,
)

# Regex: remove comentários de bloco { ... }
_BLOCK_COMMENT_RE = re.compile(
    r"\{[^}]*\}",
    re.DOTALL,
)

# Regex: remove comentários de linha //
_LINE_COMMENT_RE = re.compile(
    r"//[^\n]*",
)


def _extract_names(uses_block: str) -> list[str]:
    """Extrai nomes de units de um bloco uses, removendo 'in path' e comentários."""
    cleaned = _BLOCK_COMMENT_RE.sub("", uses_block)
    cleaned = _LINE_COMMENT_RE.sub("", cleaned)
    cleaned = _IN_PATH_RE.sub("", cleaned)
    parts = cleaned.split(",")
    names = []
    for p in parts:
        name = p.strip()
        if name:
            names.append(name)
    return names


def parse_delphi_uses(filepath: Path) -> list[ImportRef]:
    """Extrai cláusulas uses de um arquivo Delphi (.pas, .dpr, .lpr)."""
    try:
        content = filepath.read_text(encoding="utf-8", errors="replace")
    except (OSError, IOError):
        return []

    if not content.strip():
        return []

    ext = filepath.suffix.lower()
    is_program = ext in (".dpr", ".lpr")
    refs: list[ImportRef] = []

    if is_program:
        # .dpr/.lpr: um único uses no nível raiz
        for m in _USES_RE.finditer(content):
            block = m.group(1)
            line_no = content[:m.start()].count("\n") + 1
            for name in _extract_names(block):
                refs.append(ImportRef(name=name, section="program", line=line_no))
    else:
        # .pas: divide em interface e implementation
        lower = content.lower()
        iface_pos = lower.find("interface")
        impl_pos = lower.find("implementation")

        if iface_pos == -1:
            return refs

        iface_end = impl_pos if impl_pos != -1 else len(content)

        # Interface section
        iface_content = content[iface_pos:iface_end]
        for m in _USES_RE.finditer(iface_content):
            block = m.group(1)
            line_no = content[:iface_pos + m.start()].count("\n") + 1
            for name in _extract_names(block):
                refs.append(ImportRef(name=name, section="interface", line=line_no))

        # Implementation section
        if impl_pos != -1:
            impl_content = content[impl_pos:]
            for m in _USES_RE.finditer(impl_content):
                block = m.group(1)
                line_no = content[:impl_pos + m.start()].count("\n") + 1
                for name in _extract_names(block):
                    refs.append(ImportRef(name=name, section="implementation", line=line_no))

    return refs
