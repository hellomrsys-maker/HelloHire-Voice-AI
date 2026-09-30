"""
German Engine — Modal Particle Engine Skill
Analyzes and interprets German Abtönungspartikeln (ja, doch, mal, denn, eben, halt, wohl, schon).
"""

from typing import List, Dict, Any

MODAL_PARTICLES_INFO = {
    "ja": {
        "gloss": "as you know / obviously",
        "category": "shared_knowledge",
        "pragmatic_effect": "appeals to shared background knowledge or unsurprising consensus"
    },
    "doch": {
        "gloss": "contrary to expectation / surely / please do",
        "category": "corrective_appeal",
        "pragmatic_effect": "reminds interlocutor of a neglected fact or insists on compliance"
    },
    "mal": {
        "gloss": "briefly / just",
        "category": "softener",
        "pragmatic_effect": "downplays imposition, makes imperatives conversational and polite"
    },
    "denn": {
        "gloss": "then / on earth",
        "category": "interest_intensifier",
        "pragmatic_effect": "conveys genuine personal engagement or mild skepticism in questions"
    },
    "eben": {
        "gloss": "simply / that's how it is",
        "category": "inevitability",
        "pragmatic_effect": "expresses rational acceptance of an unalterable situation"
    },
    "halt": {
        "gloss": "just / like",
        "category": "colloquial_inevitability",
        "pragmatic_effect": "colloquial variant of eben, signals pragmatic resignation"
    },
    "wohl": {
        "gloss": "probably / presumably",
        "category": "epistemic_conjecture",
        "pragmatic_effect": "modulates truth claim to high probability without complete certainty"
    },
    "schon": {
        "gloss": "all right / surely / concededly",
        "category": "reassurance_concession",
        "pragmatic_effect": "offers soothing reassurance or grants an opponent's point conceded"
    },
    "bloß": {
        "gloss": "whatever you do / only",
        "category": "warning_injunction",
        "pragmatic_effect": "strengthens negative command or expresses intense bewilderment"
    }
}

def analyze_modal_particles(tokens: List[str]) -> Dict[str, Any]:
    """
    Detect and classify modal particles in a German sentence.
    Modal particles occur predominantly in the Mittelfeld (not first token, not last token).
    """
    detected = []
    
    for i, token in enumerate(tokens):
        lower = token.lower()
        # In general, particles cannot occupy Vorfeld (index 0) or sentence terminal
        if i > 0 and i < len(tokens) - 1 and lower in MODAL_PARTICLES_INFO:
            info = MODAL_PARTICLES_INFO[lower]
            detected.append({
                "particle": lower,
                "position": i,
                "category": info["category"],
                "gloss": info["gloss"],
                "pragmatic_effect": info["pragmatic_effect"]
            })
            
    return {
        "particle_count": len(detected),
        "particles": detected,
        "has_pragmatic_coloring": len(detected) > 0
    }
