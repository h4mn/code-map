## ADDED Requirements

### Requirement: Serializer integra enriquecimento com uses
O serializer SHALL aceitar flag `with_uses` e chamar o enricher de uses quando ativado.

#### Scenario: Dirmap com uses
- **WHEN** `run_dirmap` é chamado com `with_uses=True`
- **THEN** o JSON de saída inclui campo `imports` nas entries de arquivo e `dependency_graph` no nível raiz

#### Scenario: Dirmap sem uses
- **WHEN** `run_dirmap` é chamado com `with_uses=False`
- **THEN** o JSON de saída não inclui campo `imports` (comportamento atual preservado)
