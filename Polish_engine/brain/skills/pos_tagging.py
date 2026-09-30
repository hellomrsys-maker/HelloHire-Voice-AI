"""
Polish Part-of-Speech Tagging Engine
Universal Dependencies-aligned tagger for Polish morphosyntax.
"""

from typing import List, Tuple

class PolishPOSTagger:
    def __init__(self):
        self.determiners = {
            "ten", "ta", "to", "te", "ci", "tamten", "tamta", "tamto",
            "mój", "moja", "moje", "twój", "twoja", "twoje",
            "nasz", "nasza", "nasze", "wasz", "wasza", "wasze",
            "jego", "jej", "ich", "każdy", "każda", "każde",
            "żaden", "żadna", "żadne", "jakiś", "jakaś", "jakieś"
        }
        self.pronouns = {
            "ja", "ty", "on", "ona", "ono", "my", "wy", "oni", "one",
            "mnie", "mi", "cię", "tobie", "ci", "go", "jego", "mu", "nią",
            "jej", "nas", "nam", "was", "wam", "ich", "im", "nich", "nimi",
            "się", "siebie", "sobie", "sobą",
            "kto", "co", "kogo", "czego", "komu", "czemu", "czym", "kim",
            "nikt", "nic", "nikogo", "niczego", "nikomu", "niczemu", "nikim", "niczym"
        }
        self.honorific_pronouns = {
            "pan", "pani", "państwo", "panie", "panowie"
        }
        self.subordinators = {
            "że", "żeby", "aby", "iż", "ponieważ", "bo", "gdyż", "skoro",
            "jeśli", "jeżeli", "gdy", "kiedy", "chociaż", "choć", "mimo że", "zanim"
        }
        self.coordinators = {"i", "a", "oraz", "ale", "lecz", "lub", "albo", "ani"}
        self.auxiliaries = {
            "jest", "są", "jestem", "jesteś", "jesteśmy", "jesteście",
            "był", "była", "było", "byli", "były",
            "będę", "będziesz", "będzie", "będziemy", "będziecie", "będą"
        }
        self.prepositions = {
            "do", "od", "z", "ze", "bez", "dla", "u", "koło", "obok",
            "dzięki", "ku", "przeciwko",
            "przez", "o", "w", "we", "na", "po", "przy", "pod", "nad", "przed", "za", "między"
        }
        self.adverbs = {
            "bardzo", "dobrze", "źle", "wczoraj", "dzisiaj", "dziś", "jutro",
            "teraz", "zawsze", "nigdy", "nigdzie", "często", "rzadko",
            "chyba", "przecież", "właśnie", "naprawdę", "już", "jeszcze"
        }
        self.particles = {"nie", "czy", "no", "niech", "by", "oby", "tylko", "aż"}
        self.adjectives = {
            "dobry", "dobra", "dobre", "dobrzy", "dobrego", "dobrej",
            "nowy", "nowa", "nowe", "nowi", "nowego", "nowej",
            "wielki", "wielka", "wielkie", "wielcy",
            "mały", "mała", "małe", "mali",
            "piękny", "piękna", "piękne", "piękni",
            "polski", "polska", "polskie", "polscy",
            "cały", "cała", "całe", "cali",
            "szanowny", "szanowna", "szanowni", "szanowne"
        }
        self.known_verbs = {
            "mam", "masz", "ma", "mamy", "macie", "mają", "miał", "miała", "mieli", "mieć",
            "czytam", "czytasz", "czyta", "czytamy", "czytacie", "czytają", "czytał", "czytać",
            "piszę", "piszesz", "pisze", "piszemy", "piszecie", "piszą", "pisał", "pisać",
            "kupuję", "kupujesz", "kupuje", "kupujemy", "kupujecie", "kupują", "kupił", "kupić",
            "robię", "robisz", "robi", "robimy", "robicie", "robią", "robił", "robić",
            "widzę", "widzisz", "widzi", "widzimy", "widzicie", "widzą", "widział", "widzieć",
            "wiem", "wiesz", "wie", "wiemy", "wiecie", "wiedzą", "wiedział", "wiedzieć",
            "rozumiem", "rozumiesz", "rozumie", "rozumiemy", "rozumiecie", "rozumieją",
            "lubię", "lubisz", "lubi", "lubimy", "lubicie", "lubią",
            "znam", "znasz", "zna", "znamy", "znacie", "znają",
            "piję", "pijesz", "pije", "pijemy", "pijecie", "piją",
            "jem", "jesz", "je", "jemy", "jecie", "jedzą",
            "mogę", "możesz", "może", "możemy", "możecie", "mogą",
            "chcę", "chcesz", "chce", "chcemy", "chcecie", "chcą",
            "idę", "idziesz", "idzie", "idziemy", "idziecie", "idą", "poszedł", "poszła",
            "napiszę", "przeczytam", "zrobię", "kupię", "zobaczę"
        }

    def tag_token(self, token: str) -> str:
        low = token.lower()
        if token in {".", ",", "!", "?", ":", ";", "(", ")", "-", "\"", "'"}:
            return "PUNCT"
        if low in self.particles:
            return "PART"
        if low in self.honorific_pronouns:
            return "PRON_HONORIFIC"
        if low in self.determiners:
            return "DET"
        if low in self.pronouns:
            return "PRON"
        if low in self.subordinators:
            return "SCONJ"
        if low in self.coordinators:
            return "CCONJ"
        if low in self.auxiliaries:
            return "AUX"
        if low in self.prepositions:
            return "ADP"
        if low in self.adverbs:
            return "ADV"
        if low in self.adjectives:
            return "ADJ"
        if low in self.known_verbs:
            return "VERB"
        return "NOUN"

    def tag(self, tokens: List[str]) -> List[Tuple[str, str]]:
        return [(tok, self.tag_token(tok)) for tok in tokens]
