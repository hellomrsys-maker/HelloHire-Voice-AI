"""
Persian Matrix Bridge
Direct synchronous physical memory interface conforming to
The Zero-Bridge Synchronous Memory Rule.
Allocates / wraps the 64-byte Atomic Memory State Vector (AMSV) with magic 0x46415253 ("FARS").
"""

import struct
from typing import Dict, Any, Optional

PERSIAN_MAGIC_BYTES = b"FARS"
PERSIAN_MAGIC_INT = 0x46415253
AMSV_TOTAL_SIZE = 64

class PersianMatrixBridge:
    """
    Direct zero-bridge hardware synchronization bridge for Persian.
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
        self.buffer[0:4] = PERSIAN_MAGIC_BYTES
        self.buffer[4] = 0x01  # Major version
        self.buffer[5] = 0x00  # Minor version
        self.buffer[6] = 0x01  # Engine mode: Inference
        self.buffer[7] = 0x01  # Script mode: Perso-Arabic RTL

    def verify_magic(self) -> bool:
        """Verifies that the 4-byte ASCII magic matches 'FARS'."""
        return bytes(self.buffer[0:4]) == PERSIAN_MAGIC_BYTES

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
            "script_mode": self.buffer[7],
            "syntax_status": self.buffer[18],
            "dom_accuracy": self.buffer[19],
            "zwnj_orthography": self.buffer[20],
            "light_verb_flag": self.buffer[21],
            "taarof_register": self.buffer[22],
            "deference_flag": self.buffer[23],
            "confidence_score": round(confidence, 4),
            "sub_ais_active": {
                "syntax": bool(self.buffer[52]),
                "phonology": bool(self.buffer[53]),
                "pragmatic": bool(self.buffer[54]),
                "editorial": bool(self.buffer[55])
            }
        }
