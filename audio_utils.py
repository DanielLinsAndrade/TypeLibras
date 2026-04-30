import os
import subprocess
import tempfile

import imageio_ffmpeg
import sounddevice as sd
from scipy.io.wavfile import write


def configurar_ffmpeg():
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    ffmpeg_dir = os.path.dirname(ffmpeg_exe)

    os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ["PATH"]

    subprocess.run([ffmpeg_exe, "-version"], check=True)


def gravar_audio(caminho_audio, duracao, taxa_amostragem):
    audio = sd.rec(
        int(duracao * taxa_amostragem),
        samplerate=taxa_amostragem,
        channels=1,
        dtype="int16"
    )

    sd.wait()
    write(caminho_audio, taxa_amostragem, audio)

    return caminho_audio


def gravar_audio_temporario(duracao, taxa_amostragem):
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
        caminho_temp = temp_audio.name

    gravar_audio(caminho_temp, duracao, taxa_amostragem)

    return caminho_temp