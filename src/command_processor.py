"""
command_processor.py
---------------------
Módulo de processamento de linguagem natural usando NLTK.
Responsável por identificar qual comando o usuário quis dizer
a partir do texto transcrito.
"""

import json
import nltk
from nltk.metrics.distance import jaccard_distance

# Stopwords em português embutidas como fallback (caso NLTK offline)
_STOPWORDS_PT_FALLBACK = {
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


def _load_stopwords() -> set:
    """Tenta carregar stopwords do NLTK; usa fallback embutido se offline."""
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
    # Fallback: lista embutida
    return _STOPWORDS_PT_FALLBACK.copy()


def _tokenize(text: str) -> list:
    """Tokeniza o texto; usa NLTK se disponível, senão split simples."""
    try:
        nltk.data.find("tokenizers/punkt_tab")
        return nltk.word_tokenize(text.lower(), language="portuguese")
    except LookupError:
        pass
    try:
        nltk.download("punkt_tab", quiet=True)
        return nltk.word_tokenize(text.lower(), language="portuguese")
    except Exception:
        pass
    try:
        nltk.download("punkt", quiet=True)
        return nltk.word_tokenize(text.lower(), language="portuguese")
    except Exception:
        pass
    # Fallback: tokenização simples por espaço
    return text.lower().split()


class CommandProcessor:
    """
    Processador de comandos baseado em NLTK.
    Compara o texto transcrito com os keywords do arquivo JSON
    usando tokenização, remoção de stopwords e similaridade de Jaccard.
    """

    def __init__(self, config_path: str = "config/commands.json"):
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)

        self.commands = self.config["commands"]
        self.threshold = self.config["settings"].get("confidence_threshold", 0.5)
        self.stop_words = _load_stopwords()

    def _preprocess(self, text: str) -> set:
        """
        Tokeniza e remove stopwords do texto.

        Returns:
            Conjunto de tokens relevantes.
        """
        tokens = _tokenize(text)
        return {
            token
            for token in tokens
            if token.isalpha() and token not in self.stop_words
        }

    def _jaccard_similarity(self, set_a: set, set_b: set) -> float:
        """Similaridade de Jaccard: 1 - distância_de_Jaccard."""
        if not set_a or not set_b:
            return 0.0
        return 1.0 - jaccard_distance(set_a, set_b)

    def find_command(self, transcribed_text: str) -> dict | None:
        """
        Encontra o comando mais adequado para o texto transcrito.

        Args:
            transcribed_text: Texto vindo do módulo de transcrição.

        Returns:
            Dicionário do comando encontrado ou None se não houver match.
        """
        input_tokens = self._preprocess(transcribed_text)

        if not input_tokens:
            print("[PROCESSOR] Texto vazio ou apenas stopwords. Ignorando.")
            return None

        best_command = None
        best_score = 0.0

        for command in self.commands:
            for keyword in command["keywords"]:
                keyword_tokens = self._preprocess(keyword)
                if not keyword_tokens:
                    continue
                score = self._jaccard_similarity(input_tokens, keyword_tokens)
                if score > best_score:
                    best_score = score
                    best_command = command

        print(
            f"[PROCESSOR] Melhor match: "
            f"'{best_command['id'] if best_command else None}' "
            f"com score={best_score:.2f} (threshold={self.threshold})"
        )

        if best_score >= self.threshold:
            return best_command

        print("[PROCESSOR] Nenhum comando reconhecido com confiança suficiente.")
        return None
