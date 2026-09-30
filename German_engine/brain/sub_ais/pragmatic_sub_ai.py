"""
German Engine — Pragmatic Sub-AI
Responsible for Duzen vs Siezen, honorific address, epistolary formulas, and modal particles.
Under the Zero-Bridge Synchronous Memory Rule, writes directly to AMSV byte offsets 22, 23, and 54.
"""

from typing import Dict, Any
from ..skills.tokenization import tokenize_words
from ..skills.pragmatics_engine import analyze_register
from ..skills.modal_particle_engine import analyze_modal_particles

class GermanPragmaticSubAI:
    """Sub-AI dedicated to German pragmatic registers and communicative stance."""

    def __init__(self):
        pass

    def process(self, text: str, amsv_buffer: bytearray) -> Dict[str, Any]:
        """
        Process German pragmatics and synchronously update AMSV buffer.
        Byte 22: register_type (0=Neutral, 1=Duzen, 2=Siezen, 3=Mixed Clash)
        Byte 23: modal_particle_count
        Byte 54: pragmatic_sub_ai_id = 1 (active)
        """
        tokens = tokenize_words(text)
        reg_res = analyze_register(text, tokens)
        particles_res = analyze_modal_particles(tokens)
        
        reg_type = 0
        if reg_res["register"] == "duzen":
            reg_type = 1
        elif reg_res["register"] == "siezen":
            reg_type = 2
        elif reg_res["register"] == "mixed_clash":
            reg_type = 3
            
        particle_count = min(255, particles_res["particle_count"])
        
        # Zero-bridge synchronous write
        if amsv_buffer is not None and len(amsv_buffer) >= 64:
            amsv_buffer[22] = reg_type
            amsv_buffer[23] = particle_count
            amsv_buffer[54] = 1 # Active
            
        return {
            "sub_ai": "GermanPragmaticSubAI",
            "status": "success",
            "register": reg_res["register"],
            "register_consistent": reg_res["is_consistent"],
            "modal_particles": particles_res["particles"],
            "modal_particle_count": particle_count,
            "reg_type_code": reg_type
        }
