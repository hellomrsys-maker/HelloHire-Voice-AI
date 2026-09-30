package com.solorock.grammar.engine_a;

import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.util.Map;
import java.util.HashMap;

/**
 * WrittenGrammarService - Engine A Sub-Core A5 (Java 21)
 * Written Grammar & Discourse Engine: Document ingestion pipeline,
 * Spring REST coordination, and Direct ByteBuffer zero-bridge AMSV synchronization.
 */
public class WrittenGrammarService {

    private final ByteBuffer directAmsvBuffer;

    public WrittenGrammarService() {
        // Allocate direct off-heap buffer aligned to 64 bytes
        this.directAmsvBuffer = ByteBuffer.allocateDirect(64).order(ByteOrder.LITTLE_ENDIAN);
    }

    public WrittenGrammarService(ByteBuffer sharedAmsvBuffer) {
        this.directAmsvBuffer = sharedAmsvBuffer;
    }

    /**
     * Evaluates document grammar structure and synchronizes scores to AMSV.
     */
    public Map<String, Object> evaluateDocument(String documentText) {
        Map<String, Object> result = new HashMap<>();
        if (documentText == null || documentText.isBlank()) {
            result.put("status", "EMPTY_PAYLOAD");
            result.put("structure_score", 0.0);
            return result;
        }

        int length = documentText.length();
        int words = documentText.trim().split("\\s+").length;
        int sentences = Math.max(1, documentText.split("[.!?]+").length);

        double structureScore = Math.min(1.0, 0.4 + (words / (double)(sentences * 20)) * 0.6);
        double registerScore = Math.min(1.0, 0.5 + (length / (double)(words * 7)) * 0.5);

        // Direct zero-bridge synchronization to AMSV Offset 0x30 (maio_global_state_alpha)
        // Offset 0x34: structure_score Q16
        // Offset 0x36: register_score Q16
        synchronized (directAmsvBuffer) {
            short structQ16 = (short)(int)(structureScore * 65535.0);
            short regQ16 = (short)(int)(registerScore * 65535.0);
            directAmsvBuffer.putShort(0x34, structQ16);
            directAmsvBuffer.putShort(0x36, regQ16);
        }

        result.put("sub_core", "A5_Java");
        result.put("word_count", words);
        result.put("sentence_count", sentences);
        result.put("structure_score", Math.round(structureScore * 1000.0) / 1000.0);
        result.put("register_score", Math.round(registerScore * 1000.0) / 1000.0);
        result.put("amsv_offset_0x30_synced", true);

        return result;
    }

    public ByteBuffer getDirectAmsvBuffer() {
        return directAmsvBuffer;
    }
}
