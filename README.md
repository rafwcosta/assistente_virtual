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
├── audios/
│   ├── abrir_navegador.wav     ← Áudio de teste gravado
│   ├── abrir_editor.wav        ← Áudio de teste gravado
│   ├── aumentar_volume.wav     ← Áudio de teste gravado
│   └── bloquear_tela.wav       ← Áudio de teste gravado
├── config/
│   └── commands.json           ← Configuração de todos os comandos e ações
├── src/
│   ├── transcritor.py          ← Sensor: Whisper (HuggingFace) para transcrição
│   ├── processador_comandos.py ← NLP: NLTK (tokenização + similaridade Jaccard)
│   └── atuadores.py            ← Atuadores: ações reais no SO
├── tests/
│   └── teste_assistente.py     ← Testes automatizados com unittest
├── assistente.py               ← Script principal (ponto de entrada)
├── interface.py                ← Interface gráfica (CustomTkinter)
└── requirements.txt
```

---

## Comandos Disponíveis

| Comando          | Exemplo de frase               | Ação                           |
|------------------|--------------------------------|--------------------------------|
| Abrir navegador  | "abrir navegador"              | Abre o navegador padrão        |
| Abrir editor     | "abrir editor de código"       | Abre o VS Code (ou alternativa)|
| Aumentar volume  | "aumentar volume"              | Aumenta o volume em 10%        |
| Bloquear tela    | "bloquear a tela"              | Bloqueia a sessão do usuário   |

---

## Instalação

### 1. Pré-requisitos
```bash
# Linux (Ubuntu/Debian)
sudo apt install ffmpeg portaudio19-dev python3-dev
```

### 2. Dependências Python
```bash
pip install -r requirements.txt
```

### 3. Pacotes NLTK
Os pacotes `punkt`, `punkt_tab` e `stopwords` são baixados automaticamente
na primeira execução, caso haja conexão com a internet.

---

## Como Usar

### Interface gráfica
```bash
python interface.py
```

### Modo interativo (terminal)
```bash
python assistente.py
```

### Processar um arquivo de áudio
```bash
python assistente.py --arquivo audios/abrir_navegador.wav
```

---

## Testes Automatizados

### Executar os testes
```bash
python -m unittest tests/teste_assistente.py -v
```

Na primeira execução o Whisper baixa o modelo (~250 MB) e armazena em cache.

### Suítes de testes

| Suíte                      | Descrição                                       |
|----------------------------|-------------------------------------------------|
| `TesteProcessadorComandos` | Testa o NLP isolado (sem áudio, sem SO)         |
| `TesteAtuador`             | Testa os atuadores com mocks do SO              |
| `TesteIntegracao`          | Pipeline completo com mocks e arquivos de áudio |

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

Em seguida, adicione o método `_acao_meu_novo_comando` em `atuadores.py`.
