package com.solorock.rsse;

import com.solorock.rsse.dto.VerbalEvaluationDTO;

import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.util.Arrays;
import java.util.List;

/**
 * Enterprise Service for Recruitment Verbal Communication & STAR Evaluation.
 * Directly maps candidate evaluation metrics into the 64-byte AMSV physical vector.
 */
public class RecruitmentVerbalService {

    private final ByteBuffer amsvBuffer;

    private static final List<String> FILLERS = Arrays.asList(
        "um", "uh", "like", "you know", "sort of", "kind of", "basically", "literally"
    );

    private static final List<String> SIT_CUES = Arrays.asList(
        "when i was at", "in my previous role", "the situation was", "our team was facing"
    );
    private static final List<String> TASK_CUES = Arrays.asList(
        "my objective was", "i was tasked with", "the goal was to", "we needed to resolve"
    );
    private static final List<String> ACT_CUES = Arrays.asList(
        "i initiated", "i refactored", "i architected", "i implemented", "we deployed"
    );
    private static final List<String> RES_CUES = Arrays.asList(
        "resulting in", "achieved a", "reduced latency by", "improved throughput", "which delivered"
    );

    public RecruitmentVerbalService(ByteBuffer amsvBuffer) {
        if (amsvBuffer != null) {
            this.amsvBuffer = amsvBuffer.order(ByteOrder.LITTLE_ENDIAN);
        } else {
            this.amsvBuffer = null;
        }
    }

    public VerbalEvaluationDTO evaluateVerbalTurn(
        String candidateId,
        String transcript,
        int formatCode,
        float measuredWpm
    ) {
        String lower = transcript.toLowerCase();

        boolean hasS = SIT_CUES.stream().anyMatch(lower::contains);
        boolean hasT = TASK_CUES.stream().anyMatch(lower::contains);
        boolean hasA = ACT_CUES.stream().anyMatch(lower::contains);
        boolean hasR = RES_CUES.stream().anyMatch(lower::contains);

        float sScore = hasS ? 0.90f : 0.35f;
        float tScore = hasT ? 0.92f : 0.40f;
        float aScore = hasA ? 0.95f : 0.45f;
        float rScore = hasR ? 0.94f : 0.30f;

        int count = (hasS ? 1 : 0) + (hasT ? 1 : 0) + (hasA ? 1 : 0) + (hasR ? 1 : 0);
        float starCoherence;
        switch (count) {
            case 4: starCoherence = 0.98f; break;
            case 3: starCoherence = 0.85f; break;
            case 2: starCoherence = 0.65f; break;
            case 1: starCoherence = 0.40f; break;
            default: starCoherence = 0.20f; break;
        }

        // Filler penalty calculation
        long fillerHits = FILLERS.stream().filter(lower::contains).count();
        int words = Math.max(1, transcript.split("\\s+").length);
        float fillerPenalty = Math.min(0.40f, ((float) fillerHits / words) * 5.0f);

        // WPM pacing score
        float wpmScore;
        if (measuredWpm >= 130.0f && measuredWpm <= 155.0f) wpmScore = 1.0f;
        else if (measuredWpm >= 115.0f && measuredWpm <= 170.0f) wpmScore = 0.85f;
        else if (measuredWpm >= 90.0f && measuredWpm <= 190.0f)  wpmScore = 0.65f;
        else wpmScore = 0.40f;

        float regCompliance = Math.max(0.10f, Math.min(1.0f, (1.0f - fillerPenalty) * wpmScore));

        float formatWeight = (formatCode == 2 || formatCode == 3) ? 0.50f : 0.35f;
        float composite = (starCoherence * formatWeight) + (regCompliance * (1.0f - formatWeight));

        boolean passed = composite >= 0.70f;

        // Synchronize to 64-byte AMSV Offset 0x20
        syncToAmsv(formatCode, 1, regCompliance, 2);

        return new VerbalEvaluationDTO(
            candidateId,
            formatCode,
            measuredWpm,
            regCompliance,
            sScore,
            tScore,
            aScore,
            rScore,
            starCoherence,
            0.88f,
            fillerPenalty,
            composite,
            passed
        );
    }

    private void syncToAmsv(int scenarioId, int turn, float compliance, int phase) {
        if (amsvBuffer == null || amsvBuffer.capacity() < 64) {
            return;
        }
        int compQ16 = (int) (Math.max(0.0f, Math.min(1.0f, compliance)) * 65535.0f) & 0xFFFF;
        long word = ((long) scenarioId & 0xFFFF)
                  | (((long) turn & 0xFFFF) << 16)
                  | (((long) compQ16 & 0xFFFF) << 32)
                  | (((long) phase & 0xFFFF) << 48);

        // Offset 0x20 is slot 4 (4 * 8 = 32 bytes)
        amsvBuffer.putLong(0x20, word);
    }
}
