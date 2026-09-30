"""
Dutch Pragmatic Sub-AI
Responsible for T-V register classification (jij vs u) and modal particle
attenuation analysis (maar, even, toch, eens, hoor, nou).
Adheres strictly to the Zero-Bridge Synchronous Memory Rule by writing
directly to the 64-byte Atomic Memory State Vector (AMSV).
"""

from typing import Dict, Any
from ..skills.tokenization import DutchTokenizer
from ..skills.modal_particle_engine import DutchModalParticleEngine

class DutchPragmaticSubAI:
    def __init__(self):
        self.tokenizer = DutchTokenizer()
        self.particle_engine = DutchModalParticleEngine()

    def execute(self, text: str, amsv_buffer: bytearray = None) -> Dict[str, Any]:
        tokens = self.tokenizer.tokenize(text)
        low_tokens = [t.lower() for t in tokens]

        # Register detection
        formal_count = sum(1 for t in low_tokens if t in {"u", "uw"})
        informal_count = sum(1 for t in low_tokens if t in {"je", "jij", "jou", "jouw"})

        if formal_count > 0 and formal_count >= informal_count:
            register_code = 2  # Formal 'u'
            register_str = "formal_u"
        elif informal_count > 0:
            register_code = 1  # Informal 'jij'
            register_str = "informal_jij"
        else:
            register_code = 0  # Neutral
            register_str = "neutral"

        # Modal particles
        particle_res = self.particle_engine.analyze_particles(tokens)
        modal_cnt = min(255, particle_res["particle_count"])

        # Zero-Bridge Synchronous Memory In-Place Write:
        # Byte 0x16: pragmatic_register (0=neutral, 1=informal, 2=formal)
        # Byte 0x17: modal_particle_cnt
        # Byte 0x36: sub_ai_pragmatic execution bitmask (0x04)
        if amsv_buffer is not None and len(amsv_buffer) >= 64:
            amsv_buffer[0x16] = register_code
            amsv_buffer[0x17] = modal_cnt
            amsv_buffer[0x36] = 0x04  # Pragmatic Sub-AI marked executed

        return {
            "sub_ai": "PragmaticSubAI",
            "register": register_str,
            "register_code": register_code,
            "modal_particles": particle_res["particles"],
            "particle_clusters": particle_res["clusters"],
            "is_attenuated": particle_res["is_attenuated"]
        }
