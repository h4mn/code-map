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

# Com métricas e dependências
codemap dirmap ./meu-projeto --with-metrics --with-uses

# Ver resultado no terminal (sem escrever no disco)
codemap dirmap ./meu-projeto --stdout

# Consultar o índice (filepath opcional com .codemap.yml)
codemap query --ext .pas
codemap query --path Etiqueta
codemap query --path "*Modelo*" --count
codemap query --summary

# Buscar declarações de tipos/constantes/enums
codemap lookup TRelatorioModelo
codemap lookup MAX_RETRIES --lang delphi

# Explorar interativamente
codemap repl

# Help dinâmico (lista todos os comandos)
codemap
```

### Configuração

Crie `.codemap.yml` na raiz do projeto:

```yaml
dirmap:
  default_dirmap: dirmap.json    # filepath padrão — não precisa mais digitar
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
  uses:
    delphi_search_paths: [src, lib]
    python_paths: [src]
```

Config merge de 4 camadas: defaults → global (`~/.codemap/config.yml`) → projeto (`.codemap.yml`) → flags CLI.

### Consultas (query)

| Flag | Descrição | Exemplo |
|------|-----------|---------|
| `--ext` | Filtra por extensão | `--ext .pas` |
| `--lang` | Filtra por linguagem | `--lang delphi` |
| `--path` | Busca substring/glob no caminho | `--path Etiqueta`, `--path "*.pas"` |
| `--type` | Filtra por tipo (file/dir) | `--type file` |
| `--count` | Conta resultados | `--count` |
| `--summary` | Resumo do codebase | `--summary` |
| `--metrics` | Inclui métricas na saída | `--metrics` |
| `--top N --by campo` | Top N por métrica | `--top 10 --by loc_code` |
| `--min-loc N` | LOC mínimo | `--min-loc 100` |
| `--depends-on` | Quem importa o arquivo | `--depends-on src/Utils.pas` |
| `--depended-by` | O que o arquivo importa | `--depended-by src/Main.pas` |
| `--cycles` | Lista ciclos de dependência | `--cycles` |
| `--case-sensitive` | Busca case-sensitive | `--case-sensitive` |

Todas as buscas são **case-insensitive** por padrão. O `--path` suporta substring e glob (`*`, `?`, `[seq]`).

### Lookup de símbolos

Busca declarações de tipos, constantes e enums via regex:

```bash
codemap lookup TRelatorioModelo         # encontra declarações de type
codemap lookup MAX_RETRIES              # encontra declarações de const
codemap lookup TRDinTp_Etiqueta         # encontra declarações de enum
codemap lookup Relatorio --lang delphi  # substring + filtro de linguagem
```

### REPL

```
codemap> ext .pas              # filtra por extensão
codemap> lang delphi           # filtra por linguagem
codemap> path Etiqueta         # busca substring no caminho
codemap> path "*.pas"          # glob matching
codemap> case-sensitive        # ativa busca case-sensitive
codemap> type dir              # lista apenas diretórios
codemap> count                 # conta resultados
codemap> summary               # resumo do codebase
codemap> top 5 by loc_code     # top 5 por LOC de código
codemap> depends-on Utils      # quem importa Utils
codemap> cycles                # ciclos de dependência
codemap> help                  # detalhes dos filtros
```

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
| 2 | Métricas — LOC, órfãos, duplicatas, análise estrutural | **Feito** |
| 3 | Extração de `uses` — mapa de dependências | **Feito** |
| 4 | Parser AST — classes, métodos, herança | Planejado |
| 5 | Grafo de impacto — "o que quebra se eu mudar X?" | Planejado |
| 6 | RAG Semântico — ChromaDB + busca semântica | Planejado |
| 7 | Agente — interface conversacional (MCP / webchat) | Planejado |

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
├── cli.py              # Entrypoint CLI + resolução de default_dirmap
├── registry.py         # Registro dinâmico de comandos
├── config.py           # Configuração (merge de 4 camadas)
├── health.py           # Validação de dependências
└── dirmap/
    ├── walker.py       # Caminha árvore de diretórios
    ├── ignore.py       # Parser de .gitignore / .codemap-ignore
    ├── classifier.py   # Extensão → linguagem
    ├── serializer.py   # WalkResult → JSON
    ├── query.py        # Motor de consultas + REPL
    └── lookup.py       # Lookup de símbolos (tipos, consts, enums)
└── uses/
    ├── parser.py       # Dispatcher de parsers por linguagem
    ├── delphi.py       # Parser de uses Delphi
    ├── python.py       # Parser de imports Python
    ├── js_ts.py        # Parser de imports JS/TS
    ├── resolver.py     # Resolução de paths de dependência
    ├── graph.py        # Grafo de dependências + ciclos
    └── enricher.py     # Enriquece dirmap com dependências
└── metrics/
    ├── counter.py      # Contador de LOC por linguagem
    ├── finder.py       # Duplicatas e órfãos
    ├── aggregator.py   # Agregação de métricas
    └── enricher.py     # Enriquece dirmap com métricas
tests/
├── test_registry.py
├── test_health.py
├── test_cli_integration.py
├── dirmap/
│   ├── test_config.py
│   ├── test_walker.py
│   ├── test_ignore.py
│   ├── test_classifier.py
│   ├── test_serializer.py
│   ├── test_query.py
│   └── test_lookup.py
├── metrics/
│   ├── test_counter.py
│   ├── test_finder.py
│   ├── test_aggregator.py
│   └── test_enricher.py
└── uses/
    ├── test_delphi.py
    ├── test_python.py
    ├── test_js_ts.py
    ├── test_parser.py
    ├── test_resolver.py
    ├── test_graph.py
    ├── test_enricher.py
    └── test_uses_config.py
```

## Convenção de Alias

Cada repositório indexado recebe um alias: `[Repo]Atlas`

Exemplos: HadstecaAtlas, DelphiAtlas

## Autor

Desenvolvido 
- por [.dobrador](https://github.com/h4mn)
- com a parceira Sky 🌟 (Persona e Infra de desenvolvimento)
- através do modelo GLM-5-Turbo

---

[English](README-en.md)

> "Todo codebase tem uma história pra contar — o CodeMap dá voz a ela." – made by Sky 🗺️
