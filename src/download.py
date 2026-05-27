import os
import zipfile
import kaggle

# Caminho relativo ao diretório do script para localizar o diretório 'data/raw'
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DATA_DIR = os.path.join(BASE_DIR, 'data', 'raw')

os.makedirs(RAW_DATA_DIR, exist_ok=True)

print("Iniciando o download e extração das bases...")

# 1. Baixa o Ranking FIFA
kaggle.api.dataset_download_file(
    'cashncarry/fifaworldranking',
    file_name='fifa_ranking-2024-04-04.csv',
    path=RAW_DATA_DIR
)

# 2. Baixa o Histórico de Partidas
kaggle.api.dataset_download_files(
    'martj42/international-football-results-from-1872-to-2017',
    path=RAW_DATA_DIR,
    unzip=True
)

# 3. Descompacta o arquivo do Ranking
arquivo_zip_ranking = os.path.join(RAW_DATA_DIR, 'fifa_ranking-2024-04-04.csv.zip')
if os.path.exists(arquivo_zip_ranking):
    with zipfile.ZipFile(arquivo_zip_ranking, 'r') as zip_ref:
        zip_ref.extractall(RAW_DATA_DIR)
    # Opcional: apaga o arquivo .zip para manter a pasta limpa
    os.remove(arquivo_zip_ranking)

print(f"Tudo pronto! Arquivos CSV extraídos com sucesso em {RAW_DATA_DIR}.")
