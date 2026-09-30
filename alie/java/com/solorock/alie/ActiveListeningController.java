package com.solorock.alie;

import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.util.*;

/**
 * ActiveListeningController — High-concurrency enterprise controller for ALIE.
 * Supports direct 0-nanosecond ByteBuffer memory mapping into AMSV offset 0x10.
 */
public class ActiveListeningController {

    private final ByteBuffer amsvBuffer;

    private static final List<String> REPAIR_CUES = Arrays.asList(
        "can you clarify", "did you mean", "if i understand correctly",
        "to confirm", "are you asking whether"
    );

    public ActiveListeningController(ByteBuffer amsvBuffer) {
        if (amsvBuffer != null) {
            this.amsvBuffer = amsvBuffer.order(ByteOrder.LITTLE_ENDIAN);
        } else {
            this.amsvBuffer = null;
        }
    }

    public Map<String, Object> evaluateTurn(
        String question,
        String answer,
        int turnNumber,
        float latencyMs
    ) {
        String lowerQ = question.toLowerCase();
        String lowerA = answer.toLowerCase();

        Set<String> qWords = new HashSet<>(Arrays.asList(lowerQ.split("\\s+")));
        Set<String> aWords = new HashSet<>(Arrays.asList(lowerA.split("\\s+")));

        // Jaccard similarity
        Set<String> intersection = new HashSet<>(qWords);
        intersection.retainAll(aWords);
        Set<String> union = new HashSet<>(qWords);
        union.addAll(aWords);
        float jaccard = union.isEmpty() ? 0.0f : (float) intersection.size() / union.size();

        // Repair cues
        long repairCount = REPAIR_CUES.stream().filter(lowerA::contains).count();
        float repairScore = Math.min(1.0f, 0.40f + repairCount * 0.30f);

        // Latency score (optimal: 800 - 2200 ms)
        float latScore;
        if (latencyMs >= 800.0f && latencyMs <= 2200.0f) {
            latScore = 1.0f;
        } else if (latencyMs < 300.0f) {
            latScore = 0.40f;
        } else {
            latScore = (float) Math.max(0.1, Math.exp(-0.00045 * (latencyMs - 2200.0f)));
        }

        float composite = Math.min(1.0f, Math.max(0.0f, jaccard * 0.45f + repairScore * 0.25f + latScore * 0.30f));
        int grade = composite >= 0.80f ? 1 : (composite >= 0.60f ? 2 : (composite >= 0.40f ? 3 : 4));

        if (amsvBuffer != null && amsvBuffer.capacity() >= 32) {
            int q16 = (int) (composite * 65535.0f);
            amsvBuffer.putShort(0x10, (short) q16);
        }

        Map<String, Object> res = new HashMap<>();
        res.put("jaccard", jaccard);
        res.put("latency_score", latScore);
        res.put("composite_listening", composite);
        res.put("listening_grade", grade);
        return res;
    }
}
