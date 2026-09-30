"""
French POS Tagging Skill.
Assigns Universal Dependencies (UD) morphosyntactic tags to French tokens.
"""

from typing import List, Tuple, Dict, Any, Optional

FRENCH_CLOSED_CLASS = {
    # Determiners (DET)
    "le": "DET", "la": "DET", "les": "DET", "l'": "DET",
    "un": "DET", "une": "DET", "des": "DET",
    "du": "DET", "de la": "DET",
    "ce": "DET", "cet": "DET", "cette": "DET", "ces": "DET",
    "mon": "DET", "ma": "DET", "mes": "DET",
    "ton": "DET", "ta": "DET", "tes": "DET",
    "son": "DET", "sa": "DET", "ses": "DET",
    "notre": "DET", "nos": "DET",
    "votre": "DET", "vos": "DET",
    "leur": "DET", "leurs": "DET",
    "aucun": "DET", "aucune": "DET", "chaque": "DET", "plusieurs": "DET",

    # Pronouns (PRON)
    "je": "PRON", "j'": "PRON", "tu": "PRON", "il": "PRON", "elle": "PRON", "on": "PRON",
    "nous": "PRON", "vous": "PRON", "ils": "PRON", "elles": "PRON",
    "me": "PRON", "m'": "PRON", "te": "PRON", "t'": "PRON", "se": "PRON", "s'": "PRON",
    "lui": "PRON", "leur": "PRON", "y": "PRON", "en": "PRON",
    "moi": "PRON", "toi": "PRON", "soi": "PRON", "eux": "PRON",
    "ceci": "PRON", "cela": "PRON", "ça": "PRON", "c'": "PRON",
    "qui": "PRON", "que": "PRON", "qu'": "PRON", "dont": "PRON", "où": "PRON",
    "chacun": "PRON", "chacune": "PRON", "tout": "PRON", "rien": "PRON", "personne": "PRON",

    # Prepositions (ADP)
    "à": "ADP", "au": "ADP", "aux": "ADP", "de": "ADP", "d'": "ADP",
    "dans": "ADP", "en": "ADP", "par": "ADP", "pour": "ADP",
    "sur": "ADP", "avec": "ADP", "sans": "ADP", "sous": "ADP",
    "chez": "ADP", "entre": "ADP", "vers": "ADP", "pendant": "ADP",
    "depuis": "ADP", "contre": "ADP", "selon": "ADP", "malgré": "ADP",

    # Conjunctions (CCONJ / SCONJ)
    "et": "CCONJ", "ou": "CCONJ", "mais": "CCONJ", "donc": "CCONJ", "car": "CCONJ", "ni": "CCONJ",
    "quand": "SCONJ", "lorsque": "SCONJ", "puisque": "SCONJ", "si": "SCONJ",
    "comme": "SCONJ", "quoique": "SCONJ",

    # Adverbs (ADV)
    "ne": "ADV", "n'": "ADV", "pas": "ADV", "plus": "ADV", "jamais": "ADV",
    "bien": "ADV", "mal": "ADV", "très": "ADV", "trop": "ADV", "assez": "ADV",
    "toujours": "ADV", "souvent": "ADV", "ici": "ADV", "là": "ADV", "aussi": "ADV",
    "encore": "ADV", "peu": "ADV", "beaucoup": "ADV", "oui": "ADV", "non": "ADV",

    # Auxiliaries (AUX)
    "suis": "AUX", "es": "AUX", "est": "AUX", "sommes": "AUX", "êtes": "AUX", "sont": "AUX",
    "étais": "AUX", "était": "AUX", "étions": "AUX", "étiez": "AUX", "étaient": "AUX",
    "serai": "AUX", "seras": "AUX", "sera": "AUX", "serons": "AUX", "serez": "AUX", "seront": "AUX",
    "été": "AUX", "sois": "AUX", "soit": "AUX", "soyons": "AUX", "soyez": "AUX", "soient": "AUX",
    "ai": "AUX", "as": "AUX", "a": "AUX", "avons": "AUX", "avez": "AUX", "ont": "AUX",
    "avais": "AUX", "avait": "AUX", "avions": "AUX", "aviez": "AUX", "avaient": "AUX",
    "aurai": "AUX", "auras": "AUX", "aura": "AUX", "aurons": "AUX", "aurez": "AUX", "auront": "AUX",
    "eu": "AUX", "aie": "AUX", "ait": "AUX", "ayons": "AUX", "ayez": "AUX", "aient": "AUX",
}

