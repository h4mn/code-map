## 1. Estrutura e Config

- [x] 1.1 Criar módulo `codemap/uses/__init__.py` com registro do comando `uses` no registry
- [x] 1.2 Estender `DirmapConfig` com campos `delphi_search_paths`, `python_paths`, `js_aliases` na seção `uses`
- [x] 1.3 Escrever testes de config para seção `uses` (defaults, parcial, completo)
- [x] 1.4 Adicionar `import codemap.uses` no `cli.py`

## 2. Parser Delphi (TDD)

- [x] 2.1 Escrever testes para parser Delphi (uses interface, implementation, multi-linha, dpr, sem uses)
- [x] 2.2 Implementar `codemap/uses/delphi.py` — extração de cláusulas `uses` via regex
- [x] 2.3 Validar testes passando

## 3. Parser Python (TDD)

- [x] 3.1 Escrever testes para parser Python (import, from, relativo, multi-level)
- [x] 3.2 Implementar `codemap/uses/python.py` — extração via `ast` module
- [x] 3.3 Validar testes passando

## 4. Parser JS/TS (TDD)

- [x] 4.1 Escrever testes para parser JS/TS (import default, named, require, dynamic)
- [x] 4.2 Implementar `codemap/uses/js_ts.py` — extração via regex
- [x] 4.3 Validar testes passando

## 5. Parser Dispatcher

- [x] 5.1 Escrever testes para dispatcher (seleção por linguagem, linguagem não suportada, arquivo inexistente)
- [x] 5.2 Implementar `codemap/uses/parser.py` — dispatcher que seleciona parser por linguagem
- [x] 5.3 Validar testes passando

## 6. Resolver (TDD)

- [x] 6.1 Escrever testes para resolver (Delphi por nome, search paths, Python absoluto/relativo, JS relativo, aliases, unresolved)
- [x] 6.2 Implementar `codemap/uses/resolver.py` — resolução de nomes → caminhos usando dirmap
- [x] 6.3 Validar testes passando

## 7. Graph (TDD)

- [x] 7.1 Escrever testes para graph (construção, ciclos diretos/transitivos, fan-in/fan-out, serialização, hotspots)
- [x] 7.2 Implementar `codemap/uses/graph.py` — grafo dirigido com detecção de ciclos
- [x] 7.3 Validar testes passando

## 8. Enricher e Integração CLI

- [x] 8.1 Implementar `codemap/uses/enricher.py` — orquestra parser + resolver + graph, enriquece dirmap
- [x] 8.2 Estender `dirmap/serializer.py` com flag `with_uses`
- [x] 8.3 Estender `dirmap/__init__.py` — `cmd_dirmap` aceita `--with_uses`, `cmd_query` aceita `--depends-on`, `--depended-by`, `--cycles`
- [x] 8.4 Estender `dirmap/query.py` — novos filtros `depends_on`, `depended_by`, `cycles`
- [x] 8.5 Estender REPL com comandos `depends-on`, `depended-by`, `cycles`

## 9. Testes de Integração

- [x] 9.1 Teste E2E: `codemap uses dirmap.json --stdout` gera JSON com grafo
- [x] 9.2 Teste E2E: `codemap dirmap ./path --with-uses` gera dirmap enriquecido
- [x] 9.3 Teste E2E: `codemap query dirmap.json --cycles` detecta ciclos
- [x] 9.4 Teste E2E: `codemap query dirmap.json --depends-on UnitX` filtra dependentes
- [x] 9.5 Validar `python -m pytest` passa com 0 falhas
