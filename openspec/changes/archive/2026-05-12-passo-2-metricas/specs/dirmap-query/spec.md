## ADDED Requirements

### Requirement: Query ordena por métrica
O motor de consulta SHALL suportar `--top N --by <campo>` para ordenar por métricas.

#### Scenario: Top 10 por LOC
- **WHEN** query é executado com `--top 10 --by loc_code`
- **THEN** retorna os 10 arquivos com maior `loc_code`, ordenados desc

#### Scenario: Campo inexistente
- **WHEN** query é executado com `--by campo_inexistente`
- **THEN** exibe erro informando campos disponíveis

### Requirement: Query filtra por métrica mínima
O motor de consulta SHALL suportar `--min-loc <N>` para filtrar arquivos com LOC mínimo.

#### Scenario: Filtro por LOC
- **WHEN** query é executado com `--min-loc 100`
- **THEN** retorna apenas arquivos com `loc_code >= 100`

### Requirement: Query mostra métricas
O motor de consulta SHALL suportar flag `--metrics` para incluir campo de métricas na saída.

#### Scenario: Saída com métricas
- **WHEN** query é executado com `--metrics`
- **THEN** cada entrada inclui campo `metrics` com LOC e flags

#### Scenario: Saída sem métricas
- **WHEN** query é executado sem `--metrics`
- **THEN** saída não inclui campo `metrics` (comportamento atual)

### Requirement: REPL suporta filtros de métrica
O REPL SHALL aceitar comandos `top`, `by`, `min-loc`, `metrics`.

#### Scenario: REPL com top
- **WHEN** usuário digita `top 5 by loc_code`
- **THEN** REPL exibe os 5 arquivos com mais linhas de código
