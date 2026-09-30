"""
test_vocal_cord_frequency_engine.py - Unit tests for Vocal Cord Biophysics & Situational Frequency Modulation.

Validates:
1. Multi-record statistical envelopes (min_floor, average_mean, max_nominal, absolute_ceiling).
2. Demographic speaker cohorts (low_register ~110Hz, medium_register ~188Hz, high_register ~240Hz).
3. Relative situational multipliers across all 6 scenarios for "It's okay".
4. Zero-bridge 64-byte AMSV memory vector synchronization.
"""

from English_engine.brain.Analysis.vocal_cord_frequency_engine import (
    VocalCordFrequencyEngine,
    SituationalScenario,
    SpeakerRegisterCohort
)
from amsv.python.amsv_embedded import AMSVEmbeddedView


def test_vocal_cord_benchmark_its_okay_multirecord():
    engine = VocalCordFrequencyEngine()
    result = engine.analyze_benchmark_phrase_all_scenarios("It's okay")

    assert result["total_scenarios"] == 6
    scenarios = result["scenarios_breakdown"]

    # 1. Calm Reassurance Multi-Record Envelope
    calm = scenarios["CALM_REASSURANCE"]
    assert calm["frequency_envelope_hz"]["min_f0_floor"] == 140.0
    assert calm["frequency_envelope_hz"]["average_f0_mean"] == 188.0
    assert calm["frequency_envelope_hz"]["max_f0_nominal"] == 215.0
    assert calm["frequency_envelope_hz"]["absolute_peak_ceiling"] == 260.0
    assert calm["relative_multiplier"] == 1.0
    assert calm["glottal_roughness_envelope"]["average"] == 0.15

    # 2. Aggressive Violence Maximum Ceiling & Relative Multiplier
    viol = scenarios["AGGRESSIVE_VIOLENCE"]
    assert viol["frequency_envelope_hz"]["max_f0_nominal"] == 440.0
    assert viol["frequency_envelope_hz"]["absolute_peak_ceiling"] == 520.0
    assert viol["relative_multiplier"] == 1.85
    assert viol["glottal_roughness_envelope"]["average"] == 0.96
    assert viol["post_utterance_pause_ms"] == 220

    # 3. Deep Melancholy Low Floor
    mel = scenarios["DEEP_MELANCHOLY"]
    assert mel["frequency_envelope_hz"]["min_f0_floor"] == 65.0
    assert mel["frequency_envelope_hz"]["average_f0_mean"] == 118.0
    assert mel["relative_multiplier"] == 0.68
    assert mel["post_utterance_pause_ms"] == 880


def test_speaker_cohort_adaptation():
    engine = VocalCordFrequencyEngine()

    # Compare Low vs Medium vs High register speakers for "It's okay" under Violence
    low_res = engine.modulate_phrase("It's okay", SituationalScenario.AGGRESSIVE_VIOLENCE, speaker_cohort=SpeakerRegisterCohort.LOW_REGISTER)
    med_res = engine.modulate_phrase("It's okay", SituationalScenario.AGGRESSIVE_VIOLENCE, speaker_cohort=SpeakerRegisterCohort.MEDIUM_REGISTER)
    high_res = engine.modulate_phrase("It's okay", SituationalScenario.AGGRESSIVE_VIOLENCE, speaker_cohort=SpeakerRegisterCohort.HIGH_REGISTER)

    assert low_res.speaker_scaled_f0_hz < med_res.speaker_scaled_f0_hz < high_res.speaker_scaled_f0_hz
    assert low_res.speaker_scaled_f0_hz == 240.0
    assert med_res.speaker_scaled_f0_hz == 365.0
    assert high_res.speaker_scaled_f0_hz == 465.0

    # Custom baseline speaker (e.g. 100 Hz baritone)
    custom_res = engine.modulate_phrase("It's okay", SituationalScenario.AGGRESSIVE_VIOLENCE, custom_baseline_f0_hz=100.0)
    assert custom_res.speaker_scaled_f0_hz == 185.0  # 100 * 1.85


def test_vocal_cord_amsv_zero_bridge_sync():
    amsv = AMSVEmbeddedView()
    engine = VocalCordFrequencyEngine(amsv_view=amsv)

    res = engine.modulate_phrase("Step back right now!", SituationalScenario.AGGRESSIVE_VIOLENCE)
    assert res.amsv_synced is True

    assert amsv._view.nbytes == 64
    assert amsv._view[8] > 150  # Pitch byte for 365 Hz
    assert amsv._view[16] > 200 # High roughness byte
    assert amsv._view[20] == 0x23 # Scenario stance byte


def test_word_frequency_trajectory():
    engine = VocalCordFrequencyEngine()
    res = engine.modulate_phrase("It is completely under control.", SituationalScenario.CONFIDENCE_AUTHORITY)

    assert len(res.words) == 5
    for w in res.words:
        assert w.duration_ms >= 100
        assert w.open_quotient_oq == 0.50
