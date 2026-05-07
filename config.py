"""
Arquivo de configurações globais da aplicação.

Este módulo centraliza constantes utilizadas em diferentes partes
do sistema, incluindo parâmetros de áudio, modelo Whisper e
configurações visuais da interface.
"""

# Caminho da pasta que armazena os arquivos de áudio do dataset
PASTA_DATASET = "dataset"

# Modelo Whisper utilizado no reconhecimento de fala
MODELO_WHISPER = "small"

# Duração, em segundos, dos blocos capturados ao vivo
DURACAO_BLOCO = 4

# Duração, em segundos, da gravação utilizada pela DNN
DURACAO_DNN = 2

# Taxa de amostragem dos áudios utilizados no sistema
TAXA_AMOSTRAGEM = 16000

# Fonte utilizada em títulos da interface
FONTE_TITULO = ("Arial", 18, "bold")

# Fonte padrão utilizada em textos da interface
FONTE_NORMAL = ("Arial", 13)

# Fonte utilizada para representação visual em Libras
FONTE_LIBRAS = ("Sutton BR", 16)
