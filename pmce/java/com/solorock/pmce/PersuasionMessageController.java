package com.solorock.pmce;

import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.util.*;

/**
 * PersuasionMessageController — High-concurrency enterprise controller for PMCE.
 * Supports direct 0-nanosecond ByteBuffer memory mapping into AMSV offset 0x28.
 */
public class PersuasionMessageController {

    private final ByteBuffer amsvBuffer;

    private static final List<String> LOGOS_CUES = Arrays.asList(
        "because", "therefore", "consequently", "specifically", "data shows", "evidence", "result"
    );
    private static final List<String> ETHOS_CUES = Arrays.asList(
        "in my experience", "having led", "architected", "delivered", "built", "managed", "track record"
    );
    private static final List<String> CTA_CUES = Arrays.asList(
        "recommend", "propose", "suggest", "we should", "plan is to", "next step", "execute"
    );

    public PersuasionMessageController(ByteBuffer amsvBuffer) {
        if (amsvBuffer != null) {
            this.amsvBuffer = amsvBuffer.order(ByteOrder.LITTLE_ENDIAN);
        } else {
            this.amsvBuffer = null;
        }
    }

    public Map<String, Object> evaluateTurn(String text, int turnNumber) {
        String lower = text.toLowerCase();

        long logosHits = LOGOS_CUES.stream().filter(lower::contains).count();
        float logos = Math.min(1.0f, 0.35f + logosHits * 0.15f);

        long ethosHits = ETHOS_CUES.stream().filter(lower::contains).count();
        float ethos = Math.min(1.0f, 0.30f + ethosHits * 0.20f);

        long ctaHits = CTA_CUES.stream().filter(lower::contains).count();
        float cta = Math.min(1.0f, 0.25f + ctaHits * 0.25f);

        float composite = Math.min(1.0f, logos * 0.40f + ethos * 0.35f + cta * 0.25f);
        int grade = composite >= 0.82f ? 1 : (composite >= 0.65f ? 2 : (composite >= 0.48f ? 3 : 4));

        if (amsvBuffer != null && amsvBuffer.capacity() >= 48) {
            int q16 = (int) (composite * 65535.0f);
            amsvBuffer.putShort(0x28, (short) q16);
        }

        Map<String, Object> res = new HashMap<>();
        res.put("logos", logos);
        res.put("ethos", ethos);
        res.put("cta", cta);
        res.put("composite_persuasion", composite);
        res.put("persuasion_grade", grade);
        return res;
    }
}
