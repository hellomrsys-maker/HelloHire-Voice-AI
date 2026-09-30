"""
Portuguese Part-of-Speech Tagger adhering to Universal Dependencies (UD) standards.
"""

from typing import List, Dict, Any


class PortuguesePOSTagger:
    """
    Assigns Universal Dependencies POS tags to Portuguese tokens.
    """

    PRONOUNS = {
        "eu": "PRON", "tu": "PRON", "ele": "PRON", "ela": "PRON",
        "nós": "PRON", "vós": "PRON", "eles": "PRON", "elas": "PRON",
        "você": "PRON", "vocês": "PRON",
        "me": "PRON", "te": "PRON", "se": "PRON", "lhe": "PRON",
        "nos": "PRON", "vos": "PRON", "lhes": "PRON",
        "o": "PRON", "a": "PRON", "os": "PRON", "as": "PRON",
        "mim": "PRON", "ti": "PRON", "si": "PRON", "comigo": "PRON", "contigo": "PRON", "consigo": "PRON",
        "alguém": "PRON", "ninguém": "PRON", "tudo": "PRON", "nada": "PRON", "algo": "PRON",
        "quem": "PRON", "que": "PRON", "qual": "PRON", "quais": "PRON"
    }

    DETERMINERS = {
        "o": "DET", "a": "DET", "os": "DET", "as": "DET",
        "um": "DET", "uma": "DET", "uns": "DET", "umas": "DET",
        "este": "DET", "esta": "DET", "estes": "DET", "estas": "DET",
        "esse": "DET", "essa": "DET", "esses": "DET", "essas": "DET",
        "aquele": "DET", "aquela": "DET", "aqueles": "DET", "aquelas": "DET",
        "meu": "DET", "minha": "DET", "meus": "DET", "minhas": "DET",
        "teu": "DET", "tua": "DET", "teus": "DET", "tuas": "DET",
        "seu": "DET", "sua": "DET", "seus": "DET", "suas": "DET",
        "nosso": "DET", "nossa": "DET", "nossos": "DET", "nossas": "DET"
    }

    PREPOSITIONS = {
        "de", "em", "a", "para", "por", "com", "sem", "sob", "sobre",
        "trás", "ante", "até", "contra", "desde", "entre", "perante",
        "do", "da", "dos", "das", "no", "na", "nos", "nas", "ao", "aos", "à", "às",
        "pelo", "pela", "pelos", "pelas", "num", "numa", "deste", "neste"
    }

    CONJUNCTIONS = {
        "e": "CCONJ", "mas": "CCONJ", "ou": "CCONJ", "porém": "CCONJ", "contudo": "CCONJ",
        "todavia": "CCONJ", "portanto": "CCONJ",
        "que": "SCONJ", "se": "SCONJ", "quando": "SCONJ", "porque": "SCONJ", "como": "SCONJ",
        "embora": "SCONJ", "caso": "SCONJ", "enquanto": "SCONJ"
    }

    ADVERBS = {
        "não": "ADV", "nunca": "ADV", "jamais": "ADV", "sempre": "ADV", "já": "ADV",
        "ainda": "ADV", "muito": "ADV", "pouco": "ADV", "bem": "ADV", "mal": "ADV",
        "aqui": "ADV", "ali": "ADV", "lá": "ADV", "ontem": "ADV", "hoje": "ADV",
        "amanhã": "ADV", "talvez": "ADV", "depois": "ADV", "antes": "ADV"
    }

    ADJECTIVES = {
        "bom": "ADJ", "boa": "ADJ", "bons": "ADJ", "boas": "ADJ",
        "mau": "ADJ", "má": "ADJ", "maus": "ADJ", "más": "ADJ",
        "grande": "ADJ", "pequeno": "ADJ", "pequena": "ADJ",
        "novo": "ADJ", "nova": "ADJ", "velho": "ADJ", "velha": "ADJ",
        "fácil": "ADJ", "difícil": "ADJ", "inteligente": "ADJ", "cansado": "ADJ",
        "cansada": "ADJ", "ótimo": "ADJ", "ótima": "ADJ", "importante": "ADJ"
    }

    PUNCTUATION = {",", ".", "!", "?", ";", ":", "\"", "'", "-", "—", "(", ")"}

    VERB_SUFFIXES = [
        "ando", "endo", "indo", "ado", "ido", "ar", "er", "ir",
        "amos", "emos", "imos", "aram", "eram", "iram",
        "ava", "avas", "ávamos", "avam", "ia", "ias", "íamos", "iam",
        "asse", "esses", "íssemos", "assem", "essem", "issem",
        "arei", "arás", "ará", "aremos", "arão",
        "aria", "arias", "aríamos", "ariam"
    ]

    def tag_tokens(self, tokens: List[str]) -> List[Dict[str, str]]:
        """Assigns UD POS tags to tokens."""
        tagged = []
        for tok in tokens:
            pos = self._predict_pos(tok)
            tagged.append({"token": tok, "pos": pos})
        return tagged

    def _predict_pos(self, tok: str) -> str:
        low = tok.lower()

        if low in self.PUNCTUATION:
            return "PUNCT"
        if low in ("o", "a", "os", "as"):
            return "DET"
        if low in self.PREPOSITIONS:
            return "ADP"
        if low in self.CONJUNCTIONS:
            return self.CONJUNCTIONS[low]
        if low in self.ADVERBS:
            return "ADV"
        if low in self.ADJECTIVES:
            return "ADJ"
        if low in self.PRONOUNS:
            return "PRON"
        if low in self.DETERMINERS:
            return "DET"

        # Check verbal patterns or hyphenated clitics
        if "-" in low:
            base, _ = low.split("-", 1)
            return "VERB"

        from .verb_conjugator import PortugueseVerbConjugator
        try:
            if PortugueseVerbConjugator().lemmatize(low) is not None:
                return "VERB"
        except Exception:
            pass

        for sfx in self.VERB_SUFFIXES:
            if low.endswith(sfx) and len(low) >= len(sfx) + 2:
                if low not in self.ADJECTIVES and low not in self.ADVERBS:
                    return "VERB"

        return "NOUN"
