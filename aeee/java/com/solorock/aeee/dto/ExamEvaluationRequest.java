package com.solorock.aeee.dto;

import java.util.Map;

/**
 * Request DTO containing candidate response and dimension signals for adaptive examination.
 */
public class ExamEvaluationRequest {
    private String sessionId;
    private String transcript;
    private float itemDifficulty;
    private float itemDiscrimination;
    private Map<String, Float> dimensionScores;

    public ExamEvaluationRequest() {}

    public ExamEvaluationRequest(String sessionId, String transcript, float itemDifficulty,
                                 float itemDiscrimination, Map<String, Float> dimensionScores) {
        this.sessionId = sessionId;
        this.transcript = transcript;
        this.itemDifficulty = itemDifficulty;
        this.itemDiscrimination = itemDiscrimination;
        this.dimensionScores = dimensionScores;
    }

    public String getSessionId() { return sessionId; }
    public void setSessionId(String sessionId) { this.sessionId = sessionId; }

    public String getTranscript() { return transcript; }
    public void setTranscript(String transcript) { this.transcript = transcript; }

    public float getItemDifficulty() { return itemDifficulty; }
    public void setItemDifficulty(float itemDifficulty) { this.itemDifficulty = itemDifficulty; }

    public float getItemDiscrimination() { return itemDiscrimination; }
    public void setItemDiscrimination(float itemDiscrimination) { this.itemDiscrimination = itemDiscrimination; }

    public Map<String, Float> getDimensionScores() { return dimensionScores; }
    public void setDimensionScores(Map<String, Float> dimensionScores) { this.dimensionScores = dimensionScores; }
}
