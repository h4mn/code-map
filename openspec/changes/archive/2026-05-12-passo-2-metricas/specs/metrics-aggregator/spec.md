## ADDED Requirements

### Requirement: Agregação por diretório
O `MetricsAggregator` SHALL agregar métricas por diretório somando LOC e contando arquivos por linguagem.

#### Scenario: Diretório com múltiplos arquivos
- **WHEN** agregador recebe métricas de 3 arquivos `.pas` (10, 20, 30 loc_code)
- **THEN** diretório pai recebe `loc_code: 60` e `file_count: {"delphi": 3}`

#### Scenario: Diretório vazio
- **WHEN** diretório não contém arquivos com métricas
- **THEN** métricas do diretório são zeros

### Requirement: Diversidade de linguagens
O agregador SHALL computar quantas linguagens distintas existem em cada diretório.

#### Scenario: Diretório multilingual
- **WHEN** diretório contém arquivos `.pas` e `.py`
- **THEN** `language_diversity: 2`

#### Scenario: Diretório monolinguagem
- **WHEN** diretório contém apenas `.pas`
- **THEN** `language_diversity: 1`

### Requirement: Árvore hierárquica
O agregador SHALL produzir árvore de métricas espelhando a estrutura de diretórios.

#### Scenario: Subdiretórios
- **WHEN** existem `src/` com `src/Model/` e `src/View/`
- **THEN** métricas de `src/` incluem soma dos subdiretórios

### Requirement: Ratio código/comentário
O agregador SHALL computar `code_comment_ratio` por diretório (loc_code / loc_comment).

#### Scenario: Ratio normal
- **WHEN** diretório tem `loc_code: 100` e `loc_comment: 20`
- **THEN** `code_comment_ratio: 5.0`

#### Scenario: Sem comentários
- **WHEN** diretório tem `loc_comment: 0`
- **THEN** `code_comment_ratio: null`
