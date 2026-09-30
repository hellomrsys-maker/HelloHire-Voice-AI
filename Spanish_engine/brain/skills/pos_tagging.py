"""
Spanish POS Tagging Skill.
Assigns Universal Dependencies (UD) morphosyntactic tags to Spanish tokens.
"""

from typing import List, Tuple, Dict, Any, Optional

SPANISH_CLOSED_CLASS = {
    # Determiners (DET)
    "el": "DET", "la": "DET", "los": "DET", "las": "DET",
    "un": "DET", "una": "DET", "unos": "DET", "unas": "DET",
    "este": "DET", "esta": "DET", "estos": "DET", "estas": "DET",
    "ese": "DET", "esa": "DET", "esos": "DET", "esas": "DET",
    "aquel": "DET", "aquella": "DET", "aquellos": "DET", "aquellas": "DET",
    "mi": "DET", "mis": "DET", "tu": "DET", "tus": "DET", "su": "DET", "sus": "DET",
    "nuestro": "DET", "nuestra": "DET", "nuestros": "DET", "nuestras": "DET",
    "vuestro": "DET", "vuestra": "DET", "vuestros": "DET", "vuestras": "DET",

    # Pronouns (PRON)
    "yo": "PRON", "tú": "PRON", "vos": "PRON", "él": "PRON", "ella": "PRON", "ello": "PRON",
    "nosotros": "PRON", "nosotras": "PRON", "vosotros": "PRON", "vosotras": "PRON",
    "ellos": "PRON", "ellas": "PRON", "usted": "PRON", "ustedes": "PRON",
    "me": "PRON", "te": "PRON", "se": "PRON", "nos": "PRON", "os": "PRON",
    "le": "PRON", "les": "PRON", "lo": "PRON",
    "mí": "PRON", "ti": "PRON", "sí": "PRON", "conmigo": "PRON", "contigo": "PRON",
    "quien": "PRON", "quienes": "PRON", "que": "PRON",

    # Prepositions (ADP)
    "a": "ADP", "ante": "ADP", "bajo": "ADP", "cabe": "ADP", "con": "ADP",
    "contra": "ADP", "de": "ADP", "desde": "ADP", "durante": "ADP", "en": "ADP",
    "entre": "ADP", "hacia": "ADP", "hasta": "ADP", "mediante": "ADP", "para": "ADP",
    "por": "ADP", "según": "ADP", "sin": "ADP", "so": "ADP", "sobre": "ADP",
    "tras": "ADP", "versus": "ADP", "vía": "ADP", "al": "ADP", "del": "ADP",

    # Conjunctions (CCONJ / SCONJ)
    "y": "CCONJ", "e": "CCONJ", "ni": "CCONJ", "o": "CCONJ", "u": "CCONJ", "pero": "CCONJ", "sino": "CCONJ",
    "porque": "SCONJ", "si": "SCONJ", "aunque": "SCONJ", "como": "SCONJ", "cuando": "SCONJ",
    "donde": "SCONJ", "mientras": "SCONJ",

    # Adverbs (ADV)
    "no": "ADV", "sí": "ADV", "bien": "ADV", "mal": "ADV", "muy": "ADV", "más": "ADV", "menos": "ADV",
    "casi": "ADV", "tan": "ADV", "tanto": "ADV", "ya": "ADV", "todavía": "ADV", "aún": "ADV",
    "siempre": "ADV", "nunca": "ADV", "jamás": "ADV", "hoy": "ADV", "mañana": "ADV", "ayer": "ADV",
    "aquí": "ADV", "allí": "ADV", "acá": "ADV", "allá": "ADV", "lejos": "ADV", "cerca": "ADV",

    # Auxiliaries (AUX)
    "he": "AUX", "has": "AUX", "ha": "AUX", "hemos": "AUX", "habéis": "AUX", "han": "AUX",
    "había": "AUX", "habías": "AUX", "habíamos": "AUX", "habíais": "AUX", "habían": "AUX",
    "haya": "AUX", "hayas": "AUX", "hayamos": "AUX", "hayáis": "AUX", "hayan": "AUX",
    "soy": "AUX", "eres": "AUX", "es": "AUX", "somos": "AUX", "sois": "AUX", "son": "AUX",
    "era": "AUX", "eras": "AUX", "éramos": "AUX", "erais": "AUX", "eran": "AUX",
    "fui": "AUX", "fuiste": "AUX", "fue": "AUX", "fuimos": "AUX", "fuisteis": "AUX", "fueron": "AUX",
    "estoy": "AUX", "estás": "AUX", "está": "AUX", "estamos": "AUX", "estáis": "AUX", "están": "AUX",
    "estaba": "AUX", "estabas": "AUX", "estábamos": "AUX", "estabais": "AUX", "estaban": "AUX",
}

