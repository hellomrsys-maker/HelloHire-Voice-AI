"""
Dutch Part-of-Speech Tagging Engine
Universal Dependencies-aligned tagger for European Dutch.
"""

from typing import List, Dict, Tuple, Any

class DutchPOSTagger:
    def __init__(self):
        self.determiners = {
            "de", "het", "'t", "een", "geen", "deze", "die", "dit", "dat",
            "elk", "ieder", "elke", "iedere", "veel", "vele", "weinig"
        }
        self.pronouns = {
            "ik", "jij", "je", "u", "hij", "zij", "ze", "het", "wij", "we",
            "jullie", "me", "mij", "jou", "hem, haar", "ons", "hen", "hun",
            "zich", "elkaar", "wie", "wat", "mijn", "m'n", "jouw", "uw",
            "zijn", "z'n", "haar", "d'r", "onze", "hun"
        }
        self.subordinators = {
            "dat", "omdat", "doordat", "zodat", "als", "wanneer", "toen",
            "hoewel", "tenzij", "mits", "nadat", "voordat", "terwijl", "sinds",
            "zodra", "of", "ingeval"
        }
        self.coordinators = {"en", "maar", "want", "of", "dus"}
        self.auxiliaries = {
            "ben", "bent", "is", "zijn", "was", "waren", "geweest",
            "heb", "hebt", "heeft", "hebben", "had", "hadden", "gehad",
            "word", "wordt", "worden", "werd", "werden", "geworden",
            "kan", "kunt", "kunnen", "kon", "konden",
            "moet", "moeten", "moest", "moesten",
            "mag", "mogen", "mocht", "mochten",
            "wil", "wilt", "willen", "wou", "wilde", "wilden",
            "zal", "zult", "zullen", "zou", "zouden"
        }
        self.prepositions = {
            "in", "op", "aan", "bij", "van", "naar", "voor", "door", "met",
            "over", "onder", "tussen", "zonder", "tegen", "om", "langs", "tot"
        }
        self.adverbs = {
            "morgen", "vandaag", "gisteren", "straks", "hier", "daar", "nu",
            "erg", "heel", "niet", "wel", "ook", "altijd", "nooit", "soms",
            "al", "nog", "misschien", "zeker", "waarom", "hoe", "toen"
        }
        self.modal_particles = {"maar", "even", "toch", "eens", "hoor", "nou"}
        self.adjectives = {
            "mooi", "mooie", "groot", "grote", "klein", "kleine", "nieuw", "nieuwe",
            "oud", "oude", "goed", "goede", "lekker", "lekkere", "koud", "koude",
            "warm", "warme", "wit", "witte", "zwart", "zwarte", "jong", "jonge",
            "lang", "lange", "kort", "korte", "gezellig", "gezellige", "belangrijk", "belangrijke"
        }
        self.known_verbs = {
            "leest", "lees", "lezen", "las", "lazen", "gelezen",
            "loopt", "loop", "lopen", "liep", "liepen", "gelopen",
            "gaat", "ga", "gaan", "ging", "gingen", "gegaan",
            "kijkt", "kijk", "kijken", "keek", "keken", "gekeken",
            "belt", "bel", "bellen", "belde", "belden", "gebeld",
            "koopt", "koop", "kopen", "kocht", "kochten", "gekocht",
            "eet", "eten", "at", "aten", "gegeten",
            "drinkt", "drink", "drinken", "dronk", "dronken", "gedronken",
            "schrijft", "schrijf", "schrijven", "schreef", "schreven", "geschreven",
            "ziet", "zie", "zien", "zag", "zagen", "gezien",
            "helpt", "help", "helpen", "hielp", "hielpen", "geholpen",
            "woont", "woon", "wonen", "woonde", "woonden", "gewoond",
            "werkt", "werk", "werken", "werkte", "werkten", "gewerkt",
            "vertrekt", "vertrek", "vertrekken", "vertrok", "vertrokken"
        }
        self.known_nouns = {
            "man", "vrouw", "kind", "meisje", "tafel", "stoel", "hond", "kat",
            "auto", "stad", "weg", "straat", "school", "trein", "fiets", "winkel",
            "taal", "computer", "telefoon", "sleutel", "deur", "kamer", "vriend",
            "vriendin", "leraar", "lerares", "krant", "boom", "zee", "bloem",
            "huis", "boek", "dier", "water", "brood", "geld", "werk", "land",
            "dorp", "oog", "oor", "been", "raam", "jaar", "feest", "bier", "paard",
            "bed", "probleem", "voorbeeld", "leven", "lichaam", "hart", "idee",
            "resultaat", "bericht", "bibliotheek", "student", "universiteit"
        }

    def tag_token(self, token: str, prev_tag: str = None) -> str:
        low = token.lower()
        if token in {".", ",", "!", "?", ":", ";", "(", ")", "-", "\"", "'"}:
            return "PUNCT"
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
        if low in self.modal_particles:
            return "PART"
        if low in self.adverbs:
            return "ADV"
        if low in self.prepositions:
            return "ADP"
        if low in self.adjectives:
            return "ADJ"
        if low in self.known_verbs:
            return "VERB"
        if low in self.known_nouns or low.endswith(("tje", "je", "pje", "etje", "kje", "heid", "ing", "schap", "teit")):
            return "NOUN"
        if low.endswith("en") and len(low) > 3:
            # Infinitive or plural noun; default to VERB if preceded by AUX/PRON, else NOUN
            return "VERB" if prev_tag in {"AUX", "PRON"} else "NOUN"
        if low.endswith("de") or low.endswith("te") or low.startswith("ge"):
            return "VERB"
        return "NOUN"

    def tag(self, tokens: List[str]) -> List[Tuple[str, str]]:
        tagged = []
        prev = None
        for tok in tokens:
            t = self.tag_token(tok, prev)
            tagged.append((tok, t))
            prev = t
        return tagged
