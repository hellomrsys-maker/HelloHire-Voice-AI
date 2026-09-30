"""
AMSV Hierarchical Namespace (AHN) — Two-Tier Memory Architecture
================================================================
TIER 1: Master AMSV (64 bytes, system-global, never written by language engines)
         Lives in bandhu_toolkit/matrix_bridge.py :: AtomicStateView
         Owned by: VCE, CCTE, RSSE, AEEE, MAIO

TIER 2: Engine AMSV (64 bytes, private per language engine)
         Owned by: Polish_engine, English_engine, etc.
         Layout is engine-specific (magic bytes, case flags, etc.)

BINDING LAYER:
  Engine orchestrators call `publish_to_master_amsv()` after completing their
  processing cycle. This maps the engine's aggregate linguistic quality score
  into master AMSV offset 0x1C-0x1D (Verbal Reasoning in ccte_cog_bank_beta).

  This is architecturally correct: language engine correctness performance IS
  verbal reasoning performance. It must feed CCTE directly.

Zero-Bridge Synchronous Memory Rule:
  All writes are direct in-place memory mutations. No serialization.
  No deserialization. No network sockets. No bridges.
"""

import ctypes
import struct
from typing import Optional

# ─── Master AMSV field offsets (immutable, system-wide) ──────────────────────
# These constants define WHERE each language engine may write into the master AMSV.
# Language engines MUST NOT write to any other offset.
MASTER_AMSV_VERBAL_REASONING_OFFSET = 0x1C  # uint16 Q16 in ccte_cog_bank_beta
MASTER_AMSV_VERBAL_REASONING_SIZE   = 2      # bytes

# Reserved byte in ccte_cog_bank_beta for cognitive difficulty vector
MASTER_AMSV_COGNITIVE_DIFF_OFFSET = 0x1E   # uint8 nibble: [morph_tier | tonal | case | script]
MASTER_AMSV_COGNITIVE_DIFF_SIZE   = 1

# Reserved byte for engine resonance error flag
MASTER_AMSV_ENGINE_RESONANCE_OFFSET = 0x1F  # uint8 flag: 0=no conflict, 1=syntax/pragmatic conflict
MASTER_AMSV_ENGINE_RESONANCE_SIZE   = 1

# ─── Cognitive Difficulty Tier Encodings ────────────────────────────────────
class MorphologicalTier:
    ISOLATING   = 0   # Vietnamese, Mandarin
    ANALYTIC    = 1   # English, Afrikaans
    AGGLUTINATIVE = 2 # Turkish, Finnish, Swahili, Japanese, Korean
    FUSIONAL    = 3   # Polish, Russian, Arabic, Latin (highest cognitive load)

class TonalLoad:
    NONE        = 0   # Polish, German, English
    LEXICAL_PITCH = 1 # Japanese, Swedish
    FULL_TONAL  = 2   # Mandarin (4+neutral), Cantonese (9), Vietnamese (6), Thai (5)

class CaseDepth:
    MINIMAL     = 0   # 0-2 cases: English, Mandarin, Vietnamese, French
    MODERATE    = 1   # 3-4 cases: German, Dutch
    DEEP        = 2   # 5-7 cases: Polish, Russian, Latin
    EXTREME     = 3   # 8+ cases: Tamil (8), Finnish (15), Hungarian (18)

class ScriptComplexity:
    ALPHABETIC  = 0   # Latin, Cyrillic, Arabic, Hebrew, Thai
    SYLLABIC    = 1   # Japanese Kana, Devanagari, Tamil
    LOGOGRAPHIC = 2   # Mandarin, Cantonese (mixed script)


def encode_cognitive_difficulty_vector(
    morph_tier: int,
    tonal_load: int,
    case_depth: int,
    script_complexity: int
) -> int:
    """
    Packs 4 cognitive dimensions into a single byte:
      bits 7-6: morphological_tier   (0-3)
      bits 5-4: tonal_load           (0-2, clamped to 2 bits)
      bits 3-2: case_depth           (0-3)
      bits 1-0: script_complexity    (0-2, clamped to 2 bits)
    """
    packed = (
        ((morph_tier & 0x3) << 6) |
        ((tonal_load & 0x3) << 4) |
        ((case_depth & 0x3) << 2) |
        (script_complexity & 0x3)
    )
    return packed & 0xFF


def decode_cognitive_difficulty_vector(byte: int) -> dict:
    """Unpacks the cognitive difficulty byte back to named fields."""
    return {
        "morphological_tier":  (byte >> 6) & 0x3,
        "tonal_load":          (byte >> 4) & 0x3,
        "case_depth":          (byte >> 2) & 0x3,
        "script_complexity":    byte       & 0x3,
    }


