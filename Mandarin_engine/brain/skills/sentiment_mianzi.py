"""
Mandarin Mianzi (面子) Politeness and Pragmatic Sentiment Skill.
Evaluates deference levels, face protection, and indirect speech acts.
"""

from typing import Dict, Any, List

HONORIFIC_MARKERS = {"您", "贵姓", "请教", "拜托", "劳驾", "指点", "尊姓", "谨上", "此致敬礼"}
POLITE_MODIFIERS = {"请", "谢谢", "不好意思", "麻烦", "哪里哪里", "抱歉", "对不起"}
INDIRECT_REFUSALS = {"不太方便", "再考虑考虑", "再研究研究", "可能有点困难", "改天"}
CASUAL_COLLOQUIAL = {"哥们", "嗨", "喂", "咋样", "走起", "扯淡"}


class MianziPragmaticSkill:
    """
    Evaluator for Chinese communicative register, face preservation, and indirect refusal.
    """

    def evaluate_pragmatics(self, text: str) -> Dict[str, Any]:
        has_honorific = any(m in text for m in HONORIFIC_MARKERS)
        has_polite = any(m in text for m in POLITE_MODIFIERS)
        has_indirect_refusal = any(m in text for m in INDIRECT_REFUSALS)
        has_casual = any(m in text for m in CASUAL_COLLOQUIAL)

        # Compute Mianzi Politeness Index (0.0 to 1.0)
        score = 0.50
        if has_honorific:
            score += 0.35
        if has_polite:
            score += 0.15
        if has_indirect_refusal:
            score += 0.10  # Face-preserving indirectness
        if has_casual:
            score -= 0.20

        score = max(0.0, min(1.0, score))

        if score >= 0.80:
            tier = "High Deference / Formal Mianzi (典雅庄重 / 极尊敬)"
        elif score >= 0.55:
            tier = "Standard Polite / Business (得体礼貌)"
        elif score >= 0.35:
            tier = "Neutral / Descriptive (中性平实)"
        else:
            tier = "Casual / Informal (随意口语)"

        return {
            "mianzi_score": round(score, 4),
            "register_tier": tier,
            "has_honorific": has_honorific,
            "has_indirect_refusal": has_indirect_refusal,
            "face_preservation": "High" if score >= 0.70 else ("Moderate" if score >= 0.40 else "Low"),
        }

    def evaluate_mianzi(self, text: str) -> Dict[str, Any]:
        """
        Evaluates politeness, face preservation, and indirect refusals.
        """
        res = self.evaluate_pragmatics(text)
        politeness = "High" if res["mianzi_score"] >= 0.80 else ("Polite" if res["mianzi_score"] >= 0.55 else "Neutral")
        return {
            "mianzi_score": res["mianzi_score"],
            "politeness_level": politeness,
            "register_tier": res["register_tier"],
            "has_honorific": res["has_honorific"],
            "has_indirect_refusal": res["has_indirect_refusal"],
            "face_preservation_score": res["mianzi_score"],
            "face_preservation": res["face_preservation"],
        }
