"""
Hindustani Oblique Case Skill.
Transforms direct nominal heads into oblique case forms preceding postpositions
and flags ungrammatical direct case occurrences before postpositional clitics.
"""

from typing import Dict, Any, List, Optional, Tuple


class ObliqueCaseEngine:
    """
    Engine evaluating and executing Hindustani direct-to-oblique nominal case declensions.
    """

    POSTPOSITIONS = {
        "ne", "ko", "se", "ka", "ke", "ki", "mein", "par", "tak",
        "ने", "को", "से", "का", "के", "की", "में", "पर", "तक"
    }

    def to_oblique(self, noun: str, gender: str = "M", number: str = "SG") -> str:
        """
        Converts a noun from direct to oblique case form.
        """
        n_clean = noun.strip()
        low = n_clean.lower()

        if gender == "M" and number == "SG":
            # Marked masculine singular ending in -a -> -e
            if low.endswith("a") and not low.endswith(("ta", "da")):  # general -a nouns like ladka, baccha
                return n_clean[:-1] + "e"
            elif n_clean.endswith("ा"):
                return n_clean[:-1] + "े"
            return n_clean

        elif number == "PL":
            # Plural oblique ends in -on / -ओं
            if low == "kitaab":
                return "kitabon"
            elif low.endswith("aab"):
                return n_clean[:-3] + "abon"
            elif n_clean.endswith("ा") or n_clean.endswith("े"):
                return n_clean[:-1] + "ों"
            elif low.endswith(("a", "e")):
                return n_clean[:-1] + "on"
            elif n_clean.endswith("ी"):
                return n_clean[:-1] + "ियों"
            elif low.endswith("i"):
                return n_clean[:-1] + "iyon"
            else:
                return n_clean + ("ों" if any('\u0900' <= c <= '\u097F' for c in n_clean) else "on")

        return n_clean

    def evaluate_noun_phrase(self, noun: str, postposition: str, gender: str = "M", number: str = "SG") -> Dict[str, Any]:
        """
        Evaluates whether a noun preceding a postposition correctly exhibits oblique case inflection.
        """
        expected_oblique = self.to_oblique(noun, gender, number)
        is_oblique = noun.lower() == expected_oblique.lower()

        # If it should have changed (e.g. ladka -> ladke) but didn't:
        requires_morph_change = expected_oblique.lower() != noun.lower()
        has_error = requires_morph_change and (noun.lower() != expected_oblique.lower())

        return {
            "surface_noun": noun,
            "postposition": postposition,
            "expected_oblique": expected_oblique,
            "is_valid": not has_error,
            "message": "Forme oblique correcte." if not has_error else f"Erreur de cas oblique: '{noun} {postposition}' est incorrect; utiliser '{expected_oblique} {postposition}'."
        }
