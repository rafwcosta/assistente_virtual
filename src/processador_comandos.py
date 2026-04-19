import json
import nltk
from nltk.metrics.distance import jaccard_distance

_STOPWORDS_PT = {
    'a','ao','aos','aquela','aquelas','aquele','aqueles','aquilo','as','ate',
    'com','como','da','das','de','dela','delas','dele','deles','depois','do',
    'dos','e','ela','elas','ele','eles','em','entre','era','essa','essas',
    'esse','esses','esta','estas','este','estes','eu','foi','foram','isso',
    'isto','ja','la','lhe','lhes','mais','mas','me','mesmo','meu','meus',
    'minha','minhas','muito','na','nas','nao','nem','no','nos','num','numa',
    'o','os','ou','para','pela','pelas','pelo','pelos','por','qual','quando',
    'que','quem','se','sem','seu','seus','si','so','sua','suas','tambem',
    'te','tem','tendo','ter','toda','todas','todo','todos','tu','tua','tuas',
    'tudo','um','uma','umas','uns','voce','voces'
}


def _carregar_stopwords() -> set:
    try:
        nltk.data.find("corpora/stopwords")
        from nltk.corpus import stopwords
        return set(stopwords.words("portuguese"))
    except LookupError:
        pass
    try:
        nltk.download("stopwords", quiet=True)
        from nltk.corpus import stopwords
        return set(stopwords.words("portuguese"))
    except Exception:
        pass
    return _STOPWORDS_PT.copy()


def _tokenizar(texto: str) -> list:
    for pacote in ["tokenizers/punkt_tab", "tokenizers/punkt"]:
        try:
            nltk.data.find(pacote)
            return nltk.word_tokenize(texto.lower(), language="portuguese")
        except LookupError:
            pass
    for nome in ["punkt_tab", "punkt"]:
        try:
            nltk.download(nome, quiet=True)
            return nltk.word_tokenize(texto.lower(), language="portuguese")
        except Exception:
            pass
    return texto.lower().split()


class ProcessadorComandos:

    def __init__(self, caminho_config: str = "config/commands.json"):
        with open(caminho_config, "r", encoding="utf-8") as f:
            self.config = json.load(f)

        self.comandos = self.config["commands"]
        self.limiar = self.config["settings"].get("confidence_threshold", 0.5)
        self.stopwords = _carregar_stopwords()

    def _preprocessar(self, texto: str) -> set:
        tokens = _tokenizar(texto)
        return {
            token
            for token in tokens
            if token.isalpha() and token not in self.stopwords
        }

    def _similaridade_jaccard(self, conjunto_a: set, conjunto_b: set) -> float:
        if not conjunto_a or not conjunto_b:
            return 0.0
        return 1.0 - jaccard_distance(conjunto_a, conjunto_b)

    def encontrar_comando(self, texto_transcrito: str) -> dict | None:
        tokens_entrada = self._preprocessar(texto_transcrito)

        if not tokens_entrada:
            print("[PROCESSADOR] Texto vazio ou apenas stopwords. Ignorando.")
            return None

        melhor_comando = None
        melhor_pontuacao = 0.0

        for comando in self.comandos:
            for palavra_chave in comando["keywords"]:
                tokens_chave = self._preprocessar(palavra_chave)
                if not tokens_chave:
                    continue
                pontuacao = self._similaridade_jaccard(tokens_entrada, tokens_chave)
                if pontuacao > melhor_pontuacao:
                    melhor_pontuacao = pontuacao
                    melhor_comando = comando

        print(
            f"[PROCESSADOR] Melhor match: "
            f"'{melhor_comando['id'] if melhor_comando else None}' "
            f"com pontuacao={melhor_pontuacao:.2f} (limiar={self.limiar})"
        )

        if melhor_pontuacao >= self.limiar:
            return melhor_comando

        print("[PROCESSADOR] Nenhum comando reconhecido com confiança suficiente.")
        return None
