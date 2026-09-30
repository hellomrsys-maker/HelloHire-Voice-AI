"""
Hindustani POS Tagging Skill.
Assigns Universal Dependencies (UD) morphosyntactic tags to Hindustani tokens
in both Romanized and Devanagari orthographies.
"""

from typing import List, Tuple, Dict, Any, Optional

HINDUSTANI_CLOSED_CLASS = {
    # Postpositions (ADP)
    "ne": "ADP", "ko": "ADP", "se": "ADP", "mein": "ADP", "par": "ADP",
    "ka": "ADP", "ke": "ADP", "ki": "ADP", "tak": "ADP",
    "ने": "ADP", "को": "ADP", "से": "ADP", "में": "ADP", "पर": "ADP",
    "का": "ADP", "के": "ADP", "की": "ADP", "तक": "ADP",

    # Pronouns (PRON)
    "main": "PRON", "tu": "PRON", "tum": "PRON", "aap": "PRON",
    "yeh": "PRON", "woh": "PRON", "hum": "PRON",
    "maine": "PRON", "tune": "PRON", "usne": "PRON", "isne": "PRON",
    "humne": "PRON", "tumne": "PRON", "aapne": "PRON",
    "unhonne": "PRON", "inhonne": "PRON", "mujhe": "PRON", "tujhe": "PRON",
    "humein": "PRON", "tumhein": "PRON", "unhein": "PRON", "inhein": "PRON",
    "kaun": "PRON", "koi": "PRON", "kya": "PRON", "kuch": "PRON",
    "मैं": "PRON", "तू": "PRON", "तुम": "PRON", "आप": "PRON",
    "यह": "PRON", "वह": "PRON", "हम": "PRON",
    "मैंने": "PRON", "तूने": "PRON", "उसने": "PRON", "इसने": "PRON",
    "हमने": "PRON", "तुमने": "PRON", "आपने": "PRON",
    "उन्होंने": "PRON", "इन्होंने": "PRON", "मुझे": "PRON", "तुझे": "PRON",
    "हमें": "PRON", "तुम्हें": "PRON", "उन्हें": "PRON", "इन्हें": "PRON",
    "कौन": "PRON", "कोई": "PRON", "क्या": "PRON", "कुछ": "PRON",

    # Auxiliaries (AUX)
    "hai": "AUX", "hain": "AUX", "ho": "AUX", "hoon": "AUX",
    "tha": "AUX", "the": "AUX", "thi": "AUX", "thin": "AUX",
    "hoga": "AUX", "honge": "AUX", "hogi": "AUX", "hongi": "AUX",
    "sakta": "AUX", "sakte": "AUX", "sakti": "AUX",
    "chahiye": "AUX",
    "है": "AUX", "हैं": "AUX", "हो": "AUX", "हूँ": "AUX",
    "था": "AUX", "थे": "AUX", "थी": "AUX", "थीं": "AUX",
    "होगा": "AUX", "होंगे": "AUX", "होगी": "AUX", "होंगी": "AUX",
    "सकता": "AUX", "सकते": "AUX", "सकती": "AUX",
    "चाहिए": "AUX",

    # Particles (PART)
    "bhi": "PART", "hi": "PART", "to": "PART", "na": "PART", "nahin": "PART", "mat": "PART",
    "ji": "PART", "saab": "PART",
    "भी": "PART", "ही": "PART", "तो": "PART", "न": "PART", "नहीं": "PART", "मत": "PART",
    "जी": "PART", "साहब": "PART",

    # Conjunctions (CCONJ / SCONJ)
    "aur": "CCONJ", "lekin": "CCONJ", "parantu": "CCONJ", "magar": "CCONJ", "ya": "CCONJ",
    "ki": "SCONJ", "kyonki": "SCONJ", "agar": "SCONJ", "yadi": "SCONJ", "jab": "SCONJ",
    "और": "CCONJ", "लेकिन": "CCONJ", "परंतु": "CCONJ", "मगर": "CCONJ", "या": "CCONJ",
    "कि": "SCONJ", "क्योंकि": "SCONJ", "अगर": "SCONJ", "यदि": "SCONJ", "जब": "SCONJ",

    # Adverbs (ADV)
    "aaj": "ADV", "kal": "ADV", "yahan": "ADV", "wahan": "ADV", "kahan": "ADV",
    "jaldi": "ADV", "dheere": "ADV", "hamesha": "ADV", "kabhi": "ADV",
    "आज": "ADV", "कल": "ADV", "यहाँ": "ADV", "वहाँ": "ADV", "कहाँ": "ADV",
    "जल्दी": "ADV", "धीरे": "ADV", "हमेशा": "ADV", "कभी": "ADV",
}

