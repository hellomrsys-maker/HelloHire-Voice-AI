"""Turkish POS Tagging Skill.

Provides UPOS tagging tailored for Turkish agglutinative morpho-syntax,
accurately distinguishing postpositions, pronouns, particles, verbs, adjectives, and nouns.
"""

import re
from typing import List, Dict, Any
from .tokenization import TurkishTokenizer


class TurkishPOSTagger:
    POSTPOSITIONS = {
        "için", "ile", "gibi", "kadar", "doğru", "göre", "rağmen",
        "karşın", "sonra", "önce", "beri", "dolayı", "ötürü", "karşı", "birlikte"
    }

    PRONOUNS = {
        "ben", "sen", "o", "biz", "siz", "onlar",
        "bana", "sana", "ona", "bize", "size", "onlara",
        "beni", "seni", "onu", "bizi", "sizi", "onları",
        "bende", "sende", "onda", "bizde", "sizde", "onlarda",
        "benden", "senden", "ondan", "bizden", "sizden", "onlardan",
        "benim", "senin", "onun", "bizim", "sizin", "onların",
        "bu", "şu", "bunlar", "şunlar", "bunu", "şunu", "buna", "şuna", "bunda", "şunda",
        "kim", "ne", "nerede", "nereye", "nereden", "nasıl", "neden", "niçin", "hangi",
        "kendi", "kendim", "kendin", "kendisi", "kendimiz", "kendiniz", "kendileri",
        "herkes", "hiçbiri", "biri", "bazıları"
    }

    CONJUNCTIONS = {
        "ve", "veya", "ya da", "ama", "fakat", "lakin", "ancak", "çünkü",
        "halbuki", "oysa", "oysaki", "madem", "mademki", "ile"
    }

    SUBORDINATING_CONJUNCTIONS = {"ki", "eğer"}

    PARTICLES = {
        "mi", "mı", "mü", "mu",
        "misin", "mısın", "müsün", "musun",
        "misiniz", "mısınız", "müsünüz", "musunuz",
        "de", "da", "dahi", "bile", "ise"
    }

    NUMERAL_WORDS = {
        "sıfır", "bir", "iki", "üç", "dört", "beş", "altı", "yedi", "sekiz", "dokuz",
        "on", "yirmi", "otuz", "kırk", "elli", "altmış", "yetmiş", "seksen", "doksan",
        "yüz", "bin", "milyon", "milyar"
    }

    COMMON_ADJECTIVES = {
        "yeni", "eski", "büyük", "küçük", "güzel", "çirkin", "iyi", "kötü",
        "kolay", "zor", "uzun", "kısa", "geniş", "dar", "sıcak", "soğuk",
        "kırmızı", "mavi", "yeşil", "sarı", "siyah", "beyaz", "ak", "kara",
        "doğru", "yanlış", "önemli", "farklı", "aynı", "bütün", "tüm", "her"
    }

    COMMON_ADVERBS = {
        "dün", "bugün", "yarın", "şimdi", "sonra", "önce", "erken", "geç",
        "çok", "az", "fazla", "daha", "en", "oldukça", "gayet", "özellikle",
        "hızlı", "yavaş", "dikkatle", "birlikte", "hemen", "asla", "daima", "her zaman"
    }

    def __init__(self):
        pass

    def tag_token(self, token: str) -> str:
        tok_lower = TurkishTokenizer.turkish_lower(token.strip())

        if re.match(r"^[^\w\s]+$", token):
            return "PUNCT"
        if re.match(r"^\d+(?:[.,]\d+)?$", token) or tok_lower in self.NUMERAL_WORDS:
            return "NUM"
        if tok_lower in self.POSTPOSITIONS:
            return "ADP"
        if tok_lower in self.PRONOUNS:
            return "PRON"
        if tok_lower in self.PARTICLES:
            return "PART"
        if tok_lower in self.SUBORDINATING_CONJUNCTIONS:
            return "SCONJ"
        if tok_lower in self.CONJUNCTIONS:
            return "CCONJ"
        if tok_lower in self.COMMON_ADVERBS:
            return "ADV"
        if tok_lower in self.COMMON_ADJECTIVES:
            return "ADJ"

        # Check for verbs
        if tok_lower.endswith(("mek", "mak")):
            return "VERB"
        if any(tok_lower.endswith(sfx) for sfx in (
            "iyor", "ıyor", "üyor", "uyor",
            "iyorum", "ıyorsun", "iyoruz", "iyorsunuz", "iyorlar",
            "di", "dı", "dü", "du", "ti", "tı", "tü", "tu",
            "dim", "dın", "dik", "diniz", "diler",
            "tim", "tın", "tik", "tiniz", "tiler",
            "miş", "mış", "müş", "muş",
            "mişim", "mişsin", "mişiz", "mişsiniz", "mişler",
            "ecek", "acak", "eceğim", "eceksin", "eceğiz", "eceksiniz", "ecekler",
            "acağam", "acaksın", "acağız", "acaksınız", "acaklar",
            "meli", "malı", "meliyim", "melisin", "meliyiz", "melisiniz",
            "elim", "alım"
        )):
            return "VERB"

        # Adjective derivational suffixes: -li, -siz, -lik
        if any(tok_lower.endswith(sfx) for sfx in ("li", "lı", "lü", "lu", "siz", "sız", "süz", "suz")):
            if len(tok_lower) >= 4:
                return "ADJ"

        # Adverbs ending in -ce / -ca
        if tok_lower.endswith(("ce", "ca", "çe", "ça")) and len(tok_lower) >= 5:
            return "ADV"

        # Default open class for Turkish words
        return "NOUN"

    def tag(self, tokens: List[str]) -> List[Dict[str, str]]:
        """Tags a sequence of Turkish tokens."""
        tagged = []
        for tok in tokens:
            tag = self.tag_token(tok)
            tagged.append({"token": tok, "pos": tag})
        return tagged
