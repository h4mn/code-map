"""Resolver — converte nomes de import em caminhos resolved_path usando dirmap tree."""

from __future__ import annotations

import sys
from pathlib import PurePosixPath
from typing import Any

from codemap.config import DirmapConfig

# ---------------------------------------------------------------------------
# Stdlib detection
# ---------------------------------------------------------------------------

_PYTHON_STDLIB: set[str] = {
    "abc", "aifc", "argparse", "array", "ast", "asyncio", "atexit",
    "base64", "binascii", "bisect", "builtins", "bz2", "calendar",
    "cgi", "cmath", "cmd", "code", "codecs", "collections",
    "colorsys", "concurrent", "configparser", "contextlib", "contextvars",
    "copy", "copyreg", "cProfile", "csv", "ctypes", "dataclasses",
    "datetime", "dbm", "decimal", "difflib", "dis", "doctest",
    "email", "encodings", "enum", "errno", "faulthandler", "fcntl",
    "fileinput", "fnmatch", "fractions", "ftplib", "functools", "gc",
    "getopt", "getpass", "gettext", "glob", "graphlib", "gzip",
    "hashlib", "heapq", "hmac", "html", "http", "idlelib",
    "imaplib", "importlib", "inspect", "io", "ipaddress",
    "itertools", "json", "keyword", "linecache", "locale",
    "logging", "lzma", "mailbox", "marshal", "math", "mimetypes",
    "mmap", "multiprocessing", "netrc", "numbers", "operator",
    "optparse", "os", "pathlib", "pdb", "pickle", "pkgutil",
    "platform", "plistlib", "poplib", "posix", "posixpath",
    "pprint", "profile", "pstats", "pty", "pwd", "py_compile",
    "pyclbr", "pydoc", "queue", "quopri", "random", "re",
    "readline", "reprlib", "resource", "rlcompleter", "runpy",
    "sched", "secrets", "select", "selectors", "shelve", "shlex",
    "shutil", "signal", "site", "smtplib", "socket", "socketserver",
    "sqlite3", "ssl", "stat", "statistics", "string", "struct",
    "subprocess", "symtable", "sys", "sysconfig", "syslog",
    "tabnanny", "tarfile", "tempfile", "test", "textwrap",
    "threading", "time", "timeit", "token", "tokenize", "tomllib",
    "trace", "traceback", "tracemalloc", "turtle", "turtledemo",
    "types", "typing", "unicodedata", "unittest", "urllib",
    "uu", "uuid", "venv", "warnings", "wave", "weakref",
    "webbrowser", "winreg", "winsound", "wsgiref", "xdrlib",
    "xml", "xmlrpc", "zipapp", "zipfile", "zipimport", "zlib",
    "zoneinfo", "_thread",
}

# Python 3.10+ tem sys.stdlib_module_names
if hasattr(sys, "stdlib_module_names"):
    _PYTHON_STDLIB = _PYTHON_STDLIB | sys.stdlib_module_names

# Known Delphi RTL/VCL units (subset of common ones)
_DELPHI_STDLIB: set[str] = {
    "SysUtils", "Classes", "Windows", "Messages", "Graphics",
    "Controls", "Forms", "Dialogs", "StdCtrls", "ExtCtrls",
    "Math", "System", "SysInit", "Types", "Variants",
    "ActiveX", "ComObj", "ComCtrls", "DateUtils", "FileCtrl",
    "HTTPApp", "IniFiles", "Mask", "Menus", "Registry",
    "ShellAPI", "StrUtils", "SyncObjs", "Threads",
}

# ---------------------------------------------------------------------------
# Index builder
# ---------------------------------------------------------------------------


def _build_basename_index(tree_entries: list[dict]) -> dict[str, list[str]]:
    """Constrói índice basename (sem ext) → lista de paths."""
    index: dict[str, list[str]] = {}
    for entry in tree_entries:
        if entry.get("type") != "file":
            continue
        path = entry.get("path", "")
        if not path:
            continue
        # basename sem extensão
        basename = PurePosixPath(path).stem
        index.setdefault(basename, []).append(path)
    return index


def _build_path_set(tree_entries: list[dict]) -> set[str]:
    """Constrói set de paths para lookup direto."""
    return {
        entry.get("path", "")
        for entry in tree_entries
        if entry.get("type") == "file" and entry.get("path")
    }


# ---------------------------------------------------------------------------
# Language detection helper
# ---------------------------------------------------------------------------


