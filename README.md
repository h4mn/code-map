# CodeMap

> Indexador de codebases multi-linguagem — estrutura, dependências, análise de impacto.

## O que é

CodeMap escaneia repositórios de código-fonte e constrói um índice consultável de arquivos, dependências, classes e cadeias de impacto. Pense em "AST + grafo de dependências + grep" combinados em uma ferramenta só.

## Por quê

Codebases legados são difíceis de navegar. Onboarding leva semanas. Refactoring quebra coisas que ninguém sabia que estavam conectadas. CodeMap existe para tornar codebases **auto-descritivos**.

## Arquitetura

```
┌─────────────────────────────────────────┐
│           QUERY LAYER                   │  CLI / MCP — faz perguntas
├─────────────────────────────────────────┤
│           INDEX LAYER                   │  Armazena o que foi descoberto
├─────────────────────────────────────────┤
│           SCAN LAYER                    │  Descobre o codebase
└─────────────────────────────────────────┘
```

## Roadmap

| Passo | O quê | Status |
|-------|-------|--------|
| 1 | Dirmap — estrutura de arquivos, tipos | Planejado |
| 2 | Métricas — LOC, órfãos, duplicatas | Planejado |
| 3 | Extração de `uses` — mapa de dependências | Planejado |
| 4 | Parser AST — classes, métodos, herança | Planejado |
| 5 | Grafo de impacto — "o que quebra se eu mudar X?" | Planejado |

## Linguagens Suportadas

Planejado (ordem de prioridade):
- Python
- Delphi
- Java
- Kotlin
- Flutter/Dart

## Integração

- **CLI** — `codemap scan <path>`, `codemap query "..."`
- **MCP** — `codemap/scan`, `codemap/query` (Claude Code, agentes de IA)

## Convenção de Alias

Cada repositório indexado recebe um alias: `[Repo]Atlas`

Exemplos: HadstecaAtlas, DelphiAtlas, FuturaAtlas

## Autor

Desenvolvido por [.dobrador](https://github.com/h4mn)

---

[English](README-en.md)
