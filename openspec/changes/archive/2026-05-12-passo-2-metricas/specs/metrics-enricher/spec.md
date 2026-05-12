## ADDED Requirements

### Requirement: Enriquecimento de dirmap.json
O `MetricsEnricher` SHALL ler `dirmap.json` existente e adicionar campo `metrics` em cada entrada de arquivo.

#### Scenario: Enriquecimento básico
- **WHEN** enricher processa dirmap.json com arquivo `src/Utils.pas`
- **THEN** entrada ganha campo `metrics` com `loc_total`, `loc_code`, `loc_comment`, `loc_blank`

#### Scenario: Arquivo sem métricas
- **WHEN** arquivo é binário (`.exe`)
- **THEN** campo `metrics` é `null`

### Requirement: Retrocompatibilidade
O enricher SHALL preservar todos os campos existentes do dirmap.json.

#### Scenario: Campos preservados
- **WHEN** entrada tinha `path`, `name`, `extension`, `size`, `type`
- **THEN** todos permanecem inalterados após enriquecimento

### Requirement: Enriquecimento de diretórios
O enricher SHALL adicionar métricas agregadas em entradas de diretório.

#### Scenario: Diretório com métricas
- **WHEN** diretório contém 5 arquivos `.pas`
- **THEN** entrada do diretório ganha `metrics` com somas e agregações

### Requirement: Flags de duplicata e órfão
O enricher SHALL adicionar flags `duplicate_candidate` e `orphan_candidate` nas entradas.

#### Scenario: Flags adicionadas
- **WHEN** finder detecta duplicata e enricher processa
- **THEN** entrada ganha `duplicate_candidate: true` e `duplicate_group: "nome.ext"`

### Requirement: Output opcional
O enricher SHALL suportar escrita em arquivo ou stdout.

#### Scenario: Escrita em arquivo
- **WHEN** enricher roda com caminho de saída
- **THEN** escreve JSON enriquecido no arquivo

#### Scenario: Saída stdout
- **WHEN** enricher roda com flag `--stdout`
- **THEN** imprime JSON enriquecido no stdout
