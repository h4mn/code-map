"""Classifier — mapeia extensão de arquivo para linguagem."""

from __future__ import annotations

DEFAULT_MAP: dict[str, str] = {
    # Delphi
    ".pas": "delphi",
    ".dpr": "delphi",
    ".dpk": "delphi",
    ".dfm": "delphi-form",
    ".inc": "delphi",
    # Python
    ".py": "python",
    ".pyw": "python",
    ".pyi": "python",
    # JavaScript / TypeScript
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".mjs": "javascript",
    ".cjs": "javascript",
    # Java / JVM
    ".java": "java",
    ".kt": "kotlin",
    ".kts": "kotlin",
    ".scala": "scala",
    # C / C++
    ".c": "c",
    ".h": "c",
    ".cpp": "cpp",
    ".hpp": "cpp",
    ".cc": "cpp",
    # Web
    ".html": "html",
    ".htm": "html",
    ".css": "css",
    ".scss": "scss",
    # Data / Config
    ".json": "json",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".toml": "toml",
    ".xml": "xml",
    # Docs
    ".md": "markdown",
    ".rst": "restructuredtext",
    ".txt": "text",
    # Shell
    ".sh": "shell",
    ".bash": "shell",
    ".bat": "batch",
    ".cmd": "batch",
    ".ps1": "powershell",
}


def classify(extension: str, custom_extensions: dict[str, str] | None = None) -> str:
    """Retorna a linguagem de uma extensão. 'unknown' se não reconhecida."""
    ext = _normalize(extension)
    if not ext:
        return "unknown"

    if custom_extensions:
        custom_normalized = {k.lstrip("."): v for k, v in custom_extensions.items()}
        name = ext.lstrip(".")
        if name in custom_normalized:
            return custom_normalized[name]

    return DEFAULT_MAP.get(ext, "unknown")


def _normalize(extension: str) -> str:
    """Normaliza extensão: garante ponto inicial, lowercase."""
    ext = extension.strip().lower()
    if ext and not ext.startswith("."):
        ext = "." + ext
    return ext
