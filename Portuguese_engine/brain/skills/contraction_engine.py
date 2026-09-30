"""
Portuguese Contraction Engine: Manages prepositional contractions (do, na, ao, pelo)
and validates Crase (à / às) accentuation rules.
"""

from typing import Dict, Any, Optional, Tuple, List
import os
import json


class PortugueseContractionEngine:
    """
    Handles prepositional fusions and validates Crase syntax.
    """

    MASCULINE_WORDS = {
        "pé", "cavalo", "bordo", "dia", "tempo", "trabalho", "carro",
        "prazo", "favor", "gosto", "lápis", "computador"
    }

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(base_dir, "rules", "contraction_matrix.json")
        
        self.db = {}
        if os.path.exists(db_path):
            with open(db_path, "r", encoding="utf-8") as f:
                self.db = json.load(f)
        
        self.contractions = self.db.get("contractions", {})

    def contract(self, preposition: str, word: str) -> Optional[str]:
        """
        Contracts a preposition with an article, demonstrative, or pronoun.
        Example: ('de', 'o') -> 'do', ('em', 'a') -> 'na', ('a', 'a') -> 'à'
        """
        prep_low = preposition.lower()
        word_low = word.lower()

        if prep_low in self.contractions and word_low in self.contractions[prep_low]:
            contracted = self.contractions[prep_low][word_low]
            if preposition.istitle():
                return contracted.capitalize()
            return contracted
        return None

    def validate_crase(self, following_word: str, has_crase: bool) -> Tuple[bool, str]:
        """
        Validates the use of the grave accent (Crase).
        Crase is forbidden before masculine nouns, verbs, or indefinite pronouns.
        """
        word_low = following_word.lower()

        # Prohibited before verbs (e.g. 'a partir de', NOT '*à partir de')
        if word_low.endswith(("ar", "er", "ir")) and has_crase:
            return False, f"Crase is prohibited before verbs; found 'à {following_word}'."

        # Prohibited before masculine nouns (e.g. 'a pé', NOT '*à pé')
        if word_low in self.MASCULINE_WORDS and has_crase:
            return False, f"Crase is prohibited before masculine nouns; found 'à {following_word}'."

        return True, "Crase usage is valid."
