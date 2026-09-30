"""
Dutch V2 Syntax & Clause Architecture Engine
Analyzes Verb-Second (V2) positioning, Vorfeld fronting inversion,
subordinate SOV verb clusters, and separable verb brackets.
"""

from typing import List, Dict, Tuple, Any

class DutchV2SyntaxEngine:
    def __init__(self):
        self.subordinators = {
            "dat", "omdat", "doordat", "zodat", "als", "wanneer", "toen",
            "hoewel", "tenzij", "mits", "nadat", "voordat", "terwijl", "sinds",
            "zodra", "of"
        }
        self.separable_particles = {
            "op", "af", "aan", "uit", "in", "mee", "toe", "over", "door", "neer", "terug"
        }
        self.fronting_adverbs = {
            "morgen", "vandaag", "gisteren", "straks", "nu", "hier", "daar",
            "toen", "daarna", "eerst", "soms", "altijd", "vaak", "waarschijnlijk",
            "helaas", "natuurlijk", "gelukkig", "plotseling"
        }

    def analyze_clause(self, tokens: List[str], tagged: List[Tuple[str, str]]) -> Dict[str, Any]:
        # Filter out punctuation for structural analysis
        struct_tokens = [tok for tok in tokens if tok not in {".", ",", "!", "?", ";", ":"}]
        struct_tags = [tag for (tok, tag) in tagged if tok not in {".", ",", "!", "?", ";", ":"}]
        
        if not struct_tokens:
            return {
                "clause_type": "empty",
                "v2_valid": True,
                "inversion_active": False,
                "subordinate_sov_valid": True,
                "separable_bracket": False,
                "syntax_score": 100,
                "errors": []
            }

        first_word = struct_tokens[0].lower()
        is_subordinate = first_word in self.subordinators

        errors = []
        inversion_active = False
        v2_valid = True
        subordinate_sov_valid = True
        separable_bracket = False

        if is_subordinate:
            # Subordinate clause: Verb should be final (SOV)
            # Find all verbs / auxiliaries
            verb_indices = [i for i, tag in enumerate(struct_tags) if tag in {"VERB", "AUX"}]
            if verb_indices:
                last_verb_idx = verb_indices[-1]
                # In SOV, verbs cluster at the end. If the last verb index is not at the end of the clause
                # and non-verbs (objects/arguments) follow it, flag subordinate word order violation
                if len(struct_tokens) > 3 and last_verb_idx < len(struct_tokens) - 1 and struct_tags[-1] in {"NOUN", "ADJ", "ADV", "PRON", "DET"}:
                    subordinate_sov_valid = False
                    v2_valid = False
                    errors.append(
                        f"Subordinate SOV violation: In subordinate clause introduced by '{first_word}', "
                        f"finite verb '{struct_tokens[verb_indices[0]]}' must appear at clause end, not position 2."
                    )
            return {
                "clause_type": "subordinate",
                "subordinator": first_word,
                "v2_valid": v2_valid,
                "inversion_active": False,
                "subordinate_sov_valid": subordinate_sov_valid,
                "separable_bracket": False,
                "syntax_score": 100 if subordinate_sov_valid else 35,
                "errors": errors
            }

        # Main clause analysis
        # Check separable particle at coda
        if struct_tokens and struct_tokens[-1].lower() in self.separable_particles:
            separable_bracket = True

        # Check Position 1 (Vorfeld)
        # Determine if position 1 is an adjunct/adverbial or prepositional phrase
        first_token_low = struct_tokens[0].lower()
        first_tag = struct_tags[0]

        is_fronted = (
            first_token_low in self.fronting_adverbs or
            first_tag in {"ADV", "ADP"} or
            (first_tag == "ADJ" and len(struct_tokens) > 1 and struct_tags[1] not in {"NOUN"})
        )

        # Locate finite verb
        verb_indices = [i for i, tag in enumerate(struct_tags) if tag in {"VERB", "AUX"}]
        first_verb_idx = verb_indices[0] if verb_indices else -1

        if first_verb_idx == -1:
            # No verb detected; minor fragment
            return {
                "clause_type": "fragment",
                "v2_valid": True,
                "inversion_active": False,
                "subordinate_sov_valid": True,
                "separable_bracket": separable_bracket,
                "syntax_score": 85,
                "errors": []
            }

        if is_fronted:
            # Vorfeld is occupied by fronted adjunct. Verb must be in position 2 (index 1), Subject in position 3 (index 2)
            if first_verb_idx == 1:
                inversion_active = True
                v2_valid = True
            elif first_verb_idx == 2:
                # Verb is at position 3, e.g. "Morgen Jan gaat..." -> V2 inversion failure!
                v2_valid = False
                errors.append(
                    f"V2 Inversion Violation: Fronted constituent '{struct_tokens[0]}' requires finite verb "
                    f"at position 2, but found '{struct_tokens[1]}' followed by verb '{struct_tokens[2]}'."
                )
            else:
                v2_valid = False
                errors.append(f"V2 Violation: Verb '{struct_tokens[first_verb_idx]}' is at index {first_verb_idx}, expected position 2 (index 1).")
        else:
            # Canonical SVO: Verb should be in position 2 (index 1) or position 1 if question/imperative
            if first_verb_idx == 1:
                v2_valid = True
            elif first_verb_idx == 0:
                # Yes/No Question or Imperative (e.g. "Leest Jan een boek?")
                v2_valid = True
            else:
                # Delayed verb in main clause without subordinator
                v2_valid = False
                errors.append(f"V2 Main Clause Violation: Finite verb '{struct_tokens[first_verb_idx]}' is at index {first_verb_idx}, expected position 2.")

        score = 100
        if not v2_valid:
            score -= 60
        if errors:
            score = max(score, 20)

        return {
            "clause_type": "main",
            "v2_valid": v2_valid,
            "inversion_active": inversion_active,
            "subordinate_sov_valid": True,
            "separable_bracket": separable_bracket,
            "verb_position": first_verb_idx + 1 if first_verb_idx >= 0 else 0,
            "syntax_score": score,
            "errors": errors
        }
