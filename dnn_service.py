import numpy as np
import librosa
import joblib

from tensorflow.keras.models import load_model


class DNNService:
    def __init__(
        self,
        caminho_modelo="modelo_dnn_libras.h5",
        caminho_label_encoder="label_encoder_dnn.pkl",
        caminho_scaler="scaler_dnn.pkl",
        taxa_amostragem=16000,
        n_mfcc=40
    ):
        self.modelo = load_model(caminho_modelo)
        self.label_encoder = joblib.load(caminho_label_encoder)
        self.scaler = joblib.load(caminho_scaler)
        self.taxa_amostragem = taxa_amostragem
        self.n_mfcc = n_mfcc

    def extrair_mfcc(self, caminho_audio):
        audio, sr = librosa.load(caminho_audio, sr=self.taxa_amostragem)

        mfcc = librosa.feature.mfcc(
            y=audio,
            sr=sr,
            n_mfcc=self.n_mfcc
        )

        return np.mean(mfcc.T, axis=0)

    def reconhecer(self, caminho_audio):
        caracteristicas = self.extrair_mfcc(caminho_audio)
        caracteristicas = np.array([caracteristicas])
        caracteristicas = self.scaler.transform(caracteristicas)

        predicao = self.modelo.predict(caracteristicas, verbose=0)

        indice = np.argmax(predicao)
        confianca = np.max(predicao)

        palavra = self.label_encoder.inverse_transform([indice])[0]

        return palavra, confianca