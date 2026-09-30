package com.solorock.ecse;

import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.util.*;

/**
 * SocialCalibrationController — High-concurrency enterprise controller for ECSE.
 * Supports direct 0-nanosecond ByteBuffer memory mapping into AMSV offset 0x20.
 */
public class SocialCalibrationController {

    private final ByteBuffer amsvBuffer;

    private static final List<String> POS_CUES = Arrays.asList(
        "excited", "passionate", "delighted", "love", "genuinely", "absolutely", "proud", "confident"
    );
    private static final List<String> WARMTH_CUES = Arrays.asList(
        "i appreciate", "thank you", "insightful", "completely agree", "understand", "empathize"
    );

    public SocialCalibrationController(ByteBuffer amsvBuffer) {
        if (amsvBuffer != null) {
            this.amsvBuffer = amsvBuffer.order(ByteOrder.LITTLE_ENDIAN);
        } else {
            this.amsvBuffer = null;
        }
    }

    public Map<String, Object> evaluateTurn(String answer, String interviewerPrompt) {
        String lower = answer.toLowerCase();

        long posHits = POS_CUES.stream().filter(lower::contains).count();
        float affect = Math.min(1.0f, 0.40f + posHits * 0.15f);

        long warmthHits = WARMTH_CUES.stream().filter(lower::contains).count();
        float warmth = Math.min(1.0f, 0.35f + warmthHits * 0.20f);

        float composite = Math.min(1.0f, affect * 0.50f + warmth * 0.50f);
        int grade = composite >= 0.80f ? 1 : (composite >= 0.63f ? 2 : (composite >= 0.45f ? 3 : 4));

        if (amsvBuffer != null && amsvBuffer.capacity() >= 40) {
            int q16 = (int) (composite * 65535.0f);
            amsvBuffer.putShort(0x20, (short) q16);
        }

        Map<String, Object> res = new HashMap<>();
        res.put("affect", affect);
        res.put("warmth", warmth);
        res.put("composite_social", composite);
        res.put("social_grade", grade);
        return res;
    }
}
