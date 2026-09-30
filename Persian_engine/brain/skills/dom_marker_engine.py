"""
Persian Differential Object Marking (DOM) Engine
Audits, validates, and positions the postpositional particle 'rā' (را) on direct objects.
"""

from typing import Dict, Any, List, Tuple
from Persian_engine.brain.skills.pos_tagging import PersianPOSTagger

class PersianDOMEngine:
    """
    Evaluates definiteness and specificity criteria for Persian direct objects:
    - Definite nouns, proper nouns, and pronouns obligatorily require 'rā' (را).
    - Generic/incorporated non-specific direct objects must NOT take 'rā'.
    """
    
    def __init__(self):
        self.tagger = PersianPOSTagger()
        self.proper_nouns = {
            "علی", "مریم", "رضا", "سارا", "تهران", "ایران", "شیراز", "اصفهان",
            "سعدی", "حافظ", "فردوسی", "کوروش", "داریوش"
        }
        self.demonstratives = {"این", "آن", "همین", "همان"}
        self.pronouns = {"من", "تو", "او", "وی", "ما", "شما", "آن‌ها", "ایشان", "اینها", "آنها"}

    def evaluate_object_definiteness(self, noun_phrase: str) -> Dict[str, Any]:
        """
        Analyzes a noun phrase to determine if it is definite/specific and demands 'rā'.
        """
        tokens = noun_phrase.strip().split()
        if not tokens:
            return {"requires_ra": False, "reason": "empty"}

        # 1. Check if it's a pronoun
        if len(tokens) == 1 and tokens[0] in self.pronouns:
            return {
                "requires_ra": True,
                "reason": "personal_pronoun",
                "status": "mandatory",
                "translit_pattern": f"{tokens[0]} rā"
            }

        # 2. Check if it's a proper noun
        if any(t in self.proper_nouns for t in tokens):
            return {
                "requires_ra": True,
                "reason": "proper_noun",
                "status": "mandatory"
            }

        # 3. Check for demonstrative determiners (این کتاب, آن خانه)
        if tokens[0] in self.demonstratives:
            return {
                "requires_ra": True,
                "reason": "demonstrative_modifier",
                "status": "mandatory"
            }

        # 4. Check for pronominal enclitics (-am, -at, -ash, -eman, -etan, -eshan)
        # e.g., کتابم (my book), خانه‌اش (his house)
        last_tok = tokens[-1]
        enclitics = ["م", "ت", "ش", "مان", "تان", "شان"]
        if any(last_tok.endswith(enc) and len(last_tok) > len(enc) + 1 for enc in enclitics):
            return {
                "requires_ra": True,
                "reason": "pronominal_enclitic_possessive",
                "status": "mandatory"
            }

        # 5. Check for indefinite marker '-i' (ی) e.g., کتابی
        if last_tok.endswith("ی") and len(last_tok) > 2:
            return {
                "requires_ra": False, # optional specific or non-specific
                "reason": "indefinite_specific_optional",
                "status": "optional"
            }

        # Default: non-specific bare object
        return {
            "requires_ra": False,
            "reason": "generic_non_specific",
            "status": "prohibited"
        }

    def attach_dom_marker(self, object_np: str) -> str:
        """Attaches 'rā' (را) with a space to a definite direct object noun phrase."""
        clean = object_np.strip()
        if clean.endswith("را"):
            return clean
        return f"{clean} را"

    def audit_sentence_dom(self, words: List[str]) -> List[Dict[str, Any]]:
        """
        Audits a tokenized sentence for correct 'rā' placement or missing 'rā'.
        """
        issues = []
        for i, word in enumerate(words):
            # If a proper noun or pronoun is followed by a verb without 'rā'
            if word in self.proper_nouns or word in self.pronouns:
                # Check if it's not the subject (e.g. if another subject exists or if it's object position)
                if i + 1 < len(words):
                    next_word = words[i + 1]
                    # If followed immediately by a verb without rā, and not in subject initial position with intransitive
                    if next_word != "را" and self.tagger.tag_word(next_word) == "VERB" and i > 0:
                        issues.append({
                            "token": word,
                            "index": i,
                            "type": "missing_dom_ra",
                            "message": f"Definite object '{word}' should be followed by 'را' before verb '{next_word}'."
                        })
        return issues
