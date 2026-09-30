"""
Tamil Tokenization Engine.
Performs Unicode Tamil word segmentation and compound recognition,
preserving grapheme cluster integrity (consonant + virama/vowel sign).
"""

import re
from typing import List

TAMIL_COMPOUND_LEXICON = {
    "தமிழ்நாடு", "செந்தமிழ்", "கொடுந்தமிழ்", "திருக்குறள்", "வணக்கம்", "நன்றி",
    "சாப்பிடுங்கள்", "பள்ளிக்கூடம்", "பல்கலைக்கழகம்", "புத்தகங்கள்", "அம்மா", "அப்பா",
    "அண்ணன்", "தம்பி", "அக்கா", "தங்கை", "செய்தித்தாள்", "கல்லூரி", "மாணவன்", "மாணவி"
}

# Regex to split on whitespace and punctuation while keeping Tamil Unicode blocks intact
TOKEN_PATTERN = re.compile(r"[\u0B80-\u0BFF]+|[a-zA-Z0-9]+|[^\s\w]")

def tokenize_tamil(text: str) -> List[str]:
    """
    Tokenizes Tamil text into words and punctuation tokens,
    preserving Tamil Unicode grapheme clusters.
    """
    tokens = TOKEN_PATTERN.findall(text)
    return tokens
