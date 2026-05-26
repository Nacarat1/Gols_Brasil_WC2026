import pandas as pd
import statsmodels.formula.api as smf

def treinar_modelo():
    print("Carregando base de dados Ouro...")
    df = pd.read_csv('gold_brasil_partidas.csv')
    
    # 1. Engenharia de Features Adicional
    # Agrupar torneios em 'Amistoso' ou 'Oficial' reduz o ruído para o modelo
    df['tipo_jogo'] = df['tournament'].apply(lambda x: 'Amistoso' if x == 'Friendly' else 'Oficial')
    
    # Remover jogos com dados nulos nas colunas que vamos usar
    df = df.dropna(subset=['gols_brasil', 'categoria_adversario'])
    
    print("Treinando o modelo de Regressão de Poisson...")
    # 2. A Fórmula Estatística
    # Lê-se: "Gols do Brasil são explicados pela Categoria do Adversário e pelo Tipo de Jogo"
    formula = 'gols_brasil ~ C(categoria_adversario) + C(tipo_jogo)'
    
    # Treinamento do modelo
    modelo = smf.poisson(formula, data=df).fit(disp=0)
    
    # 3. Exibir o resumo matemático
    print("\n--- RESUMO DO MODELO ---")
    print(modelo.summary())
    
    return modelo

def prever_lambda(modelo):
    print("\n--- TESTE DE PREVISÃO DE LAMBDA ---")
    # Vamos simular 3 cenários diferentes da Copa para ver qual Lambda o modelo cospe
    cenarios = pd.DataFrame({
        'categoria_adversario': ['E', 'C', 'A'],
        'tipo_jogo': ['Oficial', 'Oficial', 'Oficial'],
        'cenario': ['Fase de Grupos (Time Fraco)', 'Oitavas (Time Médio)', 'Final (Time Forte)']
    })
    
    # O modelo prevê o Lambda (esperança matemática de gols)
    cenarios['lambda_esperado'] = modelo.predict(cenarios)
    
    for _, row in cenarios.iterrows():
        print(f"Cenário: {row['cenario']} | Categoria: {row['categoria_adversario']}")
        print(f"Gols Esperados (Lambda): {row['lambda_esperado']:.2f}\n")

if __name__ == "__main__":
    # Garanta que a biblioteca está instalada: pip install statsmodels
    modelo_treinado = treinar_modelo()
    prever_lambda(modelo_treinado)