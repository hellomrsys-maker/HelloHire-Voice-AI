"""
Cantonese Matrix Bridge
Direct synchronous physical memory interface conforming to
The Zero-Bridge Synchronous Memory Rule.
Allocates / wraps the 64-byte Atomic Memory State Vector (AMSV) with magic 0x59554554 ("YUET").
"""

import struct
from typing import Dict, Any, Optional

CANTONESE_MAGIC_BYTES = b"YUET"
CANTONESE_MAGIC_INT = 0x59554554
AMSV_TOTAL_SIZE = 64

class CantoneseMatrixBridge:
    """
    Direct zero-bridge hardware synchronization bridge for Cantonese.
    """

    def __init__(self, memory_buffer: Optional[bytearray] = None):
        if memory_buffer is not None:
            if len(memory_buffer) < AMSV_TOTAL_SIZE:
                raise ValueError(f"Buffer must be at least {AMSV_TOTAL_SIZE} bytes")
            self.buffer = memory_buffer
        else:
            self.buffer = bytearray(AMSV_TOTAL_SIZE)
            
        self._initialize_header()

    def _initialize_header(self) -> None:
        """Initializes the 64-byte AMSV header directly in-place."""
        self.buffer[0:4] = CANTONESE_MAGIC_BYTES
        self.buffer[4] = 0x01  # Major version
        self.buffer[5] = 0x00  # Minor version
        self.buffer[6] = 0x01  # Engine mode: Inference
        self.buffer[7] = 0x01  # Dialect: Hong Kong Cantonese / HKSCS

    def verify_magic(self) -> bool:
        """Verifies that the 4-byte ASCII magic matches 'YUET'."""
        return bytes(self.buffer[0:4]) == CANTONESE_MAGIC_BYTES

    def get_magic_uint32(self) -> int:
        """Returns the magic constant as a big-endian 32-bit unsigned integer."""
        return struct.unpack(">I", self.buffer[0:4])[0]

    def read_state(self) -> Dict[str, Any]:
        """Reads all physical fields from the 64-byte shared memory state."""
        confidence = struct.unpack("<f", self.buffer[24:28])[0]
        return {
            "magic": bytes(self.buffer[0:4]).decode("ascii", errors="replace"),
            "version": f"{self.buffer[4]}.{self.buffer[5]}",
            "engine_mode": self.buffer[6],
            "dialect_mode": self.buffer[7],
            "syntax_status": self.buffer[18],
            "doc_accuracy": self.buffer[19],
            "tone_orthography": self.buffer[20],
            "aspect_marker_flag": self.buffer[21],
            "register_tier": self.buffer[22],
            "sfp_concord_flag": self.buffer[23],
            "confidence_score": round(confidence, 4),
            "sub_ais_active": {
                "syntax": bool(self.buffer[52]),
                "phonology": bool(self.buffer[53]),
                "pragmatic": bool(self.buffer[54]),
                "editorial": bool(self.buffer[55])
            }
        }
