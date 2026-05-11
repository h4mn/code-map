"""Validação de dependências — fail fast no entrypoint."""

from __future__ import annotations

import sys

REQUIRED: dict[str, tuple[str, str]] = {
    "pyyaml": ("yaml", "PyYAML é necessário. Instale: pip install pyyaml"),
}


def check_dependencies() -> None:
    """Valida dependências obrigatórias. Falha rápido com mensagem clara."""
    missing: list[str] = []
    for package, (import_name, hint) in REQUIRED.items():
        try:
            __import__(import_name)
        except ImportError:
            missing.append(f"  - {package}: {hint}")
    if missing:
        print(f"Dependências faltando:\n" + "\n".join(missing), file=sys.stderr)
        sys.exit(1)
