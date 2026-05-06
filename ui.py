import os
import sys
import traceback
import threading
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox

from PIL import Image
import customtkinter as ctk

from config import (
    PASTA_DATASET,
    MODELO_WHISPER,
    DURACAO_BLOCO,
    DURACAO_DNN,
    TAXA_AMOSTRAGEM,
    FONTE_LIBRAS
)

from audio_utils import gravar_audio, gravar_audio_temporario
from whisper_service import WhisperService
from dnn_service import DNNService
from evaluation import comparar_com_transcricao


class VozParaLibrasApp:
    def __init__(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.modo_escuro = True
        self.aplicar_paleta_escura()

        self.janela = ctk.CTk()
        self.janela.title("TalkLibras")
        self.definir_icone_janela()
        self.janela.geometry("1280x900")
        self.janela.minsize(1100, 720)

        self.whisper_service = WhisperService(MODELO_WHISPER)
        self.dnn_service = DNNService(taxa_amostragem=TAXA_AMOSTRAGEM)

        self.ao_vivo_ativo = False
        self.sessao_ao_vivo = 0
        self.dnn_ativo = False

        self.carregar_icones()
        self.criar_variaveis()
        self.criar_interface()

    def criar_variaveis(self):
        self.status_var = tk.StringVar(value="aguardando ação...")
        self.resultado_var = tk.StringVar(value="")
        self.modelo_whisper_var = tk.StringVar(value=MODELO_WHISPER)

    def carregar_icone(self, nome, tamanho=(30, 30)):
        caminho_base = os.path.dirname(os.path.abspath(__file__))
        caminho = os.path.join(caminho_base, "icons", nome)

        imagem = Image.open(caminho)
        return ctk.CTkImage(light_image=imagem, dark_image=imagem, size=tamanho)

    def carregar_icones(self):
        self.icon_folder = self.carregar_icone("folder.png", (42, 39))
        self.icon_mic = self.carregar_icone("mic.png", (36, 42))
        self.icon_pause = self.carregar_icone("pause.png", (42, 42))
        self.icon_brain = self.carregar_icone("neural.png", (42, 42))
        self.icon_train = self.carregar_icone("study.png", (50, 42))
        self.icon_clean = self.carregar_icone("cleaning.png", (42, 42))

        self.icon_hand = self.carregar_icone("hand.png", (30, 30))
        self.icon_clock = self.carregar_icone("clock.png", (17, 20))
        self.icon_wave = self.carregar_icone("wave.png", (22, 22))
        self.icon_logo = self.carregar_icone("logo.png", (120, 110))
        
        

    def criar_interface(self):
        self.janela.configure(fg_color=self.cor_fundo)

        self.container = ctk.CTkFrame(
            self.janela,
            fg_color=self.cor_card,
            corner_radius=18,
            border_width=1,
            border_color="#1b2a3e"
        )
        self.container.pack(fill="both", expand=True, padx=18, pady=18)

        self.criar_cabecalho()
        self.criar_area_acoes()
        self.criar_area_status()
        self.criar_area_textos()
        self.criar_rodape()

        self.atualizar_estado_dnn()

    def criar_cabecalho(self):
        header = ctk.CTkFrame(self.container, fg_color="transparent")
        header.pack(fill="x", padx=48, pady=(28, 18))

        icone = ctk.CTkLabel(
            header,
            image=self.icon_logo,
            text="",
            width=130
        )
        icone.pack(side="left", padx=(0, 30))

        textos = ctk.CTkFrame(header, fg_color="transparent")
        textos.pack(side="left", fill="x", expand=True)

        titulo = ctk.CTkLabel(
            textos,
            text="Conversor de Voz para Libras Escrita",
            font=("Segoe UI", 34, "bold"),
            text_color=self.cor_texto,
            anchor="w"
        )
        titulo.pack(anchor="w")

        self.botao_tema = ctk.CTkButton(
            header,
            text="Modo claro",
            font=("Segoe UI", 13, "bold"),
            fg_color="#182538",
            hover_color="#22324a",
            border_width=1,
            border_color=self.cor_destaque,
            corner_radius=10,
            width=130,
            height=36,
            command=self.alternar_tema
        )
        self.botao_tema.pack(side="right", padx=(20, 0))
        
        subtitulo = ctk.CTkLabel(
            textos,
            text="Reconhecimento de fala com Whisper e DNN para representação visual em Libras",
            font=("Segoe UI", 17),
            text_color=self.cor_texto_secundario,
            anchor="w"
        )
        subtitulo.pack(anchor="w", pady=(8, 0))

    def trocar_modelo_whisper(self, novo_modelo):
        if self.ao_vivo_ativo or self.dnn_ativo:
            messagebox.showwarning(
                "Reconhecimento em andamento",
                "Pare o reconhecimento antes de trocar o modelo."
            )
            self.modelo_whisper_var.set(self.whisper_service.nome_modelo)
            return

        if novo_modelo == self.whisper_service.nome_modelo:
            return

        self.combo_modelo_whisper.configure(state="disabled")
        self.status_var.set(f"Carregando modelo Whisper: {novo_modelo}...")

        thread = threading.Thread(
            target=self._trocar_modelo_whisper_thread,
            args=(novo_modelo,),
            daemon=True
        )
        thread.start()


    def _trocar_modelo_whisper_thread(self, novo_modelo):
        try:
            self.whisper_service.carregar_modelo(novo_modelo)

            self.janela.after(
                0,
                lambda: self._finalizar_troca_modelo_whisper(novo_modelo)
            )

        except Exception as erro:
            print(traceback.format_exc())
            self.janela.after(0, lambda: self.combo_modelo_whisper.configure(state="normal"))
            self.janela.after(0, lambda: messagebox.showerror("Erro", str(erro)))


    def _finalizar_troca_modelo_whisper(self, novo_modelo):
        self.modelo_whisper_var.set(novo_modelo)
        self.combo_modelo_whisper.configure(state="normal")
        self.status_var.set(f"Modelo Whisper carregado: {novo_modelo}")
        self.resultado_var.set("Modelo Whisper atualizado com sucesso.")


    def criar_area_acoes(self):
        card_acoes = ctk.CTkFrame(
            self.container,
            fg_color=self.cor_card_2,
            corner_radius=16,
            border_width=1,
            border_color=self.cor_borda
        )
        card_acoes.pack(fill="x", padx=30, pady=(0, 18))

        titulo_acoes = ctk.CTkLabel(
            card_acoes,
            text="⚡ Ações",
            font=("Segoe UI", 18, "bold"),
            text_color=self.cor_destaque
        )
        titulo_acoes.pack(anchor="w", padx=24, pady=(18, 8))

        botoes = ctk.CTkFrame(card_acoes, fg_color="transparent")
        botoes.pack(fill="x", padx=20, pady=(8, 20))

        self.criar_botao_card(
            botoes,
            texto="Selecionar áudio\nda base",
            icone=self.icon_folder,
            cor="#2d8cff",
            comando=self.carregar_audio
        ).pack(side="left", fill="x", expand=True, padx=6)

        self.criar_botao_card(
            botoes,
            texto="Iniciar\nreconhecimento\nao vivo",
            icone=self.icon_mic,
            cor="#34d399",
            comando=self.iniciar_ao_vivo
        ).pack(side="left", fill="x", expand=True, padx=6)

        self.criar_botao_card(
            botoes,
            texto="Parar\nreconhecimento",
            icone=self.icon_pause,
            cor="#ff5b5b",
            comando=self.parar_ao_vivo
        ).pack(side="left", fill="x", expand=True, padx=6)

        self.botao_dnn = self.criar_botao_card(
            botoes,
            texto="Reconhecer\ncom DNN",
            icone=self.icon_brain,
            cor="#8b5cf6",
            comando=self.reconhecer_microfone_dnn
        )
        self.botao_dnn.pack(side="left", fill="x", expand=True, padx=6)

        self.botao_treinar_dnn = self.criar_botao_card(
            botoes,
            texto="Treinar\nDNN",
            icone=self.icon_train,
            cor="#fbbf24",
            comando=self.treinar_dnn
        )
        self.botao_treinar_dnn.pack(side="left", fill="x", expand=True, padx=6)

        self.criar_botao_card(
            botoes,
            texto="Limpar\ntexto",
            icone=self.icon_clean,
            cor="#94a3b8",
            comando=self.limpar_texto
        ).pack(side="left", fill="x", expand=True, padx=6)

    def misturar_cor(self, cor_hex, fundo_hex=None, intensidade=0.16):
        if fundo_hex is None:
            fundo_hex = self.cor_botao_base
                
        cor_hex = cor_hex.lstrip("#")
        fundo_hex = fundo_hex.lstrip("#")

        r1, g1, b1 = int(cor_hex[0:2], 16), int(cor_hex[2:4], 16), int(cor_hex[4:6], 16)
        r2, g2, b2 = int(fundo_hex[0:2], 16), int(fundo_hex[2:4], 16), int(fundo_hex[4:6], 16)

        r = int(r2 + (r1 - r2) * intensidade)
        g = int(g2 + (g1 - g2) * intensidade)
        b = int(b2 + (b1 - b2) * intensidade)

        return f"#{r:02x}{g:02x}{b:02x}"
    
    def criar_botao_card(self, parent, texto, icone, cor, comando):
       cor_fundo_suave = self.misturar_cor(cor, self.cor_botao_base, 0.18)
       cor_hover = self.misturar_cor(cor, self.cor_botao_hover, 0.28)

       return ctk.CTkButton(
           parent,
           text=texto,
           image=icone,
           compound="left",
           font=("Segoe UI", 15, "bold"),
           text_color=self.cor_texto_botao,
           fg_color=cor_fundo_suave,
           hover_color=cor_hover,
           border_width=1,
           border_color=cor,
           corner_radius=12,
           height=100,
           command=comando
       )

    def alternar_tema(self):
        texto_normal = self.texto_normal.get("1.0", tk.END).strip()
        texto_visual = self.texto_visual.get("1.0", tk.END).strip()

        resultado_atual = self.resultado_var.get()

        for widget in self.janela.winfo_children():
            widget.destroy()

        if self.modo_escuro:
            ctk.set_appearance_mode("light")
            self.aplicar_paleta_clara()
            texto_botao = "Modo noturno"
            novo_status = "Modo claro ativado."
        else:
            ctk.set_appearance_mode("dark")
            self.aplicar_paleta_escura()
            texto_botao = "Modo claro"
            novo_status = "Modo noturno ativado."

        self.criar_interface()

        self.texto_normal.delete("1.0", tk.END)
        self.texto_normal.insert("1.0", texto_normal)

        self.texto_visual.delete("1.0", tk.END)
        self.texto_visual.insert("1.0", texto_visual)

        self.resultado_var.set(resultado_atual)
        self.status_var.set(novo_status)
        self.botao_tema.configure(text=texto_botao)

    def criar_area_status(self):
        status_card = ctk.CTkFrame(
            self.container,
            fg_color=self.cor_card_2,
            corner_radius=14,
            border_width=1,
            border_color=self.cor_borda
        )
        status_card.pack(fill="x", padx=30, pady=(0, 18))

        linha = ctk.CTkFrame(status_card, fg_color="transparent")
        linha.pack(fill="x", padx=22, pady=14)

        bolinha = ctk.CTkLabel(
            linha,
            text="●",
            font=("Segoe UI", 24),
            text_color=self.cor_destaque
        )
        bolinha.pack(side="left", padx=(0, 12))

        label_status = ctk.CTkLabel(
            linha,
            text="Status:",
            font=("Segoe UI", 16, "bold"),
            text_color=self.cor_destaque
        )
        label_status.pack(side="left")

        valor_status = ctk.CTkLabel(
            linha,
            textvariable=self.status_var,
            font=("Segoe UI", 16),
            text_color=self.cor_texto
        )
        valor_status.pack(side="left", padx=(10, 0))

        valor_resultado = ctk.CTkLabel(
            linha,
            textvariable=self.resultado_var,
            font=("Segoe UI", 13),
            text_color=self.cor_texto_secundario
        )
        valor_resultado.pack(side="right")

    def criar_area_textos(self):
        area = ctk.CTkFrame(self.container, fg_color="transparent")
        area.pack(fill="both", expand=True, padx=30, pady=(8, 18))

        area.grid_columnconfigure(0, weight=1)
        area.grid_columnconfigure(1, weight=1)
        area.grid_rowconfigure(0, weight=1)

        card_texto = self.criar_card_texto(
            area,
            titulo="Texto reconhecido",
            icone=self.icon_wave,
            coluna=0
        )

        self.texto_normal = ctk.CTkTextbox(
            card_texto,
            font=("Segoe UI", 15),
            text_color=self.cor_texto,
            fg_color=self.cor_campo_texto,
            border_width=1,
            border_color="#31435d",
            corner_radius=12,
            wrap="word"
        )
        self.texto_normal.pack(fill="both", expand=True, padx=18, pady=(8, 18))
        self.texto_normal.insert("1.0", "O texto reconhecido aparecerá aqui...")

        card_visual = self.criar_card_texto(
            area,
            titulo="Representação visual (Libras)",
            icone=self.icon_hand,
            coluna=1
        )

        self.texto_visual = ctk.CTkTextbox(
            card_visual,
            font=FONTE_LIBRAS,
            text_color=self.cor_texto,
            fg_color=self.cor_campo_texto,
            border_width=1,
            border_color="#31435d",
            corner_radius=12,
            wrap="word"
        )
        self.texto_visual.pack(fill="both", expand=True, padx=18, pady=(8, 18))
        self.texto_visual.insert("1.0", "A representação em Libras aparecerá aqui...")

    def criar_card_texto(self, parent, titulo, icone, coluna):
        card = ctk.CTkFrame(
            parent,
            fg_color=self.cor_card_2,
            corner_radius=16,
            border_width=1,
            border_color=self.cor_borda
        )
        card.grid(
            row=0,
            column=coluna,
            sticky="nsew",
            padx=(0, 10) if coluna == 0 else (10, 0)
        )

        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(anchor="w", padx=20, pady=(18, 8))

        ctk.CTkLabel(
            header,
            image=icone,
            text=""
        ).pack(side="left", padx=(0, 10))

        ctk.CTkLabel(
            header,
            text=titulo,
            font=("Segoe UI", 18, "bold"),
            text_color=self.cor_texto
        ).pack(side="left")

        return card

    def criar_rodape(self):
        footer = ctk.CTkFrame(
            self.container,
            fg_color=self.cor_card_2,
            corner_radius=14,
            border_width=1,
            border_color=self.cor_borda,
            height=70
        )
        footer.pack(fill="x", padx=30, pady=(0, 16))
        footer.pack_propagate(False)

        footer.grid_columnconfigure(0, weight=1)
        footer.grid_columnconfigure(1, weight=1)
        footer.grid_columnconfigure(2, weight=1)

        item1 = ctk.CTkFrame(footer, fg_color="transparent")
        item1.grid(row=0, column=0, sticky="w", padx=24, pady=10)

        ctk.CTkLabel(
            item1,
            image=self.icon_wave,
            text=""
        ).pack(side="left", padx=(0, 12))

        ctk.CTkLabel(
            item1,
            text="Modelo Whisper:",
            font=("Segoe UI", 12),
            text_color=self.cor_texto
        ).pack(side="left")

        self.combo_modelo_whisper = ctk.CTkComboBox(
            item1,
            values=["tiny", "base", "small", "medium"],
            variable=self.modelo_whisper_var,
            width=95,
            height=28,
            font=("Segoe UI", 12, "bold"),
            dropdown_font=("Segoe UI", 12),
            fg_color=self.cor_card_2,
            border_width=0,
            button_color=self.cor_card_2,
            button_hover_color=self.cor_botao_hover,
            text_color=self.cor_destaque,
            dropdown_fg_color=self.cor_card_2,
            dropdown_hover_color=self.cor_botao_hover,
            dropdown_text_color=self.cor_texto,
            command=self.trocar_modelo_whisper
        )
        self.combo_modelo_whisper.pack(side="left", padx=(8, 0))

        item2 = ctk.CTkFrame(footer, fg_color="transparent")
        item2.grid(row=0, column=1, sticky="n", padx=24, pady=10)

        ctk.CTkLabel(
            item2,
            image=self.icon_clock,
            text=""
        ).pack(side="left", padx=(0, 12))

        ctk.CTkLabel(
            item2,
            text="Duração do bloco:",
            font=("Segoe UI", 14),
            text_color=self.cor_texto
        ).pack(side="left")

        ctk.CTkLabel(
            item2,
            text=f"  {DURACAO_BLOCO} segundos",
            font=("Segoe UI", 14, "bold"),
            text_color=self.cor_destaque
        ).pack(side="left")

        item3 = ctk.CTkFrame(footer, fg_color="transparent")
        item3.grid(row=0, column=2, sticky="e", padx=24, pady=10)

        ctk.CTkLabel(
            item3,
            text="↗",
            font=("Segoe UI", 18, "bold"),
            text_color=self.cor_destaque
        ).pack(side="left", padx=(0, 10))

        ctk.CTkLabel(
            item3,
            text="Sistema pronto",
            font=("Segoe UI", 14, "bold"),
            text_color=self.cor_destaque
        ).pack(side="left")

    def carregar_audio(self):
        caminho_audio = filedialog.askopenfilename(
            initialdir=PASTA_DATASET,
            title="Selecione um arquivo de áudio",
            filetypes=[("Arquivos WAV", "*.wav")]
        )

        if caminho_audio:
            self.reconhecer_audio_whisper(caminho_audio)

    def limpar_placeholder(self):
        texto_normal = self.texto_normal.get("1.0", tk.END).strip()
        texto_visual = self.texto_visual.get("1.0", tk.END).strip()

        if texto_normal == "O texto reconhecido aparecerá aqui...":
            self.texto_normal.delete("1.0", tk.END)

        if texto_visual == "A representação em Libras aparecerá aqui...":
            self.texto_visual.delete("1.0", tk.END)

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
        if self.ao_vivo_ativo:
            return

        self.limpar_placeholder()

        self.ao_vivo_ativo = True
        self.sessao_ao_vivo += 1

        sessao_atual = self.sessao_ao_vivo
        self.status_var.set("Reconhecimento ao vivo iniciado...")

        thread = threading.Thread(
            target=self._loop_ao_vivo,
            args=(sessao_atual,),
            daemon=True
        )
        thread.start()

    def _loop_ao_vivo(self, sessao_atual):
        while self.ao_vivo_ativo and sessao_atual == self.sessao_ao_vivo:
            caminho_temp = None

            try:
                self.janela.after(0, lambda: self.status_var.set("Ouvindo..."))

                caminho_temp = gravar_audio_temporario(
                    DURACAO_BLOCO,
                    TAXA_AMOSTRAGEM
                )

                if not self.ao_vivo_ativo or sessao_atual != self.sessao_ao_vivo:
                    break

                self.janela.after(0, lambda: self.status_var.set("Reconhecendo..."))

                texto = self.whisper_service.transcrever(caminho_temp)

                if not self.ao_vivo_ativo or sessao_atual != self.sessao_ao_vivo:
                    break

                if texto:
                    self.janela.after(
                        0,
                        lambda t=texto, s=sessao_atual: self._append_texto_seguro(t, s)
                    )

            except Exception:
                print(traceback.format_exc())

            finally:
                if caminho_temp and os.path.exists(caminho_temp):
                    os.remove(caminho_temp)

        self.janela.after(0, lambda: self.status_var.set("Reconhecimento ao vivo parado."))

    def parar_ao_vivo(self):
        self.ao_vivo_ativo = False
        self.sessao_ao_vivo += 1
        self.dnn_ativo = False
        self.status_var.set("Reconhecimento ao vivo parado.")

    def _append_texto_seguro(self, texto, sessao_atual):
        if not self.ao_vivo_ativo or sessao_atual != self.sessao_ao_vivo:
            return

        self.limpar_placeholder()
        self.texto_normal.insert(tk.END, " " + texto)
        self.texto_visual.insert(tk.END, " " + texto.upper())

    def reconhecer_microfone_dnn(self):
        if self.dnn_ativo:
            return

        self.dnn_ativo = True
        self.status_var.set("Iniciando reconhecimento com DNN...")

        thread = threading.Thread(
            target=self._reconhecer_microfone_dnn_thread,
            daemon=True
        )
        thread.start()

    def _reconhecer_microfone_dnn_thread(self):
        try:
            self.janela.after(0, lambda: self.status_var.set("Gravando para DNN..."))

            caminho_audio = "audio_dnn_temp.wav"

            gravar_audio(
                caminho_audio,
                DURACAO_DNN,
                TAXA_AMOSTRAGEM
            )

            if not self.dnn_ativo:
                return

            self.janela.after(0, lambda: self.status_var.set("Reconhecendo com DNN..."))

            palavra, confianca = self.dnn_service.reconhecer(caminho_audio)

            if not self.dnn_ativo:
                return

            self.janela.after(
                0,
                lambda: self._exibir_resultado_dnn(palavra, confianca)
            )

        except Exception as erro:
            print(traceback.format_exc())
            self.janela.after(0, lambda: messagebox.showerror("Erro", str(erro)))

        finally:
            self.dnn_ativo = False

    def _exibir_resultado_dnn(self, palavra, confianca):
        self.texto_normal.delete("1.0", tk.END)
        self.texto_normal.insert(tk.END, f"{palavra.upper()} | Confiança: {confianca:.2f}")

        self.texto_visual.delete("1.0", tk.END)
        self.texto_visual.insert(tk.END, palavra.upper())

        self.resultado_var.set("Modo DNN: reconhecimento por classe treinada.")
        self.status_var.set("Reconhecimento DNN finalizado.")

    def limpar_texto(self):
        self.texto_normal.delete("1.0", tk.END)
        self.texto_visual.delete("1.0", tk.END)
        self.resultado_var.set("")
        self.status_var.set("Texto limpo.")

    def atualizar_estado_dnn(self):
        if self.dnn_service.modelo_disponivel():
            self.botao_dnn.configure(state="normal")
            self.resultado_var.set("Modelo DNN disponível.")
        else:
            self.botao_dnn.configure(state="disabled")
            self.resultado_var.set("Modelo DNN não encontrado. Treine a DNN primeiro.")

    def aplicar_paleta_escura(self):
        self.modo_escuro = True

        self.cor_fundo = "#08111f"
        self.cor_card = "#111b2a"
        self.cor_card_2 = "#141f30"
        self.cor_borda = "#26384f"
        self.cor_texto = "#f4f7fb"
        self.cor_texto_secundario = "#aeb8c8"
        self.cor_destaque = "#35e0c0"
        self.cor_campo_texto = "#091525"
        self.cor_botao_base = "#182538"
        self.cor_botao_hover = "#22324a"
        self.cor_texto_botao = "#ffffff"


    def aplicar_paleta_clara(self):
        self.modo_escuro = False
    
        self.cor_fundo = "#eef3f8"
        self.cor_card = "#ffffff"
        self.cor_card_2 = "#f8fafc"
        self.cor_borda = "#cbd5e1"
        self.cor_texto = "#0f172a"
        self.cor_texto_secundario = "#475569"
        self.cor_destaque = "#0f766e"
        self.cor_campo_texto = "#ffffff"
        self.cor_botao_base = "#f1f5f9"
        self.cor_botao_hover = "#e2e8f0"
        self.cor_texto_botao = "#0f172a"

    def treinar_dnn(self):
        self.botao_treinar_dnn.configure(state="disabled")
        self.botao_dnn.configure(state="disabled")
        self.status_var.set("Treinando DNN... Isso pode demorar.")

        thread = threading.Thread(target=self._treinar_dnn_thread, daemon=True)
        thread.start()

    def _treinar_dnn_thread(self):
        try:
            resultado = subprocess.run(
                [sys.executable, "treinar_dnn.py"],
                capture_output=True,
                text=True
            )

            if resultado.returncode != 0:
                self.janela.after(
                    0,
                    lambda: messagebox.showerror("Erro no treino", resultado.stderr)
                )
                return

            self.dnn_service.carregar_modelo()
            self.janela.after(0, self._finalizar_treino_dnn)

        except Exception as erro:
            print(traceback.format_exc())
            self.janela.after(
                0,
                lambda: messagebox.showerror("Erro", str(erro))
            )

    def _finalizar_treino_dnn(self):
        self.botao_treinar_dnn.configure(state="normal")
        self.botao_dnn.configure(state="normal")
        self.status_var.set("Treinamento da DNN finalizado.")
        self.resultado_var.set("Modelo DNN treinado e carregado.")

    def definir_icone_janela(self):
        try:
            base = os.path.dirname(os.path.abspath(__file__))

            caminho_ico = os.path.join(base, "icons", "logo.ico")
            caminho_png = os.path.join(base, "icons", "logo.png")

            if os.path.exists(caminho_ico):
                self.janela.iconbitmap(caminho_ico)
            else:
                self.icone_janela = tk.PhotoImage(file=caminho_png)
                self.janela.iconphoto(False, self.icone_janela)

        except Exception as e:
            print("Erro ao carregar ícone:", e)

    def executar(self):
        self.janela.mainloop()
