"""
language_profile.py — Per-Language Typological Configuration.
=============================================================

A ``LanguageProfile`` is the single source of authentic linguistic truth for one
language. All shared base classes in ``engine_common`` are parameterised by a
profile, so the SAME code produces language-correct behaviour for every engine.

The ``LANGUAGE_REGISTRY`` holds one profile per engine in the ecosystem.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple


class WordOrder(str, Enum):
    SVO = "SVO"   # Subject-Verb-Object (English, Chinese, Swahili...)
    SOV = "SOV"   # Subject-Object-Verb (Japanese, Korean, Hindi, Turkish...)
    VSO = "VSO"   # Verb-Subject-Object (Arabic, Irish, Tagalog...)
    VOS = "VOS"
    OSV = "OSV"
    OVS = "OVS"
    FREE = "FREE"  # Relatively free order (Russian, Latin, Finnish...)


class ScriptType(str, Enum):
    LATIN = "Latin"
    CYRILLIC = "Cyrillic"
    ARABIC = "Arabic"
    DEVANAGARI = "Devanagari"
    HAN = "Han"                 # Chinese characters
    KANA_KANJI = "Kana+Kanji"   # Japanese
    HANGUL = "Hangul"           # Korean
    GEEZ = "Geez"               # Amharic / Tigrinya (Ethiopic)
    HEBREW = "Hebrew"
    GREEK = "Greek"
    THAI = "Thai"
    BENGALI = "Bengali"
    TAMIL = "Tamil"
    TELUGU = "Telugu"
    KANNADA = "Kannada"
    MALAYALAM = "Malayalam"
    GUJARATI = "Gujarati"
    GURMUKHI = "Gurmukhi"       # Punjabi
    ODIA = "Odia"
    MYANMAR = "Myanmar"         # Burmese


@dataclass
class LanguageProfile:
    """Authentic typological + orthographic configuration for one language engine."""

    # Identity
    engine_dir: str                    # e.g. "Spanish_engine"
    language_name: str                 # e.g. "Spanish"
    iso_code: str                      # ISO 639 code, e.g. "es"
    class_prefix: str                  # PascalCase prefix for generated classes, e.g. "Spanish"

    # Typology
    word_order: WordOrder
    script: ScriptType
    is_tonal: bool = False
    is_agglutinative: bool = False
    has_grammatical_gender: bool = False
    has_case_marking: bool = False
    pro_drop: bool = False             # allows null subjects (Spanish, Japanese, Italian...)
    honorific_system: bool = False     # keigo/honorifics register system (Japanese, Korean...)
    rtl: bool = False                  # right-to-left script

    # Phonology / prosody baselines (per RULEBOOK calibration)
    baseline_f0_hz: float = 230.0
    speech_tempo_sps: float = 3.6
    latency_gap_ms: int = 518

    # Lexical anchors — small authentic seed lexicon mapping this language <-> English.
    # Used by the English-pivot comprehension layer. Keys are target-language surface
    # forms, values are English glosses.
    to_english_lexicon: Dict[str, str] = field(default_factory=dict)

    # Function words / particles that are structurally significant for this language.
    function_words: List[str] = field(default_factory=list)

    # Politeness / honorific markers if the language has a register system.
    honorific_markers: List[str] = field(default_factory=list)

    # Sentence terminators for tokenization (some scripts use their own punctuation).
    sentence_terminators: Tuple[str, ...] = (".", "!", "?")

    # AMSV magic id (per-engine identity stamp).
    magic_id: int = 0x534F4C4F  # "SOLO"

    @property
    def amsv_magic_hex(self) -> str:
        return hex(self.magic_id)

    def gloss(self, token: str) -> Optional[str]:
        """Return the English gloss for a target-language token, if known."""
        return self.to_english_lexicon.get(token) or self.to_english_lexicon.get(token.lower())


# ============================================================================
# LANGUAGE REGISTRY — one authentic profile per engine (45 languages).
# ============================================================================
# Lexicons are intentionally compact authentic seed sets (high-frequency words)
# used by the English-pivot layer; they are extended at runtime from each
# engine's own 6_DATA_REQUIREMENTS canonical data when available.

LANGUAGE_REGISTRY: Dict[str, LanguageProfile] = {}


def _reg(profile: LanguageProfile) -> None:
    LANGUAGE_REGISTRY[profile.engine_dir] = profile


# --- English (flagship reference) ---
_reg(LanguageProfile(
    engine_dir="English_engine", language_name="English", iso_code="en", class_prefix="English",
    word_order=WordOrder.SVO, script=ScriptType.LATIN,
    to_english_lexicon={}, function_words=["the", "a", "an", "is", "are", "and", "of", "to", "in"],
    magic_id=0x454E474C,
))

# --- Romance ---
_reg(LanguageProfile(
    engine_dir="Spanish_engine", language_name="Spanish", iso_code="es", class_prefix="Spanish",
    word_order=WordOrder.SVO, script=ScriptType.LATIN, has_grammatical_gender=True, pro_drop=True,
    to_english_lexicon={"el": "the", "la": "the", "es": "is", "y": "and", "de": "of", "yo": "i",
                        "casa": "house", "agua": "water", "libro": "book", "bueno": "good", "gato": "cat"},
    function_words=["el", "la", "los", "las", "un", "una", "de", "y", "que", "es"],
    sentence_terminators=(".", "!", "?", "¿", "¡"), magic_id=0x53504149,
))
_reg(LanguageProfile(
    engine_dir="French_engine", language_name="French", iso_code="fr", class_prefix="French",
    word_order=WordOrder.SVO, script=ScriptType.LATIN, has_grammatical_gender=True,
    to_english_lexicon={"le": "the", "la": "the", "est": "is", "et": "and", "de": "of", "je": "i",
                        "maison": "house", "eau": "water", "livre": "book", "bon": "good", "chat": "cat"},
    function_words=["le", "la", "les", "un", "une", "de", "et", "que", "est"], magic_id=0x46524149,
))
_reg(LanguageProfile(
    engine_dir="Italian_engine", language_name="Italian", iso_code="it", class_prefix="Italian",
    word_order=WordOrder.SVO, script=ScriptType.LATIN, has_grammatical_gender=True, pro_drop=True,
    to_english_lexicon={"il": "the", "la": "the", "è": "is", "e": "and", "di": "of", "io": "i",
                        "casa": "house", "acqua": "water", "libro": "book", "buono": "good", "gatto": "cat"},
    function_words=["il", "lo", "la", "i", "gli", "le", "di", "e", "che", "è"], magic_id=0x49544149,
))
_reg(LanguageProfile(
    engine_dir="Portuguese_engine", language_name="Portuguese", iso_code="pt", class_prefix="Portuguese",
    word_order=WordOrder.SVO, script=ScriptType.LATIN, has_grammatical_gender=True, pro_drop=True,
    to_english_lexicon={"o": "the", "a": "the", "é": "is", "e": "and", "de": "of", "eu": "i",
                        "casa": "house", "água": "water", "livro": "book", "bom": "good", "gato": "cat"},
    function_words=["o", "a", "os", "as", "um", "uma", "de", "e", "que", "é"], magic_id=0x50544149,
))
_reg(LanguageProfile(
    engine_dir="Romanian_engine", language_name="Romanian", iso_code="ro", class_prefix="Romanian",
    word_order=WordOrder.SVO, script=ScriptType.LATIN, has_grammatical_gender=True, has_case_marking=True, pro_drop=True,
    to_english_lexicon={"și": "and", "este": "is", "de": "of", "eu": "i", "casă": "house",
                        "apă": "water", "carte": "book", "bun": "good", "pisică": "cat"},
    function_words=["un", "o", "și", "de", "că", "este"], magic_id=0x524F4149,
))

# --- Germanic ---
_reg(LanguageProfile(
    engine_dir="German_engine", language_name="German", iso_code="de", class_prefix="German",
    word_order=WordOrder.SVO, script=ScriptType.LATIN, has_grammatical_gender=True, has_case_marking=True,
    to_english_lexicon={"der": "the", "die": "the", "das": "the", "ist": "is", "und": "and", "ich": "i",
                        "haus": "house", "wasser": "water", "buch": "book", "gut": "good", "katze": "cat"},
    function_words=["der", "die", "das", "ein", "eine", "und", "ist", "dass"], magic_id=0x44454149,
))
_reg(LanguageProfile(
    engine_dir="Dutch_engine", language_name="Dutch", iso_code="nl", class_prefix="Dutch",
    word_order=WordOrder.SVO, script=ScriptType.LATIN, has_grammatical_gender=True,
    to_english_lexicon={"de": "the", "het": "the", "is": "is", "en": "and", "ik": "i",
                        "huis": "house", "water": "water", "boek": "book", "goed": "good", "kat": "cat"},
    function_words=["de", "het", "een", "en", "is", "dat"], magic_id=0x4E4C4149,
))
_reg(LanguageProfile(
    engine_dir="Swedish_engine", language_name="Swedish", iso_code="sv", class_prefix="Swedish",
    word_order=WordOrder.SVO, script=ScriptType.LATIN,
    to_english_lexicon={"är": "is", "och": "and", "jag": "i", "hus": "house",
                        "vatten": "water", "bok": "book", "bra": "good", "katt": "cat"},
    function_words=["en", "ett", "och", "är", "att"], magic_id=0x53564149,
))
_reg(LanguageProfile(
    engine_dir="Danish_engine", language_name="Danish", iso_code="da", class_prefix="Danish",
    word_order=WordOrder.SVO, script=ScriptType.LATIN,
    to_english_lexicon={"er": "is", "og": "and", "jeg": "i", "hus": "house",
                        "vand": "water", "bog": "book", "god": "good", "kat": "cat"},
    function_words=["en", "et", "og", "er", "at"], magic_id=0x44414149,
))

# --- Slavic ---
_reg(LanguageProfile(
    engine_dir="Russian_engine", language_name="Russian", iso_code="ru", class_prefix="Russian",
    word_order=WordOrder.FREE, script=ScriptType.CYRILLIC, has_grammatical_gender=True, has_case_marking=True, pro_drop=True,
    to_english_lexicon={"и": "and", "это": "this", "я": "i", "дом": "house",
                        "вода": "water", "книга": "book", "хороший": "good", "кот": "cat"},
    function_words=["и", "в", "не", "на", "что", "это"], magic_id=0x52554149,
))
_reg(LanguageProfile(
    engine_dir="Ukrainian_engine", language_name="Ukrainian", iso_code="uk", class_prefix="Ukrainian",
    word_order=WordOrder.FREE, script=ScriptType.CYRILLIC, has_grammatical_gender=True, has_case_marking=True, pro_drop=True,
    to_english_lexicon={"і": "and", "це": "this", "я": "i", "дім": "house",
                        "вода": "water", "книга": "book", "добрий": "good", "кіт": "cat"},
    function_words=["і", "в", "не", "на", "що", "це"], magic_id=0x554B4149,
))
_reg(LanguageProfile(
    engine_dir="Polish_engine", language_name="Polish", iso_code="pl", class_prefix="Polish",
    word_order=WordOrder.FREE, script=ScriptType.LATIN, has_grammatical_gender=True, has_case_marking=True, pro_drop=True,
    to_english_lexicon={"i": "and", "to": "this", "ja": "i", "dom": "house",
                        "woda": "water", "książka": "book", "dobry": "good", "kot": "cat"},
    function_words=["i", "w", "nie", "na", "że", "to"], magic_id=0x504C4149,
))
_reg(LanguageProfile(
    engine_dir="Czech_engine", language_name="Czech", iso_code="cs", class_prefix="Czech",
    word_order=WordOrder.FREE, script=ScriptType.LATIN, has_grammatical_gender=True, has_case_marking=True, pro_drop=True,
    to_english_lexicon={"a": "and", "to": "this", "já": "i", "dům": "house",
                        "voda": "water", "kniha": "book", "dobrý": "good", "kočka": "cat"},
    function_words=["a", "v", "ne", "na", "že", "to"], magic_id=0x435A4149,
))

# --- Other European ---
_reg(LanguageProfile(
    engine_dir="Greek_engine", language_name="Greek", iso_code="el", class_prefix="Greek",
    word_order=WordOrder.SVO, script=ScriptType.GREEK, has_grammatical_gender=True, has_case_marking=True, pro_drop=True,
    to_english_lexicon={"και": "and", "είναι": "is", "εγώ": "i", "σπίτι": "house",
                        "νερό": "water", "βιβλίο": "book", "καλός": "good", "γάτα": "cat"},
    function_words=["ο", "η", "το", "και", "είναι"], magic_id=0x47524B31,
))
_reg(LanguageProfile(
    engine_dir="Finnish_engine", language_name="Finnish", iso_code="fi", class_prefix="Finnish",
    word_order=WordOrder.SVO, script=ScriptType.LATIN, is_agglutinative=True, has_case_marking=True, pro_drop=True,
    to_english_lexicon={"ja": "and", "on": "is", "minä": "i", "talo": "house",
                        "vesi": "water", "kirja": "book", "hyvä": "good", "kissa": "cat"},
    function_words=["ja", "on", "se", "että"], magic_id=0x46494E31,
))
_reg(LanguageProfile(
    engine_dir="Hungarian_engine", language_name="Hungarian", iso_code="hu", class_prefix="Hungarian",
    word_order=WordOrder.FREE, script=ScriptType.LATIN, is_agglutinative=True, has_case_marking=True, pro_drop=True,
    to_english_lexicon={"és": "and", "van": "is", "én": "i", "ház": "house",
                        "víz": "water", "könyv": "book", "jó": "good", "macska": "cat"},
    function_words=["a", "az", "egy", "és", "van", "hogy"], magic_id=0x48554E31,
))
_reg(LanguageProfile(
    engine_dir="Turkish_engine", language_name="Turkish", iso_code="tr", class_prefix="Turkish",
    word_order=WordOrder.SOV, script=ScriptType.LATIN, is_agglutinative=True, has_case_marking=True, pro_drop=True,
    to_english_lexicon={"ve": "and", "bir": "a", "ben": "i", "ev": "house",
                        "su": "water", "kitap": "book", "iyi": "good", "kedi": "cat"},
    function_words=["ve", "bir", "bu", "ki"], magic_id=0x54524B31,
))

# --- Semitic ---
_reg(LanguageProfile(
    engine_dir="Arabic_engine", language_name="Arabic", iso_code="ar", class_prefix="Arabic",
    word_order=WordOrder.VSO, script=ScriptType.ARABIC, has_grammatical_gender=True, has_case_marking=True, rtl=True,
    to_english_lexicon={"و": "and", "هو": "he", "أنا": "i", "بيت": "house",
                        "ماء": "water", "كتاب": "book", "جيد": "good", "قط": "cat"},
    function_words=["ال", "و", "في", "من", "على", "هذا"],
    sentence_terminators=(".", "!", "?", "؟"), magic_id=0x41524149,
))
_reg(LanguageProfile(
    engine_dir="Hebrew_engine", language_name="Hebrew", iso_code="he", class_prefix="Hebrew",
    word_order=WordOrder.SVO, script=ScriptType.HEBREW, has_grammatical_gender=True, rtl=True,
    to_english_lexicon={"ו": "and", "הוא": "he", "אני": "i", "בית": "house",
                        "מים": "water", "ספר": "book", "טוב": "good", "חתול": "cat"},
    function_words=["ה", "ו", "של", "את", "זה"], magic_id=0x48454231,
))
_reg(LanguageProfile(
    engine_dir="Amharic_engine", language_name="Amharic", iso_code="am", class_prefix="Amharic",
    word_order=WordOrder.SOV, script=ScriptType.GEEZ, has_case_marking=True,
    to_english_lexicon={"እና": "and", "ነው": "is", "እኔ": "i", "ቤት": "house",
                        "ውሃ": "water", "መጽሐፍ": "book", "ጥሩ": "good", "ድመት": "cat"},
    function_words=["እና", "ነው", "የ", "ን"],
    sentence_terminators=(".", "!", "?", "።"), magic_id=0x414D4841,
))
_reg(LanguageProfile(
    engine_dir="Persian_engine", language_name="Persian", iso_code="fa", class_prefix="Persian",
    word_order=WordOrder.SOV, script=ScriptType.ARABIC, pro_drop=True, rtl=True,
    to_english_lexicon={"و": "and", "است": "is", "من": "i", "خانه": "house",
                        "آب": "water", "کتاب": "book", "خوب": "good", "گربه": "cat"},
    function_words=["و", "در", "به", "از", "این"],
    sentence_terminators=(".", "!", "?", "؟"), magic_id=0x46414131,
))

# --- Indo-Aryan / Dravidian (Indian subcontinent) ---
_reg(LanguageProfile(
    engine_dir="Hindustani_engine", language_name="Hindustani", iso_code="hi", class_prefix="Hindustani",
    word_order=WordOrder.SOV, script=ScriptType.DEVANAGARI, has_grammatical_gender=True, has_case_marking=True,
    to_english_lexicon={"और": "and", "है": "is", "मैं": "i", "घर": "house",
                        "पानी": "water", "किताब": "book", "अच्छा": "good", "बिल्ली": "cat"},
    function_words=["और", "है", "का", "को", "में", "यह"],
    sentence_terminators=(".", "!", "?", "।"), magic_id=0x48494E31,
))
_reg(LanguageProfile(
    engine_dir="Bengali_engine", language_name="Bengali", iso_code="bn", class_prefix="Bengali",
    word_order=WordOrder.SOV, script=ScriptType.BENGALI, has_case_marking=True,
    to_english_lexicon={"এবং": "and", "হয়": "is", "আমি": "i", "বাড়ি": "house",
                        "জল": "water", "বই": "book", "ভালো": "good", "বিড়াল": "cat"},
    function_words=["এবং", "হয়", "এর", "কে", "এই"],
    sentence_terminators=(".", "!", "?", "।"), magic_id=0x424E4731,
))
_reg(LanguageProfile(
    engine_dir="Marathi_engine", language_name="Marathi", iso_code="mr", class_prefix="Marathi",
    word_order=WordOrder.SOV, script=ScriptType.DEVANAGARI, has_grammatical_gender=True, has_case_marking=True,
    to_english_lexicon={"आणि": "and", "आहे": "is", "मी": "i", "घर": "house",
                        "पाणी": "water", "पुस्तक": "book", "चांगले": "good", "मांजर": "cat"},
    function_words=["आणि", "आहे", "चा", "ला", "हे"],
    sentence_terminators=(".", "!", "?", "।"), magic_id=0x4D524131,
))
_reg(LanguageProfile(
    engine_dir="Gujarati_engine", language_name="Gujarati", iso_code="gu", class_prefix="Gujarati",
    word_order=WordOrder.SOV, script=ScriptType.GUJARATI, has_grammatical_gender=True, has_case_marking=True,
    to_english_lexicon={"અને": "and", "છે": "is", "હું": "i", "ઘર": "house",
                        "પાણી": "water", "પુસ્તક": "book", "સારું": "good", "બિલાડી": "cat"},
    function_words=["અને", "છે", "નો", "ને", "આ"],
    sentence_terminators=(".", "!", "?", "।"), magic_id=0x47554A31,
))
_reg(LanguageProfile(
    engine_dir="Punjabi_engine", language_name="Punjabi", iso_code="pa", class_prefix="Punjabi",
    word_order=WordOrder.SOV, script=ScriptType.GURMUKHI, is_tonal=True, has_grammatical_gender=True, has_case_marking=True,
    to_english_lexicon={"ਅਤੇ": "and", "ਹੈ": "is", "ਮੈਂ": "i", "ਘਰ": "house",
                        "ਪਾਣੀ": "water", "ਕਿਤਾਬ": "book", "ਚੰਗਾ": "good", "ਬਿੱਲੀ": "cat"},
    function_words=["ਅਤੇ", "ਹੈ", "ਦਾ", "ਨੂੰ", "ਇਹ"],
    sentence_terminators=(".", "!", "?", "।"), magic_id=0x50414231,
))
_reg(LanguageProfile(
    engine_dir="Odia_engine", language_name="Odia", iso_code="or", class_prefix="Odia",
    word_order=WordOrder.SOV, script=ScriptType.ODIA, has_case_marking=True,
    to_english_lexicon={"ଏବଂ": "and", "ଅଛି": "is", "ମୁଁ": "i", "ଘର": "house",
                        "ପାଣି": "water", "ବହି": "book", "ଭଲ": "good", "ବିଲେଇ": "cat"},
    function_words=["ଏବଂ", "ଅଛି", "ର", "କୁ", "ଏହା"],
    sentence_terminators=(".", "!", "?", "।"), magic_id=0x4F444131,
))
_reg(LanguageProfile(
    engine_dir="Tamil_engine", language_name="Tamil", iso_code="ta", class_prefix="Tamil",
    word_order=WordOrder.SOV, script=ScriptType.TAMIL, is_agglutinative=True, has_case_marking=True,
    to_english_lexicon={"மற்றும்": "and", "உள்ளது": "is", "நான்": "i", "வீடு": "house",
                        "தண்ணீர்": "water", "புத்தகம்": "book", "நல்ல": "good", "பூனை": "cat"},
    function_words=["மற்றும்", "உள்ளது", "இன்", "ஐ", "இது"], magic_id=0x54414D31,
))
_reg(LanguageProfile(
    engine_dir="Telugu_engine", language_name="Telugu", iso_code="te", class_prefix="Telugu",
    word_order=WordOrder.SOV, script=ScriptType.TELUGU, is_agglutinative=True, has_case_marking=True,
    to_english_lexicon={"మరియు": "and", "ఉంది": "is", "నేను": "i", "ఇల్లు": "house",
                        "నీరు": "water", "పుస్తకం": "book", "మంచి": "good", "పిల్లి": "cat"},
    function_words=["మరియు", "ఉంది", "యొక్క", "ను", "ఇది"], magic_id=0x54454C31,
))
_reg(LanguageProfile(
    engine_dir="Kannada_engine", language_name="Kannada", iso_code="kn", class_prefix="Kannada",
    word_order=WordOrder.SOV, script=ScriptType.KANNADA, is_agglutinative=True, has_case_marking=True,
    to_english_lexicon={"ಮತ್ತು": "and", "ಇದೆ": "is", "ನಾನು": "i", "ಮನೆ": "house",
                        "ನೀರು": "water", "ಪುಸ್ತಕ": "book", "ಒಳ್ಳೆಯದು": "good", "ಬೆಕ್ಕು": "cat"},
    function_words=["ಮತ್ತು", "ಇದೆ", "ಅ", "ನ್ನು", "ಇದು"], magic_id=0x4B414E31,
))
_reg(LanguageProfile(
    engine_dir="Malayalam_engine", language_name="Malayalam", iso_code="ml", class_prefix="Malayalam",
    word_order=WordOrder.SOV, script=ScriptType.MALAYALAM, is_agglutinative=True, has_case_marking=True,
    to_english_lexicon={"ഒപ്പം": "and", "ആണ്": "is", "ഞാൻ": "i", "വീട്": "house",
                        "വെള്ളം": "water", "പുസ്തകം": "book", "നല്ലത്": "good", "പൂച്ച": "cat"},
    function_words=["ഒപ്പം", "ആണ്", "ന്റെ", "നെ", "ഇത്"], magic_id=0x4D4C4131,
))

# --- East Asian ---
_reg(LanguageProfile(
    engine_dir="Japanese_engine", language_name="Japanese", iso_code="ja", class_prefix="Japanese",
    word_order=WordOrder.SOV, script=ScriptType.KANA_KANJI, is_agglutinative=True, pro_drop=True, honorific_system=True,
    to_english_lexicon={"私": "i", "は": "", "が": "", "です": "is", "本": "book", "水": "water",
                        "家": "house", "良い": "good", "猫": "cat", "と": "and"},
    function_words=["は", "が", "を", "に", "で", "と", "です", "だ"],
    honorific_markers=["です", "ます", "ございます", "さん", "様"],
    sentence_terminators=(".", "!", "?", "。", "！", "？"), magic_id=0x4A504E31,
))
_reg(LanguageProfile(
    engine_dir="Korean_engine", language_name="Korean", iso_code="ko", class_prefix="Korean",
    word_order=WordOrder.SOV, script=ScriptType.HANGUL, is_agglutinative=True, pro_drop=True, honorific_system=True,
    to_english_lexicon={"나": "i", "는": "", "가": "", "이다": "is", "책": "book", "물": "water",
                        "집": "house", "좋은": "good", "고양이": "cat", "그리고": "and"},
    function_words=["는", "은", "가", "이", "를", "을", "에", "와", "과"],
    honorific_markers=["습니다", "세요", "님", "요"],
    sentence_terminators=(".", "!", "?", "。"), magic_id=0x4B4F5231,
))
_reg(LanguageProfile(
    engine_dir="Mandarin_engine", language_name="Mandarin", iso_code="zh", class_prefix="Mandarin",
    word_order=WordOrder.SVO, script=ScriptType.HAN, is_tonal=True,
    to_english_lexicon={"我": "i", "是": "is", "和": "and", "书": "book", "水": "water",
                        "家": "house", "好": "good", "猫": "cat", "的": "of"},
    function_words=["的", "是", "和", "了", "在", "这"],
    sentence_terminators=(".", "!", "?", "。", "！", "？"), magic_id=0x4D414E31,
))
_reg(LanguageProfile(
    engine_dir="Cantonese_engine", language_name="Cantonese", iso_code="yue", class_prefix="Cantonese",
    word_order=WordOrder.SVO, script=ScriptType.HAN, is_tonal=True,
    to_english_lexicon={"我": "i", "係": "is", "同": "and", "書": "book", "水": "water",
                        "屋企": "house", "好": "good", "貓": "cat", "嘅": "of"},
    function_words=["嘅", "係", "同", "咗", "喺", "呢"],
    sentence_terminators=(".", "!", "?", "。", "！", "？"), magic_id=0x43414E31,
))

# --- Southeast Asian ---
_reg(LanguageProfile(
    engine_dir="Vietnamese_engine", language_name="Vietnamese", iso_code="vi", class_prefix="Vietnamese",
    word_order=WordOrder.SVO, script=ScriptType.LATIN, is_tonal=True,
    to_english_lexicon={"tôi": "i", "là": "is", "và": "and", "sách": "book", "nước": "water",
                        "nhà": "house", "tốt": "good", "mèo": "cat", "của": "of"},
    function_words=["là", "và", "của", "này", "một"], magic_id=0x56494531,
))
_reg(LanguageProfile(
    engine_dir="Thai_engine", language_name="Thai", iso_code="th", class_prefix="Thai",
    word_order=WordOrder.SVO, script=ScriptType.THAI, is_tonal=True,
    to_english_lexicon={"ฉัน": "i", "เป็น": "is", "และ": "and", "หนังสือ": "book", "น้ำ": "water",
                        "บ้าน": "house", "ดี": "good", "แมว": "cat", "ของ": "of"},
    function_words=["เป็น", "และ", "ของ", "นี้", "ที่"], magic_id=0x54484131,
))
_reg(LanguageProfile(
    engine_dir="Burmese_engine", language_name="Burmese", iso_code="my", class_prefix="Burmese",
    word_order=WordOrder.SOV, script=ScriptType.MYANMAR, is_tonal=True, has_case_marking=True,
    to_english_lexicon={"ကျွန်တော်": "i", "ဖြစ်သည်": "is", "နှင့်": "and", "စာအုပ်": "book",
                        "ရေ": "water", "အိမ်": "house", "ကောင်း": "good", "ကြောင်": "cat"},
    function_words=["နှင့်", "သည်", "ကို", "မှာ", "ဤ"],
    sentence_terminators=(".", "!", "?", "။"), magic_id=0x42555231,
))
_reg(LanguageProfile(
    engine_dir="Indonesian_engine", language_name="Indonesian", iso_code="id", class_prefix="Indonesian",
    word_order=WordOrder.SVO, script=ScriptType.LATIN,
    to_english_lexicon={"saya": "i", "adalah": "is", "dan": "and", "buku": "book", "air": "water",
                        "rumah": "house", "baik": "good", "kucing": "cat", "dari": "of"},
    function_words=["yang", "dan", "adalah", "ini", "dari"], magic_id=0x49444E31,
))
_reg(LanguageProfile(
    engine_dir="Malay_engine", language_name="Malay", iso_code="ms", class_prefix="Malay",
    word_order=WordOrder.SVO, script=ScriptType.LATIN,
    to_english_lexicon={"saya": "i", "adalah": "is", "dan": "and", "buku": "book", "air": "water",
                        "rumah": "house", "baik": "good", "kucing": "cat", "dari": "of"},
    function_words=["yang", "dan", "adalah", "ini", "dari"], magic_id=0x4D535931,
))
_reg(LanguageProfile(
    engine_dir="Tagalog_engine", language_name="Tagalog", iso_code="tl", class_prefix="Tagalog",
    word_order=WordOrder.VSO, script=ScriptType.LATIN,
    to_english_lexicon={"ako": "i", "ay": "is", "at": "and", "aklat": "book", "tubig": "water",
                        "bahay": "house", "mabuti": "good", "pusa": "cat", "ng": "of"},
    function_words=["ang", "ng", "sa", "at", "ay", "ito"], magic_id=0x54414731,
))

# --- African ---
_reg(LanguageProfile(
    engine_dir="Swahili_engine", language_name="Swahili", iso_code="sw", class_prefix="Swahili",
    word_order=WordOrder.SVO, script=ScriptType.LATIN, is_agglutinative=True,
    to_english_lexicon={"mimi": "i", "ni": "is", "na": "and", "kitabu": "book", "maji": "water",
                        "nyumba": "house", "nzuri": "good", "paka": "cat", "ya": "of"},
    function_words=["na", "ni", "ya", "wa", "hii"], magic_id=0x53574131,
))
_reg(LanguageProfile(
    engine_dir="Hausa_engine", language_name="Hausa", iso_code="ha", class_prefix="Hausa",
    word_order=WordOrder.SVO, script=ScriptType.LATIN, is_tonal=True, has_grammatical_gender=True,
    to_english_lexicon={"ni": "i", "ne": "is", "da": "and", "littafi": "book", "ruwa": "water",
                        "gida": "house", "kyau": "good", "kyanwa": "cat"},
    function_words=["da", "ne", "ce", "na", "wannan"], magic_id=0x48415531,
))
_reg(LanguageProfile(
    engine_dir="Yoruba_engine", language_name="Yoruba", iso_code="yo", class_prefix="Yoruba",
    word_order=WordOrder.SVO, script=ScriptType.LATIN, is_tonal=True,
    to_english_lexicon={"mo": "i", "jẹ": "is", "àti": "and", "ìwé": "book", "omi": "water",
                        "ilé": "house", "dára": "good", "ológbò": "cat"},
    function_words=["ni", "àti", "ti", "yìí"], magic_id=0x594F5231,
))


def get_profile(engine_dir: str) -> LanguageProfile:
    """Return the profile for an engine directory, raising if unknown."""
    if engine_dir not in LANGUAGE_REGISTRY:
        raise KeyError(f"No LanguageProfile registered for '{engine_dir}'. "
                       f"Known: {sorted(LANGUAGE_REGISTRY)}")
    return LANGUAGE_REGISTRY[engine_dir]
