import sys
import os
sys.path.insert(0, os.path.abspath("."))

from gra_voi.bandhu import BandhuPrimeOrchestrator

def test_bandhu_orchestrator():
    orch = BandhuPrimeOrchestrator()

    # 1. Email test
    email_sample = "Dear Dr. Patel, could you please review the attached document? Best regards, Alex."
    res_email = orch.process_utterance(email_sample)
    assert res_email["skill"] == "Emailing"
    assert res_email["register_score"] >= 0.90
    assert len(res_email["fatal_errors"]) == 0
    print("Email test passed:", res_email["skill"], "Score:", res_email["register_score"])

    # 2. Writing test
    writing_sample = "The research team published a definitive comparative analysis of historical syntax."
    res_writing = orch.process_utterance(writing_sample)
    assert res_writing["skill"] == "Writing"
    assert res_writing["structural_score"] >= 0.70
    print("Writing test passed:", res_writing["skill"], "Score:", res_writing["structural_score"])

    # 3. Ancient Era test
    ancient_sample = "Pāṇini formulated the Aṣṭādhyāyī comprising four thousand rules."
    res_ancient = orch.process_utterance(ancient_sample)
    assert res_ancient["historical_era"] == "Ancient"
    print("Ancient Era test passed:", res_ancient["historical_era"])

    # 4. Digital Era test
    digital_sample = "brb, that novel was yyds tbh"
    res_digital = orch.process_utterance(digital_sample)
    assert res_digital["historical_era"] == "Digital"
    print("Digital Era test passed:", res_digital["historical_era"])

    print("ALL BANDHUPRIME PYTHON TESTS PASSED WITH 100% SUCCESS!")

if __name__ == "__main__":
    test_bandhu_orchestrator()
