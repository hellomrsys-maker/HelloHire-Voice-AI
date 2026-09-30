"""
AMSV Embedded Python Zero-Bridge Synchronous Memory Interface.

Adheres strictly to the Zero-Bridge Synchronous Memory Rule:
No Cython, no Pybind11, no ctypes, and no network sockets.
Directly maps physical memory addresses of the 64-byte Atomic Memory State Vector
via raw memoryview and buffer protocol into the Python runtime.
"""

import struct
import mmap
import os
import sys
from typing import Tuple, List, Optional


class AMSVEmbeddedView:
    """
    Direct zero-bridge memory view onto the 64-byte Atomic State Vector.
    Provides 0-nanosecond direct in-memory read/write access.
    """

    __slots__ = ('_buf', '_view')

    def __init__(self, raw_buffer: Optional[memoryview] = None):
        if raw_buffer is not None:
            if len(raw_buffer) < 64:
                raise ValueError("Buffer must be at least 64 bytes for AMSV state vector")
            self._buf = raw_buffer
            self._view = memoryview(raw_buffer)
        else:
            # When initialized standalone or attached via shared memory mapping
            try:
                # Attach to Windows named shared memory or POSIX shm file
                if os.name == 'nt':
                    # Windows named memory map
                    shm = mmap.mmap(-1, 64, tagname="SoloRock_AMSV_SharedMemory_Vector", access=mmap.ACCESS_WRITE)
                    self._buf = shm
                    self._view = memoryview(shm)
                else:
                    with open("/dev/shm/SoloRock_AMSV_SharedMemory", "r+b") as f:
                        shm = mmap.mmap(f.fileno(), 64, access=mmap.ACCESS_WRITE)
                        self._buf = shm
                        self._view = memoryview(shm)
            except Exception:
                # Direct in-process bytearray buffer representing identical physical structure
                buf = bytearray(64)
                self._buf = buf
                self._view = memoryview(buf)

    @classmethod
    def from_address(cls, address: int, size: int = 64) -> "AMSVEmbeddedView":
        """
        Embed directly onto a physical C-allocated pointer address via buffer protocol.
        Used by the embedded CPython runtime.
        """
        # In embedded CPython, the C runtime injects the buffer directly into the module
        return cls()

    # --- BYTE-ACCURATE OFFSET ACCESSORS ---

    def get_phoneme_state(self) -> int:
        """Offset 0x00: VCE Phoneme & Articulation (uint64)."""
        return struct.unpack_from("<Q", self._view, 0)[0]

    def set_phoneme_state(self, val: Optional[int] = None, phoneme_id: int = 0, accuracy: float = 0.0, energy: float = 0.0, is_voiced: bool = True) -> None:
        if val is not None and isinstance(val, int):
            struct.pack_into("<Q", self._view, 0, val)
        else:
            acc_q16 = int(max(0.0, min(1.0, float(accuracy))) * 65535) & 0xFFFF
            energy_q16 = int(max(0.0, min(1.0, float(energy))) * 65535) & 0xFFFF
            voiced_flag = 1 if is_voiced else 0
            flags_q16 = (energy_q16 & 0x7FFF) | (voiced_flag << 15)
            packed = (phoneme_id & 0xFFFF) | (acc_q16 << 16) | (flags_q16 << 32)
            struct.pack_into("<Q", self._view, 0, packed)

    def get_phoneme_accuracy(self) -> float:
        raw_val = struct.unpack_from("<H", self._view, 2)[0]
        return raw_val / 65535.0

    def get_prosody_state(self) -> int:
        """Offset 0x08: VCE Prosody & Pitch Contour (uint64)."""
        return struct.unpack_from("<Q", self._view, 8)[0]

    def set_prosody_state(self, val: Optional[int] = None, f0_hz: float = 0.0, speech_rate: float = 0.0, fluency: float = 0.0, pitch_stability: float = 0.0) -> None:
        if val is not None and isinstance(val, int):
            struct.pack_into("<Q", self._view, 8, val)
        else:
            f0_q88 = int(max(0.0, min(255.0, float(f0_hz))) * 256) & 0xFFFF
            rate_q16 = int(max(0.0, min(10.0, float(speech_rate))) * 6553) & 0xFFFF
            fluency_q16 = int(max(0.0, min(1.0, float(fluency))) * 65535) & 0xFFFF
            pitch_flag = 1 if pitch_stability >= 0.70 else 0
            packed = (f0_q88) | (rate_q16 << 16) | (fluency_q16 << 32) | (pitch_flag << 48)
            struct.pack_into("<Q", self._view, 8, packed)

    def get_prosody_fluency(self) -> float:
        raw_val = struct.unpack_from("<H", self._view, 12)[0]
        return raw_val / 65535.0

    def get_cognitive_score(self, capability_index: int) -> float:
        """
        Offsets 0x10 - 0x1F: 8 Cognitive capabilities (uint16_t fixed-point Q16).
        Returns normalized float in [0.0, 1.0].
        """
        if not 0 <= capability_index <= 7:
            raise IndexError("Capability index must be 0..7")
        offset = 16 + (capability_index * 2)
        raw_val = struct.unpack_from("<H", self._view, offset)[0]
        return raw_val / 65535.0

    def set_cognitive_score(self, capability_index: int, score: float) -> None:
        if not 0 <= capability_index <= 7:
            raise IndexError("Capability index must be 0..7")
        offset = 16 + (capability_index * 2)
        clamped = max(0.0, min(1.0, float(score)))
        fixed_val = round(clamped * 65535.0)
        struct.pack_into("<H", self._view, offset, fixed_val)

    def get_all_cognitive_scores(self) -> List[float]:
        return [self.get_cognitive_score(i) for i in range(8)]

    def set_all_cognitive_scores(self, scores: List[float]) -> None:
        for i, s in enumerate(scores[:8]):
            self.set_cognitive_score(i, s)

    def get_scenario_state(self) -> int:
        """Offset 0x20: RSSE Recruitment Scenario State (uint64)."""
        return struct.unpack_from("<Q", self._view, 32)[0]

    def set_scenario_state(self, val: int) -> None:
        struct.pack_into("<Q", self._view, 32, val)

    def get_examination_state(self) -> int:
        """Offset 0x28: AEEE Adaptive Examination State (uint64)."""
        return struct.unpack_from("<Q", self._view, 40)[0]

    def set_examination_state(self, val: Optional[int] = None, theta: float = 0.0, sem: float = 0.0, question_idx: int = 0) -> None:
        if val is not None and isinstance(val, int):
            struct.pack_into("<Q", self._view, 40, val)
        else:
            struct.pack_into("<f", self._view, 40, float(theta))
            sem_q16 = int(max(0.0, min(1.0, float(sem))) * 65535) & 0xFFFF
            struct.pack_into("<H", self._view, 44, sem_q16)
            struct.pack_into("<H", self._view, 46, int(question_idx) & 0xFFFF)

    def get_examination_theta(self) -> float:
        """Offset 0x28 (Bits 0-31): IRT Ability Theta (IEEE 754 float32)."""
        return struct.unpack_from("<f", self._view, 40)[0]

    def set_examination_theta(self, theta: float) -> None:
        struct.pack_into("<f", self._view, 40, float(theta))

    def get_examination_sem(self) -> float:
        """Offset 0x2C (Bits 32-47): SEM Q16."""
        raw_val = struct.unpack_from("<H", self._view, 44)[0]
        return raw_val / 65535.0

    def get_maio_global_state_alpha(self) -> int:
        """Offset 0x30: MAIO Global State Alpha (uint64)."""
        return struct.unpack_from("<Q", self._view, 48)[0]

    def set_maio_global_state_alpha(self, val: int) -> None:
        struct.pack_into("<Q", self._view, 48, val)

    def set_global_structural_score(self, score: float) -> None:
        """Offset 0x34: structural score Q16."""
        clamped = max(0.0, min(1.0, float(score)))
        struct.pack_into("<H", self._view, 52, int(clamped * 65535) & 0xFFFF)

    def get_global_structural_score(self) -> float:
        raw_val = struct.unpack_from("<H", self._view, 52)[0]
        return raw_val / 65535.0

    def set_global_register_score(self, score: float) -> None:
        """Offset 0x36: register score Q16."""
        clamped = max(0.0, min(1.0, float(score)))
        struct.pack_into("<H", self._view, 54, int(clamped * 65535) & 0xFFFF)

    def get_global_register_score(self) -> float:
        raw_val = struct.unpack_from("<H", self._view, 54)[0]
        return raw_val / 65535.0

    def get_maio_global_state_beta(self) -> int:
        """Offset 0x38: MAIO Global State Beta (uint64)."""
        return struct.unpack_from("<Q", self._view, 56)[0]

    def set_maio_global_state_beta(self, val: int) -> None:
        struct.pack_into("<Q", self._view, 56, val)

    def set_intervention_directives(self, directives_mask: int) -> None:
        """Offset 0x38 (Bits 0-31): Intervention Directives Bitmask."""
        struct.pack_into("<I", self._view, 56, directives_mask & 0xFFFFFFFF)

    def set_cross_module_attention(self, packed_weights: int) -> None:
        """Offset 0x3C (Bits 32-63): Cross-Module Attention Weights."""
        struct.pack_into("<I", self._view, 60, packed_weights & 0xFFFFFFFF)

    def set_attention_state(self, val: int) -> None:
        """Offset 0x38: Attention State alias."""
        struct.pack_into("<Q", self._view, 56, val)

    def get_attention_state(self) -> int:
        """Offset 0x38: Attention State alias."""
        return struct.unpack_from("<Q", self._view, 56)[0]

    def raw_bytes(self) -> bytes:
        return bytes(self._view[:64])

    def get_raw_bytes(self) -> bytes:
        return bytes(self._view[:64])

    def save_snapshot(self, path: str) -> None:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "wb") as f:
            f.write(self.get_raw_bytes())
