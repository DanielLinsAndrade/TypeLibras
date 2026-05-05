# TypeLibras


## Descrição

Este projeto tem como objetivo desenvolver um sistema capaz de reconhecer fala em português e convertê-la em uma representação visual baseada em um alfabeto inspirado na Língua Brasileira de Sinais (Libras).

A aplicação implementa duas abordagens distintas de reconhecimento de fala:

- Utilização de modelo pré-treinado (Whisper)
- Utilização de uma Rede Neural Densa (DNN) treinada localmente

Essa dualidade permite comparar desempenho, generalização e limitações entre modelos robustos e modelos supervisionados simples.

---

## Funcionalidades

- Reconhecimento de fala a partir de arquivos de áudio
- Reconhecimento de fala em tempo real via microfone
- Conversão do texto reconhecido para representação visual utilizando fonte SignWriting
- Avaliação do reconhecimento com base em transcrições reais (WER)
- Classificação de palavras específicas utilizando uma rede neural DNN
- Interface gráfica desenvolvida com Tkinter

---

## Arquitetura do Projeto

O sistema foi modularizado para facilitar manutenção e evolução:

```
TalkLibras/
├── dataset/
│   └── (áudios da Constituição e transcrições)
│
├── dataset_dnn/
│   ├── oi/
│   ├── sim/
│   ├── não/
│   ├── ajuda/
│   ├── libras/
│   └── obrigado/
│
├── app.py
├── config.py
├── ui.py
│
├── whisper_service.py
├── dnn_service.py
├── audio_utils.py
├── evaluation.py
│
├── treinar_dnn.py
├── gerar_dataset_dnn.py
│
├── modelo_dnn_libras.h5
├── label_encoder_dnn.pkl
├── scaler_dnn.pkl
│
├── requirements.txt
├── README.md
├── LICENSE
└── .gitignore
```

### Descrição dos principais componentes

- `app.py`: ponto de entrada da aplicação  
- `ui.py`: interface gráfica e fluxo de interação com o usuário  
- `config.py`: configurações gerais do sistema  

- `whisper_service.py`: integração com o modelo Whisper para reconhecimento de fala  
- `dnn_service.py`: classificação de palavras utilizando rede neural treinada  
- `audio_utils.py`: funções auxiliares para gravação e processamento de áudio  
- `evaluation.py`: cálculo da métrica WER para avaliação  

- `treinar_dnn.py`: script de treinamento da rede neural  
- `gerar_dataset_dnn.py`: geração do dataset sintético para treinamento  

- `dataset/`: base de áudios reais utilizada com o Whisper  
- `dataset_dnn/`: base de dados organizada por classes para treinamento da DNN  

- `modelo_dnn_libras.h5`: modelo treinado da rede neural  
- `label_encoder_dnn.pkl`: codificador de rótulos  
- `scaler_dnn.pkl`: normalizador das features  

---

## Tecnologias Utilizadas

- Python  
- Tkinter (interface gráfica)  
- Whisper (OpenAI)  
- TensorFlow / Keras  
- Librosa  
- Scikit-learn  
- SoundDevice  
- FFmpeg  

---

## Dataset

### Base de dados para Whisper

Áudios reais da Constituição Federal Brasileira, utilizados para validação do modelo:

- [fb-audio-corpora/constituicao16k](https://gitlab.com/fb-audio-corpora/constituicao16k)

### Base de dados para DNN

A base foi gerada de forma sintética utilizando Text-to-Speech (TTS), com variações aplicadas para simular diversidade de fala:

- variação de velocidade  
- variação de volume  
- adição de ruído  
- inserção de silêncio  

Essa abordagem foi adotada devido à limitação de dados reais disponíveis.

---

## Fonte de Representação Visual

A representação visual utiliza uma fonte baseada em SignWriting.

Download da fonte:  
- [SignWriting](https://www.itdeaf.com.br/downloads/)

Referência teórica:  
- [Pesquisadora aborda os usos possíveis do SignWriting por surdos](https://www.ufsm.br/midias/arco/post395)

Observação: a fonte utilizada possui licença própria e não está incluída neste repositório.

---

## Modelo Whisper

O reconhecimento principal de fala utiliza o modelo Whisper da OpenAI:

- [OpenAI/whisper](https://github.com/openai/whisper)

---

## Como Executar o Projeto

### 1. Clonar o repositório
~~~
git clone https://github.com/DanielLinsAndrade/TypeLibras.git
~~~
~~~
cd TypeLibras
~~~
### 2. Criar ambiente virtual
~~~
python -m venv venv
~~~
~~~
venv\Scripts\activate
~~~
### 3. Instalar dependências
~~~
pip install -r requirements.txt
~~~
### 4. Executar aplicação
~~~
python app.py
~~~
---

## Observações Importantes

- Os datasets e modelos treinados não estão versionados no repositório por questões de tamanho.
- O modelo DNN possui limitações devido ao tamanho e natureza do dataset.
- É necessário possuir o FFmpeg instalado e configurado no sistema.

### Instalação e Configuração do FFmpeg

O projeto utiliza o FFmpeg para processamento de áudio. É necessário que ele esteja instalado e configurado corretamente no sistema para que o reconhecimento de fala funcione.

#### Windows

1. Acesse o site oficial de builds:

   [Download ffmpeg](https://www.gyan.dev/ffmpeg/builds/)

2. Baixe o arquivo:
~~~
ffmpeg-release-essentials.zip
~~~
3. Extraia o conteúdo em uma pasta, por exemplo:
~~~
C:\ffmpeg
~~~
4. Dentro da pasta extraída, localize o diretório `bin`, que deve conter:
~~~
C:\ffmpeg\bin\ffmpeg.exe
~~~
5. Adicione o FFmpeg ao PATH do sistema:

- Pressione `Win + S` e procure por "Variáveis de Ambiente"
- Clique em "Editar variáveis de ambiente do sistema"
- Clique em "Variáveis de Ambiente"
- Em "Variáveis do sistema", selecione `Path` e clique em "Editar"
- Clique em "Novo" e adicione:

  ```
  C:\ffmpeg\bin
  ```

- Confirme todas as janelas

6. Reinicie o terminal ou o VS Code

---

#### Linux (Ubuntu/Debian)
~~~
bash
sudo apt update
sudo apt install ffmpeg
~~~

#### macOS (usando Homebrew)
~~~
brew install ffmpeg
~~~

### Verificando a instalação
~~~
ffmpeg -version
~~~
Se a instalação estiver correta, o terminal exibirá informações sobre a versão do FFmpeg.

#### Observações

- O FFmpeg é necessário para o funcionamento do modelo Whisper.
- Caso o comando ffmpeg -version não funcione, verifique se o PATH foi configurado corretamente.
- Em alguns casos, pode ser necessário reiniciar o sistema para aplicar as alterações.
---

## Comparação entre Abordagens

| Critério       | Whisper              | DNN                   |
|---------------|----------------------|-----------------------|
| Tipo          | Pré-treinado         | Treinado localmente   |
| Entrada       | Fala livre           | Palavras específicas  |
| Precisão      | Alta                 | Baixa a moderada      |
| Generalização | Alta                 | Limitada              |
| Complexidade  | Alta                 | Baixa                 |

---

## Licença

Este projeto utiliza a licença MIT para o código-fonte.

Recursos de terceiros (como Whisper e fontes tipográficas) mantêm suas respectivas licenças.
