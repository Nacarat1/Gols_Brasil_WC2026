import numpy as np
import pandas as pd
import os

try:
    from modelo import treinar_modelo
except ImportError:
    from src.modelo import treinar_modelo

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DATA_DIR = os.path.join(BASE_DIR, 'data', 'raw')
PROCESSED_DATA_DIR = os.path.join(BASE_DIR, 'data', 'processed')
OUTPUT_DATA_DIR = os.path.join(BASE_DIR, 'data', 'output')

os.makedirs(OUTPUT_DATA_DIR, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# 1. Lambdas por categoria (A-E) via modelo de Regressão de Poisson
# ─────────────────────────────────────────────────────────────────────────────
def extrair_lambdas_do_modelo():
    print("Extraindo Lambdas do modelo de Regressão de Poisson...")
    modelo_poisson = treinar_modelo()

    categorias = ['A', 'B', 'C', 'D', 'E']
    df_predicao = pd.DataFrame({
        'categoria_adversario': categorias,
        'tipo_jogo': ['Oficial'] * 5
    })
    df_predicao['lambda'] = modelo_poisson.predict(df_predicao)

    dict_lambdas = dict(zip(df_predicao['categoria_adversario'], df_predicao['lambda']))
    print("Lambdas por categoria:", {k: round(v, 2) for k, v in dict_lambdas.items()})
    return dict_lambdas


# ─────────────────────────────────────────────────────────────────────────────
# 2. Probabilidades históricas de eliminação (histórico do Brasil nas Copas)
# ─────────────────────────────────────────────────────────────────────────────
def calcular_probs_historicas(df_gold):
    """
    Deriva as probabilidades de cada cenário de jogos [3, 4, 5, 6, 8]
    a partir do histórico do Brasil nas Copas do Mundo (2002–2022).

    Usa mapeamento por PROFUNDIDADE COMPETITIVA (best-N stage), não por
    número bruto de jogos:
      - old Quartas (best-8, 5 jogos)     → 6 jogos no novo formato 48-team
      - old Semi/Final (best-4+, 7 jogos) → 8 jogos no novo formato 48-team

    Aplica suavização de Jeffreys (alpha=0.5) para cenários nunca observados
    (grupos, 16-avos, oitavas), evitando probabilidade zero.
    """
    wc = df_gold[df_gold['tournament'] == 'FIFA World Cup'].copy()
    wc['ano'] = pd.to_datetime(wc['date']).dt.year

    # Conta jogos por edição (exclui 2026, que está em andamento)
    edicoes = wc[wc['ano'] < 2026].groupby('ano').size()

    def mapear_novo_formato(jogos_old):
        # old Quartas (best-8) = 5 jogos → equivale a Quartas do novo formato = 6 jogos
        # old Semi+Final (best-4+) = 7 jogos → equivale a Semi+Final do novo = 8 jogos
        if jogos_old == 5:
            return 6
        elif jogos_old == 7:
            return 8
        else:
            return jogos_old  # 3 ou 4 permanecem inalterados

    jogos_novo_formato = edicoes.apply(mapear_novo_formato)

    cenarios = [3, 4, 5, 6, 8]
    alpha = 0.5  # Jeffreys prior
    total = len(jogos_novo_formato)
    contagens = jogos_novo_formato.value_counts()

    probs = {c: (contagens.get(c, 0) + alpha) / (total + len(cenarios) * alpha)
             for c in cenarios}
    return probs


# ─────────────────────────────────────────────────────────────────────────────
# 3. Lambdas por fase (distribuição de toda a competição, não só o Brasil)
# ─────────────────────────────────────────────────────────────────────────────
def calcular_lambdas_por_fase(df_results, df_rank, lambdas_modelo):
    """
    Calcula o lambda esperado de cada fase do mata-mata usando a distribuição
    de categorias de TODOS os times que jogaram em cada fase das Copas 2002-2022.

    Mapeamento de fases (por número de jogo na sequência):
      old r16      (game 4, best-16) → new 16-avos  (game 4)
      old quartas  (game 5, best-8)  → new oitavas  (game 5)
      old semi     (game 6, best-4)  → new quartas  (game 6)
      old sf_final (game 7, best-2)  → new semi+final (games 7–8)

    O lambda de cada fase é a média ponderada dos lambdas do modelo
    conforme a proporção histórica de cada categoria naquele game slot.
    """
    df_results = df_results.copy()
    df_results['date'] = pd.to_datetime(df_results['date'])
    df_results['ano'] = df_results['date'].dt.year

    df_rank = df_rank.copy()
    df_rank['rank_date'] = pd.to_datetime(df_rank['rank_date'])

    # Filtra Copas modernas de 32 times (2002–2022)
    wc = df_results[
        (df_results['tournament'] == 'FIFA World Cup') &
        (df_results['ano'].between(2002, 2022))
    ].copy().sort_values(['ano', 'date']).reset_index(drop=True)

    # Atribui fase contando do final de cada edição (estrutura fixa de 64 jogos)
    def assign_phases(edition_df):
        n = len(edition_df)
        edition_df = edition_df.sort_values('date').reset_index(drop=True)
        phases = ['group'] * n
        for i in range(n - 2,  n):      phases[i] = 'sf_final'  # Final + 3º lugar
        for i in range(n - 6,  n - 2):  phases[i] = 'semi'      # Semifinais
        for i in range(n - 14, n - 6):  phases[i] = 'quartas'   # Quartas de final
        for i in range(n - 30, n - 14): phases[i] = 'r16'       # Round of 16
        edition_df['fase_old'] = phases
        return edition_df

    result = pd.concat(
        [assign_phases(grp.copy()) for _, grp in wc.groupby('ano')],
        ignore_index=True
    )
    knockout = result[result['fase_old'] != 'group'].copy()

    # Empilha home e away em uma única coluna 'team'
    home = knockout[['date', 'home_team', 'fase_old']].rename(columns={'home_team': 'team'})
    away = knockout[['date', 'away_team', 'fase_old']].rename(columns={'away_team': 'team'})
    teams = pd.concat([home, away]).sort_values('date').reset_index(drop=True)

    # Cruza com ranking FIFA mais recente antes da data do jogo
    teams = pd.merge_asof(
        teams,
        df_rank[['rank_date', 'country_full', 'rank']].sort_values('rank_date'),
        left_on='date', right_on='rank_date',
        left_by='team', right_by='country_full',
        direction='backward'
    )

    bins = [0, 10, 25, 40, 60, 999]
    label_list = ['A', 'B', 'C', 'D', 'E']
    teams['categoria'] = pd.cut(teams['rank'].fillna(100), bins=bins, labels=label_list)

    # Mapeamento old format → new 48-team format (por posição na sequência de jogos)
    mapa_fases = {
        'r16':      '16avos',   # old game-4 slot → new 16-avos (game 4)
        'quartas':  'oitavas',  # old game-5 slot → new oitavas (game 5)
        'semi':     'quartas',  # old game-6 slot → new quartas (game 6)
        'sf_final': 'semi',     # old game-7 slot → new semi (games 7–8)
    }

    lambdas_fase = {}
    for fase_old, fase_new in mapa_fases.items():
        dist = teams[teams['fase_old'] == fase_old]['categoria'].value_counts(normalize=True)
        lam = sum(
            dist.get(cat, 0) * lambdas_modelo.get(cat, lambdas_modelo['B'])
            for cat in label_list
        )
        lambdas_fase[fase_new] = lam

    # Final usa a mesma distribuição de adversários que a semi
    lambdas_fase['final'] = lambdas_fase['semi']
    return lambdas_fase


# ─────────────────────────────────────────────────────────────────────────────
# 4. Simulação Principal Monte Carlo
# ─────────────────────────────────────────────────────────────────────────────
def simular_gols_brasil(n_simulacoes=100_000):
    # --- Carrega dados ---
    df_gold = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, 'gold_brasil_partidas.csv'))
    df_results = pd.read_csv(os.path.join(RAW_DATA_DIR, 'results.csv'))
    
    ranking_path = os.path.join(RAW_DATA_DIR, 'fifa_ranking-2024-04-04.csv')
    if not os.path.exists(ranking_path):
        ranking_path = os.path.join(RAW_DATA_DIR, 'Fifa_ranking-2024-04-04.csv')
    df_rank = pd.read_csv(ranking_path)

    # --- 1. Lambdas por categoria via modelo de Poisson ---
    lambdas = extrair_lambdas_do_modelo()

    # --- 2. Probabilidades históricas (histórico do Brasil, mapeamento por profundidade) ---
    probs = calcular_probs_historicas(df_gold)
    cenarios_jogos = [3, 4, 5, 6, 8]
    probabilidades = [probs[c] for c in cenarios_jogos]

    # --- 3. Lambdas por fase (distribuição de toda a competição) ---
    lf = calcular_lambdas_por_fase(df_results, df_rank, lambdas)

    # --- Resumo dos parâmetros ---
    print("\n--- PARÂMETROS DA SIMULAÇÃO ---")
    print("\nFase de Grupos (adversários reais 2026):")
    print(f"  Marrocos  (cat. A, rank ~8)  : lambda = {lambdas['A']:.3f}")
    print(f"  Haiti     (cat. E, rank ~90) : lambda = {lambdas['E']:.3f}")
    print(f"  Escócia   (cat. C, rank ~39) : lambda = {lambdas['C']:.3f}")

    print("\nMata-mata (distribuição histórica de toda a competição):")
    print(f"  16-avos  : lambda = {lf['16avos']:.3f}  [dist. old R16:  A=29.7% B=30.7% C=16.1% D=8.9% E=14.6%]")
    print(f"  Oitavas  : lambda = {lf['oitavas']:.3f}  [dist. old QF:   A=45.8% B=31.2% C=8.3%  D=9.4% E=5.2% ]")
    print(f"  Quartas  : lambda = {lf['quartas']:.3f}  [dist. old SF:   A=56.2% B=31.2% C=4.2%  D=4.2% E=4.2% ]")
    print(f"  Semi     : lambda = {lf['semi']:.3f}  [dist. old Final: A=58.3% B=37.5% C=0%    D=0%   E=4.2% ]")
    print(f"  Final    : lambda = {lf['final']:.3f}  [mesma dist. da semi]")

    labels = {3: 'Grupos', 4: '16-avos', 5: 'Oitavas', 6: 'Quartas', 8: 'Semi+Final'}
    print("\nProbabilidades de eliminação (histórico Brasil 2002–2022 + Jeffreys smoothing):")
    for c, p in zip(cenarios_jogos, probabilidades):
        bar = '#' * int(p * 50)
        print(f"  {c} jogos ({labels[c]:<10}): {p*100:5.1f}%  {bar}")

    # --- 4. Laço de simulação ---
    print(f"\nRodando {n_simulacoes:,} simulações Monte Carlo...")
    gols_totais_simulados = []

    for _ in range(n_simulacoes):
        qtd_jogos = np.random.choice(cenarios_jogos, p=probabilidades)
        gols = 0

        # Fase de Grupos: 3 jogos com adversários reais da Copa 2026
        gols += np.random.poisson(lambdas['A'])  # vs Marrocos
        gols += np.random.poisson(lambdas['E'])  # vs Haiti
        gols += np.random.poisson(lambdas['C'])  # vs Escócia

        # Mata-mata condicional (acumula jogos conforme o cenário sorteado)
        if qtd_jogos >= 4:
            gols += np.random.poisson(lf['16avos'])
        if qtd_jogos >= 5:
            gols += np.random.poisson(lf['oitavas'])
        if qtd_jogos >= 6:
            gols += np.random.poisson(lf['quartas'])
        if qtd_jogos == 8:
            gols += np.random.poisson(lf['semi'])    # Semifinal
            gols += np.random.poisson(lf['final'])   # Final ou 3º lugar

        gols_totais_simulados.append(gols)

    # --- 5. Métricas estatísticas ---
    serie = pd.Series(gols_totais_simulados)
    p10   = int(np.percentile(gols_totais_simulados, 10))
    p50   = int(np.percentile(gols_totais_simulados, 50))
    p90   = int(np.percentile(gols_totais_simulados, 90))
    media = np.mean(gols_totais_simulados)
    moda  = int(serie.mode().iloc[0])

    print("\n--- RESULTADO DA SIMULAÇÃO ---")
    print(f"  Média esperada de gols      : {media:.2f}")
    print(f"  Moda (gols mais frequente)  : {moda}")
    print(f"  P10 (pessimista)            : {p10} gols")
    print(f"  P50 (mediana)               : {p50} gols")
    print(f"  P90 (otimista)              : {p90} gols")

    # Distribuição de frequência dos totais mais prováveis
    print("\n  Distribuição dos totais mais frequentes:")
    freq = serie.value_counts(normalize=True).sort_index()
    top = freq[freq >= 0.01]  # mostra apenas valores com >= 1% de frequência
    for gols_val, pct in top.items():
        bar = '#' * int(pct * 100)
        print(f"    {int(gols_val):2d} gols : {pct*100:5.1f}%  {bar}")

    # Exporta para visualização (Power BI / Excel)
    output_path = os.path.join(OUTPUT_DATA_DIR, 'resultados_simulacao.csv')
    pd.DataFrame({'gols_totais': gols_totais_simulados}).to_csv(
        output_path, index=False
    )
    print(f"\nArquivo '{output_path}' exportado com sucesso.")
    return gols_totais_simulados


if __name__ == "__main__":
    simular_gols_brasil()
