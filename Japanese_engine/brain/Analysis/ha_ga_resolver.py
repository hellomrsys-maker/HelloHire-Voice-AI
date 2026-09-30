"""
Japanese Topic vs Subject (は vs が) Semantic Disambiguation Engine
===================================================================
Resolves the foundational Japanese discourse distinction between
Discourse Topic / Contrast ('は' wa) and Neutral Description / Exhaustive Listing ('が' ga).
Based on Susumu Kuno's Functional Syntax and Akira Mikami's Topic Grammar.
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from Japanese_engine.brain.skills.tokenization import JapaneseTokenizer


@dataclass
class HaGaAnalysisResult:
    target_phrase: str
    particle: str  # "は" or "が"
    semantic_function: str  # "Discourse_Topic", "Contrastive_Focus", "Neutral_Description", "Exhaustive_Listing", "Stative_Object", "Subordinate_Subject"
    information_status: str  # "Known_Information (旧情報)", "New_Information (新情報)"
    confidence: float
    explanation: str


class JapaneseHaGaResolver:
    """
    Disambiguates semantic and pragmatic functions of 'は' and 'が' in Japanese discourse.
    """

    def __init__(self) -> None:
        self.tokenizer = JapaneseTokenizer()

    def resolve(self, sentence: str, target_word: Optional[str] = None) -> List[HaGaAnalysisResult]:
        results: List[HaGaAnalysisResult] = []

        # Find occurrences of は and が via token boundaries
        tokens = self.tokenizer.tokenize(sentence)
        for i, tok in enumerate(tokens):
            if tok.text in {"は", "が"} and i > 0:
                noun = tokens[i - 1].text
                particle = tok.text

                if target_word and noun != target_word:
                    continue

                # Context after particle
                after = sentence[tok.char_end:]

                if particle == "は":
                    # Check for contrastive markers or multiple は
                    has_second_wa = "は" in after
                    if has_second_wa or any(c in after for c in ["けど", "が、", "一方で"]):
                        func = "Contrastive_Focus (対比)"
                        info = "Contrastive / Marked"
                        conf = 0.88
                        exp = f"『{noun}は』は後続文節との対比（コントラスト）を表しています。"
                    else:
                        func = "Discourse_Topic (題目・主題)"
                        info = "Known_Information (旧情報)"
                        conf = 0.92
                        exp = f"『{noun}は』は文の主題（テーマ）を提示し、既知情報として後続の陳述の枠組みを設定しています。"

                else:  # が
                    # 1. Stative predicates (分かる, 好き, 欲しい, 読める, 痛い)
                    stative_predicates = ["分かる", "わかる", "好き", "きらい", "嫌い", "欲しい", "ほしい", "できる", "痛い", "読める", "飲みたい"]
                    if any(sp in after for sp in stative_predicates):
                        func = "Stative_Object (対象語)"
                        info = "Target of psychological/ability state"
                        conf = 0.95
                        exp = f"『{noun}が』は状態性述語（感情・能力・希望）が要求する対象格を表しています。"

                    # 2. Subordinate clause (followed by a relative noun or conjunctive particle before main predicate)
                    elif re.search(r"[^\s、。]+(本|人|時|こと|もの|場所|ので|から|とき|前|後)", after):
                        func = "Subordinate_Subject (従属節内の主語)"
                        info = "Embedded Subject"
                        conf = 0.90
                        exp = f"『{noun}が』は従属節または連体修飾節内部の統語的主語を担っています。"

                    # 3. Interrogative pronoun as subject (誰が, 何が, どこが) -> Exhaustive listing
                    elif noun in ["誰", "だれ", "何", "なに", "どこ", "どれ"]:
                        func = "Exhaustive_Listing (総記)"
                        info = "New_Information (新情報) - Focus"
                        conf = 0.98
                        exp = f"疑問詞『{noun}』が主語となる場合、常に新情報の焦点を表す『総記のが』となります。"

                    # 4. Neutral description of immediate phenomena (雨が降っている, 花が咲いた)
                    else:
                        func = "Neutral_Description (現象描写)"
                        info = "New_Information (新情報) - Event observation"
                        conf = 0.85
                        exp = f"『{noun}が』は目の前の知覚事象をそのまま述べる現象描写文の主語を表しています。"

                results.append(
                    HaGaAnalysisResult(
                        target_phrase=f"{noun}{particle}",
                        particle=particle,
                        semantic_function=func,
                        information_status=info,
                        confidence=conf,
                        explanation=exp,
                    )
                )

        return results
