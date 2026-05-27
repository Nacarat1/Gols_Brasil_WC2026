import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from scipy.interpolate import make_interp_spline

# 1. Carregar os dados simulados
try:
    df = pd.read_csv('resultados_simulacao.csv')
    gols = df['gols_totais'].values
except FileNotFoundError:
    import monte_carlo
    gols = np.array(monte_carlo.simular_gols_brasil())

# 2. Métricas
p10 = int(np.percentile(gols, 10))
p50 = int(np.percentile(gols, 50))
p90 = int(np.percentile(gols, 90))
media = np.mean(gols)
valores, contagem = np.unique(gols, return_counts=True)
freq_relativa = (contagem / len(gols)) * 100
dict_freq = dict(zip(valores, freq_relativa))
gols_eixo = np.arange(0, 21)  # Limitar a 20 gols para visualização limpa
freq_eixo = np.array([dict_freq.get(g, 0.0) for g in gols_eixo])
acumulada_eixo = np.cumsum(freq_eixo)

# 3. Design System (Tema Light Executive: Azul e Branco)
bg_color = '#FFFFFF'       # Fundo branco puro
card_color = '#F8FAFC'     # Slate 50 (Cinza claríssimo para dar forma aos cards)
card_edge = '#E2E8F0'      # Cinza de borda discreta
primary_blue = '#1E73BE'   # Azul clássico para destaque e título
secondary_blue = '#3A90E3' # Azul médio para barras
muted_text = '#64748B'     # Slate 500 (Texto secundário)
light_text = '#0F172A'     # Slate 900 (Texto principal escuro no fundo branco)
accent_orange = '#D97706'  # Amber 600 (Para alertas/mínimos)
accent_green = '#059669'   # Emerald 600 (Para a mediana/meta)
grid_color = '#E2E8F0'     # Slate 200 (Grids claras)

# Configurar Matplotlib para tema claro
plt.rcParams['text.color'] = light_text
plt.rcParams['axes.labelcolor'] = light_text
plt.rcParams['xtick.color'] = muted_text
plt.rcParams['ytick.color'] = muted_text
plt.rcParams['font.family'] = 'sans-serif'

# Criar a figura principal com proporção de infográfico vertical (13 x 10 para acomodar legenda inferior)
fig = plt.figure(figsize=(13, 10), facecolor=bg_color)

# GridSpec com proporção vertical ajustada para comprimir cards e expandir o gráfico
# Altura da Linha 0 (Header): 0.7
# Altura da Linha 1 (KPIs muito compactos): 0.8
# Altura da Linha 2 (Gráfico principal): 5.0
gs = GridSpec(3, 3, figure=fig, height_ratios=[0.7, 0.8, 5.0], width_ratios=[1, 1, 1])

# --- HEADER (Título principal) ---
ax_header = fig.add_subplot(gs[0, :])
ax_header.set_facecolor(bg_color)
ax_header.axis('off')
ax_header.text(0.01, 0.70, 'PREVISÃO DE GOLS DA SELEÇÃO BRASILEIRA — COPA 2026', 
               fontsize=20, fontweight='bold', color=primary_blue)
ax_header.text(0.01, 0.35, 'Simulação de Monte Carlo por Regressão de Poisson | 100.000 Campanhas Simuladas', 
               fontsize=13, color=light_text, fontweight='bold')
ax_header.text(0.01, 0.05, 'Regulamento de 48 seleções | Modelo treinado com dados Históricos do Século XXI', 
               fontsize=11, color=muted_text, fontweight='semibold')

# --- CARDS DE METRICAS CHAVE (KPIs compactos na segunda linha) ---
# Card 1: P10 (Pessimista)
ax_kpi1 = fig.add_subplot(gs[1, 0])
ax_kpi1.set_facecolor(card_color)
ax_kpi1.grid(False)
ax_kpi1.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
for spine in ax_kpi1.spines.values():
    spine.set_color(card_edge)
    spine.set_linewidth(1)
