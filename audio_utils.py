"""
Utilitários de áudio utilizados pela aplicação.

Este módulo contém funções responsáveis pela configuração do
FFmpeg e pela gravação de áudio do microfone.
"""

# Biblioteca padrão para manipulação de arquivos e caminhos
import os

# Biblioteca para execução de processos externos
import subprocess

# Biblioteca para criação de arquivos temporários
import tempfile

# Biblioteca para gerenciamento automático do FFmpeg
import imageio_ffmpeg

# Biblioteca para captura de áudio do microfone
import sounddevice as sd

# Função para salvar arquivos WAV
from scipy.io.wavfile import write


def configurar_ffmpeg():
    """
    Configura o FFmpeg para utilização na aplicação.

    O método adiciona o diretório do FFmpeg ao PATH do sistema e
    verifica se o executável está funcionando corretamente.
    """

    # Obtém o caminho do executável do FFmpeg
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

    # Obtém o diretório do executável
    ffmpeg_dir = os.path.dirname(ffmpeg_exe)

    # Adiciona o FFmpeg ao PATH do sistema
    os.environ["PATH"] = (
        ffmpeg_dir
        + os.pathsep
        + os.environ["PATH"]
    )

    # Verifica se o FFmpeg está funcionando corretamente
    subprocess.run(
        [ffmpeg_exe, "-version"],
        check=True
    )


def gravar_audio(
    caminho_audio,
    duracao,
    taxa_amostragem
):
    """
    Grava áudio do microfone e salva em arquivo WAV.

    Parâmetros

    caminho_audio : str
        Caminho do arquivo de saída.

    duracao : int | float
        Duração da gravação em segundos.

    taxa_amostragem : int
        Taxa de amostragem utilizada na captura.

    Retornos

    str
        Caminho do arquivo de áudio gerado.
    """

    # Inicia a gravação do áudio
    audio = sd.rec(
        int(duracao * taxa_amostragem),
        samplerate=taxa_amostragem,
        channels=1,
        dtype="int16"
    )

    # Aguarda o término da gravação
    sd.wait()

    # Salva o áudio em formato WAV
    write(
        caminho_audio,
        taxa_amostragem,
        audio
    )

    # Retorna o caminho do arquivo gerado
    return caminho_audio


def gravar_audio_temporario(
    duracao,
    taxa_amostragem
):
    """
    Grava áudio temporário do microfone.

    O método cria um arquivo temporário WAV, grava o áudio e
    retorna o caminho do arquivo gerado.

    Parâmetros

    duracao : int | float
        Duração da gravação em segundos.

    taxa_amostragem : int
        Taxa de amostragem utilizada na captura.

    Retornos

    str
        Caminho do arquivo temporário criado.
    """

    # Cria um arquivo temporário WAV
    with tempfile.NamedTemporaryFile(
        suffix=".wav",
        delete=False
    ) as temp_audio:

        # Armazena o caminho do arquivo temporário
        caminho_temp = temp_audio.name

    # Grava áudio no arquivo temporário
    gravar_audio(
        caminho_temp,
        duracao,
        taxa_amostragem
    )

    # Retorna o caminho do arquivo temporário
    return caminho_temp