COMMON_VERBS = {
    "hablar", "comer", "vivir", "estudiar", "escribir", "leer", "trabajar", "comprar", "vender", "abrir",
    "hablo", "hablas", "habla", "hablamos", "habláis", "hablan", "hablé", "habló", "hablaba",
    "como", "comes", "come", "comemos", "coméis", "comen", "comí", "comió", "comía",
    "vivo", "vives", "vive", "vivimos", "vivís", "viven", "viví", "vivió", "vivía",
    "lee", "leo", "lees", "leemos", "leéis", "leen", "leyó", "leyeron", "leía",
    "estudia", "estudio", "estudias", "estudiamos", "estudiáis", "estudian", "estudié", "estudió", "estudiaba",
    "escribo", "escribes", "escribe", "escribimos", "escriben", "escribí", "escribió",
    "veo", "ves", "ve", "vemos", "ven", "vi", "vio",
    "tengo", "tienes", "tiene", "tenemos", "tenéis", "tienen", "tuve", "tuvo",
    "hago", "haces", "hace", "hacemos", "hacéis", "hacen", "hice", "hizo",
    "voy", "vas", "va", "vamos", "vais", "van",
    "quiero", "quieres", "quiere", "queremos", "quieren",
    "puedo", "puedes", "puede", "podemos", "pueden",
    "sé", "sabes", "sabe", "sabemos", "saben",
    "pongo", "pones", "pone", "ponemos", "ponen",
    "digo", "dices", "dice", "decimos", "dicen", "dijo",
    "salgo", "sales", "sale", "salimos", "salen",
    "vengo", "vienes", "viene", "venimos", "vienen",
    "explica", "explican", "explico", "explicas", "explicamos", "explicó", "explicar",
    "trabaja", "trabajan", "trabajas", "trabajamos", "trabajó",
    "aprende", "aprenden", "aprendo", "aprendes", "aprendemos", "aprendió", "aprender",
    "entiende", "entienden", "entiendo", "entiendes", "entendemos", "entendió", "entender",
    "conoce", "conocen", "conozco", "conoces", "conocemos", "conoció", "conocer",
    "ayuda", "ayudan", "ayudo", "ayudas", "ayudamos", "ayudó", "ayudar",
    "busca", "buscan", "busco", "buscas", "buscamos", "buscó", "buscar",
    "mira", "miran", "miro", "miras", "miramos", "miró", "mirar",
    "escucha", "escuchan", "escucho", "escuchas", "escuchamos", "escuchó", "escuchar",
    "espera", "esperan", "espero", "esperas", "esperamos", "esperó", "esperar",
    "llega", "llegan", "llego", "llegas", "llegamos", "llegó", "llegar",
    "dudo", "deseo", "necesita", "recomienda", "sugiero"
}


class SpanishPOSTagger:
    """
    Part-of-Speech tagger for Spanish implementing Universal Dependencies standards.
    """

    def tag(self, tokens: List[str]) -> List[Tuple[str, str]]:
        tagged: List[Tuple[str, str]] = []

        for tok in tokens:
            low = tok.lower()

            if tok in {"¿", "?", "¡", "!", ",", ".", ";", ":", "—", "-", "«", "»", "(", ")"}:
                tagged.append((tok, "PUNCT"))
            elif low in SPANISH_CLOSED_CLASS:
                tagged.append((tok, SPANISH_CLOSED_CLASS[low]))
            elif low in COMMON_VERBS:
                tagged.append((tok, "VERB"))
            elif low.endswith((
                "ar", "er", "ir", "ando", "iendo", "ado", "ido",
                "amos", "emos", "imos", "aste", "iste", "aron", "ieron",
                "arás", "erás", "irás", "ará", "erá", "irá",
                "aremos", "eremos", "iremos", "arán", "erán", "irán",
                "aría", "ería", "iría", "arías", "erías", "irías", "arían", "erían", "irían",
                "aba", "abas", "ábamos", "abais", "aban"
            )):
                tagged.append((tok, "VERB"))
            elif low.endswith(("mente")):
                tagged.append((tok, "ADV"))
            elif low.endswith(("oso", "osa", "osos", "osas", "ivo", "iva", "ivos", "ivas", "able", "ible", "al", "ico", "ica")):
                tagged.append((tok, "ADJ"))
            elif low.endswith(("ción", "sión", "dad", "tad", "miento", "ismo", "ista", "eza", "or")):
                tagged.append((tok, "NOUN"))
            elif low.endswith(("o", "a", "os", "as")):
                tagged.append((tok, "NOUN"))
            else:
                tagged.append((tok, "NOUN"))

        return tagged
