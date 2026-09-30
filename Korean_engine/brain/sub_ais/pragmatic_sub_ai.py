"""
Korean Engine — Pragmatic Sub-AI
Responsible for speech levels (상대높임법), honorific concord, and social distance.
Under the Zero-Bridge Synchronous Memory Rule, writes directly to AMSV byte offsets 22, 23, and 54.
"""

from typing import Dict, Any
from ..skills.tokenization import split_sentences, tokenize_eojeol
from ..skills.pos_tagging import tag_pos
from ..skills.speech_level_engine import classify_speech_level, audit_speech_level_consistency
from ..skills.honorific_engine import analyze_honorific_concord

class KoreanPragmaticSubAI:
    """Sub-AI dedicated to Korean pragmatic registers, speech levels, and honorific harmony."""

    def __init__(self):
        pass

    def process(self, text: str, amsv_buffer: bytearray) -> Dict[str, Any]:
        """
        Process Korean pragmatics and synchronously update AMSV buffer.
        Byte 22: speech_level_code (1=Hasipsio, 2=Haeyo, 3=Hage, 4=Hao, 5=Haera, 6=Hae, 7=Mixed clash)
        Byte 23: honorific_concord_flags
          Bit 0: -(으)시- present
          Bit 1: 께서 present
          Bit 2: Lexical honorific present
          Bit 3: Concord clash error
        Byte 54: pragmatic_sub_ai_id = 1 (active)
        """
        sentences = split_sentences(text)
        if not sentences:
            sentences = [text]
            
        audit = audit_speech_level_consistency(sentences)
        
        # Primary level mapping
        level_map = {
            "hasipsio": 1, "haeyo": 2, "hage": 3,
            "hao": 4, "haera": 5, "hae": 6, "neutral": 0
        }
        level_code = 7 if audit["is_clash"] else level_map.get(audit["primary_level"], 0)
        
        # Honorific concord
        tokens = tokenize_eojeol(text)
        tags = tag_pos(tokens)
        hon_res = analyze_honorific_concord(tokens, tags)
        
        hon_flags = 0
        if hon_res["has_honorific_predicate"]:
            hon_flags |= (1 << 0)
        if hon_res["has_honorific_particle"]:
            hon_flags |= (1 << 1)
        if len(hon_res["lexical_honorific_nouns"]) > 0:
            hon_flags |= (1 << 2)
        if not hon_res["is_harmonious"]:
            hon_flags |= (1 << 3)
            
        # Zero-bridge synchronous write
        if amsv_buffer is not None and len(amsv_buffer) >= 64:
            amsv_buffer[22] = level_code
            amsv_buffer[23] = hon_flags
            amsv_buffer[54] = 1 # Active
            
        return {
            "sub_ai": "KoreanPragmaticSubAI",
            "status": "success",
            "speech_level": audit["primary_level"],
            "speech_level_code": level_code,
            "is_clash": audit["is_clash"],
            "honorific_concord": hon_res,
            "flags": hon_flags,
            "is_valid": not audit["is_clash"] and hon_res["is_harmonious"]
        }
