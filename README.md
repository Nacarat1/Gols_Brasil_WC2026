# 🏆 Previsão de Gols da Seleção Brasileira na Copa do Mundo 2026

Este repositório contém um modelo de Machine Learning acoplado a uma Simulação de Monte Carlo para estimar o número de gols mais provável da Seleção Brasileira na Copa do Mundo de 2026. 

Ao contrário de previsões tradicionais que tentam adivinhar até qual fase o Brasil chegará ou quem vencerá as partidas, **o foco exclusivo deste modelo é a distribuição probabilística de gols marcados pelo Brasil ao longo de toda a sua campanha na Copa do Mundo de 2026**.

---

## 📊 Estrutura do Projeto

A estrutura de arquivos do projeto é simples e organizada seguindo um pipeline de dados linear:

```text
Copa/
├── .gitignore                  # Arquivos ignorados no Git (dados brutos, caches e credenciais)
├── README.md                   # Este arquivo de documentação do projeto
├── requirements.txt            # Dependências de bibliotecas Python do projeto
│
├── download.py                 # 1. Faz download das bases do Kaggle via API
├── etl.py                      # 2. Pipeline ETL (Bronze -> Silver -> Gold)
├── modelo.py                   # 3. Treina o Modelo de Regressão de Poisson (statsmodels)
└── monte_carlo.py              # 4. Executa a Simulação de Monte Carlo (100k iterações)
```

Além disso, a execução gera:
* `gold_brasil_partidas.csv`: Base refinada contendo o histórico de partidas do Brasil cruzado com o Ranking FIFA de cada adversário na época do jogo.
* `resultados_simulacao.csv`: Resultados das 100.000 simulações de gols da campanha do Brasil.

---

## ⚙️ Como Executar o Projeto

### 1. Pré-requisitos
Certifique-se de ter o Python 3.8+ instalado e as dependências necessárias. Instale-as rodando:
```bash
pip install -r requirements.txt
```

### 2. Configurando as Credenciais do Kaggle
O script `download.py` utiliza a API oficial do Kaggle para baixar as bases históricas de partidas e ranking FIFA.
1. Crie uma conta no [Kaggle](https://www.kaggle.com/).
2. Vá em sua conta e gere um Token de API (`kaggle.json`).
3. Cole o arquivo `kaggle.json` na raiz deste repositório (não se preocupe, o `.gitignore` está configurado para nunca enviar este arquivo com suas credenciais para o GitHub).

### 3. Executando o Pipeline de Simulação
Execute os scripts na ordem abaixo para baixar os dados, processá-los, treinar o modelo e rodar a simulação:

```bash
# Passo 1: Baixar os dados do Kaggle
python download.py

# Passo 2: Limpar, processar e cruzar os dados (Gera gold_brasil_partidas.csv)
python etl.py

# Passo 3: Treinar o modelo de Regressão de Poisson e validar o lambda
python modelo.py

# Passo 4: Executar a simulação de Monte Carlo para a Copa 2026
python monte_carlo.py
```

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
Os gols de futebol são modelados classicamente por uma **Distribuição de Poisson**, cuja variável explicativa principal é a taxa média esperada de gols ($\lambda$).
Utilizamos uma regressão de Poisson (`statsmodels`) para prever o $\lambda$ do Brasil com base em duas variáveis:
$$\log(\lambda) = \beta_0 + \beta_1 \cdot \text{Categoria\_Adversario} + \beta_2 \cdot \text{Tipo\_Jogo}$$
* Onde `Tipo_Jogo` classifica a partida como `Oficial` ou `Amistoso`.

### 3. A Nova Estrutura da Copa do Mundo (48 Seleções)
Com a expansão da Copa do Mundo de 2026 para 48 seleções, a estrutura de fases mudou:
* O número máximo de jogos possíveis agora é **8** (em vez de 7).
* Caso o Brasil seja eliminado na Fase de Grupos, jogará exatamente **3** partidas.
* Se avançar, o número de jogos pode ser **4** (16avos), **5** (Oitavas), **6** (Quartas), ou **8** (Semifinal + Final ou disputa de 3º lugar). 
*(Nota: Pelo regulamento, quem chega à Semifinal obrigatoriamente joga 8 partidas no torneio).*

### 4. Transição das Probabilidades de Fase
As probabilidades de eliminação do Brasil em cada fase foram estimadas usando o histórico de desempenho do Brasil nas Copas do Mundo do século XXI (2002 a 2022). 
Para aproximar as fases antigas (onde a Copa tinha 32 times) para a estrutura moderna de 48 times, mapeamos as fases usando o conceito de **profundidade competitiva (Best-N)**:
* **Fase de Grupos** (Best-48 na Copa de 2026)
* **16avos de Final** (Best-32 na Copa de 2026)
* **Oitavas de Final** (Best-16 na Copa de 2026)
* **Quartas de Final** (Best-8 na Copa de 2026)
* **Finalistas / Semifinalistas** (Best-4 na Copa de 2026)

Para evitar probabilidades nulas de eliminação em fases onde o Brasil nunca caiu no histórico recente (como a fase de grupos ou os 16avos/Best-32), aplicamos o método de **Suavização de Jeffreys** ($\alpha = 0.5$):
$$P(\text{Eliminação na Fase } f) = \frac{N_{\text{eliminações na fase } f} + 0.5}{N_{\text{copas}} + 0.5 \times N_{\text{fases}}}$$

### 5. Distribuição de Adversários na Copa
Em cada fase eliminatória, a probabilidade de enfrentar adversários das categorias A, B, C, D ou E é baseada na **distribuição real histórica de todas as seleções presentes em cada fase** nas copas do século XXI, e não apenas nos adversários enfrentados pelo Brasil.

### 6. Cenários de Simulação (Grupos de 2026)
A simulação considera os adversários definidos/esperados para a fase de grupos do Brasil na Copa de 2026:
* **Jogo 1**: Adversário de Categoria B (ex: Marrocos)
* **Jogo 2**: Adversário de Categoria E (ex: Haiti)
* **Jogo 3**: Adversário de Categoria C (ex: Escócia)

---

## 📈 Resultados da Simulação

Após rodar **100.000 iterações** da campanha do Brasil na Copa do Mundo de 2026, os resultados consolidados mostram:

* **Média de Gols Marcados**: ~11.65 gols
* **Moda (Valor mais Provável)**: 11 gols
* **Mediana (P50)**: 11 gols
* **Intervalo de Confiança (P10 - P90)**: Entre 7 e 17 gols marcados

Este comportamento reflete a alta probabilidade histórica de a Seleção Brasileira avançar até as fases finais (Quartas de Final ou Semifinal/Final), acumulando assim mais partidas e consequentemente mais gols ao longo do torneio.

---

*Desenvolvido como um modelo preditivo de acoplamento direto probabilístico.*
