"""
Persian Pragmatics & Ta'arof (تعارف) Engine
Evaluates socio-pragmatic deference, honorific verb substitutions, and epistolary formulas.
"""

from typing import Dict, Any, List, Optional

# Ta'arof verb transformation mappings
HONORIFIC_ELEVATING_MAP = {
    "گفتن": "فرمودن",
    "آمدن": "تشریف آوردن",
    "رفتن": "تشریف بردن",
    "دادن": "لطف کردن",
    "دانستن": "استحضار داشتن",
    "خواستن": "میل داشتن",
    "خوردن": "میل فرمودن"
}

HONORIFIC_SELF_LOWERING_MAP = {
    "گفتن": "عرض کردن",
    "آمدن": "خدمت رسیدن",
    "رفتن": "مرخص شدن",
    "دادن": "تقدیم کردن",
    "دانستن": "اطلاع داشتن",
    "خواستن": "قصد داشتن"
}

REGISTER_MARKERS = {
    "high_taarof": {
        "pronouns": ["جناب‌عالی", "سرکار", "بنده", "حقیر", "مخلص"],
        "verbs": ["فرمودید", "فرمودند", "عرض کردم", "تشریف آوردید", "استحضار دارید"],
        "salutations": ["جناب آقای دکتر", "ریاست محترم", "با سلام و تحیات وافره"],
        "closings": ["با تجدید احترام", "ارادتمند شما", "با سپاس و احترام فراوان"]
    },
    "formal": {
        "pronouns": ["شما", "ایشان", "ما"],
        "verbs": ["گفتید", "آمدید", "دادید", "می‌دانید"],
        "salutations": ["مدیریت محترم", "با سلام و احترام"],
        "closings": ["با آرزوی توفیق الهی", "با تشکر و احترام"]
    },
    "informal": {
        "pronouns": ["تو", "من"],
        "verbs": ["گفتی", "اومدی", "دادی", "می‌دونی"],
        "salutations": ["سلام دوست من", "سلام عزیز"],
        "closings": ["قربانت", "فدات", "به امید دیدار"]
    }
}

class PersianPragmaticsEngine:
    """
    Evaluates register deference, applies Ta'arof honorific shifts,
    and formats institutional correspondence.
    """

    def detect_register(self, text: str) -> Dict[str, Any]:
        """Detects whether text is High Ta'arof, Formal, or Informal."""
        scores = {"high_taarof": 0, "formal": 0, "informal": 0}
        
        for tier, data in REGISTER_MARKERS.items():
            for pron in data["pronouns"]:
                if pron in text:
                    scores[tier] += 2
            for v in data["verbs"]:
                if v in text:
                    scores[tier] += 2
            for s in data["salutations"]:
                if s in text:
                    scores[tier] += 3
            for c in data["closings"]:
                if c in text:
                    scores[tier] += 3
                    
        # Determine dominant tier
        sorted_tiers = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        dominant_tier = sorted_tiers[0][0] if sorted_tiers[0][1] > 0 else "formal"
        
        return {
            "dominant_register": dominant_tier,
            "scores": scores,
            "tier_level": 3 if dominant_tier == "high_taarof" else (2 if dominant_tier == "formal" else 1)
        }

    def elevate_verb_for_interlocutor(self, plain_verb_lemma: str) -> str:
        """Transforms a neutral verb into its other-elevating honorific counterpart."""
        return HONORIFIC_ELEVATING_MAP.get(plain_verb_lemma, plain_verb_lemma)

    def lower_verb_for_self(self, plain_verb_lemma: str) -> str:
        """Transforms a neutral verb into its self-lowering modest counterpart."""
        return HONORIFIC_SELF_LOWERING_MAP.get(plain_verb_lemma, plain_verb_lemma)

    def format_formal_letter(self, addressee: str, title: str, body: str, sender: str, is_high_taarof: bool = True) -> str:
        """Formats a standard Persian administrative letter adhering to epistolary conventions."""
        if is_high_taarof:
            salutation = f"جناب آقای {addressee}، {title} محترم؛\nبا سلام و احترام و آرزوی توفیق روزافزون،"
            closing = f"با تجدید احترام و سپاس بیکران،\n{sender}"
        else:
            salutation = f"همکار گرامی جناب {addressee}؛\nبا سلام و احترام،"
            closing = f"با تشکر و احترام،\n{sender}"
            
        return f"{salutation}\n\n{body.strip()}\n\n{closing}"
