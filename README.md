# CodeMap

> Indexador de codebases multi-linguagem — estrutura, dependências, análise de impacto.

## O que é

CodeMap escaneia repositórios de código-fonte e constrói um índice consultável de arquivos, dependências, classes e cadeias de impacto. Pense em "AST + grafo de dependências + grep" combinados em uma ferramenta só.

## Por quê

Codebases legados são difíceis de navegar. Onboarding leva semanas. Refactoring quebra coisas que ninguém sabia que estavam conectadas. CodeMap existe para tornar codebases **auto-descritivos**.

## Instalação

```bash
pip install -e ".[dev]"
```

Ou sem instalar — basta rodar `codemap.cmd` na raiz do repositório.

## Uso

```bash
# Gerar índice de um codebase
codemap dirmap ./meu-projeto

# Ver resultado no terminal (sem escrever no disco)
codemap dirmap ./meu-projeto --stdout

# Consultar o índice
codemap query dirmap.json --ext .pas
codemap query dirmap.json --lang delphi
codemap query dirmap.json --summary

# Explorar interativamente
codemap repl dirmap.json

# Help dinâmico (lista todos os comandos)
codemap
```

### REPL

```
codemap> ext .pas              # filtra por extensão
codemap> lang delphi           # filtra por linguagem
codemap> path src/Model        # filtra por caminho
codemap> type dir              # lista apenas diretórios
codemap> count                 # conta resultados
codemap> summary               # resumo do codebase
codemap> help                  # detalhes dos filtros
```

### Configuração

Crie `.codemap.yml` na raiz do projeto:

```yaml
dirmap:
  ignore:
    files: [.gitignore, .codemap-ignore]
    extra_dirs: [bin, obj]
  output:
    format: json
    indent: 2
  walker:
    follow_symlinks: false
    max_depth: null
  classifier:
    custom_extensions:
      .dpr: delphi-entry
```

Configuração merge de 4 camadas: defaults → global (`~/.codemap/config.yml`) → projeto (`.codemap.yml`) → flags CLI.

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
| 1 | Dirmap — estrutura de arquivos, tipos | **Feito** |
| 2 | Métricas — LOC, órfãos, duplicatas | Planejado |
| 3 | Extração de `uses` — mapa de dependências | Planejado |
| 4 | Parser AST — classes, métodos, herança | Planejado |
| 5 | Grafo de impacto — "o que quebra se eu mudar X?" | Planejado |

## Linguagens Suportadas

| Linguagem | Extensões |
|-----------|-----------|
| Delphi | `.pas`, `.dfm`, `.dpr`, `.dpk`, `.inc` |
| Python | `.py`, `.pyw` |
| JavaScript | `.js`, `.jsx`, `.mjs` |
| TypeScript | `.ts`, `.tsx`, `.mts` |
| Java | `.java` |
| Kotlin | `.kt`, `.kts` |
| Dart | `.dart` |
| Markdown | `.md` |
| JSON / YAML | `.json`, `.yml`, `.yaml` |
| SQL | `.sql` |
| Web | `.html`, `.css`, `.scss` |

Extensões customizáveis via `custom_extensions` no `.codemap.yml`.

## Estrutura do Projeto

```
codemap/
├── cli.py              # Entrypoint CLI
├── registry.py         # Registro dinâmico de comandos
├── config.py           # Configuração (merge de camadas)
├── health.py           # Validação de dependências
└── dirmap/
    ├── walker.py       # Caminha árvore de diretórios
    ├── ignore.py       # Parser de .gitignore / .codemap-ignore
    ├── classifier.py   # Extensão → linguagem
    ├── serializer.py   # WalkResult → JSON
    └── query.py        # Motor de consultas + REPL
tests/
├── test_registry.py
├── test_health.py
├── test_cli_integration.py
└── dirmap/
    ├── test_config.py
    ├── test_walker.py
    ├── test_ignore.py
    ├── test_classifier.py
    ├── test_serializer.py
    └── test_query.py
```

## Convenção de Alias

Cada repositório indexado recebe um alias: `[Repo]Atlas`

Exemplos: HadstecaAtlas, DelphiAtlas, FuturaAtlas

## Autor

Desenvolvido 
- por [.dobrador](https://github.com/h4mn)
- com a parceira Sky 🌟 (Persona e Infra de desenvolvimento)
- através do modelo GLM-5-Turbo

---

[English](README-en.md)

> "Todo codebase tem uma história pra contar — o CodeMap dá voz a ela." – made by Sky 🗺️
