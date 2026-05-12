## Why

O Dirmap (Passo 1) mapeou a estrutura física do codebase — arquivos, diretórios, tipos, tamanhos. Mas não diz nada sobre a *qualidade* ou *complexidade* do código. Sem métricas, não dá pra identificar gargalos, arquivos críticos, duplicatas ou áreas que precisam de atenção. O Passo 2 adiciona essa camada analítica.

## What Changes

- Novo módulo `codemap/metrics/` com 4 submódulos: counter, aggregator, finder, enricher
- Contagem de LOC (total, código, comentário, blank) por arquivo, com suporte a Delphi, Python, JS/TS
- Agregação de métricas por diretório (somas, médias, diversidade de linguagens)
- Detecção de duplicatas por nome de arquivo (heurística inicial)
- Marcação de órfãos candidatos (sem consumidor conhecido)
- Enriquecimento do `dirmap.json` existente com métricas, mantendo compatibilidade retroativa
- Novo comando CLI `codemap metrics` e flag `--with-metrics` no `dirmap`
- Extensão do query layer para suportar filtros e ordenação por métricas

## Capabilities

### New Capabilities
- `metrics-counter`: Contagem de LOC por arquivo com heurísticas por linguagem (Delphi, Python, JS/TS)
- `metrics-aggregator`: Agregação de métricas por diretório — somas, médias, diversidade
- `metrics-finder`: Detecção de duplicatas por nome e marcação de órfãos candidatos
- `metrics-enricher`: Enriquecimento do dirmap.json com métricas, mantendo retrocompatibilidade

### Modified Capabilities
- `codemap-cli`: Novo subcomando `metrics` e flag `--with-metrics` no `dirmap`
- `dirmap-query`: Filtros e ordenação por métricas (`--metrics`, `--top`, `--by`)
- `codemap-config`: Novas opções de configuração para métricas (thresholds, linguagens suportadas)

## Impact

- **Código novo**: ~4 módulos em `codemap/metrics/`, sem alterar módulos existentes do Passo 1
- **CLI**: Registro de novo comando `metrics` no registry
- **Formato de saída**: `dirmap.json` cresce com campo `metrics` por arquivo/diretório (aditivo, sem breaking change)
- **Dependências**: Nenhuma nova — tudo com stdlib Python
- **Performance**: Leitura de todos os arquivos do codebase para LOC — pode ser lento em codebases grandes (mitigar com progress feedback)