ax_kpi1.spines['left'].set_color(accent_orange)
ax_kpi1.spines['left'].set_linewidth(4)
ax_kpi1.text(0.08, 0.65, 'CENÁRIO PESSIMISTA (P10)', fontsize=9.5, color=muted_text, fontweight='bold')
ax_kpi1.text(0.08, 0.18, f'{p10} Gols', fontsize=20, color=accent_orange, fontweight='black')

# Card 2: P50 (Mais Provável/Mediana)
ax_kpi2 = fig.add_subplot(gs[1, 1])
ax_kpi2.set_facecolor(card_color)
ax_kpi2.grid(False)
ax_kpi2.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
for spine in ax_kpi2.spines.values():
    spine.set_color(card_edge)
    spine.set_linewidth(1)
ax_kpi2.spines['left'].set_color(primary_blue)
ax_kpi2.spines['left'].set_linewidth(4)
ax_kpi2.text(0.08, 0.65, 'VALOR PROVÁVEL (P50)', fontsize=9.5, color=muted_text, fontweight='bold')
ax_kpi2.text(0.08, 0.18, f'{p50} Gols', fontsize=20, color=light_text, fontweight='black')

# Card 3: P90 (Otimista)
ax_kpi3 = fig.add_subplot(gs[1, 2])
ax_kpi3.set_facecolor(card_color)
ax_kpi3.grid(False)
ax_kpi3.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
for spine in ax_kpi3.spines.values():
    spine.set_color(card_edge)
    spine.set_linewidth(1)
ax_kpi3.spines['left'].set_color(accent_green)
ax_kpi3.spines['left'].set_linewidth(4)
ax_kpi3.text(0.08, 0.65, 'CENÁRIO OTIMISTA (P90)', fontsize=9.5, color=muted_text, fontweight='bold')
ax_kpi3.text(0.08, 0.18, f'{p90} Gols', fontsize=20, color=accent_green, fontweight='black')

# --- GRÁFICO PRINCIPAL DE DISTRIBUIÇÃO ---
ax_chart = fig.add_subplot(gs[2, :])
ax_chart.set_facecolor(bg_color)
ax_chart.grid(True, linestyle='--', alpha=0.6, color=grid_color)
ax_chart.spines['top'].set_visible(False)
ax_chart.spines['right'].set_visible(False)
ax_chart.spines['left'].set_color(card_edge)
ax_chart.spines['bottom'].set_color(card_edge)

# Plotar as barras de frequência em azul
bars = ax_chart.bar(gols_eixo, freq_eixo, color=secondary_blue, edgecolor=primary_blue, 
                    linewidth=0.5, alpha=0.9, width=0.72, zorder=3, label='Probabilidade do Total')

# Ajustar eixos do gráfico principal
ax_chart.set_xticks(gols_eixo)
ax_chart.set_xticklabels(gols_eixo, fontsize=10, fontweight='bold', color=light_text)
ax_chart.set_xlim(-0.7, 20.7)
ax_chart.set_ylim(0, max(freq_eixo) * 1.15)
ax_chart.set_ylabel('Frequência Relativa (%)', fontsize=11, fontweight='bold', color=light_text)

# Adicionar rótulos de % em cima das barras principais
for bar in bars:
    height = bar.get_height()
    if height >= 0.8:  # Mostrar rótulo para chances maiores ou iguais a 0.8%
        ax_chart.annotate(f'{height:.1f}%',
                          xy=(bar.get_x() + bar.get_width() / 2, height),
                          xytext=(0, 4), textcoords="offset points",
                          ha='center', va='bottom', fontsize=8.5, color=light_text, fontweight='semibold')

# Obter o limite superior do eixo Y para posicionar as labels no topo
y_top_limit = ax_chart.get_ylim()[1]

# Linhas verticais de referência no gráfico com rótulos posicionados no topo (evitando sobrepor barras)
ax_chart.axvline(x=p10, color=accent_orange, linestyle=':', linewidth=1.8, alpha=0.9, zorder=5)
ax_chart.text(p10 - 0.12, y_top_limit * 0.95, f'P10 ({p10} gols)', color=accent_orange, ha='right', fontweight='bold', fontsize=9.5)

