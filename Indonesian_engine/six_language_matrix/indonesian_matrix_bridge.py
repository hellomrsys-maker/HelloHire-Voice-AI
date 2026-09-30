"""
Indonesian Engine — Six-Language Matrix Bridge
Maintains zero-bridge memory synchronization on the 64-byte Atomic Memory State Vector (AMSV).
Magic constant: 0x494E444F ("INDO")
"""

import struct
from typing import Dict, Any, Optional

INDONESIAN_AMSV_MAGIC = 0x494E444F  # "INDO" in ASCII Little-Endian
INDONESIAN_AMSV_SIZE = 64

class IndonesianMatrixBridge:
    """
    Direct in-place memory bridge for Indonesian language engine state.
    Under The Zero-Bridge Synchronous Memory Rule, writes directly to shared byte offsets.
    """

    def __init__(self, shared_buffer: Optional[bytearray] = None):
        if shared_buffer is not None:
            if len(shared_buffer) < INDONESIAN_AMSV_SIZE:
                raise ValueError(f"Buffer must be at least {INDONESIAN_AMSV_SIZE} bytes")
            self.buffer = shared_buffer
        else:
            self.buffer = bytearray(INDONESIAN_AMSV_SIZE)
        self._initialize_header()

    def _initialize_header(self) -> None:
        """Write magic header and initial Sub-AI active flags."""
        struct.pack_into("<I", self.buffer, 0, INDONESIAN_AMSV_MAGIC)
        struct.pack_into("<I", self.buffer, 4, 0x00010000) # v1.0.0
        # Enable all 4 Sub-AIs by default (offsets 52..55)
        self.buffer[52] = 1 # Syntax Sub-AI
        self.buffer[53] = 1 # Phonology Sub-AI
        self.buffer[54] = 1 # Pragmatic Sub-AI
        self.buffer[55] = 1 # Editorial Sub-AI

    def update_metrics(
        self,
        token_count: int,
        sentence_count: int,
        clause_type_mask: int = 0,
        syntax_flags: int = 0,
        morphology_flags: int = 0,
        phonology_flags: int = 0,
        aspect_flags: int = 0,
        register_tier: int = 0,
        pragmatic_flags: int = 0,
        confidence: float = 1.0
    ) -> None:
        """Update metrics in-place within the physical 64-byte AMSV."""
        struct.pack_into("<I", self.buffer, 8, token_count)
        struct.pack_into("<I", self.buffer, 12, sentence_count)
        struct.pack_into("<H", self.buffer, 16, clause_type_mask)
        self.buffer[18] = syntax_flags & 0xFF
        self.buffer[19] = morphology_flags & 0xFF
        self.buffer[20] = phonology_flags & 0xFF
        self.buffer[21] = aspect_flags & 0xFF
        self.buffer[22] = register_tier & 0xFF
        self.buffer[23] = pragmatic_flags & 0xFF
        struct.pack_into("<f", self.buffer, 24, float(confidence))

    def read_metrics(self) -> Dict[str, Any]:
        """Read current state directly from the 64-byte AMSV."""
        magic = struct.unpack_from("<I", self.buffer, 0)[0]
        version = struct.unpack_from("<I", self.buffer, 4)[0]
        token_count = struct.unpack_from("<I", self.buffer, 8)[0]
        sentence_count = struct.unpack_from("<I", self.buffer, 12)[0]
        clause_mask = struct.unpack_from("<H", self.buffer, 16)[0]
        syntax_flags = self.buffer[18]
        morph_flags = self.buffer[19]
        phon_flags = self.buffer[20]
        aspect_flags = self.buffer[21]
        reg_tier = self.buffer[22]
        prag_flags = self.buffer[23]
        confidence = struct.unpack_from("<f", self.buffer, 24)[0]
        
        sub_ai_statuses = {
            "syntax": bool(self.buffer[52]),
            "phonology": bool(self.buffer[53]),
            "pragmatic": bool(self.buffer[54]),
            "editorial": bool(self.buffer[55])
        }
        
        return {
            "is_magic_valid": magic == INDONESIAN_AMSV_MAGIC,
            "version": version,
            "token_count": token_count,
            "sentence_count": sentence_count,
            "clause_type_mask": clause_mask,
            "syntax_flags": syntax_flags,
            "morphology_flags": morph_flags,
            "phonology_flags": phon_flags,
            "aspect_flags": aspect_flags,
            "register_tier": reg_tier,
            "pragmatic_flags": prag_flags,
            "confidence": round(confidence, 3),
            "sub_ai_statuses": sub_ai_statuses
        }
