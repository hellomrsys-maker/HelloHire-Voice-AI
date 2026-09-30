"""
Japanese Keigo Engine (Honorific Transformation System)
=======================================================
Bidirectional transformation across Sonkeigo (尊敬語), Kenjougo (謙譲語),
and Teineigo (丁寧語) for verbs, copulas, and prefixation (お・ご).
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple


@dataclass
class KeigoFormSet:
    dictionary_form: str
    sonkeigo: List[str]   # Respectful (subject is superior)
    kenjougo: List[str]   # Humble (subject is self/in-group)
    teineigo: List[str]   # Polite (desu/masu)


@dataclass
class KeigoTransformationResult:
    original_phrase: str
    transformed_phrase: str
    target_type: str  # "sonkeigo", "kenjougo", "teineigo", "plain"
    verb_root: str
    rule_applied: str


class JapaneseKeigoEngine:
    """
    Transforms Japanese predicates and nouns across social registers and honorific axes.
    """

    def __init__(self) -> None:
        # Suppletive irregular honorific verb dictionary
        self.verb_tables: Dict[str, KeigoFormSet] = {
            "行く": KeigoFormSet("行く", ["いらっしゃる", "おいでになる"], ["伺う", "参る"], ["行きます"]),
            "来る": KeigoFormSet("来る", ["いらっしゃる", "おいでになる", "お見えになる"], ["伺う", "参る"], ["来ます"]),
            "いる": KeigoFormSet("いる", ["いらっしゃる", "おいでになる"], ["おる"], ["います"]),
            "食べる": KeigoFormSet("食べる", ["召し上がる"], ["いただく", "頂戴する"], ["食べます"]),
            "飲む": KeigoFormSet("飲む", ["召し上がる"], ["いただく"], ["飲みます"]),
            "言う": KeigoFormSet("言う", ["おっしゃる"], ["申す", "申し上げる"], ["言います"]),
            "する": KeigoFormSet("する", ["なさる", "される"], ["いたす"], ["します"]),
            "見る": KeigoFormSet("見る", ["ご覧になる"], ["拝見する"], ["見ます"]),
            "聞く": KeigoFormSet("聞く", ["お聞きになる"], ["伺う", "拝聴する"], ["聞きます"]),
            "知る": KeigoFormSet("知る", ["ご存じだ", "ご存知です"], ["存じる", "存じ上げる"], ["知っています"]),
            "会う": KeigoFormSet("会う", ["お会いになる"], ["お目にかかる"], ["会います"]),
            "与える": KeigoFormSet("与える", ["くださる"], ["差し上げる"], ["与えます"]),
            "もらう": KeigoFormSet("もらう", ["お受け取りになる"], ["いただく", "頂戴する"], ["もらいます"]),
        }

    def transform_verb(self, verb: str, target_keigo: str) -> KeigoTransformationResult:
        """
        Transforms a verb into target keigo type:
        target_keigo: 'sonkeigo', 'kenjougo', 'teineigo', 'plain'
        """
        # Normalize verb dictionary form
        dict_verb = verb
        for base, fset in self.verb_tables.items():
            if verb in [base] + fset.sonkeigo + fset.kenjougo + fset.teineigo:
                dict_verb = base
                break

        if dict_verb in self.verb_tables:
            fset = self.verb_tables[dict_verb]
            if target_keigo == "sonkeigo":
                res = fset.sonkeigo[0]
                rule = "Suppletive Sonkeigo (Special honorific verb)"
            elif target_keigo == "kenjougo":
                res = fset.kenjougo[0]
                rule = "Suppletive Kenjougo (Special humble verb)"
            elif target_keigo == "teineigo":
                res = fset.teineigo[0]
                rule = "Teineigo (Masu-form suffixation)"
            else:  # plain
                res = fset.dictionary_form
                rule = "Dictionary / Plain Jisho-kei"

            return KeigoTransformationResult(
                original_phrase=verb,
                transformed_phrase=res,
                target_type=target_keigo,
                verb_root=dict_verb,
                rule_applied=rule,
            )

        # Regular rule-based transformation (お + 連用形 + になる / お + 連用形 + する)
        # e.g., 待つ -> お待ちになる (sonkeigo), お待ちする (kenjougo)
        renyou = verb[:-1] + "い" if verb.endswith("く") else verb[:-1] + "ち" if verb.endswith("つ") else verb[:-1]
        if target_keigo == "sonkeigo":
            res = f"お{renyou}になる"
            rule = "Regular Sonkeigo (お + 連用形 + になる)"
        elif target_keigo == "kenjougo":
            res = f"お{renyou}する"
            rule = "Regular Kenjougo (お + 連用形 + する)"
        elif target_keigo == "teineigo":
            res = f"{renyou}ます"
            rule = "Regular Teineigo (連用形 + ます)"
        else:
            res = verb
            rule = "Identity plain form"

        return KeigoTransformationResult(
            original_phrase=verb,
            transformed_phrase=res,
            target_type=target_keigo,
            verb_root=verb,
            rule_applied=rule,
        )

    def beautify_noun(self, noun: str) -> str:
        """Applies Bikago (美化語) prefixes お / ご according to Yamato-kotoba or Kango origin."""
        kango_words = {"家族", "住所", "意見", "連絡", "返信", "案内", "予定", "挨拶"}
        if noun in kango_words:
            return f"ご{noun}"
        return f"お{noun}"
