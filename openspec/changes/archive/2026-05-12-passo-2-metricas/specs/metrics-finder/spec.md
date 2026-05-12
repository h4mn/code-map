## ADDED Requirements

### Requirement: Detecção de duplicatas por nome
O `MetricsFinder` SHALL detectar arquivos com mesmo `basename.ext` em diretórios diferentes.

#### Scenario: Arquivos duplicados
- **WHEN** existem `src/A/Utils.pas` e `src/B/Utils.pas`
- **THEN** ambos são marcados como `duplicate_candidate: true` com `duplicate_group: "Utils.pas"`

#### Scenario: Mesmo diretório
- **WHEN** existem `src/A/Utils.pas` e `src/A/Helper.pas`
- **THEN** nenhum é marcado como duplicata

#### Scenario: Sem duplicatas
- **WHEN** todos os nomes de arquivo são únicos
- **THEN** nenhum arquivo é marcado como duplicata

### Requirement: Detecção de órfãos candidatos
O finder SHALL marcar arquivos como `orphan_candidate` quando heuristicamente parecem não ser consumidos.

#### Scenario: Arquivo de nome comum
- **WHEN** arquivo `Unit1.pas` existe sem referência em outras units
- **THEN** marcado como `orphan_candidate: true`

#### Scenario: Arquivo referenciado
- **WHEN** arquivo `Utils.pas` é encontrado em outros arquivos via menção textual
- **THEN** NÃO é marcado como órfão

### Requirement: Relatório de duplicatas
O finder SHALL produzir relatório com grupos de duplicatas e contagem.

#### Scenario: Relatório
- **WHEN** finder detecta 3 grupos de duplicatas
- **THEN** relatório lista cada grupo com nomes, caminhos e tamanho
