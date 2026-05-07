"""
Arquivo principal da aplicação.

Este módulo inicializa a configuração do FFmpeg e executa a
interface gráfica principal do sistema de conversão de voz para
Libras escrita.
"""

# Importa a função responsável por configurar o FFmpeg
from audio_utils import configurar_ffmpeg

# Importa a interface principal da aplicação
from ui import VozParaLibrasApp


def main():
    """
    Inicializa e executa a aplicação principal.

    A função configura o FFmpeg, cria a interface gráfica e inicia
    o loop principal da aplicação.
    """
    # Configura o caminho do FFmpeg no sistema
    configurar_ffmpeg()

    # Cria a instância principal da interface
    app = VozParaLibrasApp()

    # Inicia o loop principal da aplicação
    app.executar()


# Executa a aplicação apenas se o arquivo for iniciado diretamente
if __name__ == "__main__":
    main()