def _detect_language(source_file: str, tree_entries: list[dict]) -> str:
    """Detecta linguagem do source_file consultando o tree."""
    for entry in tree_entries:
        if entry.get("path") == source_file:
            return entry.get("language", "").lower()
    # Fallback: extensão do arquivo
    ext = PurePosixPath(source_file).suffix.lower()
    if ext in (".pas", ".dpr", ".lpr"):
        return "delphi"
    if ext == ".py":
        return "python"
    if ext in (".js", ".jsx", ".ts", ".tsx"):
        return "typescript"  # javascript também usa mesma lógica
    return ""


# ---------------------------------------------------------------------------
# Delphi resolver
# ---------------------------------------------------------------------------


def _resolve_delphi(
    name: str,
    source_file: str,
    basename_index: dict[str, list[str]],
    config: DirmapConfig,
) -> str | None:
    """Resolve unit Delphi por nome, consultando search paths."""
    # 1. Busca direta no índice (basename match)
    candidates = basename_index.get(name, [])
    if len(candidates) == 1:
        return candidates[0]
    if len(candidates) > 1:
        # Tenta desambiguar com delphi_search_paths
        for prefix in config.delphi_search_paths:
            prefix_norm = prefix.rstrip("/") + "/"
            for c in candidates:
                if c.startswith(prefix_norm):
                    return c
        # Retorna o primeiro candidato (melhor esforço)
        return candidates[0]

    # 2. Busca com search_path como prefixo de path
    for prefix in config.delphi_search_paths:
        candidate = f"{prefix.rstrip('/')}/{name}.pas"
        # Verificar se esse path existe no índice (buscar qualquer ext)
        for bn, paths in basename_index.items():
            if bn == name:
                for p in paths:
                    p_dir = str(PurePosixPath(p).parent).rstrip("/") + "/"
                    if prefix.rstrip("/") in p or p.startswith(prefix.rstrip("/") + "/"):
                        return p
        # Tentativa direta
        for bn, paths in basename_index.items():
            if bn == name:
                for p in paths:
                    return p

    return None


# ---------------------------------------------------------------------------
# Python resolver
# ---------------------------------------------------------------------------


def _resolve_python(
    imp: dict,
    source_file: str,
    path_set: set[str],
    config: DirmapConfig,
) -> str | None:
    """Resolve import Python (absoluto ou relativo)."""
    name: str = imp.get("name", "")

    # Relative import: name começa com "." (ex: ".utils")
    if name.startswith("."):
        level = name.count(".") - len(name.lstrip("."))
        if level == 0:
            level = name.count(".")
        # Remove dots para obter o módulo
        module_part = name.lstrip(".")
        # Diretório pai do source_file
        parent = str(PurePosixPath(source_file).parent)
        if parent == ".":
            parent = ""
        # Para level=1, resolve a partir do mesmo diretório
        if level == 1:
            if module_part:
                candidate = f"{parent}/{module_part.replace('.', '/')}.py"
            else:
                # from . import X — resolve ao __init__.py do pacote
                candidate = f"{parent}/__init__.py"
        else:
            # level > 1: subir level-1 diretórios
            parts = parent.split("/")
            go_up = level - 1
            if go_up < len(parts):
                base = "/".join(parts[:-go_up]) if go_up > 0 else parent
            else:
                base = ""
            if module_part:
                candidate = f"{base}/{module_part.replace('.', '/')}.py"
            else:
                candidate = f"{base}/__init__.py"

        if candidate.startswith("/"):
            candidate = candidate[1:]
        if candidate in path_set:
            return candidate
        # Tentar como pacote (__init__.py)
        pkg_candidate = candidate.replace(".py", "/__init__.py")
        if pkg_candidate in path_set:
            return pkg_candidate
        return None

    # Absolute import: "codemap.config" → "codemap/config.py"
    dotted = name.replace(".", "/")

    # Tentar search paths primeiro (se configurados)
    for prefix in config.python_paths:
        prefix_norm = prefix.rstrip("/") + "/"
        candidate = f"{prefix_norm}{dotted}.py"
        if candidate in path_set:
            return candidate
        candidate = f"{prefix_norm}{dotted}/__init__.py"
        if candidate in path_set:
            return candidate

    # Tentar como módulo .py
    candidate = f"{dotted}.py"
    if candidate in path_set:
        return candidate

    # Tentar como pacote (__init__.py)
    candidate = f"{dotted}/__init__.py"
    if candidate in path_set:
        return candidate

    return None


# ---------------------------------------------------------------------------
# JS/TS resolver
# ---------------------------------------------------------------------------

_JS_EXTENSIONS = [".tsx", ".ts", ".jsx", ".js"]
_JS_INDEX_EXTENSIONS = ["/index.tsx", "/index.ts", "/index.jsx", "/index.js"]


