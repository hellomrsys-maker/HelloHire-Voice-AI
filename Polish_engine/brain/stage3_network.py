"""
Stage 3 Network — 2×2 Sub-AI Topology with Hub and Cyclic Refinement Loop
==========================================================================
Implements the missing Stage 3 of the Reusable Four-Stage 6-Language Matrix Pattern
for the Polish Sovereign Language Engine.

Architecture:
  Group A (Structural pair):
    A1: Syntax Sub-AI       → detects case violations, genitive of negation
    A2: Editorial Sub-AI    → detects aspect misuse, neg concord, vocative

  Group B (Surface/social pair):
    B1: Phonology Sub-AI    → orthographic correctness, sibilant checking
    B2: Pragmatic Sub-AI    → honorifics, Pan/Pani register, deixis

  Hub (3.2 Central):
    → Cross-reads AMSV from both groups
    → Detects group-level conflicts (structural OK but pragmatically wrong)
    → Computes synthesized cultural-linguistic composite score
    → Emits resonance_conflict flag if a contradiction is detected

  Cyclic Refinement Loop (3.3):
    → If Hub detects a conflict: sends a refinement directive back to Group A
    → Group A re-executes with higher strictness for ONE additional pass
    → Maximum 1 refinement pass (prevents infinite recursion)

Zero-Bridge Synchronous Memory Rule:
  All groups share the same 64-byte AMSV buffer.
  AMSV reads between groups are direct in-place memory reads.
  No serialization. No deserialization. No copies.
"""

from typing import Dict, Any, Optional


class Stage3Network:
    """
    Implements the Stage 3 Connected Internal Groups for the Polish engine.
    Groups A and B share one AMSV buffer, Hub synthesizes, cyclic loop refines.
    """

    def __init__(self, syntax_sub_ai, editorial_sub_ai, phonology_sub_ai, pragmatic_sub_ai):
        self.syntax_sub_ai    = syntax_sub_ai
        self.editorial_sub_ai = editorial_sub_ai
        self.phonology_sub_ai = phonology_sub_ai
        self.pragmatic_sub_ai = pragmatic_sub_ai

    def execute(self, text: str, buf: bytearray) -> Dict[str, Any]:
        """
        Runs the full 2×2 network cycle with hub arbitration and optional
        cyclic refinement pass. Returns all sub-AI results and hub decision.
        """
        # ── Group A — Structural Pair ─────────────────────────────────────────
        # Syntax runs first (its flags are read by Editorial via Resonance Protocol)
        syntax_res   = self.syntax_sub_ai.execute(text, buf)

        # Editorial reads buf to pick up Syntax's genitive_neg_flag (0x10)
        editorial_res = self.editorial_sub_ai.execute(text, buf)

        # ── Group B — Surface/Social Pair ─────────────────────────────────────
        # Pragmatic runs first (its register is read by Phonology via Resonance Protocol)
        pragmatic_res  = self.pragmatic_sub_ai.execute(text, buf)

        # Phonology reads buf to pick up Pragmatic's honorific_score (0x15) and register (0x16)
        phonology_res  = self.phonology_sub_ai.execute(text, buf)

        # ── Hub (3.2 Central) — Cross-Group AMSV Arbitration ─────────────────
        hub_result = self._run_hub(buf)

        # ── Cyclic Refinement Loop (3.3) ──────────────────────────────────────
        # If Hub detects a structural/pragmatic contradiction, re-run Group A
        # with heightened strictness via the resonance_conflict signal.
        refinement_applied = False
        if hub_result["conflict_detected"]:
            # Signal to Group A: enforce stricter case checking this pass
            buf[0x3E] = 0xFF  # Refinement directive byte

            syntax_res    = self.syntax_sub_ai.execute(text, buf)
            editorial_res = self.editorial_sub_ai.execute(text, buf)
            refinement_applied = True

            # Clear refinement directive after use
            buf[0x3E] = 0x00

        return {
            "stage": 3,
            "group_a": {"syntax": syntax_res, "editorial": editorial_res},
            "group_b": {"phonology": phonology_res, "pragmatic": pragmatic_res},
            "hub": hub_result,
            "cyclic_refinement_applied": refinement_applied
        }

    def _run_hub(self, buf: bytearray) -> Dict[str, Any]:
        """
        Hub reads AMSV bytes from both Group A and Group B to detect conflicts.

        Reads:
          0x10: genitive_neg_flag       (Group A — Syntax)
          0x11: aspect_code             (Group A — Editorial)
          0x12: syntax_score            (Group A — Syntax)
          0x13: case_score              (Group A — Editorial)
          0x14: orthography_score       (Group B — Phonology)
          0x15: honorific_score         (Group B — Pragmatic)
          0x16: register_code           (Group B — Pragmatic)
          0x18: neg_concord_count       (Group A — Editorial)
          0x19: vocative_flag           (Group A — Editorial)

        Conflict conditions:
          1. syntax_score > 85 but honorific_score < 60:
             Structurally correct but socially inappropriate.
          2. case_score < 60 and orthography_score > 90:
             Orthographically perfect but grammatically broken.
          3. vocative_flag = 1 and register_code = 1 (informal):
             Vocative claim in informal context is suspicious.
        """
        genitive_neg_flag  = buf[0x10]
        aspect_code        = buf[0x11]
        syntax_score       = buf[0x12]
        case_score         = buf[0x13]
        orthography_score  = buf[0x14]
        honorific_score    = buf[0x15]
        register_code      = buf[0x16]
        neg_concord_count  = buf[0x18]
        vocative_flag      = buf[0x19]

        conflicts = []

        if syntax_score > 85 and honorific_score < 60:
            conflicts.append("structural-pragmatic: syntactically correct but honorific failure")

        if case_score < 60 and orthography_score > 90:
            conflicts.append("case-orthography: orthography correct but case system broken")

        if vocative_flag == 1 and register_code == 1:
            conflicts.append("vocative-register: vocative claim in informal (Ty) register is suspicious")

        # Composite cultural-linguistic score (harmonic mean of key sub-scores)
        scores = [syntax_score, case_score, orthography_score, honorific_score]
        hub_composite = round(sum(scores) / len(scores), 2) if scores else 0.0

        # Write Hub composite to AMSV at byte 0x3D
        buf[0x3D] = int(min(100, max(0, hub_composite)))

        return {
            "conflict_detected": len(conflicts) > 0,
            "conflicts": conflicts,
            "hub_composite_score": hub_composite,
            "group_a_scores": {"syntax": syntax_score, "case": case_score, "neg_concord": neg_concord_count},
            "group_b_scores": {"orthography": orthography_score, "honorific": honorific_score, "register": register_code}
        }