def compute_verbal_reasoning_bonus(cognitive_diff_byte: int) -> float:
    """
    Computes a calibrated bonus multiplier for the Verbal Reasoning score
    based on the language's cognitive difficulty vector.

    Scale: 1.0 (minimum, zero-case isolating) → 1.45 (maximum, polysynthetic tonal logographic)
    Applied at master AMSV offset 0x1C-0x1D before writing Verbal Reasoning.
    """
    fields = decode_cognitive_difficulty_vector(cognitive_diff_byte)

    morph_bonus  = fields["morphological_tier"] * 0.08   # 0.00 to 0.24
    tonal_bonus  = fields["tonal_load"]         * 0.06   # 0.00 to 0.12
    case_bonus   = fields["case_depth"]         * 0.05   # 0.00 to 0.15
    script_bonus = fields["script_complexity"]  * 0.05   # 0.00 to 0.10

    return round(1.0 + morph_bonus + tonal_bonus + case_bonus + script_bonus, 4)


class AMSVHierarchicalNamespace:
    """
    The binding layer between engine-private AMSVs (Tier 2) and the master AMSV (Tier 1).

    Usage pattern:
        ahn = AMSVHierarchicalNamespace(master_amsv_buffer)
        ahn.publish_engine_result(
            engine_name="Polish",
            aggregate_linguistic_score=0.92,
            cognitive_diff_byte=engine_config.cognitive_diff,
            resonance_conflict=False
        )
    """

    def __init__(self, master_amsv_buffer: bytearray):
        if len(master_amsv_buffer) != 64:
            raise ValueError(f"Master AMSV buffer must be exactly 64 bytes, got {len(master_amsv_buffer)}")
        self._buf = master_amsv_buffer

    def publish_engine_result(
        self,
        engine_name: str,
        aggregate_linguistic_score: float,
        cognitive_diff_byte: int,
        resonance_conflict: bool = False
    ) -> None:
        """
        Maps engine-level linguistic quality into master AMSV without
        touching any non-verbal-reasoning fields (VCE, RSSE, AEEE, MAIO).

        Writes to:
          0x1C-0x1D: Verbal Reasoning Q16 (calibrated by language difficulty)
          0x1E:      Cognitive Difficulty Vector (4-bit packed nibbles)
          0x1F:      Engine Resonance Conflict Flag (0 or 1)
        """
        bonus = compute_verbal_reasoning_bonus(cognitive_diff_byte)
        calibrated_score = min(1.0, aggregate_linguistic_score * bonus)
        verbal_q16 = int(calibrated_score * 65535) & 0xFFFF

        # Write Verbal Reasoning Q16 at 0x1C-0x1D (little-endian)
        self._buf[0x1C] =  verbal_q16        & 0xFF
        self._buf[0x1D] = (verbal_q16 >> 8)  & 0xFF

        # Write Cognitive Difficulty Vector at 0x1E
        self._buf[0x1E] = cognitive_diff_byte & 0xFF

        # Write Resonance Conflict Flag at 0x1F
        self._buf[0x1F] = 1 if resonance_conflict else 0

    def read_verbal_reasoning_q16(self) -> int:
        """Returns the raw Q16 Verbal Reasoning value from master AMSV."""
        return self._buf[0x1C] | (self._buf[0x1D] << 8)

    def read_verbal_reasoning_normalized(self) -> float:
        """Returns Verbal Reasoning as a 0.0-1.0 float."""
        return self.read_verbal_reasoning_q16() / 65535.0

    def read_cognitive_difficulty(self) -> dict:
        """Returns decoded cognitive difficulty fields."""
        return decode_cognitive_difficulty_vector(self._buf[0x1E])

    def has_resonance_conflict(self) -> bool:
        """Returns True if a sub-AI resonance conflict was detected this cycle."""
        return bool(self._buf[0x1F])


