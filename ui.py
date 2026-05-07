"""
Interface gráfica principal da aplicação TalkLibras.

Este módulo implementa a interface responsável pela interação com
o usuário, incluindo reconhecimento de fala, integração com Whisper,
utilização da DNN e representação visual em Libras.
"""

# Biblioteca padrão para manipulação de arquivos e diretórios
import os

# Biblioteca padrão para acesso a funcionalidades do sistema
import sys

# Biblioteca para exibição detalhada de exceções
import traceback

# Biblioteca para execução de tarefas paralelas
import threading

# Biblioteca para execução de processos externos
import subprocess

# Biblioteca padrão para interfaces gráficas
import tkinter as tk

# Importa componentes de diálogo do Tkinter
from tkinter import filedialog, messagebox

# Biblioteca para manipulação de imagens
from PIL import Image

# Biblioteca para interfaces modernas com Tkinter
import customtkinter as ctk

# Importa configurações globais da aplicação
from config import (
    PASTA_DATASET,
    MODELO_WHISPER,
    DURACAO_BLOCO,
    DURACAO_DNN,
    TAXA_AMOSTRAGEM,
    FONTE_LIBRAS
)

# Importa funções utilitárias de áudio
from audio_utils import gravar_audio, gravar_audio_temporario

# Importa o serviço de reconhecimento com Whisper
from whisper_service import WhisperService

# Importa o serviço de reconhecimento com DNN
from dnn_service import DNNService

# Importa função de avaliação de transcrição
from evaluation import comparar_com_transcricao

# Macro de fonte padrão para evitar repetição no código
FONTE_PADRAO = "Segoe UI"

