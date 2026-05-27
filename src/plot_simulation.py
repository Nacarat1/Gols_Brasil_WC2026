import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DATA_DIR = os.path.join(BASE_DIR, 'data', 'output')

# 1. Carregar os dados simulados
try:
    df = pd.read_csv(os.path.join(OUTPUT_DATA_DIR, 'resultados_simulacao.csv'))
    gols = df['gols_totais'].values
except FileNotFoundError:
    print("Executando a simulação primeiro para gerar resultados_simulacao.csv...")
    try:
        import monte_carlo
    except ImportError:
        from src import monte_carlo
    gols = monte_carlo.simular_gols_brasil()
    gols = np.array(gols)

# 2. Calcular estatísticas descritivas
p10 = int(np.percentile(gols, 10))
p50 = int(np.percentile(gols, 50))
p90 = int(np.percentile(gols, 90))
media = np.mean(gols)

# Calcular frequência relativa
valores, contagem = np.unique(gols, return_counts=True)
freq_relativa = (contagem / len(gols)) * 100

# Dicionário mapeando gol -> frequência %
dict_freq = dict(zip(valores, freq_relativa))
gols_eixo = np.arange(0, max(valores) + 1)
freq_eixo = np.array([dict_freq.get(g, 0.0) for g in gols_eixo])

# Calcular probabilidade acumulada (%)
acumulada_eixo = np.cumsum(freq_eixo)

# 3. Estilo e Layout Moderno (Aesthetics Premium)
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
fig, ax1 = plt.subplots(figsize=(11, 7.5), dpi=300)

# Cores e fontes
primary_color = '#1E73BE'  # Azul premium do gráfico original
accent_color = '#1C3D5A'   # Azul escuro para a linha acumulada
grid_color = '#E9ECEF'
text_color = '#333333'
font_family = 'sans-serif'

# Configurar fontes padrão
plt.rcParams['font.family'] = font_family
plt.rcParams['text.color'] = text_color

# Grid
ax1.grid(True, linestyle='--', alpha=0.5, color=grid_color, zorder=0)

# Eixo 1 (Barras - Frequência Relativa)
bars = ax1.bar(gols_eixo, freq_eixo, color=primary_color, edgecolor='#155A96', linewidth=0.5, alpha=0.9, width=0.75, label='Frequência Relativa', zorder=3)
ax1.set_xlabel('Total de gols do Brasil na Copa', fontsize=12, labelpad=12, fontweight='bold', color=text_color)
ax1.set_ylabel('Frequência Relativa (%)', fontsize=12, labelpad=12, fontweight='bold', color=text_color)
ax1.set_xticks(gols_eixo)
ax1.set_xticklabels(gols_eixo, fontsize=10)
ax1.set_xlim(-0.7, max(gols_eixo) + 0.7)
ax1.set_ylim(0, max(freq_eixo) * 1.15)

# Adicionar porcentagens acima das barras
for bar in bars:
    height = bar.get_height()
    if height >= 0.1:  # Só mostra se for relevante (>= 0.1%)
        ax1.annotate(f'{height:.1f}%',
                     xy=(bar.get_x() + bar.get_width() / 2, height),
                     xytext=(0, 4),  # 4 pontos de offset vertical
                     textcoords="offset points",
                     ha='center', va='bottom', fontsize=8, color='#444444', fontweight='semibold')

# Eixo 2 (Linha - Probabilidade Acumulada)
ax2 = ax1.twinx()
ax2.grid(False) # Não duplicar o grid

# Criar curva suavizada (spline) para a probabilidade acumulada
gols_suave = np.linspace(gols_eixo.min(), gols_eixo.max(), 300)
spl = make_interp_spline(gols_eixo, acumulada_eixo, k=3)
acumulada_suave = spl(gols_suave)
# Garantir limites físicos da probabilidade acumulada
acumulada_suave = np.clip(acumulada_suave, 0, 100)

# Plotar linha suave e marcadores nos pontos originais
ax2.plot(gols_suave, acumulada_suave, color=accent_color, linewidth=2, label='Probabilidade Acumulada', zorder=4)
ax2.scatter(gols_eixo, acumulada_eixo, color=accent_color, edgecolor='white', s=35, zorder=5)

ax2.set_ylabel('Probabilidade Acumulada (%)', fontsize=12, labelpad=12, fontweight='bold', color=text_color)
ax2.set_ylim(0, 105)
ax2.set_yticks(np.arange(0, 101, 10))
ax2.set_yticklabels([f'{y}%' for y in np.arange(0, 101, 10)], fontsize=10)

# 4. Linhas de Referência Estatística (P10, Média, P50, P90)
# P10
ax1.axvline(x=p10, color='#E28743', linestyle=':', linewidth=2, zorder=6)
ax1.text(p10 - 0.1, ax1.get_ylim()[1] * 0.93, f'P10 = {p10}', color='#E28743', ha='right', fontweight='bold', fontsize=9.5)

# Média
ax1.axvline(x=media, color='#C33C54', linestyle='--', linewidth=1.5, zorder=6)
ax1.text(media + 0.1, ax1.get_ylim()[1] * 0.93, f'Média = {media:.1f}', color='#C33C54', ha='left', fontweight='bold', fontsize=9.5)

# P50 / Mediana
ax1.axvline(x=p50, color='#25A18E', linestyle='-.', linewidth=2, zorder=6)
ax1.text(p50 + 0.1, ax1.get_ylim()[1] * 0.86, f'P50 = {p50}', color='#25A18E', ha='left', fontweight='bold', fontsize=9.5)

# P90
ax1.axvline(x=p90, color='#8E44AD', linestyle=':', linewidth=2, zorder=6)
ax1.text(p90 + 0.1, ax1.get_ylim()[1] * 0.93, f'P90 = {p90}', color='#8E44AD', ha='left', fontweight='bold', fontsize=9.5)

# Título Principal e Legenda do Gráfico
plt.title('Simulação Monte Carlo — Gols do Brasil na Copa 2026', fontsize=16, fontweight='bold', pad=25, color=accent_color)

# Rodapé com Premissas
rodape_texto = (
    "Premissas do Modelo:\n"
    "• Lambdas por Categoria: A = 1.15 | B = 1.45 | C = 1.90 | D = 1.70 | E = 2.60  (Treinados com histórico do Brasil no séc. XXI)\n"
    "• Fase de Grupos 2026 (adversários reais): Jogo 1 vs Marrocos (A), Jogo 2 vs Haiti (E), Jogo 3 vs Escócia (C)\n"
    "• Probabilidade de Avançar (Histórico Brasil): Grupos (100%) | 16avos (93.3%) | Oitavas (73.3%) | Quartas (53.3%) | Semi (33.3%)"
)

# Adicionar a caixa com as premissas na parte inferior
plt.figtext(0.1, 0.01, rodape_texto, ha='left', fontsize=8.5, color='#555555',
            bbox=dict(facecolor='#F8F9FA', edgecolor='#E9ECEF', boxstyle='round,pad=0.8', alpha=0.9))

# Ajustar layout para não cortar elementos
plt.subplots_adjust(bottom=0.20, top=0.90)

# Salvar gráfico em formato PNG de alta resolução para o post
output_image_path = os.path.join(OUTPUT_DATA_DIR, 'simulacao_monte_carlo_gols_brasil.png')
plt.savefig(output_image_path, bbox_inches='tight', dpi=300)
print(f"Gráfico salvo com sucesso em: {output_image_path}")
