"""
Italian Engine — Subjunctive Concord Analyzer
Audits presence of subjunctive triggers and verifies that subordinate verbs select
the subjunctive rather than indicative.
"""

from typing import Dict, Any, List
from ..skills.subjunctive_engine import detect_subjunctive_triggers
from ..skills.tokenization import tokenize_words

class SubjunctiveConcordAnalyzer:
    """Cognitive analyzer for Italian subordinate subjunctive mood selection."""

    def __init__(self):
        pass

    def analyze(self, text: str) -> Dict[str, Any]:
        trigger_info = detect_subjunctive_triggers(text)
        requires_sub = trigger_info["requires_subjunctive"]
        
        violations = []
        tokens = [t.lower() for t in tokenize_words(text)]
        
        # If text requires subjunctive, check if indicative was erroneously used after 'che'
        if requires_sub and "che" in tokens:
            idx = tokens.index("che")
            # Inspect next 1..3 words for verb
            sub_tokens = tokens[idx + 1:]
            for tok in sub_tokens:
                # Obvious indicative errors (e.g., 'che tu vieni' instead of 'che tu venga')
                if tok in {"vieni", "viene", "vanno", "va", "fai", "fa", "fanno", "sai", "sa", "puoi", "può"}:
                    violations.append({
                        "token": tok,
                        "rule": "subjunctive_mood_required",
                        "error": f"Verb '{tok}' is in the indicative mood after a volitional/doxastic trigger requiring the subjunctive."
                    })
                    break
                    
        return {
            "text": text,
            "requires_subjunctive": requires_sub,
            "triggers": trigger_info["triggers"],
            "violations": violations,
            "is_valid": len(violations) == 0
        }
