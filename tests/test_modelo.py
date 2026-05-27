import pandas as pd
import numpy as np
import pytest
import os
from src.modelo import treinar_modelo

def test_treinar_modelo(tmp_path, monkeypatch):
    # Cria uma pasta temporária para simular o diretório de dados processados
    d = tmp_path / "data" / "processed"
    d.mkdir(parents=True)
    gold_file = d / "gold_brasil_partidas.csv"
    
    # Cria dados artificiais mínimos para o modelo rodar sem erros
    # Precisamos de categorias variadas ou de dados consistentes
    df_dummy = pd.DataFrame({
        'date': ['2026-01-01'] * 10,
        'tournament': ['Friendly'] * 5 + ['FIFA World Cup'] * 5,
        'adversario': ['Argentina'] * 10,
        'categoria_adversario': ['A', 'B', 'C', 'D', 'E', 'A', 'B', 'C', 'D', 'E'],
        'rank': [1, 12, 30, 50, 100, 1, 12, 30, 50, 100],
        'gols_brasil': [2, 1, 3, 0, 4, 1, 2, 2, 1, 3],
        'gols_adversario': [0] * 10
    })
    df_dummy.to_csv(gold_file, index=False)
    
    # Modifica o caminho do PROCESSED_DATA_DIR do script modelo para apontar para nossa pasta temporária
    monkeypatch.setattr("src.modelo.PROCESSED_DATA_DIR", str(d))
    
    modelo = treinar_modelo()
    assert modelo is not None
    
    # Valida previsões
    cenarios = pd.DataFrame({
        'categoria_adversario': ['A'],
        'tipo_jogo': ['Oficial']
    })
    pred = modelo.predict(cenarios)
    assert len(pred) == 1
    assert pred.iloc[0] > 0
