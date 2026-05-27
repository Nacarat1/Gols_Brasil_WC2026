# Guia de Reprodução Passo a Passo

Siga as instruções abaixo para configurar seu ambiente local e reproduzir a simulação de Monte Carlo completa da Copa 2026.

---

## 🛠️ 1. Preparação do Ambiente

### Instalação do Python
Recomenda-se o uso do **Python 3.8 ou superior**. Verifique a versão instalada em sua máquina rodando:
```bash
python --version
```

### Instalação de Dependências
Instale as bibliotecas necessárias declaradas no arquivo de dependências rodando:
```bash
pip install -r requirements.txt
```

---

## 🔑 2. Configurando as Credenciais do Kaggle

Os dados brutos de histórico de partidas e ranking mundial de seleções são baixados diretamente da API pública do Kaggle.

1. Acesse sua conta em [Kaggle](https://www.kaggle.com/) (ou crie uma se não possuir).
2. Clique na sua foto de perfil no canto superior direito e vá em **Settings**.
3. Role até a seção **API** e clique em **Create New Token**. Isso baixará um arquivo chamado `kaggle.json`.
4. Mova ou copie o arquivo `kaggle.json` para a pasta raiz deste projeto:
   - Caminho: `Copa/kaggle.json`

> [!NOTE]
> O arquivo `.gitignore` já está configurado para garantir que suas credenciais privadas `kaggle.json` nunca sejam enviadas ao GitHub.

---

## 🚀 3. Execução do Pipeline Medallion

Para rodar todo o pipeline end-to-end, execute os scripts a partir do diretório raiz do projeto na ordem descrita abaixo:

### Passo 1: Ingestão de Dados (Camada Bronze)
Baixa as bases públicas de partidas e ranking e as extrai no diretório de dados brutos:
```bash
python src/download.py
```
* **Destino:** Salva arquivos CSV brutos em `data/raw/`.

### Passo 2: Pipeline ETL (Camada Silver)
Realiza a limpeza, tratamento de nulos, junção temporal de dados e enriquecimento com categorização dos adversários:
```bash
python src/etl.py
```
* **Destino:** Cria o dataset final estruturado em `data/processed/gold_brasil_partidas.csv`.

### Passo 3: Treinamento do Modelo de Regressão (Camada Gold - Modelo)
Ajusta o modelo estatístico de regressão de Poisson baseando-se no histórico de partidas do Brasil no século XXI:
```bash
python src/modelo.py
```
* **Saída:** Exibe o sumário estatístico do modelo com os coeficientes estimados e validação rápida do Lambda esperável.

### Passo 4: Execução da Simulação de Monte Carlo (Camada Gold - Simulação)
Roda 100.000 simulações de campanhas completas do Brasil e computa as estatísticas descritivas:
```bash
python src/monte_carlo.py
```
* **Destino:** Exporta a planilha com os resultados em `data/output/resultados_simulacao.csv`.

### Passo 5: Geração de Visualizações (Camada Gold - Gráficos)
Desenha os gráficos estatísticos e dashboards executivos de alta resolução sobre a simulação:
```bash
python src/plot_dashboard.py
python src/plot_simulation.py
```
* **Destino:** Salva as imagens PNG de alta fidelidade em `data/output/`.

---

## 📈 4. Verificação de Resultados

Após executar todos os scripts, valide se as seguintes saídas foram geradas com sucesso:

1. **`data/processed/gold_brasil_partidas.csv`**
2. **`data/output/resultados_simulacao.csv`**
3. **`data/output/dashboard_monte_carlo_gols.png`** (DPI 400)
4. **`data/output/simulacao_monte_carlo_gols_brasil.png`** (DPI 300)