COMMON_VERBS = {
    "karta", "karte", "karti", "karega", "karenge", "kiya", "kiye", "ki", "karna", "kar",
    "jaata", "jaate", "jaati", "jaayega", "jaayenge", "gaya", "gaye", "gayi", "jaana", "jaa",
    "aata", "aate", "aati", "aayega", "aayenge", "aaya", "aaye", "aayi", "aana", "aa",
    "dekhta", "dekhte", "dekhti", "dekhega", "dekhenge", "dekha", "dekhe", "dekhi", "dekhna", "dekh",
    "padhta", "padhte", "padhti", "padhega", "padhenge", "padha", "padhe", "padhi", "padhna", "padh",
    "likhta", "likhte", "likhti", "likhega", "likhenge", "likha", "likhe", "likhi", "likhna", "likh",
    "khata", "khate", "khati", "khayega", "khayenge", "khaya", "khaye", "khayi", "khana", "khaa",
    "peeta", "peete", "peeti", "peeyega", "peeyenge", "peeya", "peeye", "peeyi", "peena", "pee",
    "bolta", "bolte", "bolti", "bolega", "bolenge", "bola", "bole", "boli", "bolna", "bol",
    "sunta", "sunte", "sunti", "sunega", "sunenge", "suna", "sune", "suni", "sunna", "sun",
    "deta", "dete", "deti", "dega", "denge", "diya", "diye", "di", "dena", "de",
    "leta", "lete", "leti", "lega", "lenge", "liya", "liye", "li", "lena", "le",
    "raha", "rahe", "rahi", "rahin", "rahna", "rahta", "rahte", "rahti",
    "kholna", "kholta", "khola", "samajhna", "samajhta", "samjha", "samjhi",
    "padhaya", "padhaye", "padhayi", "sikhaya", "sikhaye", "sikhayi",
    "banaya", "banaye", "banayi", "dikhaya", "dikhaye", "dikhayi",
    "khilaya", "khilaye", "khilayi", "pilaya", "samjhaya", "bheja", "bheje", "bheji",
    "करता", "करते", "करती", "करेगा", "करेंगे", "किया", "किए", "की", "करना", "कर",
    "जाता", "जाते", "जाती", "जाएगा", "जाएंगे", "गया", "गए", "गई", "जाना", "जा",
    "आता", "आते", "आती", "आएगा", "आएंगे", "आया", "आए", "आई", "आना", "आ",
    "देखता", "देखते", "देखती", "देखेगा", "देखेंगे", "देखा", "देखे", "देखी", "देखना", "देख",
    "पढ़ता", "पढ़ते", "पढ़ती", "पढ़ेगा", "पढ़ेंगे", "पढ़ा", "पढ़े", "पढ़ी", "पढ़ना", "पढ़",
    "लिखता", "लिखते", "लिखती", "लिखेगा", "लिखेंगे", "लिखा", "लिखे", "लिखी", "लिखना", "लिख",
    "खाता", "खाते", "खाती", "खाएगा", "खाएंगे", "खाया", "खाए", "खाई", "खाना", "खा",
    "पीता", "पीते", "पीती", "पीएगा", "पीएंगे", "पीया", "पीए", "पीई", "पीना", "पी",
    "बोलता", "बोलते", "बोलती", "बोलेगा", "बोलेंगे", "बोला", "बोले", "बोली", "बोलना", "बोल",
    "सुनता", "सुनते", "सुनती", "सुनेगा", "सुनेंगे", "सुना", "सुने", "सुनी", "सुनना", "सुन",
    "देता", "देते", "देती", "देगा", "देंगे", "दिया", "दिए", "दी", "देना", "दे",
    "लेता", "लेते", "लेती", "लेगा", "लेंगे", "लिया", "लिए", "ली", "लेना", "ले",
    "रहा", "रहे", "रही", "रहीं", "रहना", "रहता", "रहते", "रहती",
    "पढ़ाया", "पढ़ाये", "पढ़ाई", "सिखाया", "सिखाये", "सिखाई", "बनाया", "दिखाया"
}


class HindustaniPOSTagger:
    """
    Part-of-Speech tagger for Hindustani implementing Universal Dependencies standards.
    """

    def tag(self, tokens: List[str]) -> List[Tuple[str, str]]:
        tagged: List[Tuple[str, str]] = []

        for tok in tokens:
            low = tok.lower()

            if tok in {"।", "॥", ".", ",", ";", ":", "!", "?", "—", "-", "(", ")"}:
                tagged.append((tok, "PUNCT"))
            elif low in HINDUSTANI_CLOSED_CLASS:
                tagged.append((tok, HINDUSTANI_CLOSED_CLASS[low]))
            elif tok in HINDUSTANI_CLOSED_CLASS:
                tagged.append((tok, HINDUSTANI_CLOSED_CLASS[tok]))
            elif low in COMMON_VERBS or tok in COMMON_VERBS:
                tagged.append((tok, "VERB"))
            elif low in {"naya", "nayi", "naye", "purana", "purane", "purani", "accha", "acche", "acchi", "bura", "bure", "buri", "bada", "bade", "badi", "chota", "chote", "choti", "sundar", "saaf", "नया", "नई", "नए", "पुराना", "अच्छा", "बुरा", "बड़ा", "छोटा", "सुंदर", "साफ़"}:
                tagged.append((tok, "ADJ"))
            elif low.endswith(("daar", "vaan", "shil", "mey", "ik")):
                tagged.append((tok, "ADJ"))
            elif low.endswith(("ta", "te", "ti", "raha", "rahe", "rahi", "ega", "enge", "oge", "unga", "aya", "aye", "ayi", "ayin", "aaya", "aaye", "aayi")) and len(low) > 3:
                tagged.append((tok, "VERB"))
            elif tok.endswith(("ता", "ते", "ती", "रहा", "रहे", "रही", "ेगा", "ेंगे", "ना", "ाया", "ाए", "ाई", "ाईं")) and len(tok) > 2:
                tagged.append((tok, "VERB"))
            else:
                tagged.append((tok, "NOUN"))

        return tagged
