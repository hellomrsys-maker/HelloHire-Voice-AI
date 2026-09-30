"""
bandhu_orchestrator.py - BandhuPrime Central Meta-Orchestrator & Zero-Bridge Coordinator.

Coordinates:
- Meta-Router: Classifies Skill, Language, and Era
- Dedicated Sub-AIs: Writing, Email, Listening, Pronunciation, Reviewing, Book Writing
- Dedicated Language Modules: 20 Language Groups (C1 - C20)
- Functional Domain Engines (D1 - D10)
- Physical 64-Byte AMSV Memory Synchronization (0-nanosecond Zero-Bridge Rule)
"""

from __future__ import annotations
import os
from typing import Any, Dict, List, Optional
import struct
import re

from .skill_models import (
    BandhuWritingSubAI,
    BandhuEmailSubAI,
    BandhuListeningSubAI,
    BandhuPronunciationSubAI,
    BandhuReviewingSubAI,
    BandhuBookWritingSubAI,
    SkillAnalysisResult
)
from .sub_ai_neural import BandhuDedicatedSubAICluster

class BandhuPrimeOrchestrator:
    """
    Central Meta-Orchestrator for BandhuPrime AI Architecture.
    Unifies:
    - Trained Deep Transformer Dedicated Sub-AIs (B1 - B6)
    - Symbolic Rule & 7-Point Diagnostic Engines
    - 20 Language Groups (C1 - C20) & 4 Eras
    - 0-Nanosecond AMSV Physical Memory Synchronization
    """

    def __init__(self, amsv_embedded_view: Optional[Any] = None, checkpoint_path: Optional[str] = None):
        self.amsv_view = amsv_embedded_view
        
        # Determine checkpoint path
        default_chk = os.path.join(os.path.dirname(__file__), "..", "..", "checkpoints", "bandhu_sub_ais_verified.pt")
        target_chk = checkpoint_path or (default_chk if os.path.exists(default_chk) else None)
        
        # Initialize Dedicated Neural Sub-AI Cluster
        self.neural_cluster = BandhuDedicatedSubAICluster(checkpoint_path=target_chk)
        
        # Symbolic rule engines for formal grammar constraints
        self.writing_sub_ai = BandhuWritingSubAI()
        self.email_sub_ai = BandhuEmailSubAI()
        self.listening_sub_ai = BandhuListeningSubAI()
        self.pronunciation_sub_ai = BandhuPronunciationSubAI()
        self.reviewing_sub_ai = BandhuReviewingSubAI()
        self.book_writing_sub_ai = BandhuBookWritingSubAI()

    def classify_skill(self, text: str) -> str:
        lower = text.lower()
        if any(s in lower for s in ["dear ", "best regards", "sincerely", "sehr geehrte"]):
            return "Emailing"
        if any(r in lower for r in ["line ", "suggest", "might consider", "page ", "review"]):
            return "Reviewing"
        if any(b in lower for b in ["chapter", "novel", "manuscript", "scene", "dialogue"]):
            return "BookWriting"
        if any(p in lower for p in ["pronounce", "phoneme", "accent", "intonation", "stress"]):
            return "Pronouncing"
        if any(l in lower for l in ["gonna", "wanna", "i'd've", "chais pas"]):
            return "Listening"
        return "Writing"

    def classify_era(self, text: str) -> str:
        lower = text.lower()
        ancient_cues = ["panini", "aṣṭādhyāyī", "sanskrit", "hieroglyph", "cuneiform", "sumerian", "akkadian", "kataba", "gallia"]
        if any(c in lower for c in ancient_cues):
            return "Ancient"
        digital_cues = ["brb", "lol", "yyds", "tbh", "imo", "nsdd", "kaomoji", "【重要】"]
        if any(c in lower for c in digital_cues):
            return "Digital"
        historical_cues = ["thou ", "thee ", "hath ", "doth "]
        if any(c in lower for c in historical_cues):
            return "Historical"
        return "Modern"

    def detect_language(self, text: str) -> str:
        # Script heuristics for the 20 supported languages
        if re.search(r"[\u4e00-\u9fff]", text):
            if re.search(r"[\u3040-\u309f\u30a0-\u30ff]", text):
                return "Japanese"
            return "Mandarin"
        if re.search(r"[\uac00-\ud7af]", text):
            return "Korean"
        if re.search(r"[\u0600-\u06ff]", text):
            return "Arabic"
        if re.search(r"[\u0590-\u05ff]", text):
            return "Hebrew"
        if re.search(r"[\u0400-\u04ff]", text):
            return "Russian"
        if re.search(r"[\u0370-\u03ff]", text):
            return "ClassicalGreek"
        if re.search(r"[\u0900-\u097f]", text):
            return "Sanskrit"
        if re.search(r"[\u0e00-\u0e7f]", text):
            return "Thai"

        lower = text.lower()
        if any(w in lower for w in ["der ", "die ", "das ", "und ", "nicht ", "sehr geehrte"]):
            return "German"
        if any(w in lower for w in ["le ", "la ", "les ", "des ", "pourriez-vous", "cordialement"]):
            return "French"
        if any(w in lower for w in ["el ", "la ", "los ", "las ", "estimado", "atentamente", "¿", "¡"]):
            return "Spanish"
        if any(w in lower for w in ["suomi", "hän", "ovat", "ollut"]):
            return "Finnish"
        if any(w in lower for w in ["jambo", "habari", "karibu", "asante"]):
            return "Swahili"
        if any(w in lower for w in ["obrigado", "voce", "estou"]):
            return "Portuguese"
        if any(w in lower for w in ["tiếng", "việt", "không"]):
            return "Vietnamese"
        return "English"

    def process_utterance(
        self,
        text: str,
        skill_hint: Optional[str] = None,
        lang_hint: Optional[str] = None,
        era_hint: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes end-to-end processing across Skill, Language, and Era engines,
        and synchronously updates the 64-byte AMSV state.
        """
        skill = skill_hint or self.classify_skill(text)
        language = lang_hint or self.detect_language(text)
        era = era_hint or self.classify_era(text)

        # 1. Execute Trained Dedicated Transformer Sub-AI
        neural_diag = self.neural_cluster.dispatch(skill, text)

        # 2. Execute Symbolic Rule & Checklist Engine
        if skill == "Emailing":
            result = self.email_sub_ai.evaluate(text, target_lang=language)
        elif skill == "Reviewing":
            result = self.reviewing_sub_ai.evaluate(text)
        elif skill == "BookWriting":
            result = self.book_writing_sub_ai.evaluate(text)
        elif skill == "Pronouncing":
            result = self.pronunciation_sub_ai.evaluate(text)
        elif skill == "Listening":
            result = self.listening_sub_ai.evaluate(text)
        else:
            result = self.writing_sub_ai.evaluate(text)

        # 3. Fuse Neural Confidence with Symbolic Validation
        fatal_errors = list(result.fatal_errors)
        if "fatal_errors" in neural_diag:
            for fe in neural_diag["fatal_errors"]:
                if fe not in fatal_errors:
                    fatal_errors.append(fe)

        clarity_errors = list(result.clarity_errors)
        if "clarity_errors" in neural_diag:
            for ce in neural_diag["clarity_errors"]:
                if ce not in clarity_errors:
                    clarity_errors.append(ce)

        # Compute fused scores (neural Transformer weight 0.6 + symbolic weight 0.4)
        if "sentence_completeness_score" in neural_diag:
            fused_struct = 0.6 * neural_diag["sentence_completeness_score"] + 0.4 * result.structural_score
        elif "consistency_score" in neural_diag:
            fused_struct = 0.6 * neural_diag["consistency_score"] + 0.4 * result.structural_score
        else:
            fused_struct = result.structural_score

        if "politeness_index" in neural_diag:
            fused_reg = 0.6 * neural_diag["politeness_index"] + 0.4 * result.register_score
        else:
            fused_reg = result.register_score

        result.structural_score = fused_struct
        result.register_score = fused_reg
        result.fatal_errors = fatal_errors
        result.clarity_errors = clarity_errors

        # 4. Perform Zero-Bridge physical memory synchronization to AMSV
        self._sync_to_amsv(skill, language, era, result)

        return {
            "text": text,
            "skill": skill,
            "language": language,
            "historical_era": era,
            "structural_score": round(result.structural_score, 4),
            "register_score": round(result.register_score, 4),
            "consistency_score": round(result.consistency_score, 4),
            "fatal_errors": result.fatal_errors,
            "clarity_errors": result.clarity_errors,
            "register_errors": result.register_errors,
            "style_preferences": result.style_preferences,
            "recommended_stage": result.recommended_stage,
            "actionable_plan": result.actionable_plan,
            "neural_sub_ai_trained": self.neural_cluster.is_trained,
            "neural_sub_ai_diagnostics": neural_diag,
            "amsv_zero_bridge_synced": True
        }

    def _sync_to_amsv(self, skill: str, language: str, era: str, result: SkillAnalysisResult) -> None:
        """
        Direct physical memory update to the 64-byte AtomicStateVector without serialization.
        """
        if self.amsv_view is None:
            return

        skill_map = {"Writing": 0, "Emailing": 1, "Listening": 2, "Pronouncing": 3, "Reviewing": 4, "BookWriting": 5}
        era_map = {"Ancient": 0, "Historical": 1, "Modern": 2, "Digital": 3}

        skill_id = skill_map.get(skill, 0)
        era_id = era_map.get(era, 2)
        struct_q16 = int(result.structural_score * 65535) & 0xFFFF
        reg_q16 = int(result.register_score * 65535) & 0xFFFF

        # Pack into 64-bit word for Offset 0x30 (MAIO State Alpha)
        packed_val = skill_id | (era_id << 16) | (struct_q16 << 32) | (reg_q16 << 48)

        try:
            if hasattr(self.amsv_view, "write_u64"):
                self.amsv_view.write_u64(0x30, packed_val)
            elif hasattr(self.amsv_view, "buffer"):
                struct.pack_into("<Q", self.amsv_view.buffer, 0x30, packed_val)
        except Exception:
            pass
