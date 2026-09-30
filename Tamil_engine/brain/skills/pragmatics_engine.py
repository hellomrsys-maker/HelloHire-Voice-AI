"""
Tamil Pragmatics and Diglossic Register Engine.
Audits diglossic levels:
- Formal Literary Tamil (Centamiḻ செந்தமிழ்)
- Spoken Colloquial Tamil (Koṭuntamiḻ கொடுந்தமிழ்)
Provides epistolary correspondence generators.
"""

from typing import Dict, List, Optional

CENTAMIL_MARKERS = {
    "வருகிறேன்", "சென்றான்", "சாப்பிடுங்கள்", "செய்தான்", "இல்லை",
    "அவ்வாறு", "எவ்வாறு", "நன்றாக", "அவர்கள்", "தங்கள்", "மதிப்பிற்குரிய"
}

KODUNTAMIL_MARKERS = {
    "வர்றேன்", "போனான்", "சாப்பிடுங்க", "பண்ணான்", "இல்ல",
    "அப்படி", "எப்படி", "நல்லா", "அவங்க", "போய்ட்டான்", "செஞ்சான்"
}

def detect_register(text: str) -> Dict[str, any]:
    """
    Classifies Tamil text as Literary (Centamiḻ) or Spoken (Koṭuntamiḻ).
    """
    cent_hits = [m for m in CENTAMIL_MARKERS if m in text]
    kodun_hits = [m for m in KODUNTAMIL_MARKERS if m in text]
    
    if len(kodun_hits) > len(cent_hits):
        reg = "koduntamil"
        tier = 2
        desc = "கொடுந்தமிழ் (Koṭuntamiḻ) - Spoken Colloquial Tamil"
    elif len(cent_hits) > len(kodun_hits):
        reg = "centamil"
        tier = 1
        desc = "செந்தமிழ் (Centamiḻ) - Literary Formal Tamil"
    else:
        reg = "centamil"
        tier = 1
        desc = "செந்தமிழ் (Centamiḻ) - Standard / Literary Baseline"
        
    return {
        "text": text,
        "register": reg,
        "tier_level": tier,
        "description": desc,
        "centamil_markers": cent_hits,
        "koduntamil_markers": kodun_hits
    }

def compose_email(recipient: str, subject: str, message: str, register: str = "formal") -> str:
    """
    Synthesizes a structured letter or email according to Tamil epistolary conventions.
    """
    if register == "formal":
        salutation = f"மதிப்பிற்குரிய {recipient} அவர்களுக்கு வணக்கம்,"
        closing = "இங்ஙனம்,\nதங்கள் உண்மையுள்ள,\nநன்றி."
    else:
        salutation = f"அன்புள்ள {recipient}, வணக்கம்!"
        closing = "அன்புடன்,\nநன்றி."
        
    return f"பொருள்: {subject}\n\n{salutation}\n\n{message}\n\n{closing}"
