import pandas as pd
import numpy as np

def extract_bronze():
    print("Iniciando extração da camada Bronze...")
    # ATENÇÃO: Verifique se o nome exato do arquivo do ranking bate com o que foi baixado
    df_jogos = pd.read_csv('results.csv')
    df_ranking = pd.read_csv('Fifa_ranking-2024-04-04.csv') # Pode estar como fifa_ranking-2024-04-04.csv
    return df_jogos, df_ranking

def transform_silver(df_jogos, df_ranking):
    print("Processando camada Silver (Limpeza e Padronização)...")
    
    # 1. Tipagem de Dados (Datas)
    df_jogos['date'] = pd.to_datetime(df_jogos['date'])
    df_ranking['rank_date'] = pd.to_datetime(df_ranking['rank_date'])
    
    # 2. Filtro de Negócio: Apenas jogos do Brasil no Século XXI
    df_br = df_jogos[
        ((df_jogos['home_team'] == 'Brazil') | (df_jogos['away_team'] == 'Brazil')) & 
        (df_jogos['date'].dt.year >= 2001)
    ].copy()
    
    # 3. Pivotamento de Colunas: Isolar 'Adversário', 'Gols do Brasil' e 'Gols do Adversário'
    df_br['adversario'] = np.where(df_br['home_team'] == 'Brazil', df_br['away_team'], df_br['home_team'])
    df_br['gols_brasil'] = np.where(df_br['home_team'] == 'Brazil', df_br['home_score'], df_br['away_score'])
    df_br['gols_adversario'] = np.where(df_br['home_team'] == 'Brazil', df_br['away_score'], df_br['home_score'])
    
    # 4. Padronização de Nomenclatura (Dicionário De-Para)
    # A base de jogos e a base do ranking possuem nomes diferentes para os mesmos países.
    mapa_paises = {
        'United States': 'USA',
        'South Korea': 'Korea Republic',
        'North Korea': 'Korea DPR',
        'Ivory Coast': "Côte d'Ivoire",
        'Bosnia-Herzegovina': 'Bosnia and Herzegovina'
    }
    df_br['adversario'] = df_br['adversario'].replace(mapa_paises)
    
    # 5. Ordenação obrigatória para o cruzamento temporal
    df_br = df_br.sort_values('date')
    df_ranking = df_ranking.sort_values('rank_date')
    
    return df_br, df_ranking

def transform_gold(df_br, df_ranking):
    print("Processando camada Gold (Cruzamento e Regras de Negócio)...")
    
    # 1. O Cruzamento: Trazendo o ranking na data exata da partida
    df_gold = pd.merge_asof(
        df_br, 
        df_ranking[['rank_date', 'country_full', 'rank']], 
        left_on='date', 
        right_on='rank_date', 
        left_by='adversario', 
        right_by='country_full',
        direction='backward'
    )
    
    # 2. Tratamento de Exceções (Países sem ranking na data)
    # Vamos preencher temporariamente com um ranking muito baixo (ex: 100) para não perder a linha
    df_gold['rank'] = df_gold['rank'].fillna(100)
    
    # 3. Engenharia de Features: As Categorias (A, B, C, D, E)
    bins = [0, 10, 25, 40, 60, 999]
    labels = ['A', 'B', 'C', 'D', 'E']
    df_gold['categoria_adversario'] = pd.cut(df_gold['rank'], bins=bins, labels=labels)
    
    # 4. Seleção final das colunas úteis para o modelo
    colunas_finais = [
        'date', 'tournament', 'adversario', 'categoria_adversario', 'rank', 
        'gols_brasil', 'gols_adversario'
    ]
    return df_gold[colunas_finais]

def main():
    # Orquestração do Pipeline ETL
    df_jogos, df_ranking = extract_bronze()
    df_br_silver, df_ranking_silver = transform_silver(df_jogos, df_ranking)
    df_gold = transform_gold(df_br_silver, df_ranking_silver)
    
    # Load (Salvando o artefato final)
    df_gold.to_csv('gold_brasil_partidas.csv', index=False)
    print("ETL Concluído! O arquivo 'gold_brasil_partidas.csv' foi gerado com sucesso.")
    print(f"Total de partidas processadas: {len(df_gold)}")

if __name__ == "__main__":
    main()