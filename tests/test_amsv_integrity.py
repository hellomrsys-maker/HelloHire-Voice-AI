"""
test_amsv_integrity.py — Audits AMSV memory layout, Zero-Bridge boundaries, and checkpoint state sync.
"""

import os
import struct
import pytest
from amsv.python.amsv_integrity_checker import AMSVIntegrityChecker, AMSV_REGIONS
from training.checkpoint_sync import CheckpointManager


def test_amsv_layout_audit_zero_collisions():
    errors = AMSVIntegrityChecker.audit_layout()
    assert errors == [], f"AMSV layout audit revealed collisions/gaps: {errors}"


def test_amsv_validation_and_snapshots():
    buf = bytearray(64)
    # Populate some regions with realistic Q16 values
    struct.pack_into("<HHHH", buf, 0x10, 1000, 2000, 3000, 4000)
    struct.pack_into("<HHHH", buf, 0x38, 5000, 6000, 7000, 8000)

    is_valid, issues = AMSVIntegrityChecker.validate_buffer(buf)
    assert is_valid
    assert issues == []

    snapshots = AMSVIntegrityChecker.snapshot_regions(buf)
    assert len(snapshots) == len(AMSV_REGIONS)
    assert "COGNITIVE_BANK_ALPHA_ALIE" in snapshots


def test_checkpoint_manager_amsv_state_save_load(tmp_path):
    mgr = CheckpointManager(checkpoint_dir=str(tmp_path))

    # Initialize a 64-byte AMSV state
    original_buf = bytearray(64)
    for i in range(64):
        original_buf[i] = (i * 3 + 7) & 0xFF

    filepath = mgr.save_amsv_state(original_buf, filename="test_amsv.bin")
    assert os.path.exists(filepath)
    assert os.path.exists(filepath + ".json")

    # Restore into fresh buffer
    restored_buf = bytearray(64)
    mgr.load_amsv_state(restored_buf, filepath)

    assert bytes(restored_buf) == bytes(original_buf)
