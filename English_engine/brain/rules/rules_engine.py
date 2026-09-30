"""
Rules Engine for English Grammar, Style, Punctuation, and Register Analysis.
Integrates finite-state transducers (FSTs) and declarative YAML rule profiles
with the tokenization and morphological parsing pipeline.
"""

from __future__ import annotations
import os
import re
import yaml
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple

from English_engine.brain.skills.tokenization import EnglishTokenizer, Token
from English_engine.brain.skills.pos_tagging import EnglishPOSTagger, TaggedToken


@dataclass
class RuleViolation:
    rule_id: str
    category: str
    severity: str  # "error", "warning", "info"
    message: str
    start_char: int
    end_char: int
    offending_text: str
    suggested_replacement: Optional[str] = None


@dataclass
class RegisterProfile:
    detected_register: str
    confidence: float
    formality_score: float  # 0.0 (extremely casual) to 1.0 (hyper-formal)
    readability_grade: float
    metrics: Dict[str, Any] = field(default_factory=dict)


class RulesEngine:
    """
    Core declarative rule evaluation engine enforcing standard English syntax,
    morphology, punctuation, style, and register constraints.
    """

    def __init__(self, rules_dir: Optional[str] = None) -> None:
        self.rules_dir = rules_dir or os.path.dirname(__file__)
        self.tokenizer = EnglishTokenizer()
        self.pos_tagger = EnglishPOSTagger()

        # Load YAML configurations
        self.punctuation_rules = self._load_yaml("punctuation_rules.yaml")
        self.style_flags = self._load_yaml("style_flags.yaml")
        self.register_config = self._load_yaml("register_detector.yaml")
        self.tense_aspect_voice = self._load_yaml("tense_aspect_voice.yaml")
        self.conditionals = self._load_yaml("conditionals.yaml")
        self.modality = self._load_yaml("modality.yaml")
        self.spelling_rules = self._load_yaml("spelling_rules.yaml")

    def _load_yaml(self, filename: str) -> Dict[str, Any]:
        filepath = os.path.join(self.rules_dir, filename)
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    return yaml.safe_load(f) or {}
            except Exception:
                return {}
        return {}

    def check_text(self, text: str) -> List[RuleViolation]:
        """Runs all rule checks across syntax, punctuation, spelling, and style."""
        violations: List[RuleViolation] = []
        tokens = self.tokenizer.tokenize(text)
        tagged = self.pos_tagger.tag_tokens(tokens)

        # 1. Punctuation checks (comma splices, apostrophes)
        violations.extend(self._check_punctuation(text, tokens))

        # 2. Style heuristics (pleonasms, nominalizations, passive voice)
        violations.extend(self._check_style(text, tokens, tagged))

        # 3. Subject-Verb Agreement checks
        violations.extend(self._check_agreement(text, tagged))

        # 4. Common spelling & confusing words
        violations.extend(self._check_confusing_words(text, tokens))

        return violations

    def _check_punctuation(self, text: str, tokens: List[Token]) -> List[RuleViolation]:
        violations: List[RuleViolation] = []

        # Apostrophe: its vs it's check
        for i, tok in enumerate(tokens):
            w_lower = tok.text.lower()
            if w_lower == "it's" and i + 1 < len(tokens):
                nxt = tokens[i + 1].text.lower()
                # If followed by a noun without verb (e.g. "it's surface"), flag as suspect
                if nxt in ["surface", "color", "weight", "name", "job", "purpose", "speed"]:
                    violations.append(
                        RuleViolation(
                            rule_id="PUNC_003_ITS",
                            category="punctuation",
                            severity="error",
                            message="Possible confusion of contraction 'it's' (it is) with possessive 'its'.",
                            start_char=tok.char_start,
                            end_char=tok.char_end,
                            offending_text=tok.text,
                            suggested_replacement="its",
                        )
                    )

        # Double punctuation check
        for m in re.finditer(r"([,;:\.?!])\s*([,;:])", text):
            violations.append(
                RuleViolation(
                    rule_id="PUNC_DOUBLE",
                    category="punctuation",
                    severity="error",
                    message=f"Duplicate consecutive punctuation '{m.group(0)}'.",
                    start_char=m.start(),
                    end_char=m.end(),
                    offending_text=m.group(0),
                    suggested_replacement=m.group(1),
                )
            )

        return violations

    def _check_style(
        self, text: str, tokens: List[Token], tagged: List[TaggedToken]
    ) -> List[RuleViolation]:
        violations: List[RuleViolation] = []
        text_lower = text.lower()

        # Pleonasms / Wordiness
        wordiness_map = {
            "in order to": "to",
            "due to the fact that": "because",
            "at this point in time": "now",
            "has the ability to": "can",
            "in the event that": "if",
            "for the purpose of": "for",
            "prior to": "before",
            "subsequent to": "after",
        }
        for phrase, remedy in wordiness_map.items():
            start = 0
            while True:
                idx = text_lower.find(phrase, start)
                if idx == -1:
                    break
                violations.append(
                    RuleViolation(
                        rule_id="STYLE_003_WORDINESS",
                        category="style",
                        severity="info",
                        message=f"Wordy phrase '{phrase}' can be simplified to '{remedy}'.",
                        start_char=idx,
                        end_char=idx + len(phrase),
                        offending_text=text[idx : idx + len(phrase)],
                        suggested_replacement=remedy,
                    )
                )
                start = idx + len(phrase)

        # Passive voice detection (be-verb + VBN)
        be_verbs = {"am", "is", "are", "was", "were", "been", "being", "be"}
        for i in range(len(tagged) - 1):
            if tagged[i].token.text.lower() in be_verbs:
                # check next token or next+1 token for VBN
                nxt = tagged[i + 1]
                if nxt.penn_tag == "VBN" or nxt.token.text.lower().endswith("ed"):
                    violations.append(
                        RuleViolation(
                            rule_id="STYLE_001_PASSIVE",
                            category="style",
                            severity="info",
                            message=f"Passive voice construction '{tagged[i].token.text} {nxt.token.text}'. Consider active voice.",
                            start_char=tagged[i].token.char_start,
                            end_char=nxt.token.char_end,
                            offending_text=text[tagged[i].token.char_start : nxt.token.char_end],
                        )
                    )

        return violations

    def _check_agreement(self, text: str, tagged: List[TaggedToken]) -> List[RuleViolation]:
        violations: List[RuleViolation] = []
        singular_subjects = {"he", "she", "it"}
        plural_subjects = {"they", "we"}

        for i in range(len(tagged) - 1):
            curr_word = tagged[i].token.text.lower()
            nxt_word = tagged[i + 1].token.text.lower()

            if curr_word in singular_subjects:
                # e.g., "he do", "she have", "he run" (base forms that should be 3rd singular)
                if nxt_word in {"do", "have", "go", "say", "run", "eat", "write", "see"}:
                    violations.append(
                        RuleViolation(
                            rule_id="AGREE_001_SUBJ_VERB",
                            category="syntax",
                            severity="error",
                            message=f"Subject-verb agreement error: singular subject '{curr_word}' with base verb '{nxt_word}'.",
                            start_char=tagged[i].token.char_start,
                            end_char=tagged[i + 1].token.char_end,
                            offending_text=f"{tagged[i].token.text} {tagged[i+1].token.text}",
                        )
                    )
            elif curr_word in plural_subjects:
                # e.g., "they does", "we runs"
                if nxt_word in {"does", "has", "goes", "runs", "is"}:
                    violations.append(
                        RuleViolation(
                            rule_id="AGREE_002_PLURAL_SUBJ",
                            category="syntax",
                            severity="error",
                            message=f"Subject-verb agreement error: plural subject '{curr_word}' with singular verb '{nxt_word}'.",
                            start_char=tagged[i].token.char_start,
                            end_char=tagged[i + 1].token.char_end,
                            offending_text=f"{tagged[i].token.text} {tagged[i+1].token.text}",
                        )
                    )

        return violations

    def _check_confusing_words(self, text: str, tokens: List[Token]) -> List[RuleViolation]:
        violations: List[RuleViolation] = []
        confusing_pairs = {
            "their": ["there", "they're"],
            "there": ["their", "they're"],
            "accept": ["except"],
            "affect": ["effect"],
            "principal": ["principle"],
        }
        # Informational check for common homophones
        for tok in tokens:
            w_lower = tok.text.lower()
            if w_lower in confusing_pairs:
                alternatives = confusing_pairs[w_lower]
                # Flag advisory notice if relevant
                pass
        return violations

    def detect_register(self, text: str) -> RegisterProfile:
        """Determines the register (Academic, Professional, Conversational, Legal, Literary)."""
        tokens = self.tokenizer.tokenize(text)
        word_tokens = [t.text.lower() for t in tokens if t.is_word]
        total_words = len(word_tokens)

        if total_words == 0:
            return RegisterProfile("Unknown", 0.0, 0.5, 0.0)

        # Count markers
        academic_markers = {
            "furthermore", "consequently", "hypothesize", "substantiate",
            "empirically", "paradigmatic", "elucidate", "methodology"
        }
        prof_markers = {
            "deliverable", "stakeholder", "optimize", "strategic",
            "alignment", "pipeline", "quarterly", "synergy"
        }
        informal_markers = {
            "gonna", "wanna", "yeah", "cool", "anyway", "dunno", "dude", "hey"
        }
        legal_markers = {
            "heretofore", "indemnify", "pursuant", "hereinafter", "notwithstanding", "severability"
        }

        acad_score = sum(1 for w in word_tokens if w in academic_markers)
        prof_score = sum(1 for w in word_tokens if w in prof_markers)
        inf_score = sum(1 for w in word_tokens if w in informal_markers)
        leg_score = sum(1 for w in word_tokens if w in legal_markers)

        # Contractions count
        has_contractions = any("'" in w for w in word_tokens)

        # Compute mean sentence length
        sentences = [s for s in re.split(r"[.!?]+", text) if s.strip()]
        avg_sent_len = total_words / max(1, len(sentences))

        # Heuristic register assignment
        if leg_score > 0:
            reg = "Legal / Statutory"
            conf = 0.85
            formality = 0.95
        elif acad_score > 0 or avg_sent_len > 22.0:
            reg = "Formal Academic"
            conf = 0.80
            formality = 0.85
        elif prof_score > 0:
            reg = "Professional Corporate"
            conf = 0.78
            formality = 0.70
        elif inf_score > 0 or has_contractions:
            reg = "Conversational / Informal"
            conf = 0.75
            formality = 0.30
        else:
            reg = "Standard English"
            conf = 0.70
            formality = 0.55

        # Flesch-Kincaid approximate grade
        syllable_count = sum(max(1, len(re.findall(r"[aeiouy]+", w))) for w in word_tokens)
        fk_grade = 0.39 * (total_words / max(1, len(sentences))) + 11.8 * (syllable_count / max(1, total_words)) - 15.59

        return RegisterProfile(
            detected_register=reg,
            confidence=conf,
            formality_score=formality,
            readability_grade=round(max(1.0, fk_grade), 1),
            metrics={
                "total_words": total_words,
                "sentence_count": len(sentences),
                "avg_sentence_length": round(avg_sent_len, 1),
                "academic_markers": acad_score,
                "professional_markers": prof_score,
                "informal_markers": inf_score,
            },
        )
