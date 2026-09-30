"""
Japanese Register Rewriter Pipeline
===================================
Rewrites Japanese text across register spectra:
- Casual / Colloquial (親密口語・タメ口)
- Polite Standard (日常丁寧体: です・ます)
- Business Keigo (ビジネス敬語: 謙譲語・尊敬語・美化語)
- Academic / Thesis (論文体: だ・である)
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from Japanese_engine.brain.skills.tokenization import JapaneseTokenizer
from Japanese_engine.brain.rules.rules_engine import JapaneseRulesEngine


@dataclass
class JapaneseRewriteResult:
    source_text: str
    target_register: str
    rewritten_text: str
    replacements_made: List[Dict[str, str]]
    success: bool


class JapaneseRegisterRewriter:
    """
    Transforms text across register styles while preserving core semantic propositional content.
    """

    def __init__(self) -> None:
        self.rules_engine = JapaneseRulesEngine()

    def rewrite(self, text: str, target_register: str) -> JapaneseRewriteResult:
        """
        target_register: 'casual', 'polite', 'business_keigo', 'academic'
        """
        replacements = []
        res = text

        if target_register == "polite":  # to です・ます
            transformations = [
                ("である", "です"),
                ("だ。", "です。"),
                ("だ\n", "です\n"),
                ("する。", "します。"),
                ("した。", "しました。"),
                ("食べる。", "食べます。"),
                ("食べた。", "食べました。"),
                ("行く。", "行きます。"),
                ("行った。", "行きました。"),
                ("ない。", "ありません。"),
                ("なかった。", "ありませんでした。"),
            ]
            for src, dst in transformations:
                if src in res:
                    res = res.replace(src, dst)
                    replacements.append({"from": src, "to": dst})

        elif target_register == "business_keigo":  # to ビジネス敬語 (謙譲・丁寧)
            transformations = [
                ("します。", "いたします。"),
                ("しました。", "いたしました。"),
                ("です。", "でございます。"),
                ("行きます。", "参ります。"),
                ("行きました。", "参りました。"),
                ("見ます。", "拝見します。"),
                ("見ました。", "拝見いたしました。"),
                ("言います。", "申し上げます。"),
                ("言いました。", "申し上げました。"),
                ("知っています。", "存じております。"),
                ("知っていますか。", "ご存じでしょうか。"),
            ]
            for src, dst in transformations:
                if src in res:
                    res = res.replace(src, dst)
                    replacements.append({"from": src, "to": dst})

        elif target_register == "academic":  # to だ・である
            transformations = [
                ("でございます。", "である。"),
                ("です。", "である。"),
                ("でした。", "であった。"),
                ("します。", "する。"),
                ("しました。", "した。"),
                ("行きます。", "行く。"),
                ("行きました。", "行った。"),
                ("食べます。", "食べる。"),
                ("食べました。", "食べた。"),
                ("ありません。", "ない。"),
                ("ありませんでした。", "なかった。"),
            ]
            for src, dst in transformations:
                if src in res:
                    res = res.replace(src, dst)
                    replacements.append({"from": src, "to": dst})

        elif target_register == "casual":  # to 親密タメ口
            transformations = [
                ("でございます。", "だよ。"),
                ("です。", "だよ。"),
                ("でした。", "だったよ。"),
                ("します。", "するよ。"),
                ("しました。", "したよ。"),
                ("行きます。", "行くよ。"),
                ("行きました。", "行ったよ。"),
                ("食べます。", "食べるよ。"),
                ("食べました。", "食べたよ。"),
            ]
            for src, dst in transformations:
                if src in res:
                    res = res.replace(src, dst)
                    replacements.append({"from": src, "to": dst})

        return JapaneseRewriteResult(
            source_text=text,
            target_register=target_register,
            rewritten_text=res,
            replacements_made=replacements,
            success=len(replacements) > 0 or res == text,
        )
