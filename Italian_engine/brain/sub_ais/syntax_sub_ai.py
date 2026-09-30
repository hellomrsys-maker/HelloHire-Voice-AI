"""
Italian Engine — Syntax Sub-AI
Responsible for SVO clausal syntax, null-subject (pro-drop) evaluation, and subjunctive concord.
Under the Zero-Bridge Synchronous Memory Rule, writes directly to AMSV byte offsets 18 and 52.
"""

from typing import Dict, Any, List
from ..skills.tokenization import tokenize_words
from ..skills.pos_tagging import tag_pos
from ..analysis.clitic_placement_analyzer import CliticPlacementAnalyzer
from ..analysis.subjunctive_concord_analyzer import SubjunctiveConcordAnalyzer

class ItalianSyntaxSubAI:
    """Sub-AI dedicated to Italian syntactic structure and clausal concord."""

    def __init__(self):
        self.clitic_analyzer = CliticPlacementAnalyzer()
        self.subj_analyzer = SubjunctiveConcordAnalyzer()

    def process(self, text: str, amsv_buffer: bytearray) -> Dict[str, Any]:
        """
        Process Italian syntax and synchronously update AMSV buffer.
        Byte 18: syntax_flags
          Bit 0: SVO valid
          Bit 1: Pro-drop active
          Bit 2: Clitic cluster verified
          Bit 3: Subjunctive verified
        Byte 52: syntax_sub_ai_id = 1 (active)
        """
        tokens = tokenize_words(text)
        tags = tag_pos(tokens)
        
        has_verb = any(t["upos"] in {"VERB", "AUX"} for t in tags)
        has_explicit_subject = any(
            t["upos"] in {"NOUN", "PROPN"} or (t["upos"] == "PRON" and t["token"].lower() in {"io", "tu", "lui", "lei", "noi", "voi", "loro"})
            for t in tags
        )
        is_pro_drop = has_verb and not has_explicit_subject
        
        c_res = self.clitic_analyzer.analyze(text)
        s_res = self.subj_analyzer.analyze(text)
        
        flags = 0
        if has_verb:
            flags |= (1 << 0) # SVO valid
        if is_pro_drop:
            flags |= (1 << 1) # Pro-drop
        if c_res["is_valid"] and len(c_res.get("clusters_found", [])) > 0:
            flags |= (1 << 2) # Clitic cluster valid
        if s_res["is_valid"]:
            flags |= (1 << 3) # Subjunctive valid
            
        # Zero-bridge synchronous write
        if amsv_buffer is not None and len(amsv_buffer) >= 64:
            amsv_buffer[18] = flags
            amsv_buffer[52] = 1 # Active
            
        is_valid = c_res["is_valid"] and s_res["is_valid"]
        
        return {
            "sub_ai": "ItalianSyntaxSubAI",
            "status": "success",
            "has_verb": has_verb,
            "is_pro_drop": is_pro_drop,
            "clitic_analysis": c_res,
            "subjunctive_analysis": s_res,
            "flags": flags,
            "is_valid": is_valid
        }
