import os
import traceback
import tkinter as tk
from tkinter import filedialog, messagebox

from config import (
    PASTA_DATASET,
    MODELO_WHISPER,
    DURACAO_BLOCO,
    DURACAO_DNN,
    TAXA_AMOSTRAGEM,
    FONTE_TITULO,
    FONTE_NORMAL,
    FONTE_LIBRAS
)

from audio_utils import gravar_audio, gravar_audio_temporario
from whisper_service import WhisperService
from dnn_service import DNNService
from evaluation import comparar_com_transcricao


class VozParaLibrasApp:
    def __init__(self):
        self.janela = tk.Tk()
        self.janela.title("Protótipo Voz para Libras Escrita")
        self.janela.geometry("1000x850")

        self.whisper_service = WhisperService(MODELO_WHISPER)
        self.dnn_service = DNNService(taxa_amostragem=TAXA_AMOSTRAGEM)

        self.ao_vivo_ativo = False

        self.criar_variaveis()
        self.criar_interface()

    def criar_variaveis(self):
        self.status_var = tk.StringVar(value="Selecione um áudio para iniciar.")
        self.resultado_var = tk.StringVar(value="")

    def criar_interface(self):
        titulo = tk.Label(
            self.janela,
            text="Conversor de Voz para Libras Escrita",
            font=FONTE_TITULO
        )
        titulo.pack(pady=15)

        tk.Button(
            self.janela,
            text="Selecionar áudio da base",
            font=("Arial", 14),
            command=self.carregar_audio,
            width=30,
            height=2
        ).pack(pady=5)

        tk.Button(
            self.janela,
            text="Iniciar reconhecimento ao vivo",
            font=("Arial", 14),
            command=self.iniciar_ao_vivo,
            width=30,
            height=2
        ).pack(pady=5)

        tk.Button(
            self.janela,
            text="Parar reconhecimento",
            font=("Arial", 14),
            command=self.parar_ao_vivo,
            width=30,
            height=2
        ).pack(pady=5)

        tk.Button(
            self.janela,
            text="Reconhecer com DNN",
            font=("Arial", 14),
            command=self.reconhecer_microfone_dnn,
            width=30,
            height=2
        ).pack(pady=5)

        tk.Button(
            self.janela,
            text="Limpar texto",
            font=("Arial", 14),
            command=self.limpar_texto,
            width=30,
            height=2
        ).pack(pady=5)

        tk.Label(
            self.janela,
            textvariable=self.status_var,
            font=("Arial", 11)
        ).pack(pady=5)

        tk.Label(
            self.janela,
            textvariable=self.resultado_var,
            font=("Arial", 11)
        ).pack(pady=5)

        tk.Label(
            self.janela,
            text="Texto reconhecido:",
            font=("Arial", 14, "bold")
        ).pack(pady=5)

        self.texto_normal = tk.Text(
            self.janela,
            height=8,
            width=100,
            font=FONTE_NORMAL,
            wrap="word"
        )
        self.texto_normal.pack(pady=5)

        tk.Label(
            self.janela,
            text="Representação visual:",
            font=("Arial", 14, "bold")
        ).pack(pady=5)

        self.texto_visual = tk.Text(
            self.janela,
            height=8,
            width=100,
            font=FONTE_LIBRAS,
            wrap="word"
        )
        self.texto_visual.pack(pady=5)

    def carregar_audio(self):
        caminho_audio = filedialog.askopenfilename(
            initialdir=PASTA_DATASET,
            title="Selecione um arquivo de áudio",
            filetypes=[("Arquivos WAV", "*.wav")]
        )

        if caminho_audio:
            self.reconhecer_audio_whisper(caminho_audio)

    def reconhecer_audio_whisper(self, caminho_audio):
        try:
            self.status_var.set("Reconhecendo áudio...")
            self.janela.update()

            texto_reconhecido = self.whisper_service.transcrever(caminho_audio)

            self.texto_normal.delete("1.0", tk.END)
            self.texto_normal.insert(tk.END, texto_reconhecido)

            self.texto_visual.delete("1.0", tk.END)
            self.texto_visual.insert(tk.END, texto_reconhecido.upper())

            erro_wer = comparar_com_transcricao(caminho_audio, texto_reconhecido)

            if erro_wer is None:
                self.resultado_var.set("Arquivo .txt correspondente não encontrado.")
            else:
                self.resultado_var.set(
                    f"Comparação com transcrição original | WER: {erro_wer:.2f}"
                )

            self.status_var.set("Reconhecimento finalizado.")

        except Exception as erro:
            print(traceback.format_exc())
            messagebox.showerror("Erro", str(erro))

    def iniciar_ao_vivo(self):
        self.ao_vivo_ativo = True
        self.status_var.set("Reconhecimento ao vivo iniciado...")
        self.janela.after(100, self.reconhecer_bloco_ao_vivo)

    def parar_ao_vivo(self):
        self.ao_vivo_ativo = False
        self.status_var.set("Reconhecimento ao vivo parado.")

    def reconhecer_bloco_ao_vivo(self):
        if not self.ao_vivo_ativo:
            return

        caminho_temp = None

        try:
            self.status_var.set("Ouvindo...")
            self.janela.update()

            caminho_temp = gravar_audio_temporario(
                DURACAO_BLOCO,
                TAXA_AMOSTRAGEM
            )

            self.status_var.set("Reconhecendo trecho...")
            self.janela.update()

            texto_reconhecido = self.whisper_service.transcrever(caminho_temp)

            if texto_reconhecido:
                self.texto_normal.insert(tk.END, " " + texto_reconhecido)
                self.texto_visual.insert(tk.END, " " + texto_reconhecido.upper())

            if caminho_temp and os.path.exists(caminho_temp):
                os.remove(caminho_temp)

            if self.ao_vivo_ativo:
                self.janela.after(100, self.reconhecer_bloco_ao_vivo)

        except Exception as erro:
            if caminho_temp and os.path.exists(caminho_temp):
                os.remove(caminho_temp)

            print(traceback.format_exc())
            messagebox.showerror("Erro", str(erro))
            self.parar_ao_vivo()

    def reconhecer_microfone_dnn(self):
        try:
            self.status_var.set("Gravando para DNN...")
            self.janela.update()

            caminho_audio = "audio_dnn_temp.wav"

            gravar_audio(
                caminho_audio,
                DURACAO_DNN,
                TAXA_AMOSTRAGEM
            )

            self.status_var.set("Reconhecendo com DNN...")
            self.janela.update()

            palavra, confianca = self.dnn_service.reconhecer(caminho_audio)

            self.texto_normal.delete("1.0", tk.END)
            self.texto_normal.insert(
                tk.END,
                f"{palavra.upper()} | Confiança: {confianca:.2f}"
            )

            self.texto_visual.delete("1.0", tk.END)
            self.texto_visual.insert(tk.END, palavra.upper())

            self.resultado_var.set("Modo DNN: reconhecimento por classe treinada.")
            self.status_var.set("Reconhecimento DNN finalizado.")

        except Exception as erro:
            print(traceback.format_exc())
            messagebox.showerror("Erro", str(erro))

    def limpar_texto(self):
        self.texto_normal.delete("1.0", tk.END)
        self.texto_visual.delete("1.0", tk.END)
        self.resultado_var.set("")
        self.status_var.set("Texto limpo.")

    def executar(self):
        self.janela.mainloop()