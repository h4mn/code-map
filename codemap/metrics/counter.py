"""Counter — contagem de LOC por arquivo com heurísticas por linguagem."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

CommentStyle = Literal["line", "block_start", "block_end", "none"]

LANG_COMMENT_RULES: dict[str, dict] = {
    "delphi": {
        "line": r"//",
        "block_start": r"\{",
        "block_end": r"\}",
        "block_alt_start": r"\(\*",
        "block_alt_end": r"\*\)",
    },
    "python": {
        "line": r"#",
        "block_start": r'"""',
        "block_end": r'"""',
        "block_alt_start": r"'''",
        "block_alt_end": r"'''",
    },
    "javascript": {
        "line": r"//",
        "block_start": r"/\*",
        "block_end": r"\*/",
    },
    "typescript": {
        "line": r"//",
        "block_start": r"/\*",
        "block_end": r"\*/",
    },
    "java": {
        "line": r"//",
        "block_start": r"/\*",
        "block_end": r"\*/",
    },
    "kotlin": {
        "line": r"//",
        "block_start": r"/\*",
        "block_end": r"\*/",
    },
    "c": {
        "line": r"//",
        "block_start": r"/\*",
        "block_end": r"\*/",
    },
    "cpp": {
        "line": r"//",
        "block_start": r"/\*",
        "block_end": r"\*/",
    },
    "html": {
        "block_start": r"<!--",
        "block_end": r"-->",
    },
    "css": {
        "block_start": r"/\*",
        "block_end": r"\*/",
    },
    "scss": {
        "line": r"//",
        "block_start": r"/\*",
        "block_end": r"\*/",
    },
    "shell": {"line": r"#"},
    "batch": {"line": r"REM", "line_ci": True},
    "powershell": {"line": r"#"},
    "yaml": {"line": r"#"},
    "toml": {"line": r"#"},
    "markdown": {},
    "text": {},
    "sql": {
        "line": r"--",
        "block_start": r"/\*",
        "block_end": r"\*/",
    },
}


@dataclass
class LocResult:
    loc_total: int
    loc_code: int
    loc_comment: int
    loc_blank: int


def _get_lang_for_ext(ext: str) -> str | None:
    ext = ext.lower()
    if not ext.startswith("."):
        ext = "." + ext
    from codemap.dirmap.classifier import DEFAULT_MAP
    lang = DEFAULT_MAP.get(ext, "unknown")
    return lang if lang in LANG_COMMENT_RULES else None


def count_loc(filepath: str | Path, language: str | None = None) -> LocResult | None:
    if language is None:
        ext = Path(filepath).suffix
        language = _get_lang_for_ext(ext)
        if language is None:
            return None

    rules = LANG_COMMENT_RULES.get(language)
    if rules is None:
        return None

    try:
        text = Path(filepath).read_text(encoding="utf-8", errors="replace")
    except (OSError, PermissionError):
        return None

    lines = text.splitlines()
    loc_total = len(lines)
    loc_blank = 0
    loc_comment = 0
    loc_code = 0

    in_block = False
    block_end_re = None
    line_re = _build_line_re(rules)
    block_start_re = _build_block_start_re(rules)
    block_alt_start_re = _build_alt_block_start_re(rules)
    line_ci = rules.get("line_ci", False)

    for raw_line in lines:
        stripped = raw_line.strip()

        if not stripped:
            loc_blank += 1
            continue

        if in_block:
            loc_comment += 1
            if block_end_re and block_end_re.search(stripped):
                in_block = False
                block_end_re = None
            continue

        # Check block comments
        if block_start_re and block_start_re.search(stripped):
            loc_comment += 1
            block_end_re = re.compile(rules["block_end"])
            if block_end_re.search(stripped):
                block_end_re = None
            else:
                in_block = True
            continue

        if block_alt_start_re and block_alt_start_re.search(stripped):
            loc_comment += 1
            block_end_re = re.compile(rules["block_alt_end"])
            if block_end_re.search(stripped):
                block_end_re = None
            else:
                in_block = True
            continue

        # Check line comments
        if line_re:
            if line_ci:
                if line_re.search(stripped.lower()):
                    loc_comment += 1
                    continue
            else:
                if line_re.search(stripped):
                    loc_comment += 1
                    continue

        loc_code += 1

    return LocResult(
        loc_total=loc_total,
        loc_code=loc_code,
        loc_comment=loc_comment,
        loc_blank=loc_blank,
    )


def _build_line_re(rules: dict) -> re.Pattern | None:
    if "line" not in rules:
        return None
    pattern = rules["line"]
    return re.compile(rf"^\s*{pattern}")


def _build_block_start_re(rules: dict) -> re.Pattern | None:
    if "block_start" not in rules:
        return None
    return re.compile(rf"^\s*{rules['block_start']}")


def _build_alt_block_start_re(rules: dict) -> re.Pattern | None:
    if "block_alt_start" not in rules:
        return None
    return re.compile(rf"^\s*{rules['block_alt_start']}")
