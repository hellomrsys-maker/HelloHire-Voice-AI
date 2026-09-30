"""
Korean Engine — Syntax Sub-AI
Responsible for SOV head-final structure, topic/subject marking, and particle binding.
Under the Zero-Bridge Synchronous Memory Rule, writes directly to AMSV byte offsets 18 and 52.
"""

from typing import Dict, Any, List
from ..skills.tokenization import tokenize_eojeol
from ..skills.pos_tagging import tag_pos

class KoreanSyntaxSubAI:
    """Sub-AI dedicated to Korean clausal syntax and SOV dependency tracking."""

    def __init__(self):
        pass

    def process(self, text: str, amsv_buffer: bytearray) -> Dict[str, Any]:
        """
        Process Korean syntactic structure and synchronously update AMSV buffer.
        Byte 18: syntax_flags
          Bit 0: Head-final verb detected
          Bit 1: Topic particle (은/는) present
          Bit 2: Subject particle (이/가/께서) present
          Bit 3: Object particle (을/를) present
        Byte 52: syntax_sub_ai_id = 1 (active)
        """
        tokens = tokenize_eojeol(text)
        tags = tag_pos(tokens)
        
        has_final_verb = len(tags) > 0 and tags[-1]["upos"] == "VERB"
        has_topic = any(t.get("particle") in {"은", "는"} for t in tags)
        has_subject = any(t.get("particle") in {"이", "가", "께서"} for t in tags)
        has_object = any(t.get("particle") in {"을", "를"} for t in tags)
        
        flags = 0
        if has_final_verb:
            flags |= (1 << 0)
        if has_topic:
            flags |= (1 << 1)
        if has_subject:
            flags |= (1 << 2)
        if has_object:
            flags |= (1 << 3)
            
        # Zero-bridge synchronous write
        if amsv_buffer is not None and len(amsv_buffer) >= 64:
            amsv_buffer[18] = flags
            amsv_buffer[52] = 1 # Active
            
        return {
            "sub_ai": "KoreanSyntaxSubAI",
            "status": "success",
            "is_head_final": has_final_verb,
            "has_topic": has_topic,
            "has_subject": has_subject,
            "has_object": has_object,
            "flags": flags,
            "is_valid": True
        }
