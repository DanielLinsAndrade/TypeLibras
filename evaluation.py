"""
Módulo de avaliação de reconhecimento de fala.

Este módulo compara o texto reconhecido pelo sistema com a
transcrição original utilizando a métrica WER.
"""

# Biblioteca padrão para manipulação de arquivos
import os

# Biblioteca para cálculo da taxa de erro de palavras
from jiwer import wer


def comparar_com_transcricao(
    caminho_audio,
    texto_reconhecido
):
    """
    Compara a transcrição reconhecida com a original.

    O método procura um arquivo .txt com o mesmo nome do áudio e
    calcula a métrica WER entre os textos.

    Parâmetros

    caminho_audio : str
        Caminho do arquivo de áudio analisado.

    texto_reconhecido : str
        Texto gerado pelo reconhecimento de fala.

    Retornos

    float | None
        Valor da métrica WER caso exista transcrição original.
        Retorna None caso o arquivo .txt não seja encontrado.
    """

    # Define o caminho esperado do arquivo de transcrição
    caminho_txt = (
        os.path.splitext(caminho_audio)[0]
        + ".txt"
    )

    # Verifica se o arquivo de transcrição existe
    if not os.path.exists(caminho_txt):
        return None

    # Abre o arquivo de transcrição original
    with open(
        caminho_txt,
        "r",
        encoding="utf-8",
        errors="ignore"
    ) as arquivo:

        # Lê e limpa o conteúdo da transcrição
        texto_original = arquivo.read().strip()

    # Calcula e retorna a métrica WER
    return wer(
        texto_original.lower(),
        texto_reconhecido.lower()
    )
