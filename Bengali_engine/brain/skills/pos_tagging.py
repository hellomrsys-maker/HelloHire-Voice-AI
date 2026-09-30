"""
Bengali Part-of-Speech Tagger adhering to Universal Dependencies (UD) standards.
"""

from typing import List, Dict, Any


class BengaliPOSTagger:
    """
    Assigns Universal Dependencies POS tags to Bengali tokens.
    """

    PRONOUNS = {
        "আমি": "PRON", "আমরা": "PRON", "আমাকে": "PRON", "আমাদের": "PRON",
        "তুমি": "PRON", "তোমরা": "PRON", "তোমাকে": "PRON", "তোমাদের": "PRON", "তোকে": "PRON",
        "তুই": "PRON", "তোরা": "PRON", "তোর": "PRON",
        "আপনি": "PRON", "আপনারা": "PRON", "আপনাকে": "PRON", "আপনাদের": "PRON", "আপনার": "PRON",
        "সে": "PRON", "তারা": "PRON", "তাকে": "PRON", "তাদের": "PRON", "তার": "PRON",
        "তিনি": "PRON", "তাঁরা": "PRON", "তাঁকে": "PRON", "তাঁদের": "PRON", "তাঁর": "PRON",
        "এ": "PRON", "ও": "PRON", "ইনি": "PRON", "উনি": "PRON", "কে": "PRON", "কারা": "PRON",
        "কী": "PRON", "যিনি": "PRON", "যে": "PRON", "যাহারা": "PRON", "উহার": "PRON"
    }

    POSTPOSITIONS = {
        "জন্য", "সাথে", "সঙ্গে", "কাছে", "সামনে", "পিছনে", "ভিতরে", "বাইরে",
        "উপরে", "নিচে", "পরে", "কারণে", "দিয়ে", "থেকে", "হতে", "পর্যন্ত",
        "দ্বারা", "বিনা", "ছাড়া", "ছাড়া", "সহিত", "হইতে"
    }

    NEGATIVE_PARTICLES = {
        "না": "PART", "নি": "PART", "নয়": "AUX", "নই": "AUX", "নও": "AUX", "নন": "AUX", "নেই": "AUX"
    }

    CONJUNCTIONS = {
        "এবং": "CCONJ", "ও": "CCONJ", "আর": "CCONJ", "কিন্তু": "CCONJ", "অথবা": "CCONJ",
        "বা": "CCONJ", "কিংবা": "CCONJ", "যেহেতু": "SCONJ", "সুতরাং": "CCONJ", "কারণ": "SCONJ",
        "যদি": "SCONJ", "তবে": "SCONJ", "তাহলে": "SCONJ"
    }

    ADVERBS = {
        "খুব": "ADV", "অনেক": "ADV", "কাল": "ADV", "আজ": "ADV", "এখন": "ADV",
        "তখন": "ADV", "সবসময়": "ADV", "ধীরে": "ADV", "তাড়াতাড়ি": "ADV",
        "বেশ": "ADV", "একটু": "ADV", "এখানে": "ADV", "সেখানে": "ADV"
    }

    ADJECTIVES = {
        "ভালো": "ADJ", "খারাপ": "ADJ", "সুন্দর": "ADJ", "বড়": "ADJ", "ছোট": "ADJ",
        "নতুন": "ADJ", "পুরনো": "ADJ", "সহজ": "ADJ", "কঠিন": "ADJ", "মিষ্টি": "ADJ",
        "ঠান্ডা": "ADJ", "গরম": "ADJ", "শান্ত": "ADJ", "প্রিয়": "ADJ", "শ্রদ্ধেয়": "ADJ"
    }

    NUMERALS = {
        "এক": "NUM", "দুই": "NUM", "তিন": "NUM", "চার": "NUM", "পাঁচ": "NUM",
        "ছয়": "NUM", "সাত": "NUM", "আট": "NUM", "নয়": "NUM", "দশ": "NUM",
        "দু": "NUM", "একটি": "NUM", "একটিও": "NUM", "প্রথম": "NUM"
    }

    VERB_SUFFIXES = [
        "ছি", "ছিস", "ছেন", "ছ", "লাম", "লে", "লি", "লেন", "ল", "তাম", "তিস",
        "তেন", "ত", "ব", "বি", "বেন", "বে", "তে", "লে", "ুন", "িস"
    ]

    PUNCTUATION = {"।", "॥", ".", ",", "!", "?", ";", ":", "\"", "'", "-", "—"}

    def tag_tokens(self, tokens: List[str]) -> List[Dict[str, str]]:
        """
        Assigns UD POS tags to a token sequence.
        """
        tagged = []
        for tok in tokens:
            pos = self._predict_pos(tok)
            tagged.append({"token": tok, "pos": pos})
        return tagged

    def _predict_pos(self, tok: str) -> str:
        if tok in self.PUNCTUATION:
            return "PUNCT"
        if tok in self.PRONOUNS:
            return self.PRONOUNS[tok]
        if tok in self.POSTPOSITIONS:
            return "ADP"
        if tok in self.NEGATIVE_PARTICLES:
            return self.NEGATIVE_PARTICLES[tok]
        if tok in self.CONJUNCTIONS:
            return self.CONJUNCTIONS[tok]
        if tok in self.ADVERBS:
            return "ADV"
        if tok in self.ADJECTIVES:
            return "ADJ"
        if tok in self.NUMERALS:
            return "NUM"
        
        # Check verbal inflection endings
        for sfx in self.VERB_SUFFIXES + ["াস"]:
            if tok.endswith(sfx) and len(tok) >= len(sfx) + 1:
                # Exclude nouns/adjectives ending coincidentally in these letters
                if not (tok in self.ADJECTIVES or tok in self.ADVERBS):
                    return "VERB"

        # Check known verb database
        from .verb_conjugator import BengaliVerbConjugator
        try:
            if BengaliVerbConjugator().lemmatize(tok) is not None:
                return "VERB"
        except Exception:
            pass
        
        # Default to NOUN
        return "NOUN"
