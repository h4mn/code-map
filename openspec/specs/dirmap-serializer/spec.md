## ADDED Requirements

### Requirement: Serializer gera JSON válido
O serializer SHALL receber uma lista de entradas do walker e gerar um JSON válido no disco.

#### Scenario: Geração de JSON
- **WHEN** o walker retorna 3 arquivos
- **THEN** o serializer escreve um arquivo JSON contendo `meta`, `summary`, `errors` e `tree`

### Requirement: Meta contém dados de execução
O campo `meta` SHALL conter: `tool`, `command`, `version`, `timestamp`, `root`, `root_name`.

#### Scenario: Meta completo
- **WHEN** o dirmap é executado com root `C:\Hadsteca`
- **THEN** `meta.root` é `C:\Hadsteca` e `meta.root_name` é `Hadsteca`

### Requirement: Summary pré-computa estatísticas
O campo `summary` SHALL conter: `total_files`, `total_dirs`, `total_size_bytes`, `by_extension` (dict), `by_language` (dict).

#### Scenario: Summary com dados corretos
- **WHEN** o walker retornou 2 arquivos `.pas` e 1 `.md`
- **THEN** `summary.total_files` é 3 e `summary.by_extension[".pas"]` é 2

### Requirement: Tree contém lista de entradas
O campo `tree` SHALL ser uma lista de objetos com: `path` (relativo ao root), `type` (`file` ou `dir`), `extension`, `language`, `size_bytes`.

#### Scenario: Entrada de arquivo
- **WHEN** o walker encontrou `src/Model/Clientes.pas` com 2048 bytes
- **THEN** `tree` contém `{"path": "src/Model/Clientes.pas", "type": "file", "extension": ".pas", "language": "delphi", "size_bytes": 2048}`

### Requirement: Errors captura problemas do scan
O campo `errors` SHALL ser uma lista de objetos com `path` e `reason`. Quando não há erros, SHALL ser uma lista vazia.

#### Scenario: Scan sem erros
- **WHEN** todos os diretórios são acessíveis
- **THEN** `errors` é `[]`

#### Scenario: Scan com erros
- **WHEN** um diretório sem permissão foi encontrado
- **THEN** `errors` contém `{"path": "src/secreto", "reason": "permission_denied"}`

### Requirement: Serializer suporta stdout
O serializer SHALL suportar saída via `--stdout`, imprimindo o JSON no terminal sem escrever no disco.

#### Scenario: Flag --stdout
- **WHEN** `--stdout` é passado
- **THEN** o JSON é impresso no stdout e nenhum arquivo é escrito no disco

### Requirement: Serializer respeita indent da config
O serializer SHALL usar `DirmapConfig.indent` para formatação do JSON.

#### Scenario: Indent customizado
- **WHEN** a config tem `indent: 4`
- **THEN** o JSON gerado usa indentação de 4 espaços

### Requirement: Serializer integra enriquecimento com uses
O serializer SHALL aceitar flag `with_uses` e chamar o enricher de uses quando ativado.

#### Scenario: Dirmap com uses
- **WHEN** `run_dirmap` é chamado com `with_uses=True`
- **THEN** o JSON de saída inclui campo `imports` nas entries de arquivo e `dependency_graph` no nível raiz

#### Scenario: Dirmap sem uses
- **WHEN** `run_dirmap` é chamado com `with_uses=False`
- **THEN** o JSON de saída não inclui campo `imports` (comportamento atual preservado)
