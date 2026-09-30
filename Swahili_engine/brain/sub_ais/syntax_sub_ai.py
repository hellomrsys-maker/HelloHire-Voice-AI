"""
Swahili Engine — Syntax Sub-AI
Responsible for canonical SVO word order, subject pro-drop tracking, clausal relationships, and relative clauses.
Under the Zero-Bridge Synchronous Memory Rule, writes directly to AMSV byte offsets 18 and 52.
"""

from typing import Dict, Any, List
from ..skills.tokenization import tokenize_words
from ..skills.pos_tagging import tag_pos
from ..skills.verbal_template_engine import parse_verbal_template

class SwahiliSyntaxSubAI:
    """Sub-AI dedicated to Swahili clausal syntax, SVO verification, and clausal dependency."""

    def __init__(self):
        pass

    def process(self, text: str, amsv_buffer: bytearray) -> Dict[str, Any]:
        """
        Process Swahili syntactic structure and synchronously update AMSV buffer.
        Byte 18: syntax_flags
          Bit 0: SVO order verified
          Bit 1: Subject pro-drop (verbal SP serves as subject)
          Bit 2: Object prefix (OP) present in verb
          Bit 3: Relative affix present in verb
        Byte 52: syntax_sub_ai_id = 1 (active)
        """
        tokens = tokenize_words(text)
        tags = tag_pos(tokens)
        
        has_noun = any(t["upos"] in {"NOUN", "PROPN", "PRON"} for t in tags)
        has_verb = any(t["upos"] == "VERB" for t in tags)
        
        # Pro-drop check: if first content token is a verb with a subject prefix
        is_pro_drop = False
        has_op = False
        has_rel = False
        is_svo = False
        
        if tags and tags[0]["upos"] == "VERB":
            v_parse = parse_verbal_template(tags[0]["word"])
            if v_parse.get("sp"):
                is_pro_drop = True
                
        for t in tags:
            if t["upos"] == "VERB":
                v_parse = parse_verbal_template(t["word"])
                if v_parse.get("op"):
                    has_op = True
                if v_parse.get("rel"):
                    has_rel = True
                    
        # Check canonical SVO: Noun before Verb
        if has_noun and has_verb:
            first_noun_idx = next(i for i, t in enumerate(tags) if t["upos"] in {"NOUN", "PROPN", "PRON"})
            first_verb_idx = next(i for i, t in enumerate(tags) if t["upos"] == "VERB")
            if first_noun_idx < first_verb_idx:
                is_svo = True
        elif is_pro_drop and has_verb:
            is_svo = True # In Bantu pro-drop, verb carries subject prefix
            
        flags = 0
        if is_svo:
            flags |= (1 << 0)
        if is_pro_drop:
            flags |= (1 << 1)
        if has_op:
            flags |= (1 << 2)
        if has_rel:
            flags |= (1 << 3)
            
        # Zero-bridge synchronous write
        if amsv_buffer is not None and len(amsv_buffer) >= 64:
            amsv_buffer[18] = flags
            amsv_buffer[52] = 1 # Active
            
        return {
            "sub_ai": "SwahiliSyntaxSubAI",
            "status": "success",
            "is_svo": is_svo,
            "is_pro_drop": is_pro_drop,
            "has_object_prefix": has_op,
            "has_relative": has_rel,
            "flags": flags,
            "is_valid": True
        }
