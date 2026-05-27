import pandas as pd
import numpy as np
import pytest
from src.etl import transform_silver, transform_gold

def test_transform_silver():
    # Dados fictícios para teste
    df_jogos = pd.DataFrame({
        'date': ['2002-06-30', '1994-07-17'],
        'home_team': ['Brazil', 'Brazil'],
        'away_team': ['Germany', 'Italy'],
        'home_score': [2, 0],
        'away_score': [0, 0],
        'tournament': ['FIFA World Cup', 'FIFA World Cup']
    })
    df_ranking = pd.DataFrame({
        'rank_date': ['2002-06-15', '1994-07-01'],
        'country_full': ['Germany', 'Italy'],
        'rank': [8, 4]
    })
    
    df_br, df_rank = transform_silver(df_jogos, df_ranking)
    
    # Deve filtrar apenas jogos do Século XXI (>= 2001)
    assert len(df_br) == 1
    assert df_br.iloc[0]['adversario'] == 'Germany'
    assert df_br.iloc[0]['gols_brasil'] == 2
    assert df_br.iloc[0]['gols_adversario'] == 0

def test_transform_gold():
    df_br = pd.DataFrame({
        'date': [pd.to_datetime('2002-06-30')],
        'tournament': ['FIFA World Cup'],
        'adversario': ['Germany'],
        'gols_brasil': [2],
        'gols_adversario': [0]
    })
    df_ranking = pd.DataFrame({
        'rank_date': [pd.to_datetime('2002-06-15')],
        'country_full': ['Germany'],
        'rank': [8]
    })
    
    df_gold = transform_gold(df_br, df_ranking)
    
    assert len(df_gold) == 1
    assert df_gold.iloc[0]['categoria_adversario'] == 'A'  # Rank 8 está na Categoria A (0-10)
    assert df_gold.iloc[0]['rank'] == 8
