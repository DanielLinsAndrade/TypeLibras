"""
Script de treinamento da rede neural DNN.

Este módulo carrega os áudios organizados por classes, extrai
características MFCC, treina uma rede neural densa e salva os
artefatos necessários para uso posterior na aplicação.
"""

# Biblioteca padrão para manipulação de arquivos e diretórios
import os

# Biblioteca para processamento de áudio
import librosa

# Biblioteca para operações numéricas
import numpy as np

# Biblioteca para salvar objetos serializados
import joblib

# Função para separação entre treino e teste
from sklearn.model_selection import train_test_split

# Codificador de rótulos e normalizador de atributos
from sklearn.preprocessing import LabelEncoder, StandardScaler

# Modelo sequencial do Keras
from tensorflow.keras.models import Sequential

# Camadas utilizadas na arquitetura da rede neural
from tensorflow.keras.layers import Dense, Dropout

# Função para converter rótulos em formato categórico
from tensorflow.keras.utils import to_categorical


# Caminho da pasta contendo os áudios organizados por classe
DATASET_DIR = "dataset_dnn"

# Taxa de amostragem utilizada no processamento dos áudios
TAXA_AMOSTRAGEM = 16000

# Quantidade de coeficientes MFCC extraídos de cada áudio
N_MFCC = 40


def extrair_mfcc(caminho_audio):
    """
    Extrai características MFCC de um arquivo de áudio.

    Parâmetros

    caminho_audio : str
        Caminho do arquivo de áudio que será processado.

    Retornos

    numpy.ndarray
        Vetor médio contendo os coeficientes MFCC extraídos.
    """

    # Carrega o áudio com a taxa de amostragem definida
    audio, sr = librosa.load(
        caminho_audio,
        sr=TAXA_AMOSTRAGEM
    )

    # Extrai os coeficientes MFCC do áudio
    mfcc = librosa.feature.mfcc(
        y=audio,
        sr=sr,
        n_mfcc=N_MFCC
    )

    # Calcula a média temporal dos coeficientes
    mfcc_media = np.mean(mfcc.T, axis=0)

    # Retorna o vetor de características
    return mfcc_media


# Lista de características extraídas dos áudios
X = []

# Lista de rótulos correspondentes às classes
y = []

# Percorre cada classe existente no dataset
for classe in os.listdir(DATASET_DIR):
    # Monta o caminho da pasta da classe
    pasta_classe = os.path.join(
        DATASET_DIR,
        classe
    )

    # Ignora itens que não sejam diretórios
    if not os.path.isdir(pasta_classe):
        continue

    # Percorre os arquivos da pasta da classe
    for arquivo in os.listdir(pasta_classe):
        # Processa apenas arquivos WAV
        if arquivo.lower().endswith(".wav"):
            caminho = os.path.join(
                pasta_classe,
                arquivo
            )

            # Extrai as características do áudio
            caracteristicas = extrair_mfcc(caminho)

            # Adiciona as características à lista de entrada
            X.append(caracteristicas)

            # Adiciona o nome da classe à lista de rótulos
            y.append(classe)

# Converte as listas para arrays NumPy
X = np.array(X)
y = np.array(y)

# Cria o codificador de rótulos
label_encoder = LabelEncoder()

# Converte rótulos textuais para valores numéricos
y_encoded = label_encoder.fit_transform(y)

# Converte os rótulos para formato one-hot
y_categorical = to_categorical(y_encoded)

# Cria o normalizador dos atributos
scaler = StandardScaler()

# Normaliza as características extraídas
X_scaled = scaler.fit_transform(X)

# Divide os dados em treino e teste
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled,
    y_categorical,
    test_size=0.2,
    random_state=42,
    stratify=y_categorical
)

# Cria o modelo sequencial da rede neural
modelo = Sequential()

# Adiciona a primeira camada densa
modelo.add(
    Dense(
        128,
        activation="relu",
        input_shape=(N_MFCC,)
    )
)

# Adiciona dropout para reduzir overfitting
modelo.add(Dropout(0.3))

# Adiciona a segunda camada densa
modelo.add(Dense(64, activation="relu"))

# Adiciona dropout após a segunda camada
modelo.add(Dropout(0.3))

# Adiciona a terceira camada densa
modelo.add(Dense(32, activation="relu"))

# Adiciona a camada de saída com softmax
modelo.add(
    Dense(
        y_categorical.shape[1],
        activation="softmax"
    )
)

# Compila o modelo
modelo.compile(
    optimizer="adam",
    loss="categorical_crossentropy",
    metrics=["accuracy"]
)

# Treina o modelo
modelo.fit(
    X_train,
    y_train,
    epochs=80,
    batch_size=8,
    validation_data=(X_test, y_test)
)

# Avalia o modelo com os dados de teste
loss, acc = modelo.evaluate(
    X_test,
    y_test
)

# Exibe a acurácia obtida no teste
print(f"Acurácia da DNN no teste: {acc:.2f}")

# Salva o modelo treinado
modelo.save("modelo_dnn_libras.h5")

# Salva o codificador de rótulos
joblib.dump(
    label_encoder,
    "label_encoder_dnn.pkl"
)

# Salva o normalizador utilizado no treinamento
joblib.dump(
    scaler,
    "scaler_dnn.pkl"
)

# Informa que os arquivos foram salvos
print("Modelo DNN salvo com sucesso.")
