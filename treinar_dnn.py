import os
import librosa
import numpy as np
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.utils import to_categorical


DATASET_DIR = "dataset_dnn"
TAXA_AMOSTRAGEM = 16000
N_MFCC = 40


def extrair_mfcc(caminho_audio):
    audio, sr = librosa.load(caminho_audio, sr=TAXA_AMOSTRAGEM)

    mfcc = librosa.feature.mfcc(
        y=audio,
        sr=sr,
        n_mfcc=N_MFCC
    )

    mfcc_media = np.mean(mfcc.T, axis=0)

    return mfcc_media


X = []
y = []

for classe in os.listdir(DATASET_DIR):
    pasta_classe = os.path.join(DATASET_DIR, classe)

    if not os.path.isdir(pasta_classe):
        continue

    for arquivo in os.listdir(pasta_classe):
        if arquivo.lower().endswith(".wav"):
            caminho = os.path.join(pasta_classe, arquivo)

            caracteristicas = extrair_mfcc(caminho)

            X.append(caracteristicas)
            y.append(classe)

X = np.array(X)
y = np.array(y)

label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)
y_categorical = to_categorical(y_encoded)

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(
    X_scaled,
    y_categorical,
    test_size=0.2,
    random_state=42,
    stratify=y_categorical
)

modelo = Sequential()

modelo.add(Dense(128, activation="relu", input_shape=(N_MFCC,)))
modelo.add(Dropout(0.3))

modelo.add(Dense(64, activation="relu"))
modelo.add(Dropout(0.3))

modelo.add(Dense(32, activation="relu"))

modelo.add(Dense(y_categorical.shape[1], activation="softmax"))

modelo.compile(
    optimizer="adam",
    loss="categorical_crossentropy",
    metrics=["accuracy"]
)

modelo.fit(
    X_train,
    y_train,
    epochs=80,
    batch_size=8,
    validation_data=(X_test, y_test)
)

loss, acc = modelo.evaluate(X_test, y_test)

print(f"Acurácia da DNN no teste: {acc:.2f}")

modelo.save("modelo_dnn_libras.h5")
joblib.dump(label_encoder, "label_encoder_dnn.pkl")
joblib.dump(scaler, "scaler_dnn.pkl")

print("Modelo DNN salvo com sucesso.")