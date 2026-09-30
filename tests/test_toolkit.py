"""
test_toolkit.py - End-to-End Test Suite for BandhuPrime Application Toolkit.
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from bandhu_toolkit import BandhuApplicationToolkit, SixLanguageMatrixBridge

def test_toolkit_full_flow():
    toolkit = BandhuApplicationToolkit()

    # 1. Test Writing Analysis
    writing_sample = "The linguist analyzed syntactic typology across ancient languages."
    res_w = toolkit.analyze_utterance(writing_sample, skill_hint="Writing")
    assert res_w["skill"] == "Writing"
    assert res_w["structural_score"] >= 0.80
    assert res_w["rust_engine_verified"] is True
    print("[PASS] Toolkit Writing Analysis Verified (Rust C-ABI active).")

    # 2. Test Email Analysis
    email_sample = "Dear Dr. Patel,\n\nCould you please review the attached document?\n\nBest regards,\nAlex"
    res_e = toolkit.analyze_utterance(email_sample, skill_hint="Emailing")
    assert res_e["skill"] == "Emailing"
    assert res_e["register_score"] >= 0.90
    assert len(res_e["fatal_errors"]) == 0
    print("[PASS] Toolkit Email Analysis Verified.")

    # 3. Test Editorial Review
    review_sample = "In line 42, the author might consider clarifying the relative clause."
    res_r = toolkit.review_editorial_text(review_sample)
    assert res_r["skill"] == "Reviewing"
    assert len(res_r["clarity_errors"]) == 0
    print("[PASS] Toolkit Editorial Review Verified.")

    # 4. Test Book Manuscript Audit
    book_sample = "He opened the door. The corridor was silent. She looked at him with quiet suspicion."
    res_b = toolkit.audit_book_manuscript(book_sample)
    assert res_b["skill"] == "BookWriting"
    assert res_b["consistency_score"] >= 0.70
    print("[PASS] Toolkit Book Manuscript Audit Verified.")


    # 5. Test Pronunciation & Julia Rhythm
    res_p = toolkit.coach_pronunciation("She walked home", vocalic_durations=[110.0, 50.0, 130.0, 45.0])
    assert res_p["rhythm_metrics"]["rhythm_class"] == "StressTimed"
    assert len(res_p["seven_step_correction_path"]) == 7
    print("[PASS] Toolkit Pronunciation & Julia Rhythm Verified.")

    # 6. Test Zero-Bridge AMSV Memory State
    amsv_state = toolkit.inspect_amsv_state()
    assert len(amsv_state["raw_hex"]) == 128  # 64 bytes = 128 hex chars
    print("[PASS] 64-Byte AMSV Zero-Bridge Synchronous Memory Verified.")

    print("\n================================================================================")
    print("  ALL BANDHUPRIME APPLICATION TOOLKIT TESTS PASSED WITH 100% SUCCESS!")
    print("================================================================================")

if __name__ == "__main__":
    test_toolkit_full_flow()
