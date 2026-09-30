"""
Japanese Keigo Rewriter Task Pipeline
=====================================
Transforms input Japanese sentences across honorific tiers:
- Plain (常体 / 辞書形)
- Polite (丁寧語 / です・ます)
- Respectful (尊敬語 / 目上を立てる)
- Humble (謙譲語 / 自己をへりくだる)
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from Japanese_engine.brain.skills.keigo_engine import JapaneseKeigoEngine


@dataclass
class KeigoRewriteResult:
    source_sentence: str
    target_tier: str
    rewritten_sentence: str
    transformations_applied: List[str] = field(default_factory=list)


class JapaneseKeigoRewriter:
    """
    Sentence-level rewriter converting predicates and nominal arguments across Keigo registers.
    """

    def __init__(self) -> None:
        self.keigo_engine = JapaneseKeigoEngine()

    def rewrite_to_tier(self, sentence: str, target_tier: str) -> KeigoRewriteResult:
        """
        target_tier: 'sonkeigo', 'kenjougo', 'teineigo', 'plain'
        """
        res = sentence
        applied = []

        if target_tier == "sonkeigo":
            conversions = [
                ("言いました", "おっしゃいました"),
                ("言います", "おっしゃいます"),
                ("食べた", "召し上がった"),
                ("食べました", "召し上がりました"),
                ("行きました", "いらっしゃいました"),
                ("来ました", "お見えになりました"),
                ("見ました", "ご覧になりました"),
                ("知っています", "ご存じです"),
                ("しました", "なさいました"),
            ]
            for src, dst in conversions:
                if src in res:
                    res = res.replace(src, dst)
                    applied.append(f"{src} -> {dst} (Sonkeigo)")

        elif target_tier == "kenjougo":
            conversions = [
                ("言いました", "申し上げました"),
                ("言います", "申し上げます"),
                ("食べた", "いただきました"),
                ("食べました", "いただきました"),
                ("行きました", "参りました"),
                ("来ました", "参りました"),
                ("見ました", "拝見いたしました"),
                ("知っています", "存じております"),
                ("しました", "いたしました"),
            ]
            for src, dst in conversions:
                if src in res:
                    res = res.replace(src, dst)
                    applied.append(f"{src} -> {dst} (Kenjougo)")

        elif target_tier == "teineigo":
            conversions = [
                ("だ。", "です。"),
                ("である。", "です。"),
                ("食べる。", "食べます。"),
                ("食べた。", "食べました。"),
                ("行く。", "行きます。"),
                ("行った。", "行きました。"),
                ("言う。", "言います。"),
                ("言った。", "言いました。"),
            ]
            for src, dst in conversions:
                if src in res:
                    res = res.replace(src, dst)
                    applied.append(f"{src} -> {dst} (Teineigo)")

        elif target_tier == "plain":
            conversions = [
                ("です。", "だ。"),
                ("でございます。", "だ。"),
                ("食べます。", "食べる。"),
                ("食べました。", "食べた。"),
                ("行きます。", "行く。"),
                ("行きました。", "行った。"),
                ("言います。", "言う。"),
                ("言いました。", "言った。"),
                ("いたします。", "する。"),
                ("参ります。", "行く。"),
            ]
            for src, dst in conversions:
                if src in res:
                    res = res.replace(src, dst)
                    applied.append(f"{src} -> {dst} (Plain)")

        return KeigoRewriteResult(
            source_sentence=sentence,
            target_tier=target_tier,
            rewritten_sentence=res,
            transformations_applied=applied,
        )
