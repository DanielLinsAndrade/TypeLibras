"""
Serviço responsável pelo reconhecimento de fala utilizando DNN.

Este módulo gerencia o carregamento do modelo treinado, extração
de características MFCC e classificação de áudio utilizando uma
rede neural profunda.
"""

# Biblioteca padrão para manipulação de arquivos
import os

# Biblioteca para operações numéricas
import numpy as np

# Biblioteca para processamento de áudio
import librosa

# Biblioteca para carregamento de objetos serializados
import joblib

# Importa o carregador de modelos do TensorFlow/Keras
from tensorflow.keras.models import load_model


class DNNService:
    """
    Classe responsável pelo reconhecimento de fala com DNN.

    A classe realiza o carregamento do modelo treinado, do scaler
    e do label encoder, além da extração de características MFCC
    para classificação de áudio.
    """

    def __init__(
        self,
        caminho_modelo="modelo_dnn_libras.h5",
        caminho_label_encoder="label_encoder_dnn.pkl",
        caminho_scaler="scaler_dnn.pkl",
        taxa_amostragem=16000,
        n_mfcc=40
    ):
        """
        Inicializa o serviço de reconhecimento com DNN.

        Parâmetros
        
        caminho_modelo : str
            Caminho do arquivo do modelo treinado.

        caminho_label_encoder : str
            Caminho do arquivo do label encoder.

        caminho_scaler : str
            Caminho do arquivo do scaler utilizado no treinamento.

        taxa_amostragem : int
            Taxa de amostragem utilizada nos áudios.

        n_mfcc : int
            Quantidade de coeficientes MFCC extraídos.
        """

        # Armazena os caminhos dos arquivos do modelo
        self.caminho_modelo = caminho_modelo
        self.caminho_label_encoder = caminho_label_encoder
        self.caminho_scaler = caminho_scaler

        # Armazena parâmetros de processamento de áudio
        self.taxa_amostragem = taxa_amostragem
        self.n_mfcc = n_mfcc

        # Inicializa variáveis dos componentes do modelo
        self.modelo = None
        self.label_encoder = None
        self.scaler = None

        # Carrega o modelo automaticamente, caso exista
        if self.modelo_disponivel():
            self.carregar_modelo()

    def modelo_disponivel(self):
        """
        Verifica se todos os arquivos necessários existem.

        Retornos
        
        bool
            True caso todos os arquivos estejam disponíveis.
        """

        # Verifica a existência dos arquivos necessários
        return (
            os.path.exists(self.caminho_modelo)
            and os.path.exists(self.caminho_label_encoder)
            and os.path.exists(self.caminho_scaler)
        )

    def carregar_modelo(self):
        """
        Carrega o modelo treinado e os arquivos auxiliares.
        """

        # Carrega o modelo treinado da DNN
        self.modelo = load_model(self.caminho_modelo)

        # Carrega o label encoder utilizado no treinamento
        self.label_encoder = joblib.load(self.caminho_label_encoder)

        # Carrega o scaler utilizado na normalização
        self.scaler = joblib.load(self.caminho_scaler)

    def extrair_mfcc(self, caminho_audio):
        """
        Extrai características MFCC de um arquivo de áudio.

        Parâmetros
        
        caminho_audio : str
            Caminho do arquivo de áudio.

        Retornos
        
        numpy.ndarray
            Vetor médio contendo os coeficientes MFCC.
        """

        # Carrega o áudio utilizando a taxa de amostragem definida
        audio, sr = librosa.load(
            caminho_audio,
            sr=self.taxa_amostragem
        )

        # Extrai os coeficientes MFCC do áudio
        mfcc = librosa.feature.mfcc(
            y=audio,
            sr=sr,
            n_mfcc=self.n_mfcc
        )

        # Retorna a média temporal dos coeficientes MFCC
        return np.mean(mfcc.T, axis=0)

    def reconhecer(self, caminho_audio):
        """
        Realiza o reconhecimento de fala utilizando a DNN.

        Parâmetros
        
        caminho_audio : str
            Caminho do arquivo de áudio que será reconhecido.

        Retornos
        
        tuple
            Palavra reconhecida e nível de confiança da predição.
        """

        # Verifica se o modelo foi carregado corretamente
        if self.modelo is None:
            raise RuntimeError(
                "Modelo DNN não carregado. "
                "Treine a DNN primeiro."
            )

        # Extrai as características MFCC do áudio
        caracteristicas = self.extrair_mfcc(caminho_audio)

        # Converte as características para formato matricial
        caracteristicas = np.array([caracteristicas])

        # Aplica a normalização utilizando o scaler treinado
        caracteristicas = self.scaler.transform(caracteristicas)

        # Executa a predição do modelo
        predicao = self.modelo.predict(
            caracteristicas,
            verbose=0
        )

        # Obtém o índice da maior probabilidade
        indice = np.argmax(predicao)

        # Obtém o valor de confiança da predição
        confianca = np.max(predicao)

        # Converte o índice previsto para a palavra original
        palavra = self.label_encoder.inverse_transform([indice])[0]

        # Retorna a palavra prevista e sua confiança
        return palavra, confianca
