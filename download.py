import kaggle
import zipfile
import os

print("Iniciando o download e extração das bases...")

# 1. Baixa o Ranking FIFA
kaggle.api.dataset_download_file(
    'cashncarry/fifaworldranking',
    file_name='fifa_ranking-2024-04-04.csv',
    path='.'
)

# 2. Baixa o Histórico de Partidas
kaggle.api.dataset_download_files(
    'martj42/international-football-results-from-1872-to-2017',
    path='.',
    unzip=True
)

# 3. Descompacta o arquivo do Ranking
arquivo_zip_ranking = 'fifa_ranking-2024-04-04.csv.zip'
if os.path.exists(arquivo_zip_ranking):
    with zipfile.ZipFile(arquivo_zip_ranking, 'r') as zip_ref:
        zip_ref.extractall('.')
    # Opcional: apaga o arquivo .zip para manter a pasta limpa
    os.remove(arquivo_zip_ranking)

print("Tudo pronto! Arquivos CSV extraídos com sucesso na sua pasta.")