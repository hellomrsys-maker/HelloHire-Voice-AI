"""
Persian Part-of-Speech Tagger
Universal Dependencies conformant tagger for Persian (Farsi).
"""

from typing import List, Tuple, Dict
from Persian_engine.brain.skills.tokenization import PersianTokenizer, ZWNJ

# Core closed-class Persian lexicons
PERSIAN_PRONOUNS = {"من", "تو", "او", "وی", "ما", "شما", "آن‌ها", "ایشان", "اینها", "آنها", "این", "آن", "خود"}
PERSIAN_PREPOSITIONS = {"به", "از", "در", "با", "برای", "تا", "بی", "بر", "چون", "مانند", "روی", "زیر"}
PERSIAN_CONJUNCTIONS = {"و", "یا", "اما", "ولی", "اگر", "که", "چون", "زیرا", "بلکه"}
PERSIAN_ADVERBS = {"همیشه", "هرگز", "دیروز", "امروز", "فردا", "خیلی", "بسیار", "هنوز", "شاید", "حتما"}
PERSIAN_AUXILIARIES = {"بودن", "شدن", "داشتن", "بایستن", "توانستن", "خواستن", "است", "هست", "نیست", "بود", "شد"}

COMMON_LIGHT_VERB_STEMS = {
    "کردن", "کن", "کرد", "کرده",
    "شدن", "شو", "شد", "شده",
    "زدن", "زن", "زد", "زده",
    "دادن", "ده", "داد", "داده",
    "گرفتن", "گیر", "گرفت", "گرفته",
    "رفتن", "رو", "رفت", "رفته",
    "آمدن", "آی", "آمد", "آمده",
    "دیدن", "بین", "دید", "دیده",
    "خواندن", "خوان", "خواند", "خوانده",
    "نوشتن", "نویس", "نوشت", "نوشته",
    "خوردن", "خور", "خورد", "خورده"
}

COMMON_ADJECTIVES = {
    "خوب", "بزرگ", "کوچک", "جدید", "قدیم", "زیبا", "مهم", "بلند", "کوتاه", "پاک",
    "سفید", "سیاه", "قرمز", "آبی", "روشن", "تاریک", "آسان", "دشوار", "سخت", "محترم"
}

class PersianPOSTagger:
    """
    Morpho-syntactic POS tagger assigning UD-style tags:
    NOUN, VERB, ADJ, PRON, ADP, CCONJ, ADV, AUX, PART, PUNCT.
    """
    
    def __init__(self):
        self.tokenizer = PersianTokenizer()

    def tag_word(self, word: str, prev_word: str = "", next_word: str = "") -> str:
        """Determines the POS tag of a single token in context."""
        # Punctuation
        if word in {"،", "؛", "؟", "!", ".", ":", "«", "»", "-", "(", ")"}:
            return "PUNCT"
            
        # Postposition rā
        if word == "را":
            return "PART"
            
        # Pronouns
        if word in PERSIAN_PRONOUNS:
            return "PRON"
            
        # Prepositions
        if word in PERSIAN_PREPOSITIONS:
            return "ADP"
            
        # Conjunctions
        if word in PERSIAN_CONJUNCTIONS:
            return "CCONJ"
            
        # Adverbs
        if word in PERSIAN_ADVERBS:
            return "ADV"
            
        # Known Adjectives
        if word in COMMON_ADJECTIVES:
            return "ADJ"
            
        # Verbs with prefixes (mi-, be-, ne-, na-)
        if word.startswith(f"می{ZWNJ}") or word.startswith("می‌") or word.startswith("می"):
            return "VERB"
        if word.startswith(f"نمی{ZWNJ}") or word.startswith("نمی‌"):
            return "VERB"
        if (word.startswith("ب") or word.startswith("ن")) and any(word.endswith(end) for end in ["م", "ی", "د", "یم", "ید", "ند"]):
            return "VERB"
            
        # Check verbal stems / suffixes
        base = word
        for stem in COMMON_LIGHT_VERB_STEMS:
            if stem in word:
                return "VERB"
                
        # Plural nouns
        if word.endswith(f"{ZWNJ}ها") or word.endswith("‌ها") or word.endswith("ها") or word.endswith("ان"):
            return "NOUN"
            
        # Default noun
        return "NOUN"

    def tag_sentence(self, text: str) -> List[Tuple[str, str]]:
        """Tokenizes and returns a list of (token, pos_tag) pairs."""
        tokens = self.tokenizer.tokenize_words(text)
        tagged = []
        for i, tok in enumerate(tokens):
            prev_tok = tokens[i - 1] if i > 0 else ""
            next_tok = tokens[i + 1] if i + 1 < len(tokens) else ""
            pos = self.tag_word(tok, prev_tok, next_tok)
            tagged.append((tok, pos))
        return tagged
