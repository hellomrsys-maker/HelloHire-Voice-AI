"""
Vietnamese Pragmatics & Epistolary Engine
Evaluates politeness particles (ạ, dạ), register tiers, and formats official correspondence.
"""

from typing import Dict, Any, List, Optional

REGISTER_INDICATORS = {
    "high_formal": {
        "salutations": ["kính gửi", "kính thưa", "đồng chí", "quý công ty"],
        "closings": ["trân trọng cảm ơn", "trân trọng kính chào", "kính chúc"],
        "particles": ["ạ", "kính mong"]
    },
    "formal": {
        "salutations": ["chào anh", "chào chị", "thưa quý khách"],
        "closings": ["trân trọng", "cảm ơn bạn"],
        "particles": ["vâng", "dạ"]
    },
    "informal": {
        "salutations": ["alo", "ê", "chào mày", "chào cậu"],
        "closings": ["gặp lại sau nhé", "bye nhé"],
        "particles": ["nhé", "nha", "hả", "cơ", "á"]
    }
}

class VietnamesePragmaticsEngine:
    """
    Evaluates register, detects deference particles (ạ), and formats formal correspondence.
    """

    def detect_register(self, text: str) -> Dict[str, Any]:
        """Detects whether text is High Formal, Formal, or Informal."""
        lower = text.lower()
        scores = {"high_formal": 0, "formal": 0, "informal": 0}
        
        clean_tokens = [t.strip(',.?!;:«»"—"') for t in lower.split()]
        clean_tokens = [t for t in clean_tokens if t]

        for tier, data in REGISTER_INDICATORS.items():
            for s in data["salutations"]:
                if s in lower:
                    scores[tier] += 3
            for c in data["closings"]:
                if c in lower:
                    scores[tier] += 3
            for p in data["particles"]:
                if p in clean_tokens:
                    scores[tier] += 2

        sorted_tiers = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        dominant = sorted_tiers[0][0] if sorted_tiers[0][1] > 0 else "formal"
        
        tier_level = 3 if dominant == "high_formal" else (2 if dominant == "formal" else 1)
        return {
            "dominant_register": dominant,
            "scores": scores,
            "tier_level": tier_level
        }

    def audit_politeness_particle(self, text: str, is_senior_addressee: bool = False) -> Dict[str, Any]:
        """
        Audits the presence of the mandatory deference particle 'ạ'
        when communicating with seniors or superiors.
        """
        raw_tokens = text.lower().split()
        tokens = [t.strip(',.?!;:«»"—"') for t in raw_tokens]
        tokens = [t for t in tokens if t]
        has_a = "ạ" in tokens or any(t.endswith("ạ") for t in tokens)
        has_da = "dạ" in tokens
        has_vang = "vâng" in tokens
        
        is_polite = has_a or has_da or has_vang
        needs_polite_flag = is_senior_addressee and not has_a
        
        return {
            "has_particle_a": has_a,
            "has_particle_da": has_da,
            "has_particle_vang": has_vang,
            "is_polite": is_polite,
            "missing_mandatory_a": needs_polite_flag
        }

    def format_formal_letter(
        self,
        recipient_name: str,
        recipient_title: str,
        body: str,
        sender_name: str
    ) -> str:
        """
        Synthesizes an official administrative Vietnamese letter.
        """
        salutation = f"Kính gửi: {recipient_title} {recipient_name},"
        closing = f"Trân trọng,\n{sender_name}"
        return f"{salutation}\n\n{body.strip()}\n\n{closing}"
