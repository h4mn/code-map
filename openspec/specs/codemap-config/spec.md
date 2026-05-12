## ADDED Requirements

### Requirement: Config carrega com hierarquia de 4 camadas
O `DirmapConfig` SHALL resolver configuração na seguinte ordem (menor → maior precedência): defaults hardcoded, `~/.codemap/config.yml`, `<repo>/.codemap.yml`, flags CLI.

#### Scenario: Merge de camadas
- **WHEN** o default tem `follow_symlinks: False`, o config do projeto tem `follow_symlinks: True` e o CLI não passa flag
- **THEN** o config final tem `follow_symlinks: True`

#### Scenario: CLI sobrepõe tudo
- **WHEN** o config do projeto tem `max_depth: 3` e o CLI passa `--max-depth 5`
- **THEN** o config final tem `max_depth: 5`

### Requirement: Config funciona sem arquivos
O `DirmapConfig` SHALL funcionar com defaults quando nenhum arquivo de config existe.

#### Scenario: Sem config
- **WHEN** não existe `~/.codemap/config.yml` nem `.codemap.yml` no repo
- **THEN** o config usa valores default sem erro

### Requirement: Config suporta chave dirmap
O `.codemap.yml` SHALL aceitar a seção `dirmap` com subchaves: `ignore.files`, `ignore.extra_dirs`, `output.format`, `output.indent`, `walker.follow_symlinks`, `walker.max_depth`, `classifier.custom_extensions`.

#### Scenario: Config completo
- **WHEN** `.codemap.yml` contém todas as chaves válidas incluindo métricas
- **THEN** todas são lidas e aplicadas corretamente

#### Scenario: Config parcial
- **WHEN** `.codemap.yml` contém apenas `walker.max_depth: 3`
- **THEN** os demais valores usam default

### Requirement: Config ignora chaves desconhecidas
O `DirmapConfig` SHALL ignorar chaves desconhecidas no YAML sem levantar erro.

#### Scenario: Chave inválida
- **WHEN** `.codemap.yml` contém `foo: bar`
- **THEN** `foo` é ignorado e o config funciona normalmente

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
