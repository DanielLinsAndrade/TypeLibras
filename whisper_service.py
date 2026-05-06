import whisper


class WhisperService:
    def __init__(self, nome_modelo="base"):
        self.nome_modelo = nome_modelo
        self.modelo = whisper.load_model(nome_modelo)

    def carregar_modelo(self, nome_modelo):
        self.nome_modelo = nome_modelo
        self.modelo = whisper.load_model(nome_modelo)

    def transcrever(self, caminho_audio):
        resultado = self.modelo.transcribe(
            caminho_audio,
            language="pt"
        )

        return resultado["text"].strip()
