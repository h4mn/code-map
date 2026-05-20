"""Entrypoint CLI do CodeMap."""

from __future__ import annotations

import argparse
import sys

from codemap.health import check_dependencies
from codemap.registry import CommandRegistry

import codemap.dirmap  # registra comandos dirmap e version
import codemap.metrics  # registra comando metrics
import codemap.uses     # registra comando uses

# Comandos que usam filepath de dirmap (podem omitir se config tiver default_dirmap)
_DIRMAP_COMMANDS = {"query", "repl", "lookup", "uses", "metrics"}


def _resolve_filepath(kwargs: dict, command: str | None) -> dict:
    """Se filepath for None, tenta resolver via default_dirmap do config."""
    if kwargs.get("filepath") is not None:
        return kwargs
    if command not in _DIRMAP_COMMANDS:
        return kwargs
    from codemap.config import DirmapConfig
    config = DirmapConfig.load()
    if config.default_dirmap:
        kwargs["filepath"] = config.default_dirmap
    return kwargs


def main():
    check_dependencies()
    parser = argparse.ArgumentParser(
        prog="codemap",
        description="CodeMap — Indexador de codebases multi-linguagem",
    )
    CommandRegistry.add_to_parser(parser)

    args = parser.parse_args()

    if not args.command:
        print(CommandRegistry.help_text())
        sys.exit(0)

    cmd = CommandRegistry.get(args.command)
    if cmd is None:
        print(f"Comando desconhecido: {args.command}", file=sys.stderr)
        sys.exit(1)

    kwargs = vars(args)
    command_name = kwargs.pop("command", None)
    # Mapeia nomes reservados de volta (type -> type para query)
    if "filter_type" in kwargs:
        kwargs["type"] = kwargs.pop("filter_type")

    kwargs = _resolve_filepath(kwargs, command_name)

    try:
        cmd.fn(**kwargs)
    except (FileNotFoundError, KeyboardInterrupt):
        raise
    except Exception as e:
        print(f"Erro: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
