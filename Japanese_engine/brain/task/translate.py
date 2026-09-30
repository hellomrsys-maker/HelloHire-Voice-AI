"""
Japanese Cross-Lingual Translation Engine
=========================================
Typological transfer between Japanese (head-final SOV) and English / European languages (head-initial SVO).
Handles particle case-frame mapping, verbal morphology inflection, and constituent reordering.
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from Japanese_engine.brain.skills.tokenization import JapaneseTokenizer
from Japanese_engine.brain.skills.pos_tagging import JapanesePOSTagger
from Japanese_engine.brain.skills.lemmatization import JapaneseLemmatizer


@dataclass
class JapaneseTranslationResult:
    source_text: str
    target_language: str
    translated_text: str
    structural_alignment: str  # e.g., "SOV -> SVO" or "SVO -> SOV"
    lexical_alignments: List[Dict[str, str]]
    confidence: float


class JapaneseCrossLingualTranslator:
    """
    Translates Japanese sentences to English (SOV -> SVO) and English to Japanese (SVO -> SOV).
    """

    def __init__(self) -> None:
        self.tokenizer = JapaneseTokenizer()
        self.pos_tagger = JapanesePOSTagger()
        self.lemmatizer = JapaneseLemmatizer()

        # Japanese to English lexicon mapping
        self.ja_en_lexicon: Dict[str, str] = {
            "私": "I", "彼": "he", "彼女": "she", "学生": "student", "先生": "teacher",
            "本": "book", "水": "water", "リンゴ": "apple", "車": "car", "猫": "cat",
            "犬": "dog", "東京": "Tokyo", "学校": "school", "友達": "friend",
            "読む": "read", "書く": "write", "飲む": "drink", "食べる": "eat", "見る": "see",
            "買う": "buy", "行く": "go", "来る": "come", "勉強する": "study",
            "新しい": "new", "良い": "good", "大きい": "big", "美しい": "beautiful",
            "です": "is", "だ": "is", "である": "is",
        }

        # English to Japanese lexicon mapping
        self.en_ja_lexicon: Dict[str, str] = {
            "i": "私", "he": "彼", "she": "彼女", "student": "学生", "teacher": "先生",
            "book": "本", "water": "水", "apple": "リンゴ", "car": "車", "cat": "猫",
            "dog": "犬", "tokyo": "東京", "school": "学校", "friend": "友達",
            "read": "読む", "reads": "読む", "write": "書く", "writes": "書く",
            "drink": "飲む", "drinks": "飲む", "eat": "食べる", "eats": "食べる",
            "see": "見る", "sees": "見る", "buy": "買う", "buys": "買う",
            "go": "行く", "goes": "行く", "new": "新しい", "good": "良い",
            "is": "です", "are": "です", "the": "", "a": "", "an": "",
        }

    def translate(self, text: str, target_lang: str = "en") -> JapaneseTranslationResult:
        if target_lang == "en":
            return self._translate_ja_to_en(text)
        elif target_lang in {"ja", "jp"}:
            return self._translate_en_to_ja(text)
        else:
            return self._translate_ja_to_en(text)

    def _translate_ja_to_en(self, text: str) -> JapaneseTranslationResult:
        tokens = self.tokenizer.tokenize(text)
        tagged = self.pos_tagger.tag_tokens(tokens)

        # Identify syntactic roles via case particles
        # Identify syntactic roles via case particles from tokens
        subject = ""
        direct_obj = ""
        predicate = ""
        alignments: List[Dict[str, str]] = []

        for i, tok in enumerate(tokens):
            if tok.text in {"は", "が"} and i > 0:
                subj_raw = tokens[i - 1].text
                subject = self.ja_en_lexicon.get(subj_raw, subj_raw)
                alignments.append({"ja": subj_raw, "en": subject, "role": "Subject"})
            elif tok.text == "を" and i > 0:
                obj_raw = tokens[i - 1].text
                direct_obj = self.ja_en_lexicon.get(obj_raw, obj_raw)
                alignments.append({"ja": obj_raw, "en": direct_obj, "role": "DirectObject"})

        for t in reversed(tagged):
            t_str = t.token.text
            lemma = self.lemmatizer.lemmatize(t_str).dictionary_form
            cand_keys = [t_str, lemma]
            matched_en = None
            for k in cand_keys:
                if k in self.ja_en_lexicon and self.ja_en_lexicon[k] not in {"is", "I", "book", "student", "Tokyo"}:
                    matched_en = self.ja_en_lexicon[k]
                    break
            if matched_en:
                predicate = matched_en
                alignments.append({"ja": t_str, "en": predicate, "role": "Predicate"})
                break
            elif t_str in ["です", "だ", "である"]:
                predicate = "is"
                alignments.append({"ja": t_str, "en": "is", "role": "Copula"})
                break

        # Fallback word-by-word if components missing
        if not subject and not predicate:
            translated_words = []
            for t in tokens:
                lemma = self.lemmatizer.lemmatize(t.text).dictionary_form
                en_w = self.ja_en_lexicon.get(t.text, self.ja_en_lexicon.get(lemma, t.text))
                if en_w:
                    translated_words.append(en_w)
            res_str = " ".join(translated_words)
        else:
            # Construct English SVO: Subject + Predicate + Object
            parts = []
            if subject:
                parts.append(subject)
            if predicate:
                # 3rd person singular 's' if he/she/it
                if subject.lower() in ["he", "she", "the student", "student"]:
                    pred_form = predicate + "s" if not predicate.endswith("s") else predicate
                    parts.append(pred_form)
                else:
                    parts.append(predicate)
            if direct_obj:
                # Add article if countable noun
                if direct_obj.lower() in ["book", "apple", "car", "cat", "dog"]:
                    parts.append(f"the {direct_obj}")
                else:
                    parts.append(direct_obj)
            res_str = " ".join(parts).capitalize() + "."

        return JapaneseTranslationResult(
            source_text=text,
            target_language="en",
            translated_text=res_str,
            structural_alignment="SOV -> SVO",
            lexical_alignments=alignments,
            confidence=0.88 if subject and predicate else 0.70,
        )

    def _translate_en_to_ja(self, text: str) -> JapaneseTranslationResult:
        words = re.findall(r"\b[A-Za-z']+\b", text)
        lower_words = [w.lower() for w in words]

        # Basic English SVO constituent identification
        subj, verb, obj = "", "", ""
        alignments = []

        if len(lower_words) >= 3:
            s_word, v_word, o_word = lower_words[0], lower_words[1], lower_words[2]
            subj = self.en_ja_lexicon.get(s_word, s_word)
            verb = self.en_ja_lexicon.get(v_word, v_word)
            obj = self.en_ja_lexicon.get(o_word, o_word)

            alignments.append({"en": s_word, "ja": subj})
            alignments.append({"en": v_word, "ja": verb})
            alignments.append({"en": o_word, "ja": obj})

            # Format Japanese SOV: Subject は Object を Verb ます。
            ja_trans = f"{subj}は{obj}を{verb}ます。"
        else:
            mapped = [self.en_ja_lexicon.get(w, w) for w in lower_words if self.en_ja_lexicon.get(w, "")]
            ja_trans = "".join(mapped) + "。"

        return JapaneseTranslationResult(
            source_text=text,
            target_language="ja",
            translated_text=ja_trans,
            structural_alignment="SVO -> SOV",
            lexical_alignments=alignments,
            confidence=0.85,
        )
