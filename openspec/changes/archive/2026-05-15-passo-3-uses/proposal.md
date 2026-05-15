## Why

O dirmap (Passo 1) mapeia a estrutura física do codebase e as métricas (Passo 2) quantificam cada arquivo. Mas não sabemos **como as unidades se relacionam** — quem depende de quem, quais são os pontos críticos de acoplamento, onde existem ciclos. Sem o mapa de dependências, análises de impacto e refactoring seguro são impossíveis. O codebase-alvo (TRUNK Delphi com 52K arquivos) tem dependências implícitas que só ficam visíveis ao extrair as cláusulas `uses`.

## What Changes

- Novo módulo `codemap/uses/` com 6 submódulos: parser dispatcher, parsers por linguagem (Delphi, Python, JS/TS), resolver de nomes e construtor de grafo
- Novo comando CLI `codemap uses <dirmap.json>` que extrai dependências e enriquece o dirmap
- Flag `--with-uses` no comando `dirmap` para gerar tudo em um passo
- Novas opções de query: `--depends-on`, `--depended-by`, `--cycles`
- Configuração de search paths Delphi, PYTHONPATH e aliases JS/TS no `.codemap.yml`

## Capabilities

### New Capabilities
- `uses-parser`: Extração de imports/uses por linguagem (Delphi, Python, JS/TS) — dispatcher + parsers específicos
- `uses-resolver`: Resolução de nomes de unidade/módulo para caminhos físicos usando o dirmap como índice
- `uses-graph`: Construção do grafo dirigido de dependências com detecção de ciclos e cálculo de fan-in/fan-out

### Modified Capabilities
- `codemap-cli`: Novo subcomando `uses` e flags `--with-uses` no dirmap
- `codemap-config`: Novos campos de configuração para search paths e aliases de import
- `dirmap-query`: Novos filtros `--depends-on`, `--depended-by`, `--cycles`
- `dirmap-serializer`: Integração do enriquecimento com uses no pipeline do dirmap

## Impact

- **Novos módulos**: `codemap/uses/` (6 arquivos)
- **Modificados**: `cli.py`, `config.py`, `dirmap/__init__.py`, `dirmap/query.py`, `dirmap/serializer.py`
- **Novos testes**: `tests/uses/` (parsers, resolver, graph)
- **Sem deps externas** — tudo stdlib (ast, re, pathlib, collections)
- **Compatível** com dirmaps gerados nos Passos 1 e 2 (retrocompatível)
