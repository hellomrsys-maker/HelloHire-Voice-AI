"""
French Clitic Pronoun Sequencing Skill.
Validates the canonical linear ordering of pre-verbal clitic pronouns and
postposed hyphenated imperative clusters.
"""

from typing import List, Dict, Any, Optional, Tuple


class FrenchCliticEngine:
    """
    Evaluates relative ordering and grammatical validity of French pronominal clitic sequences.
    """

    # Pre-verbal hierarchy ranks (lower number precedes higher number)
    PREVERBAL_RANKS = {
        # Rank 1: Reflexives and 1st/2nd person clitics
        "me": 1, "m'": 1, "te": 1, "t'": 1, "se": 1, "s'": 1, "nous": 1, "vous": 1,
        # Rank 2: 3rd person direct object clitics
        "le": 2, "la": 2, "les": 2, "l'": 2,
        # Rank 3: 3rd person indirect object clitics
        "lui": 3, "leur": 3,
        # Rank 4: Adverbial locative / prepositional y
        "y": 4,
        # Rank 5: Genitive / partitive en
        "en": 5
    }

    def evaluate_clitic_sequence(self, clitics: List[str]) -> Dict[str, Any]:
        """
        Validates whether a sequence of pre-verbal clitic pronouns satisfies
        the canonical French relative ordering constraints.
        """
        normalized = [c.lower().strip("'-") for c in clitics]
        ranks: List[int] = []

        for c in normalized:
            # Handle elided clitics
            key = c + "'" if c in {"m", "t", "s", "l", "qu", "n"} else c
            if key in self.PREVERBAL_RANKS:
                ranks.append(self.PREVERBAL_RANKS[key])
            elif c in self.PREVERBAL_RANKS:
                ranks.append(self.PREVERBAL_RANKS[c])

        if len(ranks) < 2:
            return {
                "is_valid": True,
                "clitics": clitics,
                "ranks": ranks,
                "message": "Séquence valide (un seul ou aucun clitique)."
            }

        # Check strictly ascending ranks
        for i in range(len(ranks) - 1):
            if ranks[i] >= ranks[i + 1]:
                return {
                    "is_valid": False,
                    "clitics": clitics,
                    "ranks": ranks,
                    "error_at": (clitics[i], clitics[i + 1]),
                    "message": f"Violation de l'ordre clitique: '{clitics[i]}' (rang {ranks[i]}) ne peut pas précéder '{clitics[i+1]}' (rang {ranks[i+1]})."
                }

        return {
            "is_valid": True,
            "clitics": clitics,
            "ranks": ranks,
            "message": "Ordre clitique rigoureusement respecté."
        }

    def evaluate_imperative_clitics(self, imperative_text: str) -> Dict[str, Any]:
        """
        Validates affirmative imperative postposed clitic sequence (e.g. 'donne-le-moi').
        In affirmative imperative, direct object precedes indirect (le/la/les before moi/toi/lui/nous/vous/leur).
        """
        parts = imperative_text.lower().split("-")
        if len(parts) <= 1:
            return {"is_imperative_chain": False, "is_valid": True}

        clitics = parts[1:]
        # In imperative, Direct (le, la, les) precedes Indirect (moi, toi, lui, etc.)
        if len(clitics) == 2:
            c1, c2 = clitics[0], clitics[1]
            if c1 in {"le", "la", "les"} and c2 in {"moi", "toi", "lui", "nous", "vous", "leur", "y", "en"}:
                return {"is_imperative_chain": True, "is_valid": True, "message": "Ordre impératif canonique respecté."}
            elif c1 in {"moi", "toi"} and c2 in {"le", "la", "les"}:
                return {"is_imperative_chain": True, "is_valid": False, "message": f"Inversion requise: '{c2}-{c1}' attendu."}

        return {"is_imperative_chain": True, "is_valid": True, "message": "Ordre impératif acceptable."}
