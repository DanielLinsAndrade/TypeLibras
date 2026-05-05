from audio_utils import configurar_ffmpeg
from ui import VozParaLibrasApp


def main():
    configurar_ffmpeg()

    app = VozParaLibrasApp()
    app.executar()


if __name__ == "__main__":
    main()
