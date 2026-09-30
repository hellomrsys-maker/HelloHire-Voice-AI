package com.solorock.hcte;

import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.util.*;

/**
 * HumanCognitiveThinkingController — High-concurrency enterprise controller for HCTE.
 * Supports direct 0-nanosecond ByteBuffer memory mapping into AMSV offset 0x38.
 */
public class HumanCognitiveThinkingController {

    private final ByteBuffer amsvBuffer;

    private static final List<String> PREMORTEM_CUES = Arrays.asList(
        "fail", "failure", "mitigat", "bottleneck", "catastrophic", "worst-case", "edge-case", "pre-mortem"
    );

    public HumanCognitiveThinkingController(ByteBuffer amsvBuffer) {
        if (amsvBuffer != null) {
            this.amsvBuffer = amsvBuffer.order(ByteOrder.LITTLE_ENDIAN);
        } else {
            this.amsvBuffer = null;
        }
    }

    public Map<String, Object> evaluateTurn(String scenario) {
        String lower = scenario.toLowerCase();

        long premortemHits = PREMORTEM_CUES.stream().filter(lower::contains).count();
        float premortem = Math.min(1.0f, 0.40f + premortemHits * 0.25f);
        float analyst = lower.matches(".*\\d+.*") ? 0.85f : 0.50f;
        float systems = lower.contains("architecture") || lower.contains("distributed") ? 0.90f : 0.50f;

        // Weighted GCI with 2x pre-mortem
        float gci = (premortem * 2.0f + analyst + systems) / 4.0f;
        int grade = gci >= 0.75f ? 1 : (gci >= 0.55f ? 2 : (gci >= 0.35f ? 3 : 4));

        if (amsvBuffer != null && amsvBuffer.capacity() >= 60) {
            int q16 = (int) (gci * 65535.0f);
            amsvBuffer.putShort(0x38, (short) q16);
        }

        Map<String, Object> res = new HashMap<>();
        res.put("premortem_score", premortem);
        res.put("global_cognitive_index", gci);
        res.put("cognitive_grade", grade);
        return res;
    }
}
