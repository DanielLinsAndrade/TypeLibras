"""
Serviço responsável pelo reconhecimento de fala utilizando Whisper.

Este módulo encapsula o carregamento e utilização dos modelos
Whisper da OpenAI para transcrição de áudio em português.
"""

# Importa a biblioteca Whisper
import whisper


class WhisperService:
    """
    Classe responsável pelo gerenciamento do modelo Whisper.

    A classe permite carregar diferentes modelos Whisper e realizar
    transcrições de arquivos de áudio.
    """

    def __init__(self, nome_modelo="base"):
        """
        Inicializa o serviço Whisper.

        Parameters
        ----------
        nome_modelo : str, optional
            Nome do modelo Whisper que será carregado.
        """

        # Armazena o nome do modelo selecionado
        self.nome_modelo = nome_modelo

        # Carrega o modelo Whisper especificado
        self.modelo = whisper.load_model(nome_modelo)

    def carregar_modelo(self, nome_modelo):
        """
        Carrega um novo modelo Whisper.

        Parameters
        ----------
        nome_modelo : str
            Nome do modelo Whisper que será carregado.
        """

        # Atualiza o nome do modelo atual
        self.nome_modelo = nome_modelo

        # Carrega o novo modelo Whisper
        self.modelo = whisper.load_model(nome_modelo)

    def transcrever(self, caminho_audio):
        """
        Realiza a transcrição de um arquivo de áudio.

        Parâmetros
        
        caminho_audio : str
            Caminho do arquivo de áudio que será transcrito.

        Retornos
        
        str
            Texto reconhecido pelo modelo Whisper.
        """

        # Executa a transcrição do áudio em português
        resultado = self.modelo.transcribe(
            caminho_audio,
            language="pt"
        )

        # Retorna o texto reconhecido sem espaços extras
        return resultado["text"].strip()
