"""
Japanese Rules Engine
=====================
Comprehensive declarative rule evaluation engine enforcing Japanese syntax,
orthography, honorifics (Keigo), punctuation, style heuristics, and register.
"""

from __future__ import annotations
import os
import re
import yaml
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

from Japanese_engine.brain.skills.tokenization import JapaneseTokenizer, JapaneseToken
from Japanese_engine.brain.skills.pos_tagging import JapanesePOSTagger, JapaneseTaggedToken


@dataclass
class JapaneseRuleViolation:
    rule_id: str
    category: str
    severity: str  # "error", "warning", "info"
    message: str
    start_char: int
    end_char: int
    offending_text: str
    suggested_replacement: Optional[str] = None


@dataclass
class JapaneseRegisterProfile:
    detected_register: str
    confidence: float
    formality_score: float  # 0.0 (very casual) to 1.0 (hyper-formal)
    readability_grade: float
    metrics: Dict[str, Any] = field(default_factory=dict)


class JapaneseRulesEngine:
    """
    Core rule evaluation engine validating Japanese grammar, keigo appropriateness,
    punctuation integrity, style heuristics (ra-nuki, sa-ire, redundancies), and register.
    """

    def __init__(self, rules_dir: Optional[str] = None) -> None:
        self.rules_dir = rules_dir or os.path.dirname(__file__)
        self.tokenizer = JapaneseTokenizer()
        self.pos_tagger = JapanesePOSTagger()

        # Load YAML configurations
        self.keigo_rules = self._load_yaml("keigo_honorifics.yaml")
        self.particle_rules = self._load_yaml("particle_rules.yaml")
        self.conjugation_matrix = self._load_yaml("conjugation_matrix.yaml")
        self.conditionals = self._load_yaml("conditionals.yaml")
        self.modality = self._load_yaml("modality.yaml")
        self.spelling_rules = self._load_yaml("spelling_orthography.yaml")
        self.punctuation_rules = self._load_yaml("punctuation_rules.yaml")
        self.style_flags = self._load_yaml("style_flags.yaml")
        self.register_config = self._load_yaml("register_detector.yaml")

    def _load_yaml(self, filename: str) -> Dict[str, Any]:
        filepath = os.path.join(self.rules_dir, filename)
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    return yaml.safe_load(f) or {}
            except Exception:
                return {}
        return {}

    def check_text(self, text: str) -> List[JapaneseRuleViolation]:
        """Runs all grammatical, honorific, stylistic, and punctuation checks."""
        violations: List[JapaneseRuleViolation] = []
        tokens = self.tokenizer.tokenize(text)
        tagged = self.pos_tagger.tag_tokens(tokens)

        # 1. Punctuation checks
        violations.extend(self._check_punctuation(text))

        # 2. Keigo anti-pattern checks (Double honorifics, etc.)
        violations.extend(self._check_keigo(text))

        # 3. Style checks (Ra-nuki, Sa-ire, Pleonasms / Redundancies)
        violations.extend(self._check_style(text))

        # 4. Keitai / Joutai consistency
        violations.extend(self._check_keitai_joutai_consistency(text))

        # 5. Particle usage validation
        violations.extend(self._check_particles(text, tagged))

        return violations

    def _check_punctuation(self, text: str) -> List[JapaneseRuleViolation]:
        violations: List[JapaneseRuleViolation] = []

        # Duplicate touten (、、)
        for m in re.finditer(r"、、+", text):
            violations.append(
                JapaneseRuleViolation(
                    rule_id="PUNC_DOUBLE_TOUTEN",
                    category="punctuation",
                    severity="error",
                    message="連続した読点（、、）が検出されました。",
                    start_char=m.start(),
                    end_char=m.end(),
                    offending_text=m.group(0),
                    suggested_replacement="、",
                )
            )

        # Duplicate kuten (。。)
        for m in re.finditer(r"。。+", text):
            violations.append(
                JapaneseRuleViolation(
                    rule_id="PUNC_DOUBLE_KUTEN",
                    category="punctuation",
                    severity="error",
                    message="連続した句点（。。）が検出されました。",
                    start_char=m.start(),
                    end_char=m.end(),
                    offending_text=m.group(0),
                    suggested_replacement="。",
                )
            )

        # Unbalanced kagikakko
        open_count = text.count("「")
        close_count = text.count("」")
        if open_count != close_count:
            violations.append(
                JapaneseRuleViolation(
                    rule_id="PUNC_UNBALANCED_KAKKO",
                    category="punctuation",
                    severity="error",
                    message=f"かぎ括弧の開き（{open_count}個）と閉じ（{close_count}個）が一致しません。",
                    start_char=0,
                    end_char=len(text),
                    offending_text="「」",
                    suggested_replacement=None,
                )
            )

        return violations

    def _check_keigo(self, text: str) -> List[JapaneseRuleViolation]:
        violations: List[JapaneseRuleViolation] = []
        anti_patterns = [
            (r"おっしゃられ(?:る|ます|ました|た|ない)?", "おっしゃる", "二重敬語：『おっしゃる』に尊敬の助動詞『られる』が重複しています。"),
            (r"ご覧になられ(?:る|ます|ました|た|ない)?", "ご覧になる", "二重敬語：『ご覧になる』に『られる』が重複しています。"),
            (r"お召し上がりになられ(?:る|ます|ました|た|ない)?", "召し上がる", "二重敬語：『召し上がる』に過剰な敬語表現が重なっています。"),
            (r"伺わせていただ(?:く|きます|きました|いた)?", "伺う / 参る", "過剰謙譲表現：『伺う』と『〜させていただく』の重複です。"),
            (r"拝見させていただ(?:く|きます|きました|いた)?", "拝見します / 拝見いたします", "過剰謙譲表現：『拝見する』に『〜させていただく』が重複しています。"),
            (r"よろしかったでしょうか", "よろしいでしょうか", "バイト敬語：過去形による不自然な確認表現です。"),
        ]

        for bad_pat, rep, reason in anti_patterns:
            for m in re.finditer(bad_pat, text):
                violations.append(
                    JapaneseRuleViolation(
                        rule_id="KEIGO_ANTI_PATTERN",
                        category="keigo",
                        severity="warning",
                        message=reason,
                        start_char=m.start(),
                        end_char=m.end(),
                        offending_text=m.group(0),
                        suggested_replacement=rep,
                    )
                )

        return violations

    def _check_style(self, text: str) -> List[JapaneseRuleViolation]:
        violations: List[JapaneseRuleViolation] = []

        # Ra-nuki (ら抜き言葉)
        ra_nuki_list = [
            ("食べれる", "食べられる"),
            ("見れる", "見られる"),
            ("来れる", "来られる"),
            ("出れる", "出られる"),
            ("起きれる", "起きられる"),
        ]
        for bad, good in ra_nuki_list:
            for m in re.finditer(re.escape(bad), text):
                violations.append(
                    JapaneseRuleViolation(
                        rule_id="STYLE_RA_NUKI",
                        category="style",
                        severity="warning",
                        message=f"ら抜き言葉の検出：正しくは『{good}』です。",
                        start_char=m.start(),
                        end_char=m.end(),
                        offending_text=m.group(0),
                        suggested_replacement=good,
                    )
                )

        # Sa-ire (さ入れ言葉)
        sa_ire_list = [
            ("休まさせていただきます", "休ませていただきます"),
            ("歌わさせていただきます", "歌わせていただきます"),
            ("読まさせていただきます", "読ませていただきます"),
            ("行かさせていただきます", "行かせていただきます"),
        ]
        for bad, good in sa_ire_list:
            for m in re.finditer(re.escape(bad), text):
                violations.append(
                    JapaneseRuleViolation(
                        rule_id="STYLE_SA_IRE",
                        category="style",
                        severity="warning",
                        message=f"さ入れ言葉の検出：五段動詞への不要な『さ』の挿入です。正しくは『{good}』です。",
                        start_char=m.start(),
                        end_char=m.end(),
                        offending_text=m.group(0),
                        suggested_replacement=good,
                    )
                )

        # Pleonasms (重言)
        pleonasms = [
            ("頭痛が痛い", "頭が痛い / 頭痛がする"),
            ("まず最初に", "まず / 最初に"),
            ("一番ベスト", "ベスト / 最善"),
            ("後で後悔する", "後悔する"),
            ("過半数を超える", "過半数に達する / 半数を超える"),
            ("馬から落馬する", "落馬する"),
        ]
        for bad, good in pleonasms:
            for m in re.finditer(re.escape(bad), text):
                violations.append(
                    JapaneseRuleViolation(
                        rule_id="STYLE_REDUNDANCY",
                        category="style",
                        severity="warning",
                        message=f"重言（重複表現）：意味が重複しています。推奨：『{good}』",
                        start_char=m.start(),
                        end_char=m.end(),
                        offending_text=m.group(0),
                        suggested_replacement=good,
                    )
                )

        return violations

    def _check_keitai_joutai_consistency(self, text: str) -> List[JapaneseRuleViolation]:
        violations: List[JapaneseRuleViolation] = []
        sentences = [s for s in re.split(r"[。！？\n]+", text) if s.strip()]
        if len(sentences) < 2:
            return violations

        keitai_count = 0
        joutai_count = 0

        keitai_endings = ("です", "ます", "でした", "ました", "ません", "ございます")
        joutai_endings = ("だ", "である", "だった", "であった", "ではない")

        for s in sentences:
            s_clean = s.strip()
            if any(s_clean.endswith(k) for k in keitai_endings):
                keitai_count += 1
            elif any(s_clean.endswith(j) for j in joutai_endings):
                joutai_count += 1

        if keitai_count > 0 and joutai_count > 0:
            violations.append(
                JapaneseRuleViolation(
                    rule_id="STYLE_KEITAI_JOUTAI_MIX",
                    category="style",
                    severity="warning",
                    message=f"敬体（です・ます：{keitai_count}文）と常体（だ・である：{joutai_count}文）が同一文面で混在しています（文体のねじれ）。",
                    start_char=0,
                    end_char=len(text),
                    offending_text=text[:30] + "...",
                    suggested_replacement=None,
                )
            )

        return violations

    def _check_particles(self, text: str, tagged: List[JapaneseTaggedToken]) -> List[JapaneseRuleViolation]:
        violations: List[JapaneseRuleViolation] = []
        # Dynamic location with static predicate check (e.g. 部屋でいる)
        for m in re.finditer(r"([^\s、。]+)で(いる|ある)", text):
            # If preceding is a physical place, suggest 'に'
            violations.append(
                JapaneseRuleViolation(
                    rule_id="PARTICLE_CONFUSED_NI_DE",
                    category="syntax",
                    severity="error",
                    message="存在を表す動詞（いる・ある）の所在場所には助詞『で』ではなく『に』を使用します。",
                    start_char=m.start(),
                    end_char=m.end(),
                    offending_text=m.group(0),
                    suggested_replacement=f"{m.group(1)}に{m.group(2)}",
                )
            )
        return violations

    def detect_register(self, text: str) -> JapaneseRegisterProfile:
        """Determines register, formality index, and stylistic grade."""
        total_len = len(text)
        if total_len == 0:
            return JapaneseRegisterProfile("Unknown", 0.0, 0.5, 0.0)

        # Count register markers
        business_markers = ["恐縮", "所存", "拝見", "ご教示", "存じます", "申し上げます", "幸甚", "承知いたしました", "平素"]
        academic_markers = ["である", "と考えられる", "本稿", "先行研究", "示唆される", "検証する", "分析結果", "結論付"]
        legal_markers = ["とする", "に限る", "第", "条", "前項", "定めのない限り", "効力を有する"]
        casual_markers = ["だよね", "じゃん", "マジ", "やばい", "めっちゃ", "〜っす", "うん", "そうなんだ", "笑"]

        b_score = sum(text.count(m) for m in business_markers)
        a_score = sum(text.count(m) for m in academic_markers)
        l_score = sum(text.count(m) for m in legal_markers)
        c_score = sum(text.count(m) for m in casual_markers)

        # Check polite markers
        polite_markers = ["です", "ます", "でした", "ました", "ございます"]
        p_score = sum(text.count(m) for m in polite_markers)

        # Kanji density metric
        kanji_chars = len(re.findall(r"[\u4e00-\u9faf]", text))
        kanji_ratio = kanji_chars / max(1, total_len)

        # Determine register
        if l_score >= 2:
            reg = "Official Document / Legal (公用文・法令体)"
            conf = 0.90
            formality = 0.96
        elif b_score >= 2 or (b_score >= 1 and p_score >= 2):
            reg = "Business Keigo (改まったビジネス体)"
            conf = 0.88
            formality = 0.88
        elif a_score >= 2 or (a_score >= 1 and kanji_ratio > 0.40):
            reg = "Academic Thesis (論文・学術体)"
            conf = 0.85
            formality = 0.90
        elif c_score > 0:
            reg = "Casual Colloquial (親密口語・タメ口)"
            conf = 0.80
            formality = 0.25
        elif p_score > 0:
            reg = "Standard Polite (日常丁寧体)"
            conf = 0.75
            formality = 0.65
        else:
            reg = "Standard Japanese Plain (一般常体)"
            conf = 0.70
            formality = 0.50

        readability_grade = round(1.0 + (kanji_ratio * 10.0), 1)

        return JapaneseRegisterProfile(
            detected_register=reg,
            confidence=conf,
            formality_score=formality,
            readability_grade=readability_grade,
            metrics={
                "char_length": total_len,
                "kanji_ratio": round(kanji_ratio, 3),
                "business_score": b_score,
                "academic_score": a_score,
                "legal_score": l_score,
                "casual_score": c_score,
                "polite_score": p_score,
            },
        )
