"""Registry de comandos com auto-descoberta e help dinâmico."""

from __future__ import annotations

import argparse
import inspect
from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class CommandDef:
    name: str
    fn: Callable
    description: str
    category: str = "geral"
    args: dict = field(default_factory=dict)


class CommandRegistry:
    """Registry central — comandos se registram sozinhos via decorator."""

    _registry: dict[str, CommandDef] = {}

    @classmethod
    def register(cls, name: str, description: str, category: str = "geral"):
        """Decorator: @registry.register("dirmap", "Indexa estrutura física")"""
        def decorator(fn):
            if name in cls._registry:
                raise ValueError(
                    f"Comando '{name}' já registrado por "
                    f"{cls._registry[name].fn.__module__}"
                )
            sig = inspect.signature(fn)
            cls._registry[name] = CommandDef(
                name=name,
                fn=fn,
                description=description,
                category=category,
                args={p.name: p for p in sig.parameters.values() if p.name != "self"},
            )
            return fn
        return decorator

    @classmethod
    def get(cls, name: str) -> CommandDef | None:
        return cls._registry.get(name)

    @classmethod
    def all(cls) -> dict[str, CommandDef]:
        return dict(cls._registry)

    @classmethod
    def help_text(cls) -> str:
        lines = ["CodeMap — Indexador de codebases multi-linguagem", ""]
        categories: dict[str, list[CommandDef]] = {}
        for cmd in cls._registry.values():
            categories.setdefault(cmd.category, []).append(cmd)
        for cat, cmds in categories.items():
            lines.append(f"  {cat}:")
            for cmd in cmds:
                lines.append(f"    {cmd.name:<12} {cmd.description}")
            lines.append("")
        lines.append('Use "codemap <comando> --help" para detalhes.')
        return "\n".join(lines)

    @classmethod
    def add_to_parser(cls, parser: argparse.ArgumentParser):
        subs = parser.add_subparsers(dest="command")
        for name, cmd in cls._registry.items():
            sub = subs.add_parser(name, help=cmd.description)
            sig = inspect.signature(cmd.fn)
            for pname, param in sig.parameters.items():
                if pname in ("self",):
                    continue
                if param.kind == inspect.Parameter.VAR_KEYWORD:
                    continue
                if param.kind == inspect.Parameter.VAR_POSITIONAL:
                    continue

                ptype = param.annotation if param.annotation != inspect.Parameter.empty else None
                default = param.default if param.default != inspect.Parameter.empty else None
                has_default = param.default != inspect.Parameter.empty

                # Boolean flags: action="store_true"
                if ptype is bool or (has_default and isinstance(default, bool)):
                    sub.add_argument(
                        f"--{pname}",
                        action="store_true",
                        default=default if has_default else False,
                        help=f"ativar {pname}",
                    )
                    continue

                # filepath com default None → posicional opcional (nargs='?')
                if pname == "filepath" and has_default and default is None:
                    sub.add_argument(pname, nargs="?", default=None, help="caminho do dirmap (ou configure default_dirmap)")
                    continue

                # Parâmetros posicionais obrigatórios (sem default)
                if not has_default:
                    sub.add_argument(pname, help=f"{pname}")
                    continue

                # Parâmetros opcionais com flag
                dest = pname if pname not in ("type",) else f"filter_{pname}"
                sub.add_argument(
                    f"--{pname}",
                    dest=dest,
                    default=default,
                    type=ptype if ptype else str,
                    help=f"{pname} (default: {default})",
                )

    @classmethod
    def clear(cls):
        cls._registry.clear()
