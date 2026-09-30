"""
Persian Ezafe (کسره اضافه) Engine
Identifies, validates, and generates Ezafe connectors between head nouns,
attributive adjectives, and genitive possessive modifiers.
"""

from typing import Dict, Any, List, Optional
from Persian_engine.brain.skills.tokenization import PersianTokenizer

VOWEL_ENDINGS = {'ا', 'و', 'ی'}
SILENT_HEH = {'ه', 'ة'}

class PersianEzafeEngine:
    """
    Computes Ezafe phonetic and orthographic realization:
    - Consonant ending -> kasre (-e)
    - Vowel ending (alif/vav) -> -ye (ی)
    - Silent heh ending -> -ye (hamzeh on heh or ی)
    """

    def determine_ezafe_suffix(self, head_word: str) -> Dict[str, str]:
        """
        Determines the appropriate Ezafe surface form and pronunciation
        for a given head word.
        """
        clean_word = head_word.rstrip()
        if not clean_word:
            return {"phonetic": "-e", "orthographic": "ِ", "type": "consonant"}

        last_char = clean_word[-1]
        
        # Vowels (Alef / Vav)
        if last_char in {'ا', 'و'}:
            return {
                "phonetic": "-ye",
                "orthographic": "ی",
                "full_written": f"{clean_word} ی",
                "type": "vowel_alif_vav"
            }
        # Silent Heh (e.g., خانه, نامه)
        elif last_char in SILENT_HEH:
            return {
                "phonetic": "-ye",
                "orthographic": "ٔ",
                "full_written": f"{clean_word}ٔ",
                "type": "silent_heh"
            }
        # Yeh ending (e.g. بوی, ماهی)
        elif last_char == 'ی':
            return {
                "phonetic": "-ye",
                "orthographic": "ِ",
                "full_written": f"{clean_word}ِ",
                "type": "yeh_ending"
            }
        # Standard consonant ending
        else:
            return {
                "phonetic": "-e",
                "orthographic": "ِ",
                "full_written": f"{clean_word}ِ",
                "type": "consonant"
            }

    def construct_ezafe_phrase(self, head: str, modifier: str, explicit_diacritic: bool = False) -> str:
        """
        Constructs an Ezafe phrase linking a head to its modifier.
        In standard unvocalized Persian, consonant Ezafe is usually omitted in spelling,
        while vowel/silent-heh Ezafe is marked with ی or hamzeh.
        """
        ez = self.determine_ezafe_suffix(head)
        
        if ez["type"] == "vowel_alif_vav":
            return f"{head}ی {modifier}"
        elif ez["type"] == "silent_heh":
            return f"{head}ٔ {modifier}"
        else:
            if explicit_diacritic:
                return f"{head}ِ {modifier}"
            return f"{head} {modifier}"

    def is_ezafe_candidate(self, pos1: str, pos2: str) -> bool:
        """Checks if two consecutive POS tags form a legitimate Ezafe dependency."""
        if pos1 in {"NOUN", "PRON"} and pos2 in {"ADJ", "NOUN", "PRON"}:
            return True
        return False