ax_chart.axvline(x=p50, color=primary_blue, linestyle='-.', linewidth=1.8, alpha=0.9, zorder=5)
ax_chart.text(p50 + 0.12, y_top_limit * 0.95, f'P50 ({p50} gols)', color=primary_blue, ha='left', fontweight='bold', fontsize=9.5)

ax_chart.axvline(x=p90, color=accent_green, linestyle=':', linewidth=1.8, alpha=0.9, zorder=5)
ax_chart.text(p90 + 0.12, y_top_limit * 0.95, f'P90 ({p90} gols)', color=accent_green, ha='left', fontweight='bold', fontsize=9.5)

# Linhas de probabilidade acumulada (eixo secundário)
ax_accum = ax_chart.twinx()
ax_accum.grid(False)
ax_accum.spines['top'].set_visible(False)
ax_accum.spines['left'].set_visible(False)
ax_accum.spines['right'].set_color(card_edge)

# Suavização da linha acumulada
gols_suave = np.linspace(gols_eixo.min(), gols_eixo.max(), 300)
spl = make_interp_spline(gols_eixo, acumulada_eixo, k=3)
acumulada_suave = np.clip(spl(gols_suave), 0, 100)

ax_accum.plot(gols_suave, acumulada_suave, color='#0F172A', linewidth=2.0, linestyle='-', alpha=0.4, label='Prob. Acumulada')
ax_accum.scatter(gols_eixo, acumulada_eixo, color='#0F172A', edgecolor='white', s=25, alpha=0.6, zorder=5)
ax_accum.set_ylim(0, 105)
ax_accum.set_ylabel('Probabilidade Acumulada (%)', fontsize=11, fontweight='bold', color=muted_text)
ax_accum.set_yticks(np.arange(0, 101, 20))
ax_accum.set_yticklabels([f'{y}%' for y in np.arange(0, 101, 20)], color=muted_text, fontsize=9.5)

# --- LEGENDA TÉCNICA OBRIGATÓRIA (Rodapé) ---
# Mantendo o texto original solicitado integralmente
rodape_texto = (
    "Premissas do Modelo:\n"
    "• Lambdas por Categoria: A = 1.15 | B = 1.45 | C = 1.90 | D = 1.70 | E = 2.60\n"
    "• Fase de Grupos 2026: Jogo 1 vs Marrocos (A), Jogo 2 vs Haiti (E), Jogo 3 vs Escócia (C)\n"
    "• Probabilidade de jogar: Grupos (100%) | 16avos (93.3%) | Oitavas (73.3%) | Quartas (53.3%) | Semi (33.3%)"
)

# Adicionar a caixa com as premissas exatamente na parte inferior da figura com fonte maior e mais grossa (otimização LinkedIn)
plt.figtext(0.06, 0.02, rodape_texto, ha='left', fontsize=10.5, color='#0F172A', fontweight='semibold',
            bbox=dict(facecolor='#F8FAFC', edgecolor='#E2E8F0', boxstyle='round,pad=1.0', alpha=1.0))

# Ajuste da disposição dos subplots para focar no gráfico e deixar espaço para o rodapé técnico
gs.update(left=0.06, right=0.94, top=0.93, bottom=0.15, wspace=0.18, hspace=0.35)

ax_header.set_subplotspec(gs[0, :])
ax_kpi1.set_subplotspec(gs[1, 0])
ax_kpi2.set_subplotspec(gs[1, 1])
ax_kpi3.set_subplotspec(gs[1, 2])
ax_chart.set_subplotspec(gs[2, :])

# Salvar o infográfico com resolução ultra premium (400 DPI)
output_path = 'dashboard_monte_carlo_gols.png'
plt.savefig(output_path, bbox_inches='tight', facecolor=bg_color, dpi=400)
print(f"Painel visual premium exportado com sucesso em 400 DPI: {output_path}")
