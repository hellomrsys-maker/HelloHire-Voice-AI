"""
amsv_integrity_checker.py — AMSV Offset Boundary Integrity Validator

Validates that all engine writes to the 64-byte AMSV buffer
stay within their allocated byte boundaries without overlapping.

AMSV Offset Map (canonical):
  0x00-0x0F  (16 bytes) — Header: sequence_counter, active_bitmask, status
  0x10-0x17  (8 bytes)  — ccte_cog_bank_alpha: Think|Focus|Recall|Creativity (Q1.15 x4)
  0x18-0x1F  (8 bytes)  — ccte_cog_bank_beta: Imagi|Analy|Verbal|Emoti (Q1.15 x4)
  0x20-0x27  (8 bytes)  — rsse_scenario_state / ALIE listening state
  0x28-0x2F  (8 bytes)  — aeee_params / ECSE social state
  0x30-0x37  (8 bytes)  — maio_trajectory / PMCE persuasion state
  0x38-0x3F  (8 bytes)  — Reserved / HCTE cognitive tension
"""

from __future__ import annotations
import struct
from dataclasses import dataclass
from typing import List, Tuple, Dict

@dataclass
class AMSVRegion:
    engine: str
    offset: int       # byte offset (hex)
    size: int         # bytes
    description: str

# Canonical AMSV allocation map
AMSV_REGIONS: List[AMSVRegion] = [
    AMSVRegion("HEADER",  0x00, 16, "Sequence counter, active bitmask, system status"),
    AMSVRegion("CCTE",    0x10,  8, "ccte_cog_bank_alpha: Think|Focus|Recall|Creativity"),
    AMSVRegion("CCTE",    0x18,  8, "ccte_cog_bank_beta: Imagination|Analytical|Verbal|Emotional"),
    AMSVRegion("RSSE/ALIE", 0x20, 8, "RSSE scenario state or ALIE listening session state"),
    AMSVRegion("AEEE/ECSE", 0x28, 8, "AEEE IRT params or ECSE social calibration state"),
    AMSVRegion("MAIO/PMCE", 0x30, 8, "MAIO trajectory or PMCE persuasion index state"),
    AMSVRegion("HCTE",    0x38,  8, "HCTE: optimism|pessimism|cognitive_tension|solution_density"),
]

AMSV_TOTAL_SIZE = 64  # bytes

def check_region_overlap() -> List[str]:
    """Verifies no two regions overlap in the 64-byte AMSV."""
    errors = []
    for i, r1 in enumerate(AMSV_REGIONS):
        for j, r2 in enumerate(AMSV_REGIONS):
            if i >= j:
                continue
            r1_end = r1.offset + r1.size
            r2_end = r2.offset + r2.size
            if r1.offset < r2_end and r2.offset < r1_end:
                errors.append(
                    f"OVERLAP: {r1.engine}[0x{r1.offset:02X}-0x{r1_end:02X}] "
                    f"overlaps with {r2.engine}[0x{r2.offset:02X}-0x{r2_end:02X}]"
                )
    return errors


def check_bounds() -> List[str]:
    """Verifies all regions fit within the 64-byte AMSV."""
    errors = []
    for r in AMSV_REGIONS:
        end = r.offset + r.size
        if end > AMSV_TOTAL_SIZE:
            errors.append(
                f"OVERFLOW: {r.engine} region ends at 0x{end:02X} "
                f"but AMSV is only {AMSV_TOTAL_SIZE} bytes"
            )
    return errors


def validate_write(buffer: bytearray, engine: str, offset: int, size: int) -> Tuple[bool, str]:
    """
    Called before any engine writes to verify the write is within its allocated region.
    Returns (is_valid, message).
    """
    if offset < 0 or offset + size > AMSV_TOTAL_SIZE:
        return False, f"{engine} write at 0x{offset:02X}+{size}B exceeds AMSV bounds"

    for region in AMSV_REGIONS:
        if engine.upper() in region.engine.upper():
            allowed_start = region.offset
            allowed_end = region.offset + region.size
            write_end = offset + size
            if offset >= allowed_start and write_end <= allowed_end:
                return True, "OK"
            else:
                return False, (
                    f"{engine} tried to write at 0x{offset:02X}+{size}B "
                    f"but its region is 0x{allowed_start:02X}-0x{allowed_end:02X}"
                )

    # Engine not in map — warn but allow
    return True, f"WARNING: {engine} has no registered AMSV region — write allowed but unmonitored"


def full_audit(buffer: bytearray) -> Dict[str, object]:
    """
    Reads the entire 64-byte buffer and parses each known region.
    Returns a human-readable snapshot of all AMSV state.
    """
    if len(buffer) < 64:
        return {"error": f"Buffer too small: {len(buffer)} bytes (need 64)"}

    result = {}
    for region in AMSV_REGIONS:
        raw = buffer[region.offset: region.offset + region.size]
        values = struct.unpack_from("<HHHH", buffer, region.offset)
        decoded = [round(v / 65535.0, 4) for v in values]
        result[f"0x{region.offset:02X}_{region.engine}"] = {
            "description": region.description,
            "raw_uint16": list(values),
            "decoded_float": decoded
        }

    overlap_errors = check_region_overlap()
    bound_errors = check_bounds()
    result["integrity"] = {
        "overlap_errors": overlap_errors,
        "bound_errors": bound_errors,
        "status": "CLEAN" if not overlap_errors and not bound_errors else "ERRORS_FOUND"
    }
    return result


def print_amsv_report(buffer: bytearray) -> None:
    report = full_audit(buffer)
    print("\n" + "=" * 64)
    print("  AMSV 64-BYTE INTEGRITY REPORT")
    print("=" * 64)
    for key, val in report.items():
        if key == "integrity":
            status = val["status"]
            print(f"\n  [INTEGRITY] {status}")
            for e in val["overlap_errors"] + val["bound_errors"]:
                print(f"    ⚠  {e}")
        else:
            decoded = val["decoded_float"]
            print(f"\n  [{key}]")
            print(f"    {val['description']}")
            print(f"    Values: {decoded}")
    print("=" * 64 + "\n")
