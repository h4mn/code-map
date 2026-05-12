## ADDED Requirements

### Requirement: Contagem de LOC por arquivo
O `MetricsCounter` SHALL contar linhas de código por arquivo retornando `loc_total`, `loc_code`, `loc_comment`, `loc_blank`.

#### Scenario: Arquivo Delphi com comentários
- **WHEN** contador processa arquivo `.pas` com linhas de código, comentários `//` e `{} ` e linhas em branco
- **THEN** retorna `loc_total` = total de linhas, `loc_code` = linhas sem comentário/blank, `loc_comment` = linhas de comentário, `loc_blank` = linhas em branco

#### Scenario: Arquivo Python com docstring
- **WHEN** contador processa arquivo `.py` com `#` comentários e `"""` docstrings
- **THEN** conta docstrings como comentário

#### Scenario: Arquivo JS/TS com comentários
- **WHEN** contador processa arquivo `.js` com `//` e `/* */` comentários
- **THEN** ambos os estilos são contados como comentário

### Requirement: Extensão desconhecida é ignorada
O contador SHALL retornar `None` para extensões não suportadas, sem levantar erro.

#### Scenario: Arquivo binário
- **WHEN** contador processa arquivo `.exe`
- **THEN** retorna `None`

### Requirement: Arquivo inexistente ou ilegível
O contador SHALL retornar `None` para arquivos que não podem ser lidos, sem levantar erro.

#### Scenario: Permissão negada
- **WHEN** contador tenta ler arquivo sem permissão
- **THEN** retorna `None` e não crasha

### Requirement: Suporte a comentários Delphi multi-style
O contador SHALL reconhecer `//`, `{ ... }` e `(* ... *)` como comentários Delphi.

#### Scenario: Comentário chaves
- **WHEN** linha contém `{ este é um comentário }`
- **THEN** contada como `loc_comment`

#### Scenario: Comentário parêntese-asterisco
- **WHEN** linha contém `(* este é um comentário *)`
- **THEN** contada como `loc_comment`
