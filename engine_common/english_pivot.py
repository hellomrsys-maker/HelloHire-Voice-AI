"""
english_pivot.py — English-Pivot Comprehension Layer.
======================================================

Implements the ecosystem rule that **every language understands English first**.

For any non-English engine, incoming target-language text is:
  1. NORMALISED into an English-anchored token stream (gloss projection using the
     language's ``to_english_lexicon`` plus the engine's own canonical data).
  2. COMPREHENDED by the shared English comprehension core (the English engine's
     own skills/analysis where available, else a robust lightweight fallback), so
     the semantic backbone is computed in English exactly once.
  3. MAPPED BACK so the target engine can attach language-specific structure
     (word order, honorifics, gender, case) on top of the English comprehension.

This gives every engine an identical English-first comprehension spine while each
language keeps its own authentic surface processing. English itself uses the pivot
as an identity pass.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

from .language_profile import LanguageProfile, WordOrder


@dataclass
class PivotComprehensionResult:
    """Result of understanding target-language text through English first."""
    source_text: str
    source_language: str
    english_projection: str          # English-anchored gloss of the input
    english_tokens: List[str]
    detected_predicate: Optional[str]
    detected_subject: Optional[str]
    detected_object: Optional[str]
    canonical_english_order: str     # reconstructed canonical SVO English string
    comprehension_confidence: float
    is_identity_pass: bool           # True when the source IS English
    notes: List[str] = field(default_factory=list)


class EnglishPivotComprehension:
    """
    Understands input in English first, regardless of the target language.

    The English engine's real skills are used opportunistically; if they cannot be
    imported (e.g. during isolated engine tests), a dependency-free fallback keeps the
    pivot fully functional. Either way the contract (a ``PivotComprehensionResult``)
    is identical, so downstream engines never break.
    """

    def __init__(self, profile: LanguageProfile) -> None:
        self.profile = profile
        self.is_english = profile.iso_code == "en"
        self._english_tokenizer = None
        self._english_pos = None
        self._try_load_english_core()

    def _try_load_english_core(self) -> None:
        """Best-effort load of the real English skills for high-fidelity comprehension."""
        try:
            from English_engine.brain.skills.tokenization import EnglishTokenizer
            from English_engine.brain.skills.pos_tagging import EnglishPOSTagger
            self._english_tokenizer = EnglishTokenizer()
            self._english_pos = EnglishPOSTagger()
        except Exception:
            # Fallback mode: pivot still works without the English engine importable.
            self._english_tokenizer = None
            self._english_pos = None

    # ------------------------------------------------------------------ #
    # Step 1 — project target-language surface into English anchors.
    # ------------------------------------------------------------------ #
    def project_to_english(self, text: str) -> List[str]:
        raw_tokens = self._surface_tokens(text)
        english: List[str] = []
        for tok in raw_tokens:
            if self.is_english:
                english.append(tok)
                continue
            gloss = self.profile.gloss(tok)
            if gloss is None:
                # Unknown surface form: keep as-is (proper nouns, borrowings).
                english.append(tok)
            elif gloss != "":
                # Empty gloss means a dropped particle (は/が/を etc.).
                english.append(gloss)
        return english

    def _surface_tokens(self, text: str) -> List[str]:
        # Normalise terminators to spaces, then whitespace-split. Works for scripts
        # that separate words with spaces; for space-less scripts each surface unit is
        # still handled through the lexicon lookup on the whole run.
        cleaned = text
        for term in self.profile.sentence_terminators:
            cleaned = cleaned.replace(term, " ")
        parts = [p for p in cleaned.split() if p]
        if not parts and text.strip():
            parts = [text.strip()]
        return parts

    # ------------------------------------------------------------------ #
    # Step 2 — comprehend in English (shared spine).
    # ------------------------------------------------------------------ #
    def comprehend(self, text: str) -> PivotComprehensionResult:
        english_tokens = self.project_to_english(text)
        projection = " ".join(english_tokens)
        notes: List[str] = []

        subject = obj = predicate = None

        if self._english_tokenizer is not None and self._english_pos is not None and projection.strip():
            try:
                toks = self._english_tokenizer.tokenize(projection)
                tagged = self._english_pos.tag_tokens(toks)
                subject, predicate, obj = self._extract_roles_from_tags(tagged)
                notes.append("comprehended via English engine skills")
            except Exception:
                subject, predicate, obj = self._heuristic_roles(english_tokens)
                notes.append("comprehended via heuristic fallback (english skills errored)")
        else:
            subject, predicate, obj = self._heuristic_roles(english_tokens)
            notes.append("comprehended via heuristic fallback (english skills unavailable)")

        # Reconstruct canonical English SVO regardless of source word order.
        canonical_parts = [p for p in [subject, predicate, obj] if p]
        canonical = " ".join(canonical_parts) if canonical_parts else projection

        known = sum(1 for t in self._surface_tokens(text) if self.is_english or self.profile.gloss(t) is not None)
        total = max(1, len(self._surface_tokens(text)))
        confidence = round(0.4 + 0.6 * (known / total), 4)

        return PivotComprehensionResult(
            source_text=text,
            source_language=self.profile.language_name,
            english_projection=projection,
            english_tokens=english_tokens,
            detected_predicate=predicate,
            detected_subject=subject,
            detected_object=obj,
            canonical_english_order=canonical,
            comprehension_confidence=confidence,
            is_identity_pass=self.is_english,
            notes=notes,
        )

    # ------------------------------------------------------------------ #
    # Role extraction helpers.
    # ------------------------------------------------------------------ #
    def _extract_roles_from_tags(self, tagged: List[Any]):
        subject = predicate = obj = None
        pred_pos = None
        # First pass: find the predicate (verb) and its position.
        items = []
        for idx, tt in enumerate(tagged):
            tag = getattr(tt, "penn_tag", "")
            word = getattr(getattr(tt, "token", None), "text", None) or getattr(tt, "text", "")
            items.append((tag, word))
            if tag.startswith("VB") and predicate is None:
                predicate = word
                pred_pos = idx
        if predicate is None:
            for idx, (tag, word) in enumerate(items):
                if word.lower() in self._COPULAS or word.lower() in self._COMMON_VERBS:
                    predicate, pred_pos = word, idx
                    break

        def is_content(tag: str) -> bool:
            return tag.startswith("NN") or tag == "PRP" or tag.startswith("JJ")

        before = [w for i, (t, w) in enumerate(items)
                  if is_content(t) and (pred_pos is None or i < pred_pos)]
        after = [w for i, (t, w) in enumerate(items)
                 if is_content(t) and pred_pos is not None and i > pred_pos]

        if before:
            subject = before[0]
        elif after:
            subject = after[0]
            after = after[1:]
        if after:
            obj = after[0]          # complement (predicate nominal/adjective or object)
        elif len(before) > 1:
            obj = before[-1]
        return subject, predicate, obj

    _COPULAS = {"is", "are", "am", "was", "were", "be"}
    _COMMON_VERBS = {"read", "write", "drink", "eat", "see", "buy", "go", "come", "study", "have", "do", "run"}

    # English determiners/particles that are never content roles in the pivot.
    _ENGLISH_STOP = {"the", "a", "an", "of", "and", "to", "in", "on", "at", "for", ""}

    def _heuristic_roles(self, english_tokens: List[str]):
        subject = predicate = obj = None
        lowered = [t.lower() for t in english_tokens]

        # Locate the predicate (first copula or known verb) and its index.
        pred_idx = None
        for i, t in enumerate(lowered):
            if t in self._COPULAS or t in self._COMMON_VERBS:
                predicate = english_tokens[i]
                pred_idx = i
                break

        # Content words: exclude English stopwords, source function words, and the predicate.
        stop = self._ENGLISH_STOP | {w.lower() for w in self.profile.function_words}
        content_idx = [i for i, t in enumerate(lowered)
                       if t not in stop and i != pred_idx]

        if content_idx:
            # Subject = first content word (before the predicate when one exists).
            before = [i for i in content_idx if pred_idx is None or i < pred_idx]
            after = [i for i in content_idx if pred_idx is not None and i > pred_idx]
            if before:
                subject = english_tokens[before[0]]
            elif content_idx:
                subject = english_tokens[content_idx[0]]
            # Object/complement = first content word after the predicate.
            if after:
                obj = english_tokens[after[0]]
            elif not before and len(content_idx) > 1:
                obj = english_tokens[content_idx[-1]]
        return subject, predicate, obj
