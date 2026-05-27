# Arquitetura Medallion - Detalhes Técnicos

## Bronze Layer (Raw Data)

**Responsável:** `src/download.py`

### Fonte de Dados
- **Kaggle Dataset 1:** International Football Results (1980-2024)
- **Kaggle Dataset 2:** FIFA World Rankings Historical (2000-2024)

### Dados Capturados
- Partidas: data, seleções, gols, tipo (oficial/amistoso)
- Rankings: ranking numérico por seleção em cada data

### Validações
- Verificação de integridade de arquivo
- Detecção de duplicatas
- Logagem de erros de download

---

## Silver Layer (Transformed Data)

**Responsável:** `src/etl.py`

### Processos ETL
1. **Limpeza:** remoção de NULLs, duplicatas
2. **Normalização:** padronização de nomes, datas
3. **Enriquecimento:** cruzamento partidas + ranking FIFA na data
4. **Feature Engineering:** categorização de adversários (A-E)

### Output
**Tabela: `data/processed/gold_brasil_partidas.csv`**
```text
data, seleção, gols_brasil, gols_adversário, ranking_adversário, categoria_adversário, tipo_jogo, ...
```

### Garantia de Qualidade
- Checksums de integridade
- Validação de ranges (gols >= 0)
- Rastreabilidade completa

---

## Gold Layer (Analytical)

**Responsáveis:** `src/modelo.py`, `src/monte_carlo.py`

### Modelagem Estatística (modelo.py)

**Distribuição:** Poisson

**Equação:**
```text
log(λ) = β₀ + β₁·categoria_adversário + β₂·tipo_jogo
```

**Parâmetros Estimados:**
- β₀: intercept
- β₁: coeficiente categoria
- β₂: coeficiente tipo jogo

### Simulação (monte_carlo.py)

**100.000 iterações** com:
- Amostragem aleatória de fases (até qual o Brasil avança)
- Sorteio de adversários por categoria e fase
- Cálculo de gols esperados via λ estimado
- Agregação por campanha completa

**Output:** `data/output/resultados_simulacao.csv` com distribuição de gols
