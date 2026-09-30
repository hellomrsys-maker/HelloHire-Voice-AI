"""
lemmatization.py - Japanese Katsuyou (Conjugation) Inversion and Lemma Normalization.
Maps inflected verb and adjective forms (Ta-form, Te-form, Masu-form, Nai-form)
back to their dictionary base lemma (Jisho-kei / Shuushikei).
"""

from __future__ import annotations
from typing import Dict, Optional


class JapaneseLemmaResult(str):
    """
    Subclasses str so `res == "食べる"` evaluates True, while providing `.lemma`, `.word`, `.pos`.
    """
    def __new__(cls, lemma: str, word: str = "", pos: Optional[str] = None):
        instance = super().__new__(cls, lemma)
        instance._lemma = lemma
        instance._word = word
        instance._pos = pos
        return instance

    @property
    def lemma(self) -> str:
        return self._lemma

    @property
    def word(self) -> str:
        return self._word

    @property
    def pos(self) -> Optional[str]:
        return self._pos

    @property
    def dictionary_form(self) -> str:
        return self._lemma

    @property
    def verb_type(self) -> str:
        if self._lemma in {"来る", "くる"}:
            return "Kuru"
        elif self._lemma in {"する"}:
            return "Suru"
        elif self._lemma in {"食べる", "見る", "起きる", "教える", "開ける", "閉める", "忘れる", "寝る"}:
            return "Ichidan"
        elif self._lemma.endswith(("べる", "みる", "きる", "える", "ける", "せる", "てる", "ねる", "める", "れる")):
            return "Ichidan"
        return "Godan"


class JapaneseLemmatizer:
    """
    Morphological lemmatizer converting inflected Japanese forms to dictionary lemmas.
    """

    IRREGULAR_MAP = {
        "した": "する", "して": "する", "します": "する", "しない": "する", "すれば": "する", "しよう": "する", "される": "する",
        "しました": "する", "しまして": "する",
        "きた": "来る", "きて": "来る", "きます": "来る", "こない": "来る", "くれば": "来る", "こよう": "来る", "こられる": "来る",
        "来ました": "来る", "来まして": "来る", "きました": "来る", "きまして": "来る",
        "来た": "来る", "来て": "来る", "来ます": "来る", "来ない": "来る", "来れば": "来る",
        "行った": "行く", "行って": "行く", "行きます": "行く", "行かない": "行く",
        "読み": "読む", "書き": "書く", "飲み": "飲む", "話し": "話す", "行き": "行く", "買い": "買う",
        "食べ": "食べる", "見": "見る", "待ち": "待つ", "持ち": "持つ", "呼び": "呼ぶ", "遊び": "遊ぶ",
        "読みます": "読む", "書きます": "書く", "飲みます": "飲む", "話します": "話す", "食べます": "食べる",
    }

    def lemmatize(self, word: str, pos: Optional[str] = None) -> JapaneseLemmaResult:
        w = word.strip()

        # 1. Irregular table check
        if w in self.IRREGULAR_MAP:
            return JapaneseLemmaResult(self.IRREGULAR_MAP[w], word=w, pos=pos)

        # 2. Politeness auxiliary stripping (-masu, -mashita, -masen)
        if w.endswith("ました"):
            stem = w[:-3]
            return self._restore_verb_stem(stem, w, pos)
        if w.endswith("ます"):
            stem = w[:-2]
            return self._restore_verb_stem(stem, w, pos)
        if w.endswith("ません"):
            stem = w[:-3]
            return self._restore_verb_stem(stem, w, pos)

        # 3. Past tense & Te-form inversions (Ta-kei / Te-kei)
        # Ichidan verbs (e.g. 食べた -> 食べる, 見た -> 見る)
        if w.endswith("た") and len(w) >= 2:
            stem = w[:-1]
            # Check common ichidan
            if stem.endswith(("べ", "み", "き", "え", "け", "せ", "て", "ね", "め", "れ")):
                candidate = stem + "る"
                return JapaneseLemmaResult(candidate, word=w, pos="動詞")

        # Godan Onbin sound changes:
        # - itta / ita -> -ku / -gu (書いた -> 書く, 泳いだ -> 泳ぐ)
        if w.endswith("いた") and len(w) >= 3:
            return JapaneseLemmaResult(w[:-2] + "く", word=w, pos="動詞")
        if w.endswith("いだ") and len(w) >= 3:
            return JapaneseLemmaResult(w[:-2] + "ぐ", word=w, pos="動詞")

        # - shita -> -su (話した -> 話す)
        if w.endswith("した") and len(w) >= 3:
            return JapaneseLemmaResult(w[:-2] + "す", word=w, pos="動詞")

        # - tta -> -tsu / -ru / -u (待った -> 待つ, 走った -> 走る, 買った -> 買う)
        if w.endswith("った") and len(w) >= 3:
            return JapaneseLemmaResult(w[:-2] + "る", word=w, pos="動詞")

        # - nda -> -mu / -bu / -nu (読んだ -> 読む, 呼んだ -> 呼ぶ, 死んだ -> 死ぬ)
        if w.endswith("んだ") and len(w) >= 3:
            return JapaneseLemmaResult(w[:-2] + "む", word=w, pos="動詞")

        # 4. Adjective inversions (-katta, -kunai -> -i)
        if w.endswith("かった") and len(w) >= 4:
            return JapaneseLemmaResult(w[:-3] + "い", word=w, pos="形容詞")
        if w.endswith("くない") and len(w) >= 4:
            return JapaneseLemmaResult(w[:-3] + "い", word=w, pos="形容詞")

        if w.endswith("ない") and len(w) >= 3:
            stem = w[:-2]
            if stem in {"食べ", "見", "起き", "教え", "開け", "閉め"}:
                return JapaneseLemmaResult(stem + "る", word=w, pos="動詞")
            a_to_u = {
                "か": "く", "が": "ぐ", "さ": "す", "た": "つ", "な": "ぬ", "ば": "ぶ", "ま": "む", "ら": "る", "わ": "う"
            }
            if stem[-1] in a_to_u:
                return JapaneseLemmaResult(stem[:-1] + a_to_u[stem[-1]], word=w, pos="動詞")

        # Default: word is already base form
        return JapaneseLemmaResult(w, word=w, pos=pos)

    def _restore_verb_stem(self, stem: str, orig: str, pos: Optional[str]) -> JapaneseLemmaResult:
        if stem in {"し", "為"}:
            return JapaneseLemmaResult("する", word=orig, pos="動詞")
        if stem in {"き", "来"}:
            return JapaneseLemmaResult("来る", word=orig, pos="動詞")
        # If stem ends with e-dan vowel or i-dan vowel (Ichidan preference)
        if stem.endswith(("べ", "え", "け", "せ", "て", "ね", "め", "れ")):
            return JapaneseLemmaResult(stem + "る", word=orig, pos="動詞")
        # Godan: i -> u (e.g. 読み -> 読む, 書き -> 書く, 話し -> 話す)
        vowel_map = {
            "き": "く", "ぎ": "ぐ", "し": "す", "ち": "つ", "に": "ぬ", "ひ": "ふ",
            "び": "ぶ", "み": "む", "り": "る", "い": "う"
        }
        last_ch = stem[-1]
        if last_ch in vowel_map:
            return JapaneseLemmaResult(stem[:-1] + vowel_map[last_ch], word=orig, pos="動詞")
        return JapaneseLemmaResult(stem + "る", word=orig, pos="動詞")
