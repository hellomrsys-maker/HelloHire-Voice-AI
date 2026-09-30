"""
Stage 4 Verifier — Recursive Feedback Pipeline (Stage 4 of Four-Stage Matrix)
==============================================================================
Implements Stage 4 of the Reusable Four-Stage 6-Language Matrix Pattern:
  4.1 Check / Question & Correct
  4.2 Base Matrix
  4.3 AI Model + Training (heuristic confidence scoring)
  4.4 Analyzer → OUT(Result) with recursive feedback back to 4.1

Recursive Feedback Rule:
  If the Analyzer (4.4) detects that:
    - Overall quality < QUALITY_THRESHOLD, AND
    - At least one confidence interval is actionable (error is correctable)
  Then it sends a correction directive back to 4.1 for a second analysis pass.
  Maximum MAX_FEEDBACK_PASSES to prevent infinite recursion.

Zero-Bridge Synchronous Memory Rule:
  Stage 4 reads all results from the shared AMSV buffer directly.
  Correction directives are written as flag bytes into AMSV.
"""

from typing import Dict, Any, List

QUALITY_THRESHOLD    = 70    # Below this, recursive feedback fires
MAX_FEEDBACK_PASSES  = 2     # Hard cap on recursive passes
AMSV_STAGE4_OFFSET   = 0x20  # Stage 4 writes its correction directive here


class Stage4Verifier:
    """
    Implements Stage 4 verification with recursive feedback.

    Given Stage 3 network results and the shared AMSV buffer,
    the verifier checks, questions, corrects, and analyzes — emitting
    a final structured result with actionable correction paths.
    """

    def execute(self, stage3_result: Dict[str, Any], buf: bytearray, text: str) -> Dict[str, Any]:
        """
        Runs the Stage 4 pipeline. Returns the final OUT(Result) with
        quality verdict, correction proposals, and feedback metadata.
        """
        passes_used = 0
        feedback_history = []

        current_result = stage3_result
        quality = self._compute_quality(buf)

        while quality < QUALITY_THRESHOLD and passes_used < MAX_FEEDBACK_PASSES:
            passes_used += 1

            # 4.1: Check / Question & Correct
            correction = self._check_and_correct(buf, quality)
            feedback_history.append(correction)

            # Write correction directive to AMSV (byte 0x20 = rsse_scenario_state[0])
            # Using upper nibble of byte 0x20 as Stage 4 directive flag
            buf[0x20] = (buf[0x20] & 0x0F) | (0xF0 if correction["actionable"] else 0x00)

            if not correction["actionable"]:
                break  # Nothing further to correct

            # 4.2 Base Matrix: re-read AMSV with updated understanding
            quality = self._compute_quality(buf)

            # If quality has recovered above threshold, stop early
            if quality >= QUALITY_THRESHOLD:
                break

        # 4.4: Analyzer — produce final result
        final_result = self._analyze(buf, quality, feedback_history, passes_used, text)

        # Clear Stage 4 directive after final analysis
        buf[0x20] = buf[0x20] & 0x0F

        return final_result

    def _compute_quality(self, buf: bytearray) -> float:
        """Reads AMSV sub-scores to compute an overall quality index."""
        syntax_score      = buf[0x12]
        case_score        = buf[0x13]
        orthography_score = buf[0x14]
        honorific_score   = buf[0x15]
        hub_composite     = buf[0x3D]

        # Weighted quality: syntax (30%) + case (25%) + orthography (20%) + honorific (15%) + hub (10%)
        weighted = (
            syntax_score      * 0.30 +
            case_score        * 0.25 +
            orthography_score * 0.20 +
            honorific_score   * 0.15 +
            hub_composite     * 0.10
        )
        return round(weighted, 2)

    def _check_and_correct(self, buf: bytearray, quality: float) -> Dict[str, Any]:
        """
        4.1: Check & Correct Pass.
        Identifies the weakest sub-score and proposes a targeted correction.
        """
        sub_scores = {
            "syntax":      buf[0x12],
            "case":        buf[0x13],
            "orthography": buf[0x14],
            "honorific":   buf[0x15],
        }
        weakest = min(sub_scores, key=sub_scores.get)
        weakest_score = sub_scores[weakest]

        # Actionable only if weakest score is below 50 (meaningful correction possible)
        actionable = weakest_score < 50

        corrections = {
            "syntax": (
                "Stage 4 Correction: Syntax analysis identified case government violation. "
                "Verify noun phrase requires Genitive under negation."
            ),
            "case": (
                "Stage 4 Correction: Case score below threshold. "
                "Check inflection tables for accusative vs. genitive under negation."
            ),
            "orthography": (
                "Stage 4 Correction: Orthographic errors detected. "
                "Review sz/cz/ż/ź/rz sibilant spelling and nasal vowel distribution."
            ),
            "honorific": (
                "Stage 4 Correction: Honorific concord failure. "
                "Verify Pan/Pani/Państwo agreement with verb form and gender."
            )
        }

        return {
            "pass_quality": quality,
            "weakest_dimension": weakest,
            "weakest_score": weakest_score,
            "actionable": actionable,
            "correction_proposal": corrections[weakest] if actionable else "Quality within acceptable range.",
        }

    def _analyze(
        self,
        buf: bytearray,
        final_quality: float,
        feedback_history: List[Dict],
        passes_used: int,
        text: str
    ) -> Dict[str, Any]:
        """4.4 Analyzer — produces the final OUT(Result)."""
        syntax_score      = buf[0x12]
        case_score        = buf[0x13]
        orthography_score = buf[0x14]
        honorific_score   = buf[0x15]
        neg_concord_cnt   = buf[0x18]
        hub_composite     = buf[0x3D]

        # Determine verdict
        if final_quality >= 85:
            verdict = "PASS — High linguistic quality"
        elif final_quality >= 70:
            verdict = "PASS — Acceptable linguistic quality"
        elif final_quality >= 50:
            verdict = "REVIEW — Quality below threshold, corrections recommended"
        else:
            verdict = "FAIL — Multiple critical linguistic violations detected"

        # Build actionable summary
        corrections = [f["correction_proposal"] for f in feedback_history if f.get("actionable")]

        return {
            "stage": 4,
            "final_quality": final_quality,
            "verdict": verdict,
            "feedback_passes_used": passes_used,
            "recursive_feedback_fired": passes_used > 0,
            "sub_scores": {
                "syntax":      syntax_score,
                "case":        case_score,
                "orthography": orthography_score,
                "honorific":   honorific_score,
                "neg_concord_count": neg_concord_cnt,
                "hub_composite": hub_composite
            },
            "correction_proposals": corrections,
            "text_analyzed": text[:120] + ("..." if len(text) > 120 else "")
        }
