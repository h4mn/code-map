# CodeMap

> Multi-language codebase indexer — structure, dependencies, impact analysis.

## What

CodeMap scans source code repositories and builds a queryable index of files, dependencies, classes, and impact chains. Think "AST + dependency graph + grep" combined into one tool.

## Why

Legacy codebases are hard to navigate. Onboarding takes weeks. Refactoring breaks things nobody knew were connected. CodeMap exists to make codebases **self-describing**.

## Architecture

```
┌─────────────────────────────────────────┐
│           QUERY LAYER                   │  CLI / MCP — ask questions
├─────────────────────────────────────────┤
│           INDEX LAYER                   │  Store what was discovered
├─────────────────────────────────────────┤
│           SCAN LAYER                    │  Discover the codebase
└─────────────────────────────────────────┘
```

## Roadmap

| Step | What | Status |
|------|------|--------|
| 1 | Dirmap — file structure, types | Planned |
| 2 | Metrics — LOC, orphans, duplicates | Planned |
| 3 | `uses` extraction — dependency map | Planned |
| 4 | AST parsing — classes, methods, inheritance | Planned |
| 5 | Impact graph — "what breaks if I change X?" | Planned |

## Supported Languages

Planned (priority order):
- Python
- Delphi
- Java
- Kotlin
- Flutter/Dart

## Integration

- **CLI** — `codemap scan <path>`, `codemap query "..."`
- **MCP** — `codemap/scan`, `codemap/query` (Claude Code, AI agents)

## Alias Convention

Each indexed repository gets an alias: `[Repo]Atlas`

Examples: HadstecaAtlas, DelphiAtlas, FuturaAtlas

## Author

Built by [.dobrador](https://github.com/h4mn)

---

[Português](README.md)
