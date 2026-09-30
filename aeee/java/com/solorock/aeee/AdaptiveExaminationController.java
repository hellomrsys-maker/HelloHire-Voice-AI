package com.solorock.aeee;

import com.solorock.aeee.dto.ExamStartRequest;
import com.solorock.aeee.dto.ExamEvaluationRequest;
import com.solorock.aeee.dto.ExamEvaluationResponse;

import java.nio.ByteBuffer;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Enterprise Service Layer Controller for AI Examiner & Adaptive Examination Engine (AEEE).
 * Manages adaptive testing sessions, 3PL IRT ability updates, and AMSV zero-bridge synchronization.
 */
public class AdaptiveExaminationController {

    private final ByteBuffer amsvDirectBuffer;
    private final Map<String, ActiveExamSession> activeSessions = new ConcurrentHashMap<>();

    private static class ActiveExamSession {
        String sessionId;
        String candidateId;
        int questionIndex;
        int maxQuestions;
        float targetSem;
        float abilityTheta;
        float standardError;
        boolean isCompleted;

        ActiveExamSession(String sessionId, String candidateId, int maxQuestions, float targetSem) {
            this.sessionId = sessionId;
            this.candidateId = candidateId;
            this.questionIndex = 0;
            this.maxQuestions = maxQuestions;
            this.targetSem = targetSem;
            this.abilityTheta = 0.0f;
            this.standardError = 1.0f;
            this.isCompleted = false;
        }
    }

    public AdaptiveExaminationController(ByteBuffer amsvDirectBuffer) {
        this.amsvDirectBuffer = amsvDirectBuffer;
    }

    /**
     * Initializes an adaptive examination session.
     */
    public ExamEvaluationResponse startExamination(ExamStartRequest request) {
        String sessionId = UUID.randomUUID().toString();
        ActiveExamSession session = new ActiveExamSession(
            sessionId,
            request.getCandidateId(),
            request.getMaxQuestions(),
            request.getTargetSem()
        );
        session.questionIndex = 1;
        activeSessions.put(sessionId, session);

        String initialQuestion = "Please introduce your core technical specialization and summarize your most impactful system design.";

        // Sync with AMSV at offset 0x28 (byte offset 40)
        syncToAmsv(session.abilityTheta, session.standardError, session.questionIndex);

        return new ExamEvaluationResponse(
            sessionId,
            1,
            0.0f,
            1.0f,
            0.0f,
            Map.of(),
            initialQuestion,
            false
        );
    }

    /**
     * Evaluates candidate turn, updates IRT theta and SEM, selects next item.
     */
    public ExamEvaluationResponse evaluateResponse(ExamEvaluationRequest request) {
        ActiveExamSession session = activeSessions.get(request.getSessionId());
        if (session == null) {
            throw new IllegalArgumentException("Invalid session ID: " + request.getSessionId());
        }

        Map<String, Float> scores = request.getDimensionScores();
        float composite = calculateComposite(scores);

        // Update IRT Theta with Newton-Raphson approximation
        float a = (request.getItemDiscrimination() > 0.0f) ? request.getItemDiscrimination() : 1.5f;
        float b = request.getItemDifficulty();
        float u = composite;

        float expTerm = (float) Math.exp(-Math.max(-20.0, Math.min(20.0, a * (session.abilityTheta - b))));
        float p = 1.0f / (1.0f + expTerm);

        float grad = -session.abilityTheta + a * (u - p);
        float info = 1.0f + (a * a) * p * (1.0f - p);
        float deltaTheta = Math.max(-0.75f, Math.min(0.75f, grad / info));

        session.abilityTheta = Math.max(-3.5f, Math.min(3.5f, session.abilityTheta + deltaTheta));
        session.standardError = 1.0f / (float) Math.sqrt(Math.max(0.1, info));

        session.questionIndex++;

        // Stopping condition check
        if (session.questionIndex >= session.maxQuestions ||
           (session.questionIndex >= 3 && session.standardError <= session.targetSem)) {
            session.isCompleted = true;
        }

        String nextQuestion = session.isCompleted
            ? "Adaptive examination completed. Comprehensive audit report ready."
            : getAdaptiveQuestion(session.questionIndex, session.abilityTheta);

        // Sync to AMSV state vector
        syncToAmsv(session.abilityTheta, session.standardError, session.questionIndex);

        return new ExamEvaluationResponse(
            session.sessionId,
            session.questionIndex,
            session.abilityTheta,
            session.standardError,
            composite,
            scores,
            nextQuestion,
            session.isCompleted
        );
    }

    private float calculateComposite(Map<String, Float> scores) {
        if (scores == null || scores.isEmpty()) {
            return 0.70f;
        }
        float sum = 0.0f;
        for (float val : scores.values()) {
            sum += val;
        }
        return sum / (float) scores.size();
    }

    private String getAdaptiveQuestion(int questionIndex, float theta) {
        if (theta > 1.2f) {
            return "Advanced Probe: Formulate a board-level capital allocation strategy for an enterprise AI transformation during a 40% margin compression.";
        } else if (theta > 0.0f) {
            return "Intermediate Probe: How do you systematically analyze and resolve lock contention and memory bandwidth saturation in high-throughput pipelines?";
        } else {
            return "Foundational Probe: Explain the difference between synchronous and asynchronous communication in distributed systems.";
        }
    }

    private void syncToAmsv(float theta, float sem, int questionIndex) {
        if (amsvDirectBuffer == null || amsvDirectBuffer.capacity() < 64) {
            return;
        }
        // Offset 0x28 is byte offset 40 in AMSV state vector
        // [Bits 0-31: Theta (IEEE 754 float) | Bits 32-47: SEM Q16 | Bits 48-63: Question Index]
        int thetaBits = Float.floatToRawIntBits(theta);
        int semQ16 = (int) (Math.max(0.0f, Math.min(1.0f, sem)) * 65535.0f);

        long packedU64 = ((long) thetaBits & 0xFFFFFFFFL)
                       | (((long) (semQ16 & 0xFFFF)) << 32)
                       | (((long) (questionIndex & 0xFFFF)) << 48);

        amsvDirectBuffer.putLong(40, packedU64);
    }
}
