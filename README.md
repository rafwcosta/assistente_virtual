# Assistente Virtual por Voz 🎙️
**Disciplina: Inteligência Artificial | Automação por comandos de voz**

---

## Visão Geral

Assistente virtual em Python que escuta comandos de voz, transcreve usando
o modelo **Whisper** (HuggingFace), interpreta com **NLTK** e executa ações
no sistema operacional. Todos os comandos são configurados externamente via
**JSON**, sem hardcode no código-fonte.

---

## Estrutura do Projeto

```
assistente_virtual/
├── config/
│   └── commands.json              ← Configuração de todos os comandos e ações
├── src/
│   ├── transcritor.py             ← Sensor: Whisper (HuggingFace) para transcrição
│   ├── processador_comandos.py    ← NLP: NLTK (tokenização + similaridade Jaccard)
│   └── atuadores.py               ← Atuadores: ações reais no SO
├── tests/
│   └── teste_assistante.py         ← Testes automatizados com unittest
├── audio_tests/                   ← Áudios de teste (gerados por generate_test_audio.py)
├── assistente.py                   ← Script principal (ponto de entrada)
├── gerar_teste_audio.py           ← Gerador de áudios para testes
└── requirements.txt
```

---

## Comandos Disponíveis

| Comando          | Exemplo de frase               | Ação                          |
|------------------|--------------------------------|-------------------------------|
| Abrir navegador  | "abrir navegador"              | Abre o navegador padrão       |
| Abrir editor     | "abrir editor de código"       | Abre o VS (ou alternativa)    |
| Aumentar volume  | "aumentar volume"              | Aumenta o volume em 10%       |
| Bloquear tela    | "bloquear a tela"              | Bloqueia a sessão do usuário  |

---

## Instalação

### 1. Pré-requisitos
```bash
# Linux (Ubuntu/Debian)
sudo apt install ffmpeg portaudio19-dev python3-dev

# macOS
brew install ffmpeg portaudio
```

### 2. Dependências Python
```bash
pip install -r requirements.txt
```

### 3. Pacotes NLTK (baixados automaticamente na primeira execução)
Os pacotes `punkt`, `punkt_tab` e `stopwords` são baixados automaticamente.

---

## Como Usar

### Modo interativo (microfone)
```bash
python assistant.py
```

### Processar um arquivo de áudio
```bash
python assistant.py --file caminho/para/audio.wav
```

---

## Testes Automatizados

### 1. Gerar os arquivos de áudio de teste
```bash
python generate_test_audio.py
```

### 2. Executar os testes
```bash
python -m unittest tests/test_assistant.py -v
```

### Suites de testes

| Suite                  | Descrição                                        |
|------------------------|--------------------------------------------------|
| `TestCommandProcessor` | Testa o NLP isolado (sem áudio, sem SO)          |
| `TestActuator`         | Testa os atuadores com mocks do SO               |
| `TestIntegration`      | Pipeline completo (com e sem arquivos de áudio)  |

---

## Arquitetura — Sistema Inteligente

```
SENSOR (Microfone)
      ↓
[Transcrição Whisper]  ←→  HuggingFace Transformers
      ↓
[Processamento NLTK]   ←→  commands.json (externo)
      ↓
[Atuador]              →   SO: navegador / editor / volume / tela
```

### Componentes de IA utilizados
- **Modelo**: `openai/whisper-small` via HuggingFace Transformers
- **NLP**: NLTK — tokenização em português, remoção de stopwords,
  similaridade de Jaccard para matching fuzzy de comandos

---

## Adicionando Novos Comandos

Edite **apenas** o arquivo `config/commands.json`. Não é necessário alterar
nenhum código Python:

```json
{
  "commands": [
    {
      "id": "meu_novo_comando",
      "keywords": ["frase de ativação", "variação 1", "variação 2"],
      "action": "meu_novo_comando",
      "description": "Descrição do que faz",
      "response": "Mensagem exibida ao executar"
    }
  ],
  "actions": {
    "meu_novo_comando": {
      "parametros": "configuração aqui"
    }
  }
}
```

Em seguida, adicione o método `_action_meu_novo_comando` em `atuadores.py`.
