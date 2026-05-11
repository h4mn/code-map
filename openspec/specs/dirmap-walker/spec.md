## ADDED Requirements

### Requirement: Walker percorre árvore de diretórios
O walker SHALL caminhar recursivamente a árvore a partir de um diretório root, coletando metadados de cada arquivo encontrado.

#### Scenario: Árvore simples
- **WHEN** o root contém 3 arquivos e 1 subdiretório com 2 arquivos
- **THEN** o walker retorna 5 entradas com path relativo ao root, extensão e tamanho em bytes

#### Scenario: Diretório vazio
- **WHEN** o root não contém arquivos
- **THEN** o walker retorna lista vazia e summary.total_files igual a 0

### Requirement: Walker respeita .gitignore
O walker SHALL ler `.gitignore` no diretório root e excluir arquivos/diretórios que correspondam às regras.

#### Scenario: Arquivo listado no .gitignore
- **WHEN** o root contém `.gitignore` com `bin/` e existe `bin/app.exe`
- **THEN** o walker exclui `bin/app.exe` do resultado

#### Scenario: Padrão wildcard no .gitignore
- **WHEN** o `.gitignore` contém `*.tmp` e existe `file.tmp`
- **THEN** o walker exclui `file.tmp` do resultado

### Requirement: Walker respeita .codemap-ignore
O walker SHALL ler `.codemap-ignore` no diretório root e excluir entradas adicionais. `.codemap-ignore` sobrepõe `.gitignore`.

#### Scenario: Arquivo no .codemap-ignore mas não no .gitignore
- **WHEN** `.codemap-ignore` contém `debug/` e `.gitignore` não menciona `debug/`
- **THEN** o walker exclui `debug/` do resultado

### Requirement: Walker respeita extra_dirs da config
O walker SHALL excluir diretórios listados em `DirmapConfig.extra_dirs`, mesmo que não estejam nos arquivos de ignore.

#### Scenario: Dir em extra_dirs
- **WHEN** a config tem `extra_dirs: ["node_modules"]` e existe `node_modules/`
- **THEN** o walker exclui `node_modules/` do resultado

### Requirement: Walker aplica max_depth
O walker SHALL limitar a profundidade de recursão conforme `DirmapConfig.max_depth`. Quando `max_depth` é `None`, SHALL percorrer sem limite.

#### Scenario: max_depth definido
- **WHEN** `max_depth` é 2 e o root tem 3 níveis de profundidade
- **THEN** o walker retorna apenas arquivos até o 2º nível

#### Scenario: max_depth None
- **WHEN** `max_depth` é `None`
- **THEN** o walker percorre toda a árvore sem limite

### Requirement: Walker não segue symlinks por default
O walker SHALL ignorar symlinks quando `DirmapConfig.follow_symlinks` é `False`.

#### Scenario: Symlink no diretório
- **WHEN** existe um symlink apontando para outro diretório e `follow_symlinks` é `False`
- **THEN** o walker pula o symlink sem erro

### Requirement: Walker detecta ciclo de symlinks
Quando `follow_symlinks` é `True`, o walker SHALL detectar ciclos e parar a recursão.

#### Scenario: Symlink cíclico
- **WHEN** `follow_symlinks` é `True` e um symlink aponta para um diretório ancestral
- **THEN** o walker registra o caminho em `errors` com `reason: "symlink_cycle"` e continua

### Requirement: Walker trata falta de permissão
O walker SHALL capturar `PermissionError`, registrar no stderr e adicionar ao array `errors` do JSON.

#### Scenario: Diretório sem permissão
- **WHEN** um subdiretório não tem permissão de leitura
- **THEN** o walker avisa no stderr, registra em `errors` com `reason: "permission_denied"` e continua
