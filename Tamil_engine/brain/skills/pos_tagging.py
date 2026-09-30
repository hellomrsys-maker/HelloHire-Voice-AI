"""
Tamil Part-of-Speech (POS) Tagger.
Tags Tamil words with Universal Dependencies (UD) labels.
"""

from typing import List, Tuple
from Tamil_engine.brain.skills.tokenization import tokenize_tamil

TAMIL_POS_LEXICON = {
    # Pronouns
    "நான்": "PRON", "நாம்": "PRON", "நாங்கள்": "PRON",
    "நீ": "PRON", "நீங்கள்": "PRON", "அவன்": "PRON",
    "அவள்": "PRON", "அவர்": "PRON", "அவர்கள்": "PRON",
    "அது": "PRON", "அவை": "PRON", "எனக்கு": "PRON",
    "உனக்கு": "PRON", "அவனுக்கு": "PRON", "அவளுக்கு": "PRON",
    "என்னை": "PRON", "உன்னை": "PRON", "அவனை": "PRON",
    
    # Nouns
    "மரம்": "NOUN", "புத்தகம்": "NOUN", "வீடு": "NOUN", "நீர்": "NOUN",
    "பணம்": "NOUN", "மாணவன்": "NOUN", "மாணவி": "NOUN", "ஊர்": "NOUN",
    "மேசை": "NOUN", "தமிழ்": "NOUN", "நண்பன்": "NOUN", "மாம்பழம்": "NOUN",
    "குழந்தை": "NOUN", "பள்ளி": "NOUN", "கல்லூரி": "NOUN", "கடவுள்": "NOUN",
    
    # Verbs
    "படித்தேன்": "VERB", "படித்தான்": "VERB", "படித்தாள்": "VERB", "படித்தார்": "VERB",
    "படித்தார்கள்": "VERB", "செய்தான்": "VERB", "செய்தேன்": "VERB", "சென்றான்": "VERB",
    "வந்தான்": "VERB", "வந்தேன்": "VERB", "வாங்குகிறான்": "VERB", "வருகிறான்": "VERB",
    "வருகிறேன்": "VERB", "வர்றேன்": "VERB", "சாப்பிட்டான்": "VERB", "பார்": "VERB",
    "படி": "VERB", "செய்": "VERB", "வா": "VERB", "போ": "VERB",
    
    # Defective / Experiencer Modal Verbs
    "தெரியும்": "VERB", "புரியும்": "VERB", "வேண்டும்": "VERB", "பிடிக்கும்": "VERB", "பசிக்கிறது": "VERB",
    
    # Adjectives
    "நல்ல": "ADJ", "பெரிய": "ADJ", "சிறிய": "ADJ", "பழைய": "ADJ", "புதிய": "ADJ",
    "அழகான": "ADJ", "இனிய": "ADJ", "உயர்ந்த": "ADJ",
    
    # Adverbs
    "நன்றாக": "ADV", "வேகமாக": "ADV", "மெதுவாக": "ADV", "இங்கு": "ADV",
    "அங்கு": "ADV", "எங்கு": "ADV", "இப்போது": "ADV", "அப்போது": "ADV",
    "இனி": "ADV", "நல்லா": "ADV",
    
    # Negators & Particles
    "இல்லை": "PART", "அல்ல": "PART", "இல்ல": "PART", "தான்": "PART", "கூட": "PART",
    
    # Postpositions
    "மேலே": "ADP", "கீழே": "ADP", "உள்ளே": "ADP", "வெளியே": "ADP", "பின்னால்": "ADP",
    "முன்னால்": "ADP", "பக்கத்தில்": "ADP"
}

def tag_pos(tokens: List[str]) -> List[Tuple[str, str]]:
    """
    Tags a list of Tamil tokens with Universal Dependencies POS labels.
    """
    tagged: List[Tuple[str, str]] = []
    
    for token in tokens:
        if token in TAMIL_POS_LEXICON:
            tagged.append((token, TAMIL_POS_LEXICON[token]))
        elif token.endswith("க்கு") or token.endswith("உக்கு"):
            tagged.append((token, "NOUN"))
        elif token.endswith("ஐ") or token.endswith("ை"):
            tagged.append((token, "NOUN"))
        elif token.endswith("இல்") or token.endswith("ல்"):
            tagged.append((token, "NOUN"))
        elif token.endswith("தேன்") or token.endswith("தான்") or token.endswith("தாள்") or token.endswith("தார்கள்"):
            tagged.append((token, "VERB"))
        elif token.isdigit():
            tagged.append((token, "NUM"))
        else:
            tagged.append((token, "NOUN"))
            
    return tagged
