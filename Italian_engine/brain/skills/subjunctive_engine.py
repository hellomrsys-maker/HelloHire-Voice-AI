"""
Italian Engine — Subjunctive Engine Skill
Identifies volitional, doxastic, and conjunctional triggers mandating the Subjunctive mood (Congiuntivo).
"""

from typing import Dict, Any, List

# Main verbs of belief, volition, emotion, doubt that trigger subjunctive
SUBJUNCTIVE_VERB_TRIGGERS = {
    "voglio", "vuole", "vogliamo", "vorrei", "volere",
    "credo", "crede", "crediamo", "credere",
    "penso", "pensa", "pensiamo", "pensare",
    "spero", "spera", "speriamo", "sperare",
    "dubito", "dubita", "dubitare",
    "temo", "teme", "temere",
    "desidero", "desidera", "desiderare",
    "preferisco", "preferisce", "preferire"
}

# Impersonal triggers: è necessario che, bisogna che, sembra che
IMPERSONAL_TRIGGERS = {
    "è necessario", "è importante", "è probabile", "è possibile",
    "è facile", "è difficile", "bisogna", "sembra", "pare", "si dice"
}

# Subordinating conjunctions that require subjunctive
SUBJUNCTIVE_CONJUNCTIONS = {
    "benché", "sebbene", "quantunque", "affinché", "purché",
    "a patto che", "a meno che", "senza che", "prima che", "nel caso in cui"
}

def detect_subjunctive_triggers(sentence: str) -> Dict[str, Any]:
    """Scan text for triggers obligatorily requiring the subjunctive mood."""
    s_clean = sentence.lower().strip()
    triggers_found = []
    
    for conj in SUBJUNCTIVE_CONJUNCTIONS:
        if conj in s_clean:
            triggers_found.append({"type": "conjunction", "trigger": conj})
            
    for imp in IMPERSONAL_TRIGGERS:
        if imp in s_clean and " che" in s_clean:
            triggers_found.append({"type": "impersonal", "trigger": imp})
            
    for v in SUBJUNCTIVE_VERB_TRIGGERS:
        pattern = f"{v} che"
        if pattern in s_clean or f"{v} " in s_clean and " che" in s_clean:
            triggers_found.append({"type": "volitional_doxastic", "trigger": v})
            
    return {
        "requires_subjunctive": len(triggers_found) > 0,
        "triggers": triggers_found
    }
