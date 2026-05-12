## MODIFIED Requirements

### Requirement: Config suporta chave dirmap
O `.codemap.yml` SHALL aceitar a seção `dirmap` com subchaves: `ignore.files`, `ignore.extra_dirs`, `output.format`, `output.indent`, `walker.follow_symlinks`, `walker.max_depth`, `classifier.custom_extensions`.

#### Scenario: Config completo
- **WHEN** `.codemap.yml` contém todas as chaves válidas incluindo métricas
- **THEN** todas são lidas e aplicadas corretamente

## ADDED Requirements

### Requirement: Config suporta seção metrics
O `.codemap.yml` SHALL aceitar a seção `metrics` com subchaves: `enabled`, `loc.languages`, `duplicates.min_group_size`, `orphans.heuristic`.

#### Scenario: Config de métricas
- **WHEN** `.codemap.yml` contém `metrics: { enabled: true, loc: { languages: [delphi, python] } }`
- **THEN** apenas as linguagens listadas são processadas para LOC

#### Scenario: Métricas desabilitadas
- **WHEN** `.codemap.yml` contém `metrics: { enabled: false }`
- **THEN** LOC não é coletado, mesmo com `--with-metrics`

#### Scenario: Defaults de métricas
- **WHEN** `.codemap.yml` não contém seção `metrics`
- **THEN** usa defaults: `enabled: true`, todas as linguagens suportadas
