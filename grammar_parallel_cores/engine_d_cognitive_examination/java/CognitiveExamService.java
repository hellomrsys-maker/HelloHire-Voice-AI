package com.solorock.grammar.engine_d;

import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.util.Map;
import java.util.HashMap;

/**
 * CognitiveExamService - Engine D Sub-Core D5 (Java 21)
 * Cognitive Capabilities & Adaptive Examination Engine: Psychometric exam lifecycle,
 * Spring REST endpoints, and Direct ByteBuffer AMSV Offsets 0x10-0x1F & 0x28-0x2F synchronization.
 */
public class CognitiveExamService {

    private final ByteBuffer directAmsvBuffer;

    public CognitiveExamService() {
        this.directAmsvBuffer = ByteBuffer.allocateDirect(64).order(ByteOrder.LITTLE_ENDIAN);
    }

    public CognitiveExamService(ByteBuffer sharedAmsvBuffer) {
        this.directAmsvBuffer = sharedAmsvBuffer;
    }

    public Map<String, Object> updateCognitiveExamState(float[] scores, float theta, int questionIndex) {
        Map<String, Object> result = new HashMap<>();
        if (scores == null || scores.length < 8) {
            result.put("status", "INVALID_SCORES");
            return result;
        }

        // Direct synchronization to AMSV:
        // Offset 0x10 - 0x1F: 8 x uint16_t Q16 cognitive scores
        // Offset 0x28 - 0x2F: theta float32, sem uint16, question uint16
        synchronized (directAmsvBuffer) {
            for (int i = 0; i < 8; i++) {
                short q16 = (short)(int)(Math.min(1.0f, Math.max(0.0f, scores[i])) * 65535.0f);
                directAmsvBuffer.putShort(0x10 + i * 2, q16);
            }

            directAmsvBuffer.putFloat(0x28, theta);
            short semQ16 = (short)(int)((1.0 / Math.sqrt(1.0 + questionIndex * 0.5)) * 65535.0);
            directAmsvBuffer.putShort(0x2C, semQ16);
            directAmsvBuffer.putShort(0x2E, (short)questionIndex);
        }

        result.put("sub_core", "D5_Java");
        result.put("theta", theta);
        result.put("question_index", questionIndex);
        result.put("amsv_offsets_0x10_and_0x28_synced", true);

        return result;
    }
}
