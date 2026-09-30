package com.solorock.grammar.engine_b;

import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.util.Map;
import java.util.HashMap;

/**
 * VerbalSessionService - Engine B Sub-Core B5 (Java 21)
 * Spoken & Verbal Communication Engine: Interview session lifecycle manager,
 * Spring REST endpoints, and Direct ByteBuffer AMSV Offset 0x20 synchronization.
 */
public class VerbalSessionService {

    private final ByteBuffer directAmsvBuffer;

    public VerbalSessionService() {
        this.directAmsvBuffer = ByteBuffer.allocateDirect(64).order(ByteOrder.LITTLE_ENDIAN);
    }

    public VerbalSessionService(ByteBuffer sharedAmsvBuffer) {
        this.directAmsvBuffer = sharedAmsvBuffer;
    }

    public Map<String, Object> processTurn(String transcript, int turnNumber, int scenarioId) {
        Map<String, Object> result = new HashMap<>();
        if (transcript == null || transcript.isBlank()) {
            result.put("status", "SILENCE_DETECTED");
            result.put("compliance_score", 0.0);
            return result;
        }

        int words = transcript.trim().split("\\s+").length;
        double compliance = Math.min(1.0, 0.5 + (words / 40.0) * 0.5);

        // Synchronize directly to AMSV Offset 0x20 (rsse_scenario_state)
        // Offset 0x20: scenarioId (short)
        // Offset 0x22: turnNumber (short)
        // Offset 0x24: compliance Q16 (short)
        // Offset 0x26: phase (short)
        synchronized (directAmsvBuffer) {
            directAmsvBuffer.putShort(0x20, (short)scenarioId);
            directAmsvBuffer.putShort(0x22, (short)turnNumber);
            directAmsvBuffer.putShort(0x24, (short)(int)(compliance * 65535.0));
            directAmsvBuffer.putShort(0x26, (short)2); // Phase 2: Active Investigation
        }

        result.put("sub_core", "B5_Java");
        result.put("turn_number", turnNumber);
        result.put("scenario_id", scenarioId);
        result.put("words_detected", words);
        result.put("compliance_score", Math.round(compliance * 1000.0) / 1000.0);
        result.put("amsv_offset_0x20_synced", true);

        return result;
    }
}
