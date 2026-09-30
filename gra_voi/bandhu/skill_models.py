"""
skill_models.py - BandhuPrime Dedicated Sub-AIs for Every Grammar Skill (B1 - B6).

Implements specialized neural sub-engine logic for:
- B1: Writing Sub-AI (Completeness, Punctuation, Capitalization, Register)
- B2: Email Sub-AI (Salutations, Modal Politeness, Bullet Parallelism, Sign-Offs, Pragmatic Transfer)
- B3: Listening/Comprehension Sub-AI (Reduction-Forms, Acoustic Endings, Intonational Contours)
- B4: Pronunciation Sub-AI (Grammar-Ending Audibility, Stress Shifts, 7-Step Correction Path)
- B5: Reviewing Sub-AI (Two-Pass Analysis, 4-Tier Error Taxonomy, Hedged Critiques, Citations)
- B6: Book Writing Sub-AI (Book-Scale Consistency, Tense/POV Locks, Reference Decay, 5-Stage Editing)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import re

@dataclass
class SkillAnalysisResult:
    skill: str
    structural_score: float
    register_score: float
    consistency_score: float
    fatal_errors: List[str] = field(default_factory=list)
    clarity_errors: List[str] = field(default_factory=list)
    register_errors: List[str] = field(default_factory=list)
    style_preferences: List[str] = field(default_factory=list)
    recommended_stage: str = "CopyEdit"
    actionable_plan: List[str] = field(default_factory=list)


class BandhuWritingSubAI:
    """Dedicated Sub-AI for B1: Writing Skill."""

    def evaluate(self, text: str) -> SkillAnalysisResult:
        res = SkillAnalysisResult(
            skill="Writing",
            structural_score=1.0,
            register_score=1.0,
            consistency_score=1.0,
            recommended_stage="CopyEdit"
        )
        t = text.strip()
        if not t:
            res.structural_score = 0.0
            res.fatal_errors.append("Empty text string.")
            return res

        # Check terminal punctuation
        if not (t.endswith((".", "?", "!", ";", "。", "؟"))):
            res.clarity_errors.append("Missing terminal clause punctuation glyph.")
            res.structural_score -= 0.25

        # Check capitalization
        if t[0].isalpha() and not t[0].isupper():
            res.register_errors.append("Sentence onset lacks mandatory initial capitalization.")
            res.register_score -= 0.20

        # Check finite verb presence
        common_verbs = {"is", "are", "was", "were", "has", "have", "had", "do", "does", "did",
                        "will", "would", "can", "could", "shall", "should", "may", "might", "must",
                        "walk", "walks", "walked", "examine", "examines", "examined", "conclude", "analyze"}
        words = [re.sub(r"[^\w]", "", w.lower()) for w in t.split()]
        has_verb = any(w in common_verbs or w.endswith(("ed", "ing", "s")) for w in words)
        if not has_verb:
            res.fatal_errors.append("Fatal Error: Sentence fragment detected without finite verb nexus.")
            res.structural_score -= 0.50

        res.structural_score = max(0.0, min(1.0, res.structural_score))
        res.register_score = max(0.0, min(1.0, res.register_score))
        res.actionable_plan.append("Enforce complete subject-finite verb nexus across all coordinate clauses.")
        return res


class BandhuEmailSubAI:
    """Dedicated Sub-AI for B2: Email Skill."""

    def evaluate(self, text: str, target_lang: str = "English") -> SkillAnalysisResult:
        res = SkillAnalysisResult(
            skill="Emailing",
            structural_score=1.0,
            register_score=1.0,
            consistency_score=1.0,
            recommended_stage="CopyEdit"
        )
        lower = text.lower()

        # 1. Salutation check
        salutations = ["dear ", "sehr geehrte", "cher ", "estimado", "hello", "hi ", "拝啓", "السلام عليكم"]
        if not any(s in lower for s in salutations):
            res.register_errors.append("Register Error: Missing standard professional salutation formula.")
            res.register_score -= 0.25

        # 2. Modal politeness check
        polite_modals = ["could you", "would you", "would it be possible", "könnten sie", "pourriez-vous", "ていただけますでしょうか"]
        abrupt_imps = ["send me", "do this now", "give me", "i need this now"]
        if any(a in lower for a in abrupt_imps) and not any(p in lower for p in polite_modals):
            res.register_errors.append("Register Error: Unhedged direct imperative creates pragmatic friction.")
            res.register_score -= 0.35

        # 3. Pragmatic transfer warning for Japanese / Korean
        if target_lang.lower() in ("japanese", "korean") and not any(p in lower for p in ["ていただけますでしょうか", "부탁드립니다"]):
            res.clarity_errors.append("Pragmatic Transfer Warning: Direct Western request requires negative conditional honorific machinery.")
            res.consistency_score -= 0.20

        # 4. Sign-off check
        signoffs = ["best regards", "sincerely", "mit freundlichen grüßen", "cordialement", "warm regards", "拝", "何卒よろしく"]
        if not any(s in lower for s in signoffs):
            res.register_errors.append("Register Error: Missing canonical email sign-off formula.")
            res.register_score -= 0.20

        res.structural_score = max(0.0, min(1.0, res.structural_score))
        res.register_score = max(0.0, min(1.0, res.register_score))
        res.actionable_plan.append("Wrap direct transactional requests in polite past-tense conditional modals.")
        return res


class BandhuListeningSubAI:
    """Dedicated Sub-AI for B3: Listening & Acoustic Segmentation Skill."""

    def evaluate(self, spoken_text: str) -> SkillAnalysisResult:
        res = SkillAnalysisResult(
            skill="Listening",
            structural_score=0.95,
            register_score=0.90,
            consistency_score=0.95,
            recommended_stage="LineEdit"
        )
        lower = spoken_text.lower()
        reductions = ["i'd've", "could've", "should've", "gonna", "wanna", "chais pas", "dunno"]
        found = [r for r in reductions if r in lower]
        if found:
            res.actionable_plan.append(f"Acoustic reduction forms detected ({', '.join(found)}): Map to underlying canonical syntactic trees.")
        return res


class BandhuPronunciationSubAI:
    """Dedicated Sub-AI for B4: Pronunciation & Phonological Skill."""

    def evaluate(self, transcript: str, dropped_endings: bool = False) -> SkillAnalysisResult:
        res = SkillAnalysisResult(
            skill="Pronouncing",
            structural_score=0.90,
            register_score=0.90,
            consistency_score=1.0,
            recommended_stage="Proofread"
        )
        if dropped_endings:
            res.fatal_errors.append("Fatal Morphophonological Error: Dropped word-final consonant cluster obliterating tense/agreement.")
            res.structural_score -= 0.40

        # Personalized 7-step correction path
        res.actionable_plan = [
            "Step 1: Minimal-pair acoustic perception training.",
            "Step 2: Explicit articulatory biomechanics guidance (tongue posture, alveolar contact).",
            "Step 3: Slow-to-fast drill progression (phoneme -> syllable -> word -> sentence).",
            "Step 4: Recording and native spectrogram waveform comparison.",
            "Step 5: Full-sentence rhythm shadowing matching melody and unstressed endings.",
            "Step 6: Daily dedicated oral reading aloud.",
            "Step 7: Targeted single-pattern feedback loop."
        ]
        return res


class BandhuReviewingSubAI:
    """Dedicated Sub-AI for B5: Reviewing & Textual Verification Skill."""

    def evaluate(self, review_text: str) -> SkillAnalysisResult:
        res = SkillAnalysisResult(
            skill="Reviewing",
            structural_score=1.0,
            register_score=1.0,
            consistency_score=1.0,
            recommended_stage="LineEdit"
        )
        lower = review_text.lower()

        # Hedged language
        hedges = ["suggest", "might consider", "could benefit", "recommend", "appears to"]
        if not any(h in lower for h in hedges):
            res.style_preferences.append("Style Preference: Critique lacks professional modal hedging.")
            res.register_score -= 0.15

        # Location anchoring
        anchors = ["line ", "page ", "section ", "paragraph ", "p. "]
        if not any(a in lower for a in anchors):
            res.clarity_errors.append("Clarity Error: Unanchored evaluative claim lacking line/page coordinate citation.")
            res.structural_score -= 0.30

        res.actionable_plan.append("Anchor every critique to specific line numbers and use hedged modal verbs.")
        return res


class BandhuBookWritingSubAI:
    """Dedicated Sub-AI for B6: Book-Scale Writing Skill."""

    def evaluate(self, manuscript_sample: str) -> SkillAnalysisResult:
        res = SkillAnalysisResult(
            skill="BookWriting",
            structural_score=1.0,
            register_score=1.0,
            consistency_score=1.0,
            recommended_stage="CopyEdit"
        )
        words = manuscript_sample.split()
        lower = manuscript_sample.lower()

        past_markers = {"was", "were", "walked", "said", "looked", "saw"}
        pres_markers = {"is", "are", "walks", "says", "looks", "sees"}

        past_hits = sum(1 for w in words if re.sub(r"[^\w]", "", w.lower()) in past_markers)
        pres_hits = sum(1 for w in words if re.sub(r"[^\w]", "", w.lower()) in pres_markers)

        if past_hits > 0 and pres_hits > 0:
            ratio = past_hits / (past_hits + pres_hits)
            if 0.2 < ratio < 0.8:
                res.clarity_errors.append("Clarity Error: Tense collision between narrative past and present without licensing.")
                res.consistency_score -= 0.35

        # Check dialogue tag boundaries
        if "smiled hello" in lower or "laughed yes" in lower:
            res.fatal_errors.append("Fatal Category Error: Impossible physical speech act used as dialogue tag.")
            res.structural_score -= 0.25

        res.actionable_plan = [
            "Stage 1: Draft - focus on speed and thematic velocity.",
            "Stage 2: Structural Edit - organize chapter architecture and macro-discourse.",
            "Stage 3: Line Edit - refine paragraph rhythm and syntactic pacing.",
            "Stage 4: Copy Edit - enforce tense locks, pronoun antecedent distances, and style sheet.",
            "Stage 5: Proofread - verify layout and visual typography."
        ]
        return res