COMMON_VERBS = {
    "parler", "parle", "parles", "parlons", "parlez", "parlent", "parlé", "parlais", "parlait",
    "manger", "mange", "manges", "mangeons", "mangez", "mangent", "mangé", "mangeais",
    "finir", "finis", "finit", "finissons", "finissez", "finissent", "fini", "finissait",
    "aller", "vais", "vas", "va", "allons", "allez", "vont", "allé", "allée", "allés", "allées", "allait",
    "faire", "fais", "fait", "faisons", "faites", "font", "faisait",
    "voir", "vois", "voit", "voyons", "voyez", "voient", "vu", "voyait",
    "savoir", "sais", "sait", "savons", "savez", "savent", "su", "savait",
    "vouloir", "veux", "veut", "voulons", "voulez", "veulent", "voulu", "voulait",
    "pouvoir", "peux", "peut", "pouvons", "pouvez", "peuvent", "pu", "pouvait",
    "devoir", "dois", "doit", "devons", "devez", "doivent", "dû", "devait",
    "venir", "viens", "vient", "venons", "venez", "viennent", "venu", "venue", "venus", "venues", "venait",
    "prendre", "prends", "prend", "prenons", "prenez", "prennent", "pris", "prenait",
    "comprendre", "comprends", "comprend", "comprenons", "comprenez", "comprennent", "compris",
    "écrire", "écris", "écrit", "écrivons", "écrivez", "écrivent", "écrit", "écrite", "écrites",
    "lire", "lis", "lit", "lisons", "lisez", "lisent", "lu",
    "donner", "donne", "donnes", "donnons", "donnez", "donnent", "donné",
    "demander", "demande", "demandes", "demandons", "demandez", "demandent", "demandé",
    "aimer", "aime", "aimes", "aimons", "aimez", "aiment", "aimé",
    "penser", "pense", "penses", "pensons", "pensez", "pensent", "pensé",
    "croire", "crois", "croit", "croyons", "croyez", "croient", "cru",
    "trouver", "trouve", "trouves", "trouvons", "trouvez", "trouvent", "trouvé",
    "laisser", "laisse", "laisses", "laissons", "laissez", "laissent", "laissé",
    "travailler", "travaille", "travailles", "travaillons", "travaillez", "travaillent", "travaillé",
    "mettre", "mets", "met", "mettons", "mettez", "mettent", "mis",
    "expliquer", "explique", "expliques", "expliquons", "expliquez", "expliquent", "expliquait", "expliqué",
    "démontrer", "démontre", "démontres", "démontrons", "démontrez", "démontrent", "démontrait", "démontré",
    "présenter", "présente", "présentes", "présentons", "présentez", "présentent", "présentait", "présenté",
    "montrer", "montre", "montres", "montrons", "montrez", "montrent", "montrait", "montré",
    "analyser", "analyse", "analyses", "analysons", "analysez", "analysent", "analysait", "analysé",
    "étudier", "étudie", "étudies", "étudions", "étudiez", "étudient", "étudiait", "étudié",
    "observer", "observe", "observes", "observons", "observez", "observent", "observait", "observé",
    "falloir", "faut", "fallait", "fallu",
    "pleuvoir", "pleut", "pleuvait", "plu"
}


class FrenchPOSTagger:
    """
    Part-of-Speech tagger for French implementing Universal Dependencies standards.
    """

    def tag(self, tokens: List[str]) -> List[Tuple[str, str]]:
        tagged: List[Tuple[str, str]] = []

        for tok in tokens:
            low = tok.lower()

            if tok in {"«", "»", "\"", "'", "“", "”", ",", ".", ";", ":", "!", "?", "—", "-", "(", ")"}:
                tagged.append((tok, "PUNCT"))
            elif low in FRENCH_CLOSED_CLASS:
                tagged.append((tok, FRENCH_CLOSED_CLASS[low]))
            elif low in COMMON_VERBS:
                tagged.append((tok, "VERB"))
            elif low.endswith(("tion", "sion", "ité", "ence", "ance", "eur", "euse", "isme", "iste", "esse", "oir", "ure", "ures", "age", "ages", "erie")):
                tagged.append((tok, "NOUN"))
            elif low.endswith(("ment")):
                if low.endswith(("lement", "vement", "tement", "sement", "rement", "nement")):
                    tagged.append((tok, "ADV"))
                else:
                    tagged.append((tok, "NOUN"))
            elif low.endswith(("eux", "euse", "al", "ique", "able", "ible", "if", "ive", "el", "elle", "ien", "ienne")):
                tagged.append((tok, "ADJ"))
            elif low.endswith(("er", "ir", "issant", "dre", "uire", "ître", "ttre", "é", "ée", "és", "ées")):
                tagged.append((tok, "VERB"))
            elif low.endswith(("re")) and not low.endswith(("ure", "ère", "tre", "bre", "vre")):
                tagged.append((tok, "VERB"))
            else:
                tagged.append((tok, "NOUN"))

        return tagged
