"""
Indonesian Engine — Syntax Sub-AI
Responsible for SVO constituent ordering, voice alternation (meN- active vs di- passive),
and numeral classifier phrase structure.
Under the Zero-Bridge Synchronous Memory Rule, writes directly to AMSV byte offsets 18 and 52.
"""

from typing import Dict, Any, List
from ..skills.tokenization import tokenize_words
from ..skills.pos_tagging import tag_pos
from ..analysis.voice_symmetry_analyzer import VoiceSymmetryAnalyzer
from ..analysis.classifier_concord_analyzer import ClassifierConcordAnalyzer

class IndonesianSyntaxSubAI:
    """Sub-AI dedicated to Indonesian clausal syntax, voice symmetry, and classifier phrases."""

    def __init__(self):
        self.voice_analyzer = VoiceSymmetryAnalyzer()
        self.clf_analyzer = ClassifierConcordAnalyzer()

    def process(self, text: str, amsv_buffer: bytearray) -> Dict[str, Any]:
        """
        Process Indonesian syntax and synchronously update AMSV buffer.
        Byte 18: syntax_flags
          Bit 0: SVO valid
          Bit 1: Active voice (meN-) detected
          Bit 2: Passive voice (di-) detected
          Bit 3: Numeral classifier phrase verified
        Byte 52: syntax_sub_ai_id = 1 (active)
        """
        tokens = tokenize_words(text)
        tags = tag_pos(tokens)
        
        has_verb = any(t["upos"] == "VERB" for t in tags)
        
        v_res = self.voice_analyzer.analyze(text)
        c_res = self.clf_analyzer.analyze(text)
        
        has_active = any(f["voice"] == "active" for f in v_res.get("voice_forms_found", []))
        has_passive = any(f["voice"] == "passive" for f in v_res.get("voice_forms_found", []))
        has_clf = len(c_res.get("checked_phrases", [])) > 0
        
        flags = 0
        if has_verb or len(tokens) >= 2:
            flags |= (1 << 0) # SVO valid
        if has_active:
            flags |= (1 << 1)
        if has_passive:
            flags |= (1 << 2)
        if has_clf and c_res["is_valid"]:
            flags |= (1 << 3)
            
        # Zero-bridge synchronous write
        if amsv_buffer is not None and len(amsv_buffer) >= 64:
            amsv_buffer[18] = flags
            amsv_buffer[52] = 1 # Active
            
        is_valid = v_res["is_valid"] and c_res["is_valid"]
        
        return {
            "sub_ai": "IndonesianSyntaxSubAI",
            "status": "success",
            "has_active_voice": has_active,
            "has_passive_voice": has_passive,
            "classifier_analysis": c_res,
            "voice_analysis": v_res,
            "flags": flags,
            "is_valid": is_valid
        }
