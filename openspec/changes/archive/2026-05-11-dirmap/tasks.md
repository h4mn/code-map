## 1. Scaffolding

- [x] 1.1 Criar estrutura de pacotes (`codemap/__init__.py`, `codemap/dirmap/__init__.py`, `tests/dirmap/__init__.py`)
- [x] 1.2 Criar `pyproject.toml` com metadata, entrypoint `codemap = "codemap.cli:main"`, dependência pyyaml e dev deps (pytest, pytest-cov)
- [x] 1.3 Criar `codemap/__init__.py` com `__version__ = "0.1.0"` e export de `CommandRegistry`

## 2. Registry e CLI

- [x] 2.1 Implementar `codemap/registry.py` — `CommandRegistry` com `register()` (decorator), `help()`, detecção de duplicatas
- [x] 2.2 Implementar `codemap/cli.py` — argparse com roteamento dinâmico via registry, `codemap` sem args mostra help
- [x] 2.3 Implementar `codemap/health.py` — `check_dependencies()` com dict REQUIRED, falha rápido com mensagem clara
- [x] 2.4 Testes: `test_registry.py` (registro, duplicata, help dinâmico) e `test_health.py` (dep presente, dep faltando)

## 3. Config

- [x] 3.1 Implementar `codemap/config.py` — `DirmapConfig` dataclass com defaults, `load()` faz merge de 4 camadas (defaults → global → projeto → CLI)
- [x] 3.2 Suportar seção `dirmap` do YAML com todas as subchaves (ignore, output, walker, classifier)
- [x] 3.3 Ignorar chaves desconhecidas no YAML sem erro
- [x] 3.4 Testes: `test_config.py` (sem config, config parcial, merge de camadas, chave inválida, CLI sobrepõe)

## 4. Dirmap — Walker

- [x] 4.1 Implementar `codemap/dirmap/walker.py` — caminha árvore com `pathlib`, coleta path relativo, extensão, tamanho
- [x] 4.2 Implementar `codemap/dirmap/ignore.py` — parser de `.gitignore` (wildcards, comentários, linhas vazias) e `.codemap-ignore`
- [x] 4.3 Integrar `extra_dirs` da config no filtro de exclusão
- [x] 4.4 Implementar `max_depth` — limita profundidade de recursão
- [x] 4.5 Implementar controle de symlinks — não seguir por default, detectar ciclo quando `follow_symlinks: True`
- [x] 4.6 Tratar `PermissionError` — registrar em errors e continuar
- [x] 4.7 Testes: `test_walker.py` (árvore simples, vazio, max_depth, symlink, sem permissão) e `test_ignore.py` (gitignore, codemap-ignore, extra_dirs, linhas malformadas)

## 5. Dirmap — Classifier

- [x] 5.1 Implementar `codemap/dirmap/classifier.py` — mapeamento padrão extensão→linguagem (Delphi, Python, JS, TS, Java, Markdown, JSON)
- [x] 5.2 Suportar `custom_extensions` da config com override do mapeamento padrão
- [x] 5.3 Normalizar extensões sem ponto (adicionar `.` automaticamente)
- [x] 5.4 Testes: `test_classifier.py` (extensão conhecida, desconhecida, custom, sem ponto)

## 6. Dirmap — Serializer

- [x] 6.1 Implementar `codemap/dirmap/serializer.py` — monta JSON com meta, summary (total_files, total_dirs, total_size_bytes, by_extension, by_language), tree, errors
- [x] 6.2 Implementar saída `--stdout` (print no terminal, sem escrever no disco)
- [x] 6.3 Respeitar `indent` da config na formatação do JSON
- [x] 6.4 Registrar comando `dirmap` no registry (decorator em `codemap/dirmap/__init__.py`)
- [x] 6.5 Testes: `test_serializer.py` (JSON válido, meta, summary, errors, stdout, indent)

## 7. Dirmap — Query

- [x] 7.1 Implementar `codemap/dirmap/query.py` — motor stateless de filtros (ext, lang, path, type, count, summary) com combinação AND
- [x] 7.2 Implementar subcomando `query` — lê JSON do disco, aplica filtros, imprime resultado JSON no stdout
- [x] 7.3 Implementar REPL (`codemap repl`) — loop interativo que aceita mesmos filtros em formato curto, help, saída com Ctrl+C ou `exit`
- [x] 7.4 Mensagem de boas-vindas do REPL com nome do codebase e total de arquivos
- [x] 7.5 Registrar comandos `query` e `repl` no registry
- [x] 7.6 Testes: `test_query.py` (filtro ext, lang, path, type, count, summary, combinação, vazio)

## 8. Integração e Aceitação

- [x] 8.1 Rodar `pytest -v` — todos os testes passam
- [x] 8.2 Rodar `pytest --cov=codemap --cov-report=term-missing` — cobertura ≥80% em todos os módulos
- [x] 8.3 Teste ponta-a-ponta: `codemap dirmap <repo>` gera JSON, `codemap query <json> --ext .pas` filtra, `codemap repl <json>` funciona
- [x] 8.4 Verificar help dinâmico: `codemap` sem args mostra todos os comandos registrados
- [x] 8.5 Verificar fail fast: remover pyyaml e confirmar mensagem de erro clara
