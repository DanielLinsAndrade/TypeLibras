import os
from jiwer import wer


def comparar_com_transcricao(caminho_audio, texto_reconhecido):
    caminho_txt = os.path.splitext(caminho_audio)[0] + ".txt"

    if not os.path.exists(caminho_txt):
        return None

    with open(caminho_txt, "r", encoding="utf-8", errors="ignore") as arquivo:
        texto_original = arquivo.read().strip()

    return wer(texto_original.lower(), texto_reconhecido.lower())