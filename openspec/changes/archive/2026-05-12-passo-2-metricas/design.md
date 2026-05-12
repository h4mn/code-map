## Context

O Passo 1 (Dirmap) produziu um índice JSON com a estrutura física do codebase: arquivos, diretórios, extensões, tamanhos. O Passo 2 opera sobre esse índice para adicionar métricas quantitativas sem alterar a estrutura existente — apenas enriquece.

O codebase-alvo principal (TRUNK Delphi) tem ~52 mil arquivos e 4.8 GB. Métricas de LOC requerem leitura de cada arquivo, o que precisa ser eficiente.

## Goals / Non-Goals

**Goals:**
- Contar LOC (total, código, comentário, blank) por arquivo
- Agregar métricas por diretório
- Detectar duplicatas por nome
- Marcar órfãos candidatos
- Enriquecer dirmap.json mantendo retrocompatibilidade
- Integrar ao CLI existente

**Non-Goals:**
- Detecção de duplicatas por hash (futuro)
- Órfãos reais via `uses` (Passo 3)
- Complexidade ciclomática (Passo 4 AST)
- Dependências externas

## Decisions

### 1. Arquitetura: pipeline sequencial
**Escolha:** counter → aggregator → finder → enricher (pipeline linear)
**Alternativa:** processamento paralelo com multiprocessing
**Racional:** pipeline linear é mais simples, testável e debugável. Paralelismo pode ser adicionado depois se performance for problema.

### 2. Formato de saída: campo `metrics` aditivo no dirmap.json
**Escolha:** Adicionar campo `metrics` em cada entry de arquivo e diretório
**Racional:** Mantém retrocompatibilidade — quem não usa métricas ignora o campo. Sem breaking change.

### 3. LOC counter: heurísticas por linguagem
**Escolha:** Regex-based por linguagem (comentários de linha e bloco)
**Alternativa:** Parser AST real
**Racional:** AST seria mais preciso mas requer parser por linguagem. Heurística cobre 90% dos casos com stdlib.

### 4. Duplicatas: por nome de arquivo
**Escolha:** Agrupar por `basename.ext` e reportar grupos com >1 ocorrência
**Racional:** Simples, barato, útil. Hash-based fica pro Passo 3 com `uses`.

### 5. CLI: subcomando `metrics` + flag `--with-metrics`
**Escolha:** Ambos — `metrics` opera sobre JSON existente, `--with-metrics` integra ao dirmap
**Racional:** Flexibilidade — user pode indexar primeiro e métricas depois, ou tudo junto.

## Risks / Trade-offs

- **Performance em codebases grandes** → 52k arquivos = 52k leituras. Mitigar: progress bar, batching, early exit por extensão desconhecida
- **Heurística de comentário imprecisa** → String dentro de string pode ser contada como comentário. Mitigar: good enough pra análise macro
- **dirmap.json cresce significativamente** → Cada arquivo ganha ~4 campos de LOC + flags. Mitigar: formato compacto, campo opcional
