package com.solorock.telugu;

import java.nio.ByteBuffer;
import java.nio.ByteOrder;

/**
 * TeluguEngineService - Enterprise Service Layer for Telugu Linguistic Engine.
 * Manages conversational sessions, honorific register resolution, and AMSV 64-byte interaction.
 */
public class TeluguEngineService {
    private static final int AMSV_SIZE = 64;
    private final ByteBuffer amsvBuffer;

    public enum Register {
        FORMAL_HONORIFIC, // మీరు (Meeru)
        INFORMAL_INTIMATE // నువ్వు (Nuvvu)
    }

    public TeluguEngineService() {
        this.amsvBuffer = ByteBuffer.allocateDirect(AMSV_SIZE).order(ByteOrder.LITTLE_ENDIAN);
        // Magic header 'TELU'
        this.amsvBuffer.put(0, (byte) 'T');
        this.amsvBuffer.put(1, (byte) 'E');
        this.amsvBuffer.put(2, (byte) 'L');
        this.amsvBuffer.put(3, (byte) 'U');
    }

    public Register resolveRegister(String utterance) {
        if (utterance == null) return Register.FORMAL_HONORIFIC;
        if (utterance.contains("మీరు") || utterance.contains("గారు") || utterance.contains("అండి")) {
            return Register.FORMAL_HONORIFIC;
        } else if (utterance.contains("నువ్వు") || utterance.contains("రా") || utterance.contains("రోయ్")) {
            return Register.INFORMAL_INTIMATE;
        }
        return Register.FORMAL_HONORIFIC; // Default polite in public systems
    }

    public void updateProsodyState(float f0Hz, float tempoSps, float fluencyScore) {
        short f0Fixed = (short) Math.min(65535, Math.max(0, Math.round(f0Hz * 256.0f)));
        short tempoFixed = (short) Math.min(65535, Math.max(0, Math.round(tempoSps * 6553.0f)));
        short fluencyFixed = (short) Math.min(65535, Math.max(0, Math.round(fluencyScore * 65535.0f)));

        amsvBuffer.putShort(8, f0Fixed);
        amsvBuffer.putShort(10, tempoFixed);
        amsvBuffer.putShort(12, fluencyFixed);
        amsvBuffer.put(14, (byte) 1); // prosody lock
    }

    public ByteBuffer getDirectAmsvBuffer() {
        return amsvBuffer.asReadOnlyBuffer();
    }
}
