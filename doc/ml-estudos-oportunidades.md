# Estudos ML - Oportunidades no CodeMap

Analise do potencial de Machine Learning sobre os dados coletados pelo CodeMap (Passos 1 e 2).

## Features Disponiveis

### Por arquivo (28.786 files)
| Feature | Tipo | Fonte |
|---------|------|-------|
| path | string | Passo 1 |
| extension | categorica (70 valores) | Passo 1 |
| language | categorica (14 valores) | Passo 1 |
| size_bytes | numerica | Passo 1 |
| orphan_candidate | booleana | Passo 2 |
| loc_total | numerica | Passo 2 |
| loc_code | numerica | Passo 2 |
| loc_comment | numerica | Passo 2 |
| loc_blank | numerica | Passo 2 |

### Derivaveis por diretorio (1.353 dirs com 5+ files)
| Feature | Tipo | Como |
|---------|------|------|
| file_count | numerica | agregacao |
| total_loc | numerica | soma loc_code |
| avg_file_size | numerica | media size_bytes |
| comment_ratio | numerica | loc_comment / loc_total |
| code_density | numerica | loc_code / loc_total |
| extension_diversity | numerica | Shannon entropy |
| language_diversity | numerica | Shannon entropy |
| orphan_ratio | numerica | orphans / total_files |
| max_depth | numerica | path depth |
| size_concentration | numerica | Gini coefficient |

## Estudos ML Viaveis

### 1. Clustering de Diretorios - PERFIL DO BAIRRO
**Algoritmo:** K-Means / DBSCAN / Hierarchical
**Features por dir:** file_count, total_loc, comment_ratio, extension_diversity, orphan_ratio, max_depth
**Resultado esperado:** 4-8 clusters tipo "core denso", "biblioteca bem-documentada", "dumping ground", "assets/resources"
**Valor:** Mapa visual do codebase, decisoes de onde investir refactoring

### 2. Deteccao de Anomalias - LIMPEZA DE TRUNK
**Algoritmo:** Isolation Forest / LOF
**Features:** size_bytes, loc_total, loc_comment, orphan_candidate, extension, depth
**Alvos:** 13K orphans (46%!), files de 45K LOC, dirs com 300+ icons
**Valor:** Priorizar limpeza, remover build artifacts, assets nao versionados

**Destaques encontrados:**
- 13.120 orphan candidates (46% do codebase)
- RepTmp: 9.210 orphans, 3.4M LOC, comment ratio 2.5%
- Empresa: 2.160 orphans
- Biblioteca/Ciper/src/cDataStructs.pas: 45.087 LOC (outlier extremo)

### 3. Predicao de Orphan - CLASSIFICADOR SUPERVISIONADO
**Algoritmo:** Random Forest / Gradient Boosting
**Features:** extension, language, size_bytes, loc_total, loc_code, comment_ratio, depth
**Target:** orphan_candidate (True/False)
**Dataset:** Quase balanceado - 13K orphans vs 15.7K non-orphans
**Valor:** Entender PADROES que tornam um arquivo orfao - nao so detectar, mas explicar

### 4. Analise de Saude por Modulo - SCORE COMPOSTO
**Algoritmo:** PCA + scoring (nao supervisionado)
**Features por modulo:** comment_ratio, orphan_ratio, avg_loc, code_density
**Resultado esperado:** Ranking de saude dos 10 modulos top-level

**Destaques por modulo:**
| Modulo | Files | LOC | Comment% | Orphans | Diagnostico |
|--------|-------|-----|----------|---------|-------------|
| RepTmp | 10.035 | 3.381.626 | 2.5% | 9.210 | Pior modulo |
| Empresa | 5.137 | 1.513.678 | 13.6% | 2.160 | Bem documentado, muitos orfans |
| Biblioteca | 901 | 799.544 | 9.0% | 902 | Medio |
| RepositorioCatho | 618 | 130.250 | 2.1% | 136 | Baixa documentacao |
| Firemonkey | 227 | 72.389 | 3.6% | 297 | Medio-baixo |
| Repositorio | 309 | 64.305 | 2.4% | 375 | Baixa documentacao |
| TmpCampineira | 8 | 3.679 | 22.6% | 7 | Bem documentado, quase todos orfaos |

### 5. Regressao de Complexidade - PREVER IMPACTO
**Algoritmo:** Linear Regression / Ridge / Random Forest Regressor
**Features:** extension, language, depth, comment_ratio, orphan
**Target:** loc_code
**Valor:** Prever tamanho de arquivos nao-analisados (6.4K unknown language), estimar esforco de refactoring

### 6. NLP em Nomes de Arquivo - CONVENCOES DELPHI
**Algoritmo:** TF-IDF + K-Means nos nomes de .pas
**Features extraidas:** prefixos (u*, if*, m*), sufixos, padroes CamelCase
**Valor:** Detectar violacoes de convencao, agrupar por dominio funcional

**Padroes de prefixo encontrados:**
| Prefixo | Quantidade | Interpretacao |
|---------|-----------|---------------|
| u | 6.723 | Units Delphi (padrao) |
| if | 3.016 | Interfaces/Forms |
| m | 1.032 | Modulos/Data Modules |
| Testu | 916 | Testes |
| i | 699 | Interfaces |

## Novas Possibilidades com Passo 2

1. **Comment ratio como proxy de qualidade** - modulos com < 3% comments sao code smell
2. **Orphan ratio como proxy de manutencao** - dirs com > 70% orphans sao cemiterios
3. **Code density** - arquivos com > 85% code lines e > 1K LOC sao dificeis de manter
4. **Correlacao tamanho x orfandade** - arquivos grandes sao mais propensos a ser orfaos?

## Viabilidade

- **Dataset:** 28.786 files, 17.258 com LOC, 1.353 dirs com features agregadas
- **Stack:** scikit-learn + pandas + matplotlib/seaborn
- **Tempo de experimento:** 1-2 notebooks
- **Sem deep learning necessario** - dados tabulares puros

## Recomendacao Prioritaria

**Comecar por #2 (Anomalias) + #3 (Predicao de Orphan)** - juntos formam um "raio-X do TRUNK":

1. Quais arquivos sao problema? (anomalias)
2. Por que sao problema? (classificador explica features importantes)
3. Onde focar limpeza? (ranking por modulo)

---

> "Metricas sem acao sao apenas numeros - o ML transforma numeros em prioridades." - made by Sky 🗺
