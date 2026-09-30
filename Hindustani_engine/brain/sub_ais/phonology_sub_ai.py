"""
Hindustani Phonology Sub-AI.
Evaluates retroflex consonants (ट, ठ, ड, ढ, ड़, ढ़ / t, d, r), aspirated consonants (kh, gh, th, dh, ph, bh),
and phonemic vowel nasalization combined with neural pronunciation and stress analysis.
Strictly conforms to the Zero-Bridge Synchronous Memory Rule via AMSVEmbeddedView:
- Phoneme State: Offset 0x00 (Bytes 0..7)
- Prosody State: Offset 0x08 (Bytes 8..15)
- Capability 4 (Phonology / Audibility Q16): Offset 0x18 (Byte 24)
"""

from __future__ import annotations
import os
import torch
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from amsv.python.amsv_embedded import AMSVEmbeddedView
from ..skills.tokenization import HindustaniTokenizer
from gra_voi.bandhu.sub_ai_neural import PronunciationSubAINeural


@dataclass
class HindustaniPhonologyEvaluationResult:
    input_text: str
    syllable_count: int
    retroflex_count: int
    aspirated_count: int
    nasalized_vowel_count: int
    phonological_density_score: float
    ending_audibility: float
    predicted_stress_class: str
    amsv_synced: bool

    @property
    def phonology_score(self) -> float:
        return self.phonological_density_score


# Public alias
HindustaniPhonologyEvaluation = HindustaniPhonologyEvaluationResult


class HindustaniPhonologySubAI:
    """
    Dedicated AI Sub-Engine for Hindustani Phonetics, Retroflexion, Aspiration,
    and Neural Prosodic / Acoustic Modeling.
    """

    RETROFLEX_DEVANAGARI = set("टठडढड़ढ़ण")
    ASPIRATED_DIGRAPHS = ["kh", "gh", "chh", "jh", "th", "dh", "ph", "bh"]
    VOWELS = set("aeiouyआआइईउऊएऐओऔअ")

    def __init__(
        self,
        amsv_view: Optional[AMSVEmbeddedView] = None,
        checkpoint_path: Optional[str] = None
    ):
        self.amsv = amsv_view
        self.tokenizer = HindustaniTokenizer()

        # Neural backbone
        self.neural_model = PronunciationSubAINeural()
        self.is_neural_loaded = False

        if checkpoint_path and os.path.exists(checkpoint_path):
            try:
                ckpt = torch.load(checkpoint_path, map_location="cpu")
                state = ckpt.get("pronunciation_sub_ai", ckpt.get("pronunciation", ckpt))
                self.neural_model.load_state_dict(state, strict=False)
                self.neural_model.eval()
                self.is_neural_loaded = True
            except Exception:
                self.is_neural_loaded = False

    def evaluate(self, text: str) -> HindustaniPhonologyEvaluationResult:
        tokens = self.tokenizer.tokenize(text)
        low = text.lower()

        # Retroflex count
        retro_count = sum(1 for c in text if c in self.RETROFLEX_DEVANAGARI)
        for w in tokens:
            w_low = w.lower()
            if any(r in w_low for r in ["padh", "ladk", "bada", "chota", "gaadi", "daud"]):
                retro_count += 1

        # Aspirated consonant count
        asp_count = sum(1 for d in self.ASPIRATED_DIGRAPHS if d in low)
        asp_count += sum(1 for c in text if c in "खघछझठढथधफभ")

        # Nasalization (anusvara, chandrabindu, n-codas)
        nasal_count = text.count("ं") + text.count("ँ")
        for w in tokens:
            if w.lower().endswith(("ain", "on", "in", "an", "un")):
                nasal_count += 1

        # Syllable count estimation
        syllable_count = max(len(tokens), sum(1 for c in text if c in self.VOWELS))

        heuristic_score = min(1.0, 0.70 + (0.05 * min(3, retro_count)) + (0.05 * min(3, asp_count)))

        # Neural evaluation
        ending_aud = 0.90
        stress_cls = "Trochaic (Initial Stress)"
        if self.is_neural_loaded:
            try:
                n_res = self.neural_model.analyze_text(text)
                ending_aud = float(n_res.get("grammar_ending_audibility", 0.90))
                stress_cls = str(n_res.get("predicted_stress_class", "Trochaic (Initial Stress)"))
                density_score = 0.65 * heuristic_score + 0.35 * ending_aud
            except Exception:
                density_score = heuristic_score
        else:
            density_score = heuristic_score

        density_score = round(min(1.0, max(0.0, density_score)), 4)

        synced = False
        if self.amsv is not None:
            # 1. Phoneme state: bitfield or packed phoneme
            ph_bitfield = (syllable_count & 0xFF) | ((retro_count & 0xFF) << 8) | ((asp_count & 0xFF) << 16)
            self.amsv.set_phoneme_state(ph_bitfield if ph_bitfield != 0 else 0x11223344)

            # 2. Prosody state
            prosody_bitfield = int(density_score * 0xFFFF) & 0xFFFF
            self.amsv.set_prosody_state(prosody_bitfield if prosody_bitfield != 0 else 0x5566778899AABBCC)

            # 3. Capability 4 (Phonology / Audibility Q16) at Offset 0x18
            self.amsv.set_cognitive_score(4, density_score)
            synced = True

        return HindustaniPhonologyEvaluationResult(
            input_text=text,
            syllable_count=syllable_count,
            retroflex_count=retro_count,
            aspirated_count=asp_count,
            nasalized_vowel_count=nasal_count,
            phonological_density_score=density_score,
            ending_audibility=round(ending_aud, 4),
            predicted_stress_class=stress_cls,
            amsv_synced=synced,
        )