def _resolve_js(
    name: str,
    source_file: str,
    path_set: set[str],
    config: DirmapConfig,
) -> str | None:
    """Resolve import JS/TS (relativo, alias ou bare)."""
    # 1. Alias resolution
    for alias_pattern, alias_target in config.js_aliases.items():
        if _matches_alias(name, alias_pattern):
            resolved_alias = _apply_alias(name, alias_pattern, alias_target)
            # Tentar resolver o resultado como relativo à raiz
            result = _try_js_path(resolved_alias, "", path_set)
            if result:
                return result

    # 2. Relative import (./  ou  ../)
    if name.startswith("./") or name.startswith("../"):
        parent = str(PurePosixPath(source_file).parent)
        if parent == ".":
            parent = ""
        result = _try_js_path(name, parent, path_set)
        if result:
            return result

    # 3. Bare import (não-relativo, sem alias) — third-party ou stdlib
    return None


def _matches_alias(name: str, alias_pattern: str) -> bool:
    """Verifica se name match um alias pattern como '@/*'."""
    if alias_pattern.endswith("*"):
        prefix = alias_pattern[:-1]  # "@/"
        return name.startswith(prefix)
    return name == alias_pattern


def _apply_alias(name: str, alias_pattern: str, alias_target: str) -> str:
    """Aplica alias: '@/utils/helpers' com '@/*'→'src/*' → 'src/utils/helpers'."""
    if alias_pattern.endswith("*"):
        prefix = alias_pattern[:-1]
        suffix = name[len(prefix):]
        target_prefix = alias_target[:-1] if alias_target.endswith("*") else alias_target
        return target_prefix + suffix
    return alias_target


def _try_js_path(name: str, base: str, path_set: set[str]) -> str | None:
    """Tenta resolver um path JS com fallbacks de extensão."""
    # Normalizar: se name começa com ./, remover
    clean = name
    if clean.startswith("./"):
        clean = clean[2:]

    # Construir path completo
    if base:
        full = f"{base}/{clean}"
    else:
        full = clean

    # Normalizar ../
    parts = full.split("/")
    normalized: list[str] = []
    for part in parts:
        if part == "..":
            if normalized:
                normalized.pop()
        elif part and part != ".":
            normalized.append(part)
    full = "/".join(normalized)

    # Tentar extensões diretas
    for ext in _JS_EXTENSIONS:
        candidate = full + ext
        if candidate in path_set:
            return candidate

    # Tentar index dentro de diretório
    for idx in _JS_INDEX_EXTENSIONS:
        candidate = full + idx
        if candidate in path_set:
            return candidate

    return None


# ---------------------------------------------------------------------------
# Category detection
# ---------------------------------------------------------------------------


def _categorize_python(name: str) -> str:
    """Categoriza import Python: stdlib, third-party ou unknown."""
    top_module = name.lstrip(".").split(".")[0]
    if top_module in _PYTHON_STDLIB:
        return "stdlib"
    return "third-party"


def _categorize_delphi(name: str) -> str:
    """Categoriza unit Delphi: stdlib (RTL/VCL) ou unknown."""
    if name in _DELPHI_STDLIB:
        return "stdlib"
    return "unknown"


# ---------------------------------------------------------------------------
# Main resolver
# ---------------------------------------------------------------------------


def resolve_imports(
    imports: list[dict],
    source_file: str,
    tree_entries: list[dict],
    config: DirmapConfig,
) -> list[dict]:
    """Resolve imports de um arquivo source contra o dirmap tree.

    Cada dict retém os campos originais e adiciona:
        - resolved_path: str | None
        - unresolved: bool
        - category: "stdlib" | "third-party" | "unknown" | ""
    """
    if not imports:
        return []

    basename_index = _build_basename_index(tree_entries)
    path_set = _build_path_set(tree_entries)
    language = _detect_language(source_file, tree_entries)

    results: list[dict] = []

    for imp in imports:
        name = imp.get("name", "")
        resolved_path: str | None = None
        category = ""

        if language == "delphi":
            resolved_path = _resolve_delphi(name, source_file, basename_index, config)
            if resolved_path is None:
                category = _categorize_delphi(name)

        elif language == "python":
            resolved_path = _resolve_python(imp, source_file, path_set, config)
            if resolved_path is None:
                category = _categorize_python(name)

        elif language in ("typescript", "javascript"):
            resolved_path = _resolve_js(name, source_file, path_set, config)
            if resolved_path is None:
                # Bare imports em JS são tipicamente third-party
                if not name.startswith("./") and not name.startswith("../"):
                    category = "third-party"
                else:
                    category = "unknown"

        unresolved = resolved_path is None

        result = {
            **imp,
            "resolved_path": resolved_path,
            "unresolved": unresolved,
            "category": category,
        }
        results.append(result)

    return results
