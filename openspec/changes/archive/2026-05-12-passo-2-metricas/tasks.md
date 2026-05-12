## 1. Setup

- [x] 1.1 Criar módulo `codemap/metrics/__init__.py` com imports públicos
- [x] 1.2 Adicionar seção `metrics` no `codemap/config.py` (defaults + merge)

## 2. Metrics Counter

- [x] 2.1 Implementar `codemap/metrics/counter.py` — LOC counter com heurísticas por linguagem (Delphi, Python, JS/TS)
- [x] 2.2 Implementar testes `tests/metrics/test_counter.py` — Delphi (`//`, `{}`, `(* *)`), Python (`#`, `"""`), JS (`//`, `/**/`), extensão desconhecida, arquivo ilegível

## 3. Metrics Aggregator

- [x] 3.1 Implementar `codemap/metrics/aggregator.py` — agregação por diretório (somas, file_count por linguagem, language_diversity, code_comment_ratio)
- [x] 3.2 Implementar testes `tests/metrics/test_aggregator.py` — diretório com múltiplos arquivos, diversidade, árvore hierárquica, ratio

## 4. Metrics Finder

- [x] 4.1 Implementar `codemap/metrics/finder.py` — detecção de duplicatas por nome e órfãos candidatos
- [x] 4.2 Implementar testes `tests/metrics/test_finder.py` — duplicatas, sem duplicatas, órfãos, relatório

## 5. Metrics Enricher

- [x] 5.1 Implementar `codemap/metrics/enricher.py` — enriquecimento de dirmap.json (counter + aggregator + finder)
- [x] 5.2 Implementar testes `tests/metrics/test_enricher.py` — retrocompatibilidade, campo metrics em arquivos e dirs, flags duplicata/órfão, stdout

## 6. CLI Integration

- [x] 6.1 Registrar comando `metrics` no `codemap/registry.py`
- [x] 6.2 Implementar handler do comando `metrics` no `codemap/cli.py`
- [x] 6.3 Adicionar flag `--with-metrics` no comando `dirmap`
- [x] 6.4 Estender `codemap/dirmap/query.py` com `--metrics`, `--top`, `--by`, `--min-loc`
- [x] 6.5 Estender REPL com comandos `top`, `by`, `min-loc`, `metrics`

## 7. Testes de Integração

- [x] 7.1 Teste E2E: `codemap metrics dirmap.json` gera saída enriquecida
- [x] 7.2 Teste E2E: `codemap dirmap ./path --with-metrics` funciona em um passo
- [x] 7.3 Teste E2E: `codemap query dirmap.json --metrics --top 5 --by loc_code`
- [x] 7.4 Garantir `python -m pytest` passa com 0 falhas
