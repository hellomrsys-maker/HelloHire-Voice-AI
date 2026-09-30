"""Russian POS Tagging Skill.

Provides UPOS tagging tailored for Russian morpho-syntax, distinguishing
prepositions, pronouns, particles, conjunctions, numerals, adjectives, verbs, and nouns.
"""

import re
from typing import List, Dict, Any


class RussianPOSTagger:
    PREPOSITIONS = {
        "без", "безо", "в", "во", "ввиду", "вместо", "внутри", "для", "до",
        "за", "из", "изо", "из-за", "из-под", "к", "ко", "кроме", "между",
        "на", "над", "надо", "о", "об", "обо", "около", "от", "ото",
        "перед", "передо", "по", "под", "подо", "после", "при", "про",
        "ради", "с", "со", "сквозь", "среди", "у", "через", "благодаря",
        "согласно", "вопреки"
    }

    PRONOUNS = {
        "я", "меня", "мне", "мной", "мною",
        "ты", "тебя", "тебе", "тобой", "тобою",
        "он", "его", "него", "ему", "нему", "им", "ним",
        "она", "её", "нее", "неё", "ей", "ней", "ею", "нею",
        "оно",
        "мы", "нас", "нам", "нами",
        "вы", "вас", "вам", "вами",
        "они", "их", "них", "ими", "ними",
        "себя", "себе", "собой", "собою",
        "кто", "кого", "кому", "кем", "ком",
        "что", "чего", "чему", "чем", "чём",
        "этот", "эта", "это", "эти", "этого", "этой", "этим", "этих",
        "тот", "та", "то", "те", "того", "той", "том", "тех", "теми",
        "мой", "моя", "моё", "мои", "твой", "твоя", "твоё", "твои",
        "наш", "наша", "наше", "наши", "ваш", "ваша", "ваше", "ваши",
        "свой", "своя", "своё", "свои"
    }

    CONJUNCTIONS = {
        "и", "а", "но", "да", "или", "либо", "то", "зато", "однако",
        "что", "чтобы", "если", "когда", "хотя", "как", "будто", "словно",
        "так как", "потому что"
    }

    PARTICLES = {
        "не", "ни", "бы", "б", "ли", "ль", "же", "ж", "ведь", "даже",
        "только", "лишь", "вот", "вон", "пусть", "пускай", "давай",
        "неужели", "разве"
    }

    NUMERAL_WORDS = {
        "ноль", "нуль", "один", "одна", "одно", "одни", "два", "две", "три", "четыре",
        "пять", "шесть", "семь", "восемь", "девять", "десять",
        "одиннадцать", "двенадцать", "тринадцать", "четырнадцать", "пятнадцать",
        "шестнадцать", "семнадцать", "восемнадцать", "девятнадцать", "двадцать",
        "тридцать", "сорок", "пятьдесят", "шестьдесят", "семьдесят", "восемьдесят",
        "девяносто", "сто", "двести", "триста", "четыреста", "пятьсот",
        "шестьсот", "семьсот", "восемьсот", "девятьсот", "тысяча", "миллион"
    }

    ADVERB_SUFFIXES = ("о", "е", "ски", "ьи", "ом", "ем", "ах", "ях")

    ADJECTIVE_SUFFIXES = (
        "ый", "ий", "ой", "ая", "яя", "ое", "ее", "ые", "ие",
        "ого", "его", "ому", "ему", "ым", "им", "ом", "ем",
        "ую", "юю", "ых", "их", "ыми", "ими"
    )

    VERB_SUFFIXES = (
        "ть", "ти", "чь", "ться", "тись", "тся", "тся",
        "л", "ла", "ло", "ли", "лся", "лась", "лось", "лись",
        "ю", "ешь", "ет", "ем", "ете", "ут", "ют",
        "у", "ишь", "ит", "им", "ите", "ат", "ят",
        "ёшь", "ёт", "ём", "ёте"
    )

    def __init__(self):
        pass

    def tag_token(self, token: str) -> str:
        tok_lower = token.lower()

        if re.match(r"^[^\w\s]+$", token):
            return "PUNCT"
        if re.match(r"^\d+(?:[.,]\d+)?$", token) or tok_lower in self.NUMERAL_WORDS:
            return "NUM"
        if tok_lower in self.PREPOSITIONS:
            return "ADP"
        if tok_lower in self.PRONOUNS:
            return "PRON"
        if tok_lower in self.PARTICLES:
            return "PART"
        if tok_lower in self.CONJUNCTIONS:
            return "CCONJ" if tok_lower in {"и", "а", "но", "да", "или", "либо"} else "SCONJ"

        # Check for verbs
        for vsfx in ("ться", "тись", "тся", "тся", "ете", "ёте", "ите", "ешь", "ёшь", "ишь", "ем", "ём", "им"):
            if tok_lower.endswith(vsfx) and len(tok_lower) > len(vsfx) + 1:
                return "VERB"
        if tok_lower.endswith(("ть", "ти", "чь")) and len(tok_lower) >= 4:
            return "VERB"
        if tok_lower.endswith(("лся", "лась", "лось", "лись")) and len(tok_lower) >= 5:
            return "VERB"
        if tok_lower.endswith(("ла", "ло", "ли")) and len(tok_lower) >= 4:
            return "VERB"
        if tok_lower.endswith("л") and len(tok_lower) >= 4:
            return "VERB"

        # Check for adjectives
        for asfx in self.ADJECTIVE_SUFFIXES:
            if tok_lower.endswith(asfx) and len(tok_lower) >= len(asfx) + 2:
                return "ADJ"

        # Check for adverbs
        if tok_lower.startswith("по-") and tok_lower.endswith(("ски", "ьи", "ому", "ему")):
            return "ADV"
        if tok_lower in {
            "очень", "быстро", "медленно", "хорошо", "плохо", "часто", "редко",
            "вчера", "сегодня", "завтра", "вдруг", "наконец", "уже", "снова",
            "опять", "вместе", "всегда", "обычно", "постоянно"
        }:
            return "ADV"
        if tok_lower.endswith(("тельно", "льно", "ски")) and len(tok_lower) >= 5:
            return "ADV"
        if tok_lower.endswith("о") and len(tok_lower) >= 5:
            if tok_lower not in {
                "дело", "слово", "окно", "тело", "мыло", "море", "поле",
                "небо", "лето", "золото", "железо", "право", "место", "число"
            }:
                return "ADV"

        # Default open class for Russian words
        return "NOUN"


    def tag(self, tokens: List[str]) -> List[Dict[str, str]]:
        tagged = []
        for tok in tokens:
            tag = self.tag_token(tok)
            tagged.append({"token": tok, "pos": tag})
        return tagged