# ─── Per-Engine Cognitive Difficulty Profiles ────────────────────────────────
# Each profile is a pre-encoded byte published by the engine into master AMSV.
COGNITIVE_PROFILES = {
    # Fusional + no tones + 7 cases + alphabetic = high cognitive load
    "Polish":      encode_cognitive_difficulty_vector(MorphologicalTier.FUSIONAL,      TonalLoad.NONE,         CaseDepth.DEEP,     ScriptComplexity.ALPHABETIC),
    "Russian":     encode_cognitive_difficulty_vector(MorphologicalTier.FUSIONAL,      TonalLoad.NONE,         CaseDepth.DEEP,     ScriptComplexity.ALPHABETIC),

    # Analytic + no tones + minimal cases + alphabetic = base load
    "English":     encode_cognitive_difficulty_vector(MorphologicalTier.ANALYTIC,      TonalLoad.NONE,         CaseDepth.MINIMAL,  ScriptComplexity.ALPHABETIC),
    "French":      encode_cognitive_difficulty_vector(MorphologicalTier.ANALYTIC,      TonalLoad.NONE,         CaseDepth.MINIMAL,  ScriptComplexity.ALPHABETIC),
    "Spanish":     encode_cognitive_difficulty_vector(MorphologicalTier.ANALYTIC,      TonalLoad.NONE,         CaseDepth.MINIMAL,  ScriptComplexity.ALPHABETIC),
    "Portuguese":  encode_cognitive_difficulty_vector(MorphologicalTier.ANALYTIC,      TonalLoad.NONE,         CaseDepth.MINIMAL,  ScriptComplexity.ALPHABETIC),
    "Italian":     encode_cognitive_difficulty_vector(MorphologicalTier.ANALYTIC,      TonalLoad.NONE,         CaseDepth.MINIMAL,  ScriptComplexity.ALPHABETIC),

    # Moderate fusional + moderate cases
    "German":      encode_cognitive_difficulty_vector(MorphologicalTier.FUSIONAL,      TonalLoad.NONE,         CaseDepth.MODERATE, ScriptComplexity.ALPHABETIC),
    "Dutch":       encode_cognitive_difficulty_vector(MorphologicalTier.ANALYTIC,      TonalLoad.NONE,         CaseDepth.MINIMAL,  ScriptComplexity.ALPHABETIC),

    # Agglutinative + no tones + moderate-extreme cases
    "Turkish":     encode_cognitive_difficulty_vector(MorphologicalTier.AGGLUTINATIVE, TonalLoad.NONE,         CaseDepth.MODERATE, ScriptComplexity.ALPHABETIC),
    "Swahili":     encode_cognitive_difficulty_vector(MorphologicalTier.AGGLUTINATIVE, TonalLoad.NONE,         CaseDepth.MINIMAL,  ScriptComplexity.ALPHABETIC),
    "Indonesian":  encode_cognitive_difficulty_vector(MorphologicalTier.AGGLUTINATIVE, TonalLoad.NONE,         CaseDepth.MINIMAL,  ScriptComplexity.ALPHABETIC),

    # Agglutinative + syllabic/logographic
    "Japanese":    encode_cognitive_difficulty_vector(MorphologicalTier.AGGLUTINATIVE, TonalLoad.LEXICAL_PITCH, CaseDepth.MINIMAL, ScriptComplexity.LOGOGRAPHIC),
    "Korean":      encode_cognitive_difficulty_vector(MorphologicalTier.AGGLUTINATIVE, TonalLoad.NONE,         CaseDepth.MINIMAL,  ScriptComplexity.SYLLABIC),

    # Isolating / analytic + full tonal + logographic
    "Mandarin":    encode_cognitive_difficulty_vector(MorphologicalTier.ISOLATING,     TonalLoad.FULL_TONAL,   CaseDepth.MINIMAL,  ScriptComplexity.LOGOGRAPHIC),
    "Cantonese":   encode_cognitive_difficulty_vector(MorphologicalTier.ISOLATING,     TonalLoad.FULL_TONAL,   CaseDepth.MINIMAL,  ScriptComplexity.LOGOGRAPHIC),
    "Vietnamese":  encode_cognitive_difficulty_vector(MorphologicalTier.ISOLATING,     TonalLoad.FULL_TONAL,   CaseDepth.MINIMAL,  ScriptComplexity.ALPHABETIC),
    "Thai":        encode_cognitive_difficulty_vector(MorphologicalTier.ANALYTIC,      TonalLoad.FULL_TONAL,   CaseDepth.MINIMAL,  ScriptComplexity.ALPHABETIC),

    # Fusional + extreme cases + syllabic
    "Tamil":       encode_cognitive_difficulty_vector(MorphologicalTier.AGGLUTINATIVE, TonalLoad.NONE,         CaseDepth.EXTREME,  ScriptComplexity.SYLLABIC),
    "Hindustani":  encode_cognitive_difficulty_vector(MorphologicalTier.FUSIONAL,      TonalLoad.NONE,         CaseDepth.MODERATE, ScriptComplexity.SYLLABIC),
    "Bengali":     encode_cognitive_difficulty_vector(MorphologicalTier.FUSIONAL,      TonalLoad.NONE,         CaseDepth.MINIMAL,  ScriptComplexity.SYLLABIC),

    # Semitic root-and-pattern
    "Arabic":      encode_cognitive_difficulty_vector(MorphologicalTier.FUSIONAL,      TonalLoad.NONE,         CaseDepth.MODERATE, ScriptComplexity.ALPHABETIC),
    "Persian":     encode_cognitive_difficulty_vector(MorphologicalTier.ANALYTIC,      TonalLoad.NONE,         CaseDepth.MINIMAL,  ScriptComplexity.ALPHABETIC),
}
