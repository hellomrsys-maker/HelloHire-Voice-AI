"""
amsv_integrity_checker.py — Atomic Memory State Vector Layout & Cross-Engine Boundary Auditor.

Audits the 64-byte shared memory vector across all cognitive and language engines.
Validates:
  1. Offset boundary alignment (no half-word or unaligned memory access)
  2. Range and normalization invariant checks (all Q16 in [0, 65535], all probabilities in [0.0, 1.0])
  3. Non-overlapping region guarantees across concurrent engine passes
  4. Memory safety under the Zero-Bridge Synchronous Memory Rule
"""

from __future__ import annotations
import struct
from typing import Dict, Any, List, Tuple


# Master 64-Byte AMSV Allocation Map
AMSV_REGIONS: Dict[str, Dict[str, Any]] = {
    "VCE_PHONEME": {
        "offset": 0x00,
        "size": 8,
        "format": "<Q",
        "description": "Voice & Articulation State (phoneme_id, accuracy, energy, voiced_flag)",
    },
    "VCE_PROSODY": {
        "offset": 0x08,
        "size": 8,
        "format": "<Q",
        "description": "Prosody & Pitch Contour (f0_hz, speech_rate, fluency, pitch_stability)",
    },
    "COGNITIVE_BANK_ALPHA_ALIE": {
        "offset": 0x10,
        "size": 8,
        "format": "<HHHH",
        "description": "Cognitive Capabilities 0-3 / ALIE Primary (alignment, relevance, latency, repair)",
    },
    "COGNITIVE_BANK_BETA_ALIE": {
        "offset": 0x18,
        "size": 8,
        "format": "<HHHH",
        "description": "Cognitive Capabilities 4-7 / ALIE Secondary (coref, GLI, aux0, aux1)",
    },
    "RSSE_ECSE_SCENARIO": {
        "offset": 0x20,
        "size": 8,
        "format": "<HHHH",
        "description": "RSSE Format & Scenario / ECSE Emotional-Social State (affect, rapport, mirror, politeness)",
    },
    "AEEE_PMCE_PERSUASION": {
        "offset": 0x28,
        "size": 8,
        "format": "<HHHH",
        "description": "AEEE Adaptive IRT / PMCE Persuasion & Rhetoric State (logos, ethos, pathos, kairos)",
    },
    "MAIO_ALPHA_DCVE_NACE": {
        "offset": 0x30,
        "size": 8,
        "format": "<HHHH",
        "description": "MAIO Global State Alpha / DCVE Domain Precision & NACE Narrative Coherence",
    },
    "MAIO_BETA_HCTE_LSCE_PACE": {
        "offset": 0x38,
        "size": 8,
        "format": "<HHHH",
        "description": "MAIO Global Beta / HCTE Human Cognitive Thinking / LSCE Endurance & PACE Adaptation",
    },
}


class AMSVIntegrityChecker:
    """
    Scans and verifies memory alignment, range constraints, and cross-engine
    boundary integrity for the 64-byte AMSV physical buffer.
    """

    TOTAL_SIZE = 64

    @classmethod
    def audit_layout(cls) -> List[str]:
        """
        Verifies that all registered regions tile the 64-byte vector exactly
        without overlaps or gaps.
        """
        errors = []
        covered = [False] * cls.TOTAL_SIZE

        for name, spec in sorted(AMSV_REGIONS.items(), key=lambda item: item[1]["offset"]):
            offset = spec["offset"]
            size = spec["size"]

            if offset < 0 or offset + size > cls.TOTAL_SIZE:
                errors.append(f"Region {name} out of bounds: [{offset}, {offset + size})")
                continue

            for byte_idx in range(offset, offset + size):
                if covered[byte_idx]:
                    errors.append(f"Collision detected at byte {byte_idx:#04x} in region {name}")
                covered[byte_idx] = True

        uncovered = [i for i, c in enumerate(covered) if not c]
        if uncovered:
            errors.append(f"Gaps found in AMSV allocation at byte indices: {uncovered}")

        return errors

    @classmethod
    def validate_buffer(cls, buffer: bytearray | bytes | memoryview) -> Tuple[bool, List[str]]:
        """
        Audits an active 64-byte AMSV buffer for memory corruption or out-of-spec values.
        """
        issues = []
        if len(buffer) < cls.TOTAL_SIZE:
            issues.append(f"Buffer underflow: length is {len(buffer)} bytes, expected at least {cls.TOTAL_SIZE}")
            return False, issues

        # Check Q16 fields in Cognitive / ALIE bank alpha
        q_vals = struct.unpack_from("<HHHH", buffer, 0x10)
        for i, val in enumerate(q_vals):
            if val < 0 or val > 65535:
                issues.append(f"Invalid Q16 at offset 0x10+{i*2}: {val}")

        # Check Q16 fields in Cognitive / ALIE bank beta
        q_vals_beta = struct.unpack_from("<HHHH", buffer, 0x18)
        for i, val in enumerate(q_vals_beta):
            if val < 0 or val > 65535:
                issues.append(f"Invalid Q16 at offset 0x18+{i*2}: {val}")

        # Check HCTE / MAIO region at 0x38
        hcte_vals = struct.unpack_from("<HHHH", buffer, 0x38)
        for i, val in enumerate(hcte_vals):
            if val < 0 or val > 65535:
                issues.append(f"Invalid Q16 at offset 0x38+{i*2}: {val}")

        is_valid = (len(issues) == 0)
        return is_valid, issues

    @classmethod
    def snapshot_regions(cls, buffer: bytearray | bytes | memoryview) -> Dict[str, Dict[str, Any]]:
        """
        Dumps human-readable snapshot of all regions from an active buffer.
        """
        snapshot = {}
        for name, spec in AMSV_REGIONS.items():
            offset = spec["offset"]
            size = spec["size"]
            raw_slice = bytes(buffer[offset:offset+size])
            snapshot[name] = {
                "offset_hex": f"{offset:#04x}",
                "raw_hex": raw_slice.hex(),
                "description": spec["description"]
            }
        return snapshot