class VozParaLibrasApp:
    """
    Classe principal da interface gráfica da aplicação.

    A classe gerencia os componentes visuais, integração com os
    serviços de reconhecimento de fala e exibição da representação
    visual em Libras.
    """

    def __init__(self):
        """
        Inicializa a interface principal da aplicação.

        O construtor configura o tema visual, inicializa serviços,
        carrega ícones e cria os componentes da interface gráfica.
        """

        # Define o tema inicial da interface como escuro
        ctk.set_appearance_mode("dark")

        # Define o esquema de cores padrão do CustomTkinter
        ctk.set_default_color_theme("blue")

        # Define o estado inicial do tema da interface
        self.modo_escuro = True

        # Aplica a paleta de cores do modo escuro
        self.aplicar_paleta_escura()

        # Cria a janela principal da aplicação
        self.janela = ctk.CTk()

        # Define o título da janela
        self.janela.title("TalkLibras")

        # Define o ícone personalizado da aplicação
        self.definir_icone_janela()

        # Define o tamanho inicial da janela
        self.janela.geometry("1280x900")

        # Define o tamanho mínimo permitido para a janela
        self.janela.minsize(1100, 720)

        # Inicializa o serviço de reconhecimento Whisper
        self.whisper_service = WhisperService(MODELO_WHISPER)

        # Inicializa o serviço de reconhecimento com DNN
        self.dnn_service = DNNService(
            taxa_amostragem=TAXA_AMOSTRAGEM
        )

        # Controla o estado do reconhecimento ao vivo
        self.ao_vivo_ativo = False

        # Controla sessões de reconhecimento ao vivo
        self.sessao_ao_vivo = 0

        # Controla o estado de reconhecimento da DNN
        self.dnn_ativo = False

        # Inicializando previamente os ícones para carregar posteriormente
        self.botao_tema = None
        self.botao_dnn = None
        self.botao_treinar_dnn = None
        self.texto_normal = None
        self.texto_visual = None
        self.combo_modelo_whisper = None
        self.cor_fundo = None
        self.cor_card = None
        self.cor_card_2 = None
        self.cor_borda = None
        self.cor_texto = None
        self.cor_texto_secundario = None
        self.cor_destaque = None
        self.cor_campo_texto = None
        self.cor_botao_base = None
        self.cor_botao_hover = None
        self.cor_texto_botao = None

        # Carrega os ícones utilizados na interface
        self.carregar_icones()

        # Cria variáveis dinâmicas da interface
        self.criar_variaveis()

        # Cria todos os componentes visuais da interface
        self.criar_interface()

    def criar_variaveis(self):
        """
        Cria variáveis dinâmicas utilizadas pela interface.

        As variáveis são utilizadas para atualização automática de
        informações exibidas nos componentes visuais.
        """

        # Variável responsável pelo texto de status do sistema
        self.status_var = tk.StringVar(
            value="aguardando ação..."
        )

        # Variável responsável pelo resultado do reconhecimento
        self.resultado_var = tk.StringVar(value="")

        # Variável responsável pelo modelo Whisper atual
        self.modelo_whisper_var = tk.StringVar(
            value=MODELO_WHISPER
        )

    def carregar_icone(self, nome, tamanho=(30, 30)):
        """
        Carrega um ícone personalizado da interface.

        Parâmetros
        
        nome : str
            Nome do arquivo de imagem do ícone.

        tamanho : tuple, optional
            Tamanho do ícone em pixels.

        Retornos
        
        CTkImage
            Objeto de imagem compatível com CustomTkinter.
        """

        # Obtém o diretório base do arquivo atual
        caminho_base = os.path.dirname(
            os.path.abspath(__file__)
        )

        # Monta o caminho completo do ícone
        caminho = os.path.join(
            caminho_base,
            "icons",
            nome
        )

        # Carrega a imagem utilizando Pillow
        imagem = Image.open(caminho)

        # Retorna a imagem formatada para o CustomTkinter
        return ctk.CTkImage(
            light_image=imagem,
            dark_image=imagem,
            size=tamanho
        )

    def carregar_icones(self):
        """
        Carrega todos os ícones utilizados pela interface.
        """

        # Carrega ícones da área de ações
        self.icon_folder = self.carregar_icone(
            "folder.png",
            (42, 39)
        )

        self.icon_mic = self.carregar_icone(
            "mic.png",
            (36, 42)
        )

        self.icon_pause = self.carregar_icone(
            "pause.png",
            (42, 42)
        )

        self.icon_brain = self.carregar_icone(
            "neural.png",
            (42, 42)
        )

        self.icon_train = self.carregar_icone(
            "study.png",
            (50, 42)
        )

        self.icon_clean = self.carregar_icone(
            "cleaning.png",
            (42, 42)
        )

        # Carrega ícones auxiliares da interface
        self.icon_hand = self.carregar_icone(
            "hand.png",
            (30, 30)
        )

        self.icon_clock = self.carregar_icone(
            "clock.png",
            (17, 20)
        )

        self.icon_wave = self.carregar_icone(
            "wave.png",
            (22, 22)
        )

        self.icon_logo = self.carregar_icone(
            "logo.png",
            (120, 110)
        )

    def criar_interface(self):
        """
        Cria e organiza os componentes principais da interface.
        """

        # Define a cor de fundo da janela principal
        self.janela.configure(
            fg_color=self.cor_fundo
        )

        # Cria o container principal da interface
        self.container = ctk.CTkFrame(
            self.janela,
            fg_color=self.cor_card,
            corner_radius=18,
            border_width=1,
            border_color="#1b2a3e"
        )

        # Posiciona o container principal na janela
        self.container.pack(
            fill="both",
            expand=True,
            padx=18,
            pady=18
        )

        # Cria o cabeçalho da interface
        self.criar_cabecalho()

        # Cria a área de botões e ações
        self.criar_area_acoes()

        # Cria a área de status do sistema
        self.criar_area_status()

        # Cria as áreas de texto da aplicação
        self.criar_area_textos()

        # Cria o rodapé da interface
        self.criar_rodape()

        # Atualiza o estado do modelo DNN na interface
        self.atualizar_estado_dnn()

    def criar_cabecalho(self):
        """
        Cria o cabeçalho principal da interface.

        O cabeçalho contém o logotipo, título da aplicação,
        subtítulo descritivo e botão de alternância de tema.
        """

        # Cria o container do cabeçalho
        header = ctk.CTkFrame(
            self.container,
            fg_color="transparent"
        )

        # Posiciona o cabeçalho na interface
        header.pack(
            fill="x",
            padx=48,
            pady=(28, 18)
        )

        # Cria o logotipo principal da aplicação
        icone = ctk.CTkLabel(
            header,
            image=self.icon_logo,
            text="",
            width=130
        )

        # Posiciona o logotipo no cabeçalho
        icone.pack(side="left", padx=(0, 30))

        # Cria o container dos textos do cabeçalho
        textos = ctk.CTkFrame(
            header,
            fg_color="transparent"
        )

        # Posiciona a área de textos
        textos.pack(
            side="left",
            fill="x",
            expand=True
        )

        # Cria o título principal da aplicação
        titulo = ctk.CTkLabel(
            textos,
            text="Conversor de Voz para Libras Escrita",
            font=(FONTE_PADRAO, 34, "bold"),
            text_color=self.cor_texto,
            anchor="w"
        )

        # Posiciona o título principal
        titulo.pack(anchor="w")

        # Cria o botão de alternância de tema
        self.botao_tema = ctk.CTkButton(
            header,
            text="Modo claro",
            font=(FONTE_PADRAO, 13, "bold"),
            fg_color="#182538",
            hover_color="#22324a",
            border_width=1,
            border_color=self.cor_destaque,
            corner_radius=10,
            width=130,
            height=36,
            command=self.alternar_tema
        )

        # Posiciona o botão de tema no cabeçalho
        self.botao_tema.pack(
            side="right",
            padx=(20, 0)
        )

        # Cria o subtítulo explicativo da aplicação
        subtitulo = ctk.CTkLabel(
            textos,
            text=(
                "Reconhecimento de fala com Whisper e DNN "
                "para representação visual em Libras"
            ),
            font=(FONTE_PADRAO, 17),
            text_color=self.cor_texto_secundario,
            anchor="w"
        )

        # Posiciona o subtítulo abaixo do título principal
        subtitulo.pack(anchor="w", pady=(8, 0))

    def trocar_modelo_whisper(self, novo_modelo):
        """
        Realiza a troca do modelo Whisper utilizado.

        Parâmetros

        novo_modelo : str
            Nome do novo modelo Whisper que será carregado.
        """

        # Impede troca durante reconhecimento ativo
        if self.ao_vivo_ativo or self.dnn_ativo:
            messagebox.showwarning(
                "Reconhecimento em andamento",
                "Pare o reconhecimento antes de trocar o modelo."
            )

            # Restaura o modelo anterior na interface
            self.modelo_whisper_var.set(
                self.whisper_service.nome_modelo
            )

            return

        # Evita recarregar o mesmo modelo
        if novo_modelo == self.whisper_service.nome_modelo:
            return

        # Desabilita o seletor durante o carregamento
        self.combo_modelo_whisper.configure(state="disabled")

        # Atualiza o status da interface
        self.status_var.set(
            f"Carregando modelo Whisper: {novo_modelo}..."
        )

        # Cria thread para evitar travamento da interface
        thread = threading.Thread(
            target=self._trocar_modelo_whisper_thread,
            args=(novo_modelo,),
            daemon=True
        )

        # Inicia a thread de carregamento
        thread.start()

    def _trocar_modelo_whisper_thread(self, novo_modelo):
        """
        Executa o carregamento do modelo Whisper em paralelo.

        Parâmetros

        novo_modelo : str
            Nome do modelo Whisper que será carregado.
        """

        try:
            # Carrega o novo modelo Whisper
            self.whisper_service.carregar_modelo(
                novo_modelo
            )

            # Atualiza a interface após o carregamento
            self.janela.after(
                0,
                lambda: self._finalizar_troca_modelo_whisper(
                    novo_modelo
                )
            )

        except Exception as erro: # pylint: disable=broad-exception-caught
            # Exibe o traceback completo no terminal
            print(traceback.format_exc())

            # Reabilita o seletor de modelos
            self.janela.after(
                0,
                lambda: self.combo_modelo_whisper.configure(
                    state="normal"
                )
            )

            # Exibe mensagem de erro na interface
            self.janela.after(
                0,
                lambda: messagebox.showerror(
                    "Erro",
                    str(erro)
                )
            )

    def _finalizar_troca_modelo_whisper(self, novo_modelo):
        """
        Finaliza a troca do modelo Whisper na interface.

        Parâmetros

        novo_modelo : str
            Nome do modelo Whisper carregado.
        """

        # Atualiza o modelo exibido na interface
        self.modelo_whisper_var.set(novo_modelo)

        # Reabilita o seletor de modelos
        self.combo_modelo_whisper.configure(state="normal")

        # Atualiza o status da interface
        self.status_var.set(
            f"Modelo Whisper carregado: {novo_modelo}"
        )

        # Atualiza a mensagem de resultado
        self.resultado_var.set(
            "Modelo Whisper atualizado com sucesso."
        )

    def criar_area_acoes(self):
        """
        Cria a área de ações principais da interface.

        Esta seção contém os botões responsáveis pelas principais
        funcionalidades do sistema.
        """

        # Cria o card principal da área de ações
        card_acoes = ctk.CTkFrame(
            self.container,
            fg_color=self.cor_card_2,
            corner_radius=16,
            border_width=1,
            border_color=self.cor_borda
        )

        # Posiciona o card na interface
        card_acoes.pack(
            fill="x",
            padx=30,
            pady=(0, 18)
        )

        # Cria o título da área de ações
        titulo_acoes = ctk.CTkLabel(
            card_acoes,
            text="⚡ Ações",
            font=(FONTE_PADRAO, 18, "bold"),
            text_color=self.cor_destaque
        )

        # Posiciona o título da seção
        titulo_acoes.pack(
            anchor="w",
            padx=24,
            pady=(18, 8)
        )

        # Cria o container dos botões
        botoes = ctk.CTkFrame(
            card_acoes,
            fg_color="transparent"
        )

        # Posiciona os botões na interface
        botoes.pack(
            fill="x",
            padx=20,
            pady=(8, 20)
        )

        # Botão de seleção de áudio do dataset
        self.criar_botao_card(
            botoes,
            texto="Selecionar áudio\nda base",
            icone=self.icon_folder,
            cor="#2d8cff",
            comando=self.carregar_audio
        ).pack(
            side="left",
            fill="x",
            expand=True,
            padx=6
        )

        # Botão de reconhecimento ao vivo
        self.criar_botao_card(
            botoes,
            texto="Iniciar\nreconhecimento\nao vivo",
            icone=self.icon_mic,
            cor="#34d399",
            comando=self.iniciar_ao_vivo
        ).pack(
            side="left",
            fill="x",
            expand=True,
            padx=6
        )

        # Botão para parar reconhecimento
        self.criar_botao_card(
            botoes,
            texto="Parar\nreconhecimento",
            icone=self.icon_pause,
            cor="#ff5b5b",
            comando=self.parar_ao_vivo
        ).pack(
            side="left",
            fill="x",
            expand=True,
            padx=6
        )

        # Botão de reconhecimento com DNN
        self.botao_dnn = self.criar_botao_card(
            botoes,
            texto="Reconhecer\ncom DNN",
            icone=self.icon_brain,
            cor="#8b5cf6",
            comando=self.reconhecer_microfone_dnn
        )

        # Posiciona o botão da DNN
        self.botao_dnn.pack(
            side="left",
            fill="x",
            expand=True,
            padx=6
        )

        # Botão de treinamento da DNN
        self.botao_treinar_dnn = self.criar_botao_card(
            botoes,
            texto="Treinar\nDNN",
            icone=self.icon_train,
            cor="#fbbf24",
            comando=self.treinar_dnn
        )

        # Posiciona o botão de treino
        self.botao_treinar_dnn.pack(
            side="left",
            fill="x",
            expand=True,
            padx=6
        )

        # Botão de limpeza de texto
        self.criar_botao_card(
            botoes,
            texto="Limpar\ntexto",
            icone=self.icon_clean,
            cor="#94a3b8",
            comando=self.limpar_texto
        ).pack(
            side="left",
            fill="x",
            expand=True,
            padx=6
        )

    def misturar_cor(
        self,
        cor_hex,
        fundo_hex=None,
        intensidade=0.16
    ):
        """
        Mistura duas cores utilizando interpolação RGB.

        Parâmetros

        cor_hex : str
            Cor principal em formato hexadecimal.

        fundo_hex : str, optional
            Cor de fundo utilizada na mistura.

        intensidade : float, optional
            Intensidade da mistura entre as cores.

        Retornos

        str
            Cor resultante em formato hexadecimal.
        """

        # Utiliza a cor base padrão caso não seja informada
        if fundo_hex is None:
            fundo_hex = self.cor_botao_base

        # Remove o caractere '#' das cores
        cor_hex = cor_hex.lstrip("#")
        fundo_hex = fundo_hex.lstrip("#")

        # Converte os componentes RGB da cor principal
        r1 = int(cor_hex[0:2], 16)
        g1 = int(cor_hex[2:4], 16)
        b1 = int(cor_hex[4:6], 16)

        # Converte os componentes RGB da cor de fundo
        r2 = int(fundo_hex[0:2], 16)
        g2 = int(fundo_hex[2:4], 16)
        b2 = int(fundo_hex[4:6], 16)

        # Calcula a interpolação dos canais RGB
        r = int(r2 + (r1 - r2) * intensidade)
        g = int(g2 + (g1 - g2) * intensidade)
        b = int(b2 + (b1 - b2) * intensidade)

        # Retorna a cor final em hexadecimal
        return f"#{r:02x}{g:02x}{b:02x}"

    def criar_botao_card(
        self,
        parent,
        texto,
        icone,
        cor,
        comando
    ):
        """
        Cria um botão estilizado da interface.

        Parâmetros

        parent : widget
            Widget pai do botão.

        texto : str
            Texto exibido no botão.

        icone : CTkImage
            Ícone exibido no botão.

        cor : str
            Cor principal utilizada no botão.

        comando : function
            Função executada ao clicar no botão.

        Retornos

        CTkButton
            Botão estilizado da interface.
        """

        # Gera a cor de fundo suavizada do botão
        cor_fundo_suave = self.misturar_cor(
            cor,
            self.cor_botao_base,
            0.18
        )

        # Gera a cor de hover do botão
        cor_hover = self.misturar_cor(
            cor,
            self.cor_botao_hover,
            0.28
        )

        # Retorna o botão estilizado
        return ctk.CTkButton(
            parent,
            text=texto,
            image=icone,
            compound="left",
            font=(FONTE_PADRAO, 15, "bold"),
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
        """
        Alterna entre os modos claro e escuro da interface.

        O método recria os componentes visuais para aplicar a nova
        paleta de cores sem perder os textos exibidos.
        """

        # Armazena o conteúdo atual das áreas de texto
        texto_normal = self.texto_normal.get(
            "1.0",
            tk.END
        ).strip()

        texto_visual = self.texto_visual.get(
            "1.0",
            tk.END
        ).strip()

        # Armazena o resultado atual da interface
        resultado_atual = self.resultado_var.get()

        # Remove os widgets atuais da janela
        for widget in self.janela.winfo_children():
            widget.destroy()

        # Alterna entre os temas disponíveis
        if self.modo_escuro:
            ctk.set_appearance_mode("light")

            # Aplica a paleta clara
            self.aplicar_paleta_clara()

            # Define o texto do botão de tema
            texto_botao = "Modo noturno"

            # Define o status da interface
            novo_status = "Modo claro ativado."

        else:
            ctk.set_appearance_mode("dark")

            # Aplica a paleta escura
            self.aplicar_paleta_escura()

            # Define o texto do botão de tema
            texto_botao = "Modo claro"

            # Define o status da interface
            novo_status = "Modo noturno ativado."

        # Recria todos os componentes da interface
        self.criar_interface()

        # Restaura o conteúdo do texto reconhecido
        self.texto_normal.delete("1.0", tk.END)
        self.texto_normal.insert("1.0", texto_normal)

        # Restaura o conteúdo da representação visual
        self.texto_visual.delete("1.0", tk.END)
        self.texto_visual.insert("1.0", texto_visual)

        # Atualiza as informações de status da interface
        self.resultado_var.set(resultado_atual)
        self.status_var.set(novo_status)

        # Atualiza o texto do botão de tema
        self.botao_tema.configure(text=texto_botao)

    def criar_area_status(self):
        """
        Cria a área de status da interface.

        Esta seção exibe informações sobre o estado atual do sistema
        e resultados do reconhecimento de fala.
        """

        # Cria o card da área de status
        status_card = ctk.CTkFrame(
            self.container,
            fg_color=self.cor_card_2,
            corner_radius=14,
            border_width=1,
            border_color=self.cor_borda
        )

        # Posiciona o card na interface
        status_card.pack(
            fill="x",
            padx=30,
            pady=(0, 18)
        )

        # Cria a linha principal da área de status
        linha = ctk.CTkFrame(
            status_card,
            fg_color="transparent"
        )

        # Posiciona a linha de status
        linha.pack(
            fill="x",
            padx=22,
            pady=14
        )

        # Cria o indicador visual de status
        bolinha = ctk.CTkLabel(
            linha,
            text="●",
            font=(FONTE_PADRAO, 24),
            text_color=self.cor_destaque
        )

        # Posiciona o indicador visual
        bolinha.pack(side="left", padx=(0, 12))

        # Cria o rótulo da seção de status
        label_status = ctk.CTkLabel(
            linha,
            text="Status:",
            font=(FONTE_PADRAO, 16, "bold"),
            text_color=self.cor_destaque
        )

        # Posiciona o rótulo de status
        label_status.pack(side="left")

        # Cria o texto dinâmico de status
        valor_status = ctk.CTkLabel(
            linha,
            textvariable=self.status_var,
            font=(FONTE_PADRAO, 16),
            text_color=self.cor_texto
        )

        # Posiciona o valor de status
        valor_status.pack(side="left", padx=(10, 0))

        # Cria o texto auxiliar de resultados
        valor_resultado = ctk.CTkLabel(
            linha,
            textvariable=self.resultado_var,
            font=(FONTE_PADRAO, 13),
            text_color=self.cor_texto_secundario
        )

        # Posiciona o resultado na lateral direita
        valor_resultado.pack(side="right")

    def criar_area_textos(self):
        """
        Cria as áreas de exibição de texto da interface.

        Esta seção contém o texto reconhecido e sua representação
        visual em Libras.
        """

        # Cria o container principal das áreas de texto
        area = ctk.CTkFrame(
            self.container,
            fg_color="transparent"
        )

        # Posiciona a área de textos na interface
        area.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=(8, 18)
        )

        # Configura expansão das colunas do grid
        area.grid_columnconfigure(0, weight=1)
        area.grid_columnconfigure(1, weight=1)

        # Configura expansão vertical do grid
        area.grid_rowconfigure(0, weight=1)

        # Cria o card do texto reconhecido
        card_texto = self.criar_card_texto(
            area,
            titulo="Texto reconhecido",
            icone=self.icon_wave,
            coluna=0
        )

        # Cria a caixa de texto do reconhecimento
        self.texto_normal = ctk.CTkTextbox(
            card_texto,
            font=(FONTE_PADRAO, 15),
            text_color=self.cor_texto,
            fg_color=self.cor_campo_texto,
            border_width=1,
            border_color="#31435d",
            corner_radius=12,
            wrap="word"
        )

        # Posiciona a caixa de texto
        self.texto_normal.pack(
            fill="both",
            expand=True,
            padx=18,
            pady=(8, 18)
        )

        # Define o texto placeholder inicial
        self.texto_normal.insert(
            "1.0",
            "O texto reconhecido aparecerá aqui..."
        )

        # Cria o card da representação visual
        card_visual = self.criar_card_texto(
            area,
            titulo="Representação visual (Libras)",
            icone=self.icon_hand,
            coluna=1
        )

        # Cria a caixa de texto da representação visual
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

        # Posiciona a caixa de texto visual
        self.texto_visual.pack(
            fill="both",
            expand=True,
            padx=18,
            pady=(8, 18)
        )

        # Define o placeholder da área visual
        self.texto_visual.insert(
            "1.0",
            "A representação em Libras aparecerá aqui..."
        )

    def criar_card_texto(
        self,
        parent,
        titulo,
        icone,
        coluna
    ):
        """
        Cria um card de exibição de texto.

        Parâmetros

        parent : widget
            Widget pai do card.

        titulo : str
            Texto exibido no cabeçalho do card.

        icone : CTkImage
            Ícone exibido no cabeçalho do card.

        coluna : int
            Coluna do grid onde o card será posicionado.

        Retornos

        CTkFrame
            Card configurado para exibição de conteúdo.
        """

        # Cria o card principal
        card = ctk.CTkFrame(
            parent,
            fg_color=self.cor_card_2,
            corner_radius=16,
            border_width=1,
            border_color=self.cor_borda
        )

        # Posiciona o card no grid
        card.grid(
            row=0,
            column=coluna,
            sticky="nsew",
            padx=(0, 10) if coluna == 0 else (10, 0)
        )

        # Cria o cabeçalho do card
        header = ctk.CTkFrame(
            card,
            fg_color="transparent"
        )

        # Posiciona o cabeçalho do card
        header.pack(
            anchor="w",
            padx=20,
            pady=(18, 8)
        )

        # Cria o ícone do cabeçalho
        ctk.CTkLabel(
            header,
            image=icone,
            text=""
        ).pack(side="left", padx=(0, 10))

        # Cria o título do card
        ctk.CTkLabel(
            header,
            text=titulo,
            font=(FONTE_PADRAO, 18, "bold"),
            text_color=self.cor_texto
        ).pack(side="left")

        # Retorna o card criado
        return card

    def criar_rodape(self):
        """
        Cria o rodapé informativo da interface.

        O rodapé exibe informações relacionadas ao modelo Whisper,
        duração do bloco de áudio e estado do sistema.
        """

        # Cria o container principal do rodapé
        footer = ctk.CTkFrame(
            self.container,
            fg_color=self.cor_card_2,
            corner_radius=14,
            border_width=1,
            border_color=self.cor_borda,
            height=70
        )

        # Posiciona o rodapé na interface
        footer.pack(
            fill="x",
            padx=30,
            pady=(0, 16)
        )

        # Impede redimensionamento automático do rodapé
        footer.pack_propagate(False)

        # Configura as colunas do grid do rodapé
        footer.grid_columnconfigure(0, weight=1)
        footer.grid_columnconfigure(1, weight=1)
        footer.grid_columnconfigure(2, weight=1)

        # Cria o primeiro bloco do rodapé
        item1 = ctk.CTkFrame(
            footer,
            fg_color="transparent"
        )

        # Posiciona o primeiro bloco
        item1.grid(
            row=0,
            column=0,
            sticky="w",
            padx=24,
            pady=10
        )

        # Cria o ícone do modelo Whisper
        ctk.CTkLabel(
            item1,
            image=self.icon_wave,
            text=""
        ).pack(side="left", padx=(0, 12))

        # Cria o texto do modelo Whisper
        ctk.CTkLabel(
            item1,
            text="Modelo Whisper:",
            font=(FONTE_PADRAO, 12),
            text_color=self.cor_texto
        ).pack(side="left")

        # Cria o seletor de modelo Whisper
        self.combo_modelo_whisper = ctk.CTkComboBox(
            item1,
            values=["tiny", "base", "small", "medium"],
            variable=self.modelo_whisper_var,
            width=95,
            height=28,
            font=(FONTE_PADRAO, 12, "bold"),
            dropdown_font=(FONTE_PADRAO, 12),
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

        # Posiciona o seletor de modelo
        self.combo_modelo_whisper.pack(
            side="left",
            padx=(8, 0)
        )

        # Cria o segundo bloco do rodapé
        item2 = ctk.CTkFrame(
            footer,
            fg_color="transparent"
        )

        # Posiciona o segundo bloco
        item2.grid(
            row=0,
            column=1,
            sticky="n",
            padx=24,
            pady=10
        )

        # Cria o ícone de duração
        ctk.CTkLabel(
            item2,
            image=self.icon_clock,
            text=""
        ).pack(side="left", padx=(0, 12))

        # Cria o texto da duração do bloco
        ctk.CTkLabel(
            item2,
            text="Duração do bloco:",
            font=(FONTE_PADRAO, 14),
            text_color=self.cor_texto
        ).pack(side="left")

        # Exibe a duração configurada do bloco
        ctk.CTkLabel(
            item2,
            text=f"  {DURACAO_BLOCO} segundos",
            font=(FONTE_PADRAO, 14, "bold"),
            text_color=self.cor_destaque
        ).pack(side="left")

        # Cria o terceiro bloco do rodapé
        item3 = ctk.CTkFrame(
            footer,
            fg_color="transparent"
        )

        # Posiciona o terceiro bloco
        item3.grid(
            row=0,
            column=2,
            sticky="e",
            padx=24,
            pady=10
        )

        # Cria o indicador visual de status
        ctk.CTkLabel(
            item3,
            text="↗",
            font=(FONTE_PADRAO, 18, "bold"),
            text_color=self.cor_destaque
        ).pack(side="left", padx=(0, 10))

        # Cria o texto do estado do sistema
        ctk.CTkLabel(
            item3,
            text="Sistema pronto",
            font=(FONTE_PADRAO, 14, "bold"),
            text_color=self.cor_destaque
        ).pack(side="left")

    def carregar_audio(self):
        """
        Abre um seletor de arquivos para carregar um áudio.

        Caso um arquivo válido seja selecionado, o reconhecimento
        de fala utilizando Whisper é iniciado.
        """

        # Abre a janela de seleção de arquivos
        caminho_audio = filedialog.askopenfilename(
            initialdir=PASTA_DATASET,
            title="Selecione um arquivo de áudio",
            filetypes=[("Arquivos WAV", "*.wav")]
        )

        # Executa o reconhecimento caso exista arquivo
        if caminho_audio:
            self.reconhecer_audio_whisper(
                caminho_audio
            )

    def limpar_placeholder(self):
        """
        Remove os textos placeholder das áreas de exibição.

        O método garante que os placeholders sejam removidos antes
        da inserção de novos conteúdos.
        """

        # Obtém o conteúdo atual das caixas de texto
        texto_normal = self.texto_normal.get(
            "1.0",
            tk.END
        ).strip()

        texto_visual = self.texto_visual.get(
            "1.0",
            tk.END
        ).strip()

        # Remove o placeholder do texto reconhecido
        if texto_normal == (
            "O texto reconhecido aparecerá aqui..."
        ):
            self.texto_normal.delete(
                "1.0",
                tk.END
            )

        # Remove o placeholder da representação visual
        if texto_visual == (
            "A representação em Libras aparecerá aqui..."
        ):
            self.texto_visual.delete(
                "1.0",
                tk.END
            )

    def reconhecer_audio_whisper(self, caminho_audio):
        """
        Realiza o reconhecimento de fala utilizando Whisper.

        Parâmetros

        caminho_audio : str
            Caminho do arquivo de áudio que será processado.
        """

        try:
            # Atualiza o status da interface
            self.status_var.set("Reconhecendo áudio...")

            # Atualiza visualmente a interface
            self.janela.update()

            # Executa a transcrição do áudio
            texto_reconhecido = (
                self.whisper_service.transcrever(
                    caminho_audio
                )
            )

            # Limpa a área de texto reconhecido
            self.texto_normal.delete("1.0", tk.END)

            # Exibe o texto reconhecido
            self.texto_normal.insert(
                tk.END,
                texto_reconhecido
            )

            # Limpa a área de representação visual
            self.texto_visual.delete("1.0", tk.END)

            # Exibe o texto em formato visual
            self.texto_visual.insert(
                tk.END,
                texto_reconhecido.upper()
            )

            # Calcula o erro WER da transcrição
            erro_wer = comparar_com_transcricao(
                caminho_audio,
                texto_reconhecido
            )

            # Verifica se o arquivo de referência existe
            if erro_wer is None:
                self.resultado_var.set(
                    "Arquivo .txt correspondente não encontrado."
                )

            else:
                # Exibe a métrica WER calculada
                self.resultado_var.set(
                    "Comparação com transcrição original | "
                    f"WER: {erro_wer:.2f}"
                )

            # Atualiza o status final
            self.status_var.set(
                "Reconhecimento finalizado."
            )

        except Exception as erro: # pylint: disable=broad-exception-caught
            # Exibe o traceback completo no terminal
            print(traceback.format_exc())

            # Exibe a mensagem de erro na interface
            messagebox.showerror(
                "Erro",
                str(erro)
            )

    def iniciar_ao_vivo(self):
        """
        Inicia o reconhecimento de fala ao vivo.

        O método cria uma thread paralela responsável pela captura
        contínua de áudio do microfone.
        """

        # Impede múltiplas sessões simultâneas
        if self.ao_vivo_ativo:
            return

        # Remove placeholders da interface
        self.limpar_placeholder()

        # Ativa o reconhecimento ao vivo
        self.ao_vivo_ativo = True

        # Incrementa o identificador da sessão
        self.sessao_ao_vivo += 1

        # Armazena o identificador atual da sessão
        sessao_atual = self.sessao_ao_vivo

        # Atualiza o status da interface
        self.status_var.set(
            "Reconhecimento ao vivo iniciado..."
        )

        # Cria thread para captura contínua de áudio
        thread = threading.Thread(
            target=self._loop_ao_vivo,
            args=(sessao_atual,),
            daemon=True
        )

        # Inicia a thread de reconhecimento
        thread.start()

    def _loop_ao_vivo(self, sessao_atual):
        """
        Executa o loop contínuo de reconhecimento ao vivo.

        Parâmetros

        sessao_atual : int
            Identificador da sessão atual de reconhecimento.
        """

        # Mantém o loop ativo enquanto a sessão existir
        while (
            self.ao_vivo_ativo
            and sessao_atual == self.sessao_ao_vivo
        ):
            caminho_temp = None

            try:
                # Atualiza o status para captura de áudio
                self.janela.after(
                    0,
                    lambda: self.status_var.set(
                        "Ouvindo..."
                    )
                )

                # Grava um bloco temporário de áudio
                caminho_temp = gravar_audio_temporario(
                    DURACAO_BLOCO,
                    TAXA_AMOSTRAGEM
                )

                # Interrompe caso a sessão tenha sido encerrada
                if (
                    not self.ao_vivo_ativo
                    or sessao_atual != self.sessao_ao_vivo
                ):
                    break

                # Atualiza o status para reconhecimento
                self.janela.after(
                    0,
                    lambda: self.status_var.set(
                        "Reconhecendo..."
                    )
                )

                # Realiza a transcrição do áudio
                texto = self.whisper_service.transcrever(
                    caminho_temp
                )

                # Interrompe caso a sessão tenha sido encerrada
                if (
                    not self.ao_vivo_ativo
                    or sessao_atual != self.sessao_ao_vivo
                ):
                    break

                # Adiciona texto caso exista transcrição
                if texto:
                    self.janela.after(
                        0,
                        lambda t=texto,
                        s=sessao_atual: (
                            self._append_texto_seguro(
                                t,
                                s
                            )
                        )
                    )

            except Exception: # pylint: disable=broad-exception-caught
                # Exibe o traceback completo no terminal
                print(traceback.format_exc())

            finally:
                # Remove o arquivo temporário gerado
                if (
                    caminho_temp
                    and os.path.exists(caminho_temp)
                ):
                    os.remove(caminho_temp)

        # Atualiza o status final do reconhecimento
        self.janela.after(
            0,
            lambda: self.status_var.set(
                "Reconhecimento ao vivo parado."
            )
        )

    def parar_ao_vivo(self):
        """
        Interrompe o reconhecimento de fala ao vivo.
        """

        # Desativa o reconhecimento ao vivo
        self.ao_vivo_ativo = False

        # Invalida sessões anteriores
        self.sessao_ao_vivo += 1

        # Desativa o reconhecimento da DNN
        self.dnn_ativo = False

        # Atualiza o status da interface
        self.status_var.set(
            "Reconhecimento ao vivo parado."
        )

    def _append_texto_seguro(self, texto, sessao_atual):
        """
        Adiciona texto reconhecido à interface com segurança.

        Parâmetros

        texto : str
            Texto reconhecido pelo modelo.

        sessao_atual : int
            Identificador da sessão atual.
        """

        # Interrompe caso a sessão tenha sido encerrada
        if (
            not self.ao_vivo_ativo
            or sessao_atual != self.sessao_ao_vivo
        ):
            return

        # Remove placeholders da interface
        self.limpar_placeholder()

        # Adiciona o texto reconhecido
        self.texto_normal.insert(
            tk.END,
            " " + texto
        )

        # Adiciona o texto visual em maiúsculas
        self.texto_visual.insert(
            tk.END,
            " " + texto.upper()
        )

    def reconhecer_microfone_dnn(self):
        """
        Inicia o reconhecimento utilizando a DNN.

        O método grava áudio do microfone e realiza a predição
        utilizando o modelo treinado.
        """

        # Impede múltiplas execuções simultâneas
        if self.dnn_ativo:
            return

        # Ativa o estado de reconhecimento da DNN
        self.dnn_ativo = True

        # Atualiza o status da interface
        self.status_var.set(
            "Iniciando reconhecimento com DNN..."
        )

        # Cria a thread de reconhecimento
        thread = threading.Thread(
            target=self._reconhecer_microfone_dnn_thread,
            daemon=True
        )

        # Inicia a thread
        thread.start()

    def _reconhecer_microfone_dnn_thread(self):
        """
        Executa o reconhecimento da DNN em uma thread separada.
        """

        try:
            # Atualiza o status para gravação
            self.janela.after(
                0,
                lambda: self.status_var.set(
                    "Gravando para DNN..."
                )
            )

            # Define o nome do arquivo temporário
            caminho_audio = "audio_dnn_temp.wav"

            # Grava áudio do microfone
            gravar_audio(
                caminho_audio,
                DURACAO_DNN,
                TAXA_AMOSTRAGEM
            )

            # Interrompe caso a DNN tenha sido parada
            if not self.dnn_ativo:
                return

            # Atualiza o status para reconhecimento
            self.janela.after(
                0,
                lambda: self.status_var.set(
                    "Reconhecendo com DNN..."
                )
            )

            # Realiza a predição da DNN
            palavra, confianca = (
                self.dnn_service.reconhecer(
                    caminho_audio
                )
            )

            # Interrompe caso a DNN tenha sido parada
            if not self.dnn_ativo:
                return

            # Atualiza a interface com o resultado
            self.janela.after(
                0,
                lambda: self._exibir_resultado_dnn(
                    palavra,
                    confianca
                )
            )

        except Exception as erro: # pylint: disable=broad-exception-caught
            # Exibe o traceback completo no terminal
            print(traceback.format_exc())

            # Exibe a mensagem de erro
            self.janela.after(
                0,
                lambda: messagebox.showerror(
                    "Erro",
                    str(erro)
                )
            )

        finally:
            # Finaliza o estado de reconhecimento
            self.dnn_ativo = False

    def _exibir_resultado_dnn(
        self,
        palavra,
        confianca
    ):
        """
        Exibe o resultado do reconhecimento da DNN.

        Parâmetros

        palavra : str
            Palavra reconhecida pela rede neural.

        confianca : float
            Valor de confiança da predição.
        """

        # Limpa a área de texto reconhecido
        self.texto_normal.delete("1.0", tk.END)

        # Exibe a palavra reconhecida e confiança
        self.texto_normal.insert(
            tk.END,
            f"{palavra.upper()} | "
            f"Confiança: {confianca:.2f}"
        )

        # Limpa a área visual
        self.texto_visual.delete("1.0", tk.END)

        # Exibe a representação visual
        self.texto_visual.insert(
            tk.END,
            palavra.upper()
        )

        # Atualiza a mensagem de resultado
        self.resultado_var.set(
            "Modo DNN: reconhecimento por classe treinada."
        )

        # Atualiza o status da interface
        self.status_var.set(
            "Reconhecimento DNN finalizado."
        )

    def limpar_texto(self):
        """
        Limpa as áreas de texto da interface.
        """

        # Limpa a área de texto reconhecido
        self.texto_normal.delete("1.0", tk.END)

        # Limpa a área de representação visual
        self.texto_visual.delete("1.0", tk.END)

        # Limpa o resultado atual
        self.resultado_var.set("")

        # Atualiza o status da interface
        self.status_var.set("Texto limpo.")

    def atualizar_estado_dnn(self):
        """
        Atualiza o estado do modelo DNN na interface.

        O método verifica se o modelo treinado está disponível
        e habilita ou desabilita funcionalidades relacionadas.
        """

        # Verifica se o modelo está disponível
        if self.dnn_service.modelo_disponivel():

            # Habilita o botão da DNN
            self.botao_dnn.configure(state="normal")

            # Atualiza o status do modelo
            self.resultado_var.set(
                "Modelo DNN disponível."
            )

        else:
            # Desabilita o botão da DNN
            self.botao_dnn.configure(state="disabled")

            # Atualiza a mensagem de status
            self.resultado_var.set(
                "Modelo DNN não encontrado. "
                "Treine a DNN primeiro."
            )

    def aplicar_paleta_escura(self):
        """
        Aplica a paleta de cores do modo escuro.
        """

        # Define o estado do tema atual
        self.modo_escuro = True

        # Define as cores da interface
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
        """
        Aplica a paleta de cores do modo claro.
        """

        # Define o estado do tema atual
        self.modo_escuro = False

        # Define as cores da interface
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
        """
        Inicia o treinamento da rede neural DNN.

        O treinamento é executado em uma thread separada para evitar
        travamentos na interface gráfica.
        """

        # Desabilita botões durante o treinamento
        self.botao_treinar_dnn.configure(state="disabled")
        self.botao_dnn.configure(state="disabled")

        # Atualiza o status da interface
        self.status_var.set(
            "Treinando DNN... Isso pode demorar."
        )

        # Cria a thread de treinamento
        thread = threading.Thread(
            target=self._treinar_dnn_thread,
            daemon=True
        )

        # Inicia a thread de treinamento
        thread.start()

    def _treinar_dnn_thread(self):
        """
        Executa o treinamento da DNN em paralelo.
        """

        try:
            # Executa o script de treinamento
            resultado = subprocess.run(
                [sys.executable, "treinar_dnn.py"],
                capture_output=True,
                text=True,
                check=False
            )

            # Verifica se ocorreu erro no treinamento
            if resultado.returncode != 0:
                self.janela.after(
                    0,
                    lambda: messagebox.showerror(
                        "Erro no treino",
                        resultado.stderr
                    )
                )

                return

            # Recarrega o modelo treinado
            self.dnn_service.carregar_modelo()

            # Atualiza a interface após o treino
            self.janela.after(
                0,
                self._finalizar_treino_dnn
            )

        except Exception as erro: # pylint: disable=broad-exception-caught
            # Exibe o traceback completo no terminal
            print(traceback.format_exc())

            # Exibe a mensagem de erro
            self.janela.after(
                0,
                lambda: messagebox.showerror(
                    "Erro",
                    str(erro)
                )
            )

    def _finalizar_treino_dnn(self):
        """
        Finaliza o processo de treinamento da DNN.
        """

        # Reabilita os botões da interface
        self.botao_treinar_dnn.configure(state="normal")
        self.botao_dnn.configure(state="normal")

        # Atualiza o status do sistema
        self.status_var.set(
            "Treinamento da DNN finalizado."
        )

        # Atualiza o resultado da interface
        self.resultado_var.set(
            "Modelo DNN treinado e carregado."
        )

    def definir_icone_janela(self):
        """
        Define o ícone personalizado da janela principal.
        """

        try:
            # Obtém o diretório base da aplicação
            base = os.path.dirname(
                os.path.abspath(__file__)
            )

            # Define o caminho do ícone .ico
            caminho_ico = os.path.join(
                base,
                "icons",
                "logo.ico"
            )

            # Define o caminho do ícone .png
            caminho_png = os.path.join(
                base,
                "icons",
                "logo.png"
            )

            # Utiliza o arquivo .ico caso exista
            if os.path.exists(caminho_ico):
                self.janela.iconbitmap(
                    caminho_ico
                )

            else:
                # Utiliza o PNG como fallback
                self.icone_janela = tk.PhotoImage(
                    file=caminho_png
                )

                self.janela.iconphoto(
                    False,
                    self.icone_janela
                )

        except Exception as erro: # pylint: disable=broad-exception-caught
            # Exibe erro de carregamento do ícone
            print(
                "Erro ao carregar ícone:",
                erro
            )

    def executar(self):
        """
        Inicia o loop principal da interface gráfica.
        """

        # Executa a aplicação
        self.janela.mainloop()
