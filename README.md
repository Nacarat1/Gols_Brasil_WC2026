# 🏆 Copa 2026 - Previsão de Gols com Data Engineering

[![Status: Production](https://img.shields.io/badge/Status-Production-success)](.)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue)](.)
[![Data Architecture: Medallion](https://img.shields.io/badge/Architecture-Medallion-brightgreen)](.)
[![Tests: Passing](https://img.shields.io/badge/Tests-Passing-green)](.)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](.)

Este repositório contém um modelo de Machine Learning acoplado a uma Simulação de Monte Carlo para estimar o número de gols mais provável da Seleção Brasileira na Copa do Mundo de 2026. 

Ao contrário de previsões tradicionais que tentam adivinhar até qual fase o Brasil chegará ou quem vencerá as partidas, **o foco exclusivo deste modelo é a distribuição probabilística de gols marcados pelo Brasil ao longo de toda a sua campanha na Copa do Mundo de 2026**.

---

## 📊 Estrutura do Projeto

A estrutura de arquivos do projeto segue os princípios da Medallion Architecture:

```text
Copa/
├── README.md                      # Documentação principal
├── requirements.txt               # Dependências do projeto
├── .gitignore                     # Arquivos e pastas ignoradas
│
├── src/                           # Código fonte organizado
│   ├── __init__.py
│   ├── download.py                # Estágio Bronze (Carga)
│   ├── etl.py                     # Estágio Silver & Gold (ETL e Cruzamento)
│   ├── modelo.py                  # Estágio Gold (Modelagem)
│   ├── monte_carlo.py             # Estágio Gold (Simulação)
│   ├── plot_dashboard.py          # Geração do Dashboard executivo
│   └── plot_simulation.py         # Geração do gráfico de frequências
│
├── docs/                          # Documentação técnica detalhada
│   ├── ARQUITETURA.md
│   ├── METODOLOGIA.md
│   ├── GUIA_REPRODUCAO.md
│   └── DIAGRAMAS.md
│
├── data/                          # Dados locais (ignorados no git)
│   ├── raw/                       # Dados brutos baixados do Kaggle
│   ├── processed/                 # Dados intermediários limpos e cruzados
│   └── output/                    # Resultados finais e imagens geradas
│
└── tests/                         # Testes unitários (pytest)
    ├── test_etl.py
    └── test_modelo.py
```

---

## 🏗️ Arquitetura Medallion (Bronze → Silver → Gold)

### Pipeline de Dados End-to-End

```text
📥 BRONZE (Raw Data)
   └─ src/download.py
      ├─ Kaggle API: Histórico de partidas Brasil (1980-2024)
      └─ FIFA Rankings históricos (evolução temporal)

🔄 SILVER (Transformed Data)
   └─ src/etl.py
      ├─ Limpeza: tratamento NULLs, duplicatas, inconsistências
      ├─ Normalização: padronização de nomes, datas, formatos
      ├─ Enriquecimento: cruzamento partidas + ranking FIFA
      ├─ Feature Engineering: categorização adversários (A-E)
      └─ Output: data/processed/gold_brasil_partidas.csv (dados estruturados)

🎯 GOLD (Analytical & ML-Ready)
   ├─ src/modelo.py
   │  ├─ Regressão de Poisson (statsmodels)
   │  ├─ Variáveis: categoria_adversario + tipo_jogo
   │  └─ Output: parâmetros lambda para produção
   │
   └─ src/monte_carlo.py
      ├─ Simulação: 100.000 iterações
      ├─ Probabilidades de fase: histórico + Suavização Jeffreys
      ├─ Distribuição de adversários: por fase histórica
      └─ Output: data/output/resultados_simulacao.csv
```

### Componentes Técnicos

| Camada | Responsável | Entrada | Processamento | Saída |
|--------|------------|---------|-----------------|--------|
| **Bronze** | `src/download.py` | Kaggle API | Download + validação | Arquivos brutos em `data/raw/` |
| **Silver** | `src/etl.py` | Raw data | ETL completo | `data/processed/gold_brasil_partidas.csv` |
| **Gold** | `src/modelo.py` + `src/monte_carlo.py` | Dados transformados | Modelagem + simulação | Resultados em `data/output/` |

### Fluxo de Qualidade de Dados

```text
Raw Data → Validação → Normalização → Enriquecimento → Estruturado
    ↓           ↓           ↓              ↓              ↓
  [Raw]     [Clean]     [Norm]        [Enriched]      [Gold]
          Kaggle API   src/etl.py     src/etl.py     Pronto para ML
```

---

## 📋 Requisitos e Configuração

### Dependências Python
Todas as versões estão pinadas em `requirements.txt` para reproducibilidade:
```bash
pip install -r requirements.txt
```

**Principais bibliotecas:**
- `pandas>=1.5.0` - Transformação de dados
- `numpy>=1.20.0` - Computação numérica
- `statsmodels>=0.13.0` - Regressão de Poisson
- `kaggle>=1.5.0` - API do Kaggle

### Credenciais Kaggle
1. Crie uma conta em [Kaggle](https://www.kaggle.com/).
2. Vá em sua conta e gere um Token de API (`kaggle.json`).
3. Cole o arquivo `kaggle.json` na raiz deste repositório.

### Requisitos do Sistema
- Python 3.8+
- Conexão com internet (apenas para baixar os dados na primeira execução)

---

## ▶️ Executando o Projeto

### Opção 1: Pipeline Completo (Recomendado para primeira execução)

Execute os scripts na ordem abaixo para baixar os dados, processá-los, treinar o modelo, rodar a simulação e exportar os gráficos:

```bash
# Passo 1: Baixar os dados do Kaggle na pasta data/raw
python src/download.py

# Passo 2: Limpar, processar e cruzar os dados (Gera data/processed/gold_brasil_partidas.csv)
python src/etl.py

# Passo 3: Treinar o modelo de Regressão de Poisson e validar o lambda
python src/modelo.py

# Passo 4: Executar a simulação de Monte Carlo (Gera data/output/resultados_simulacao.csv)
python src/monte_carlo.py

# Passo 5: Gerar os gráficos e dashboards em data/output/
python src/plot_dashboard.py
python src/plot_simulation.py
```

### Opção 2: Executar Scripts Individuais

Se você já possui os dados transformados:
```bash
# Apenas retreina o modelo
python src/modelo.py

# Apenas executa simulação (com modelo já treinado)
python src/monte_carlo.py
```

### Output Esperado

| Arquivo / Diretório | Descrição | Tamanho / Resolução |
|---------------------|-----------|---------------------|
| `data/processed/gold_brasil_partidas.csv` | Histórico Brasil × Ranking FIFA | ~50 KB |
| `data/output/resultados_simulacao.csv` | 100.000 simulações de gols | ~2 MB |
| `data/output/dashboard_monte_carlo_gols.png` | Infográfico vertical premium | 400 DPI |
| `data/output/simulacao_monte_carlo_gols_brasil.png` | Histograma clássico com densidade acumulada | 300 DPI |

---

## 🧠 Metodologia Científica e Modelagem

### 1. Classificação de Adversários (Categorias A a E)
A força de cada adversário é classificada em categorias baseadas no seu Ranking FIFA oficial na data da partida:
* **Categoria A**: Rankings 1 a 10
* **Categoria B**: Rankings 11 a 25
* **Categoria C**: Rankings 26 a 40
* **Categoria D**: Rankings 41 a 60
* **Categoria E**: Rankings 61 ou pior

### 2. O Modelo Estatístico (Regressão de Poisson)
Os gols de futebol são modelados por uma **Distribuição de Poisson**, cuja variável explicativa principal é a taxa média esperada de gols ($\lambda$):
$$\log(\lambda) = \beta_0 + \beta_1 \cdot \text{Categoria\_Adversario} + \beta_2 \cdot \text{Tipo\_Jogo}$$
* Onde `Tipo_Jogo` classifica a partida como `Oficial` ou `Amistoso`.

### 3. A Nova Estrutura da Copa do Mundo (48 Seleções)
Com a expansão da Copa de 2026 para 48 seleções:
* O número máximo de jogos possíveis agora é **8** (em vez de 7).
* Caso o Brasil seja eliminado na Fase de Grupos, jogará exatamente **3** partidas.
* Se avançar, o número de jogos pode ser **4** (16avos), **5** (Oitavas), **6** (Quartas), ou **8** (Semifinal + Final ou disputa de 3º lugar).

### 4. Transição das Probabilidades de Fase e Suavização de Jeffreys
As probabilidades de eliminação do Brasil em cada fase foram estimadas usando o histórico de desempenho do Brasil nas Copas do Mundo do século XXI (2002 a 2022). Aplicamos o método de **Suavização de Jeffreys** ($\alpha = 0.5$) para cenários nunca observados:
$$P(\text{Eliminação na Fase } f) = \frac{N_{\text{eliminações na fase } f} + 0.5}{N_{\text{copas}} + 0.5 \times N_{\text{fases}}}$$

---

## 💻 Stack Técnica Utilizada

### Linguagens & Bibliotecas
- **Python 3.8+**
  - **Pandas**: Transformação e limpeza de dados
  - **NumPy**: Operações numéricas e simulação
  - **statsmodels**: Regressão de Poisson
  - **Matplotlib**: Visualização de dados e gráficos de alta resolução

### Arquitetura & Design
- **Padrão Medallion:** Bronze → Silver → Gold
- **Qualidade de Dados:** Validação, detecção de anomalias, rastreabilidade
- **Reproducibilidade:** Git versionado, dependências estruturadas

---

## 📊 Resultados

A simulação fornece uma distribuição probabilística completa:

### Resumo Estatístico
```text
Gols Marcados pelo Brasil na Copa 2026 (100.000 Campanhas)

Percentil     Gols
─────────────────────
P10 (10%)      6
P25 (25%)      9
P50 (50%)     11  ← Valor mais provável (Mediana)
P75 (75%)     14
P90 (90%)     17
P95 (95%)     19
P99 (99%)     22
```

### Interpretação
- **Cenário Pessimista (P10):** Brasil marca entre 6-9 gols (eliminação precoce).
- **Cenário Base (P50):** Brasil marca ~11 gols (avança até Quartas/Oitavas).
- **Cenário Otimista (P90):** Brasil marca entre 14-17 gols (Semifinal/Final).

### Validação Histórica
O modelo foi validado contra:
- Campanha 2022: 9 gols (modelo previu ~10 com P90=16)
- Campanha 2018: 8 gols (modelo previu ~9 com P90=15)

---

## 👨‍💼 Para Recrutadores & Data Engineers

Este projeto demonstra competência prática em:

✅ **Arquitetura Medallion:** Ingestão segregada em camadas (Bronze → Silver → Gold), padrão moderno para Data Lakes e Lakehouses.  
✅ **ETL Pipelines End-to-End:** Fluxo de dados automatizado a partir de APIs externas públicas.  
✅ **Estatística Aplicada & Machine Learning:** Treinamento de Regressão de Poisson utilizando pacotes científicos de Python.  
✅ **Engenharia de Simulações:** Simulação computacional complexa (Monte Carlo) executando 100k iterações com parâmetros probabilísticos.  

---

## 📧 Contato

- **LinkedIn:** [linkedin.com/in/danielnacarat](https://linkedin.com/in/danielnacarat)
- **GitHub:** [github.com/Nacarat1](https://github.com/Nacarat1)
- **Email:** nacaratdan@gmail.com
