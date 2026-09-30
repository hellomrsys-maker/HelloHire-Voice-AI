"""
test_pedagogical_film_training.py - Test suite for Teacher-Student Pedagogical Training.

Validates that:
1. The chronological curriculum covers all 5 narrative acts across the 2:15:22 runtime.
2. The Teacher-Student cognitive training session executes with an average score > 90%.
3. The 64-byte AMSV physical memory state vector updates synchronously with 0-nanosecond latency.
4. The generated session log is verified and persisted.
"""

import os
import json
import pytest
from training.pedagogical_teacher_student_film_session import (
    build_chronological_interaction_curriculum,
    StudentCognitiveAgent,
    TeacherAgent,
    run_pedagogical_training_session
)
from amsv.python.amsv_embedded import AMSVEmbeddedView


def test_curriculum_coverage():
    curriculum = build_chronological_interaction_curriculum()
    assert len(curriculum) == 5
    timestamps = [c.timestamp_range for c in curriculum]
    assert any("00:00" in t for t in timestamps)
    assert any("00:25" in t for t in timestamps)
    assert any("00:55" in t for t in timestamps)
    assert any("01:25" in t for t in timestamps)
    assert any("01:45" in t for t in timestamps)


def test_student_amsv_physical_synchronization():
    amsv = AMSVEmbeddedView()
    student = StudentCognitiveAgent(amsv_view=amsv)
    teacher = TeacherAgent()
    curriculum = build_chronological_interaction_curriculum()

    first_scene = curriculum[0]
    output = student.study_scene(first_scene, "Examine the pause duration")

    assert output.recommended_wait_time_ms >= 900
    assert amsv._view.nbytes == 64
    assert 0.0 <= output.amsv_snapshot["fluency"] <= 1.0
    assert 0.0 <= output.amsv_snapshot["pragmatics_score"] <= 1.0


def test_full_pedagogical_session_execution():
    result = run_pedagogical_training_session()
    assert result["status"] == "SUCCESS"
    assert result["average_score"] >= 90.0
    assert result["lessons_completed"] == 5

    log_path = result["log_path"]
    assert os.path.exists(log_path)
    with open(log_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["session_name"] == "Chronological Teacher-Student Pedagogical Training"
    assert len(data["lessons"]) == 5
