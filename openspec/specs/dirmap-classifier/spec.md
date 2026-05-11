## ADDED Requirements

### Requirement: Classifier mapeia extensão para linguagem
O classifier SHALL possuir um mapeamento padrão de extensões de arquivo para linguagens de programação.

#### Scenario: Extensão conhecida
- **WHEN** a entrada tem extensão `.pas`
- **THEN** o classifier retorna `language: "delphi"`

#### Scenario: Extensão desconhecida
- **WHEN** a entrada tem extensão `.xyz`
- **THEN** o classifier retorna `language: "unknown"`

### Requirement: Classifier suporta extensões customizadas
O classifier SHALL aceitar um dict `custom_extensions` da config que sobrepõe o mapeamento padrão.

#### Scenario: Extensão customizada no config
- **WHEN** a config tem `custom_extensions: {".dpr": "delphi-entry"}` e a entrada tem extensão `.dpr`
- **THEN** o classifier retorna `language: "delphi-entry"` em vez do valor padrão

#### Scenario: Extensão sem ponto no custom_extensions
- **WHEN** a config tem `custom_extensions: {"dpr": "delphi-entry"}` (sem ponto)
- **THEN** o classifier normaliza para `.dpr` antes de consultar

### Requirement: Mapeamento padrão inclui linguagens comuns
O classifier SHALL incluir mapeamento para pelo menos: Delphi (`.pas`, `.dpr`, `.dpk`, `.dfm`), Python (`.py`), JavaScript (`.js`, `.ts`), Java (`.java`), Markdown (`.md`), JSON (`.json`).

#### Scenario: Todas as linguagens padrão cobertas
- **WHEN** uma entrada tem extensão `.py`
- **THEN** o classifier retorna `language: "python"`
