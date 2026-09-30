package com.solorock.rsse.dto;

/**
 * Response DTO returning evaluation of the turn and next dynamic probe.
 */
public class ScenarioTurnResponse {
    private String sessionId;
    private int turnId;
    private String currentPhase;
    private float registerComplianceScore;
    private float dynamicStressMultiplier;
    private String nextPromptOrProbe;
    private boolean isConcluded;

    public ScenarioTurnResponse() {}

    public ScenarioTurnResponse(String sessionId, int turnId, String currentPhase,
                                float registerComplianceScore, float dynamicStressMultiplier,
                                String nextPromptOrProbe, boolean isConcluded) {
        this.sessionId = sessionId;
        this.turnId = turnId;
        this.currentPhase = currentPhase;
        this.registerComplianceScore = registerComplianceScore;
        this.dynamicStressMultiplier = dynamicStressMultiplier;
        this.nextPromptOrProbe = nextPromptOrProbe;
        this.isConcluded = isConcluded;
    }

    public String getSessionId() { return sessionId; }
    public void setSessionId(String sessionId) { this.sessionId = sessionId; }

    public int getTurnId() { return turnId; }
    public void setTurnId(int turnId) { this.turnId = turnId; }

    public String getCurrentPhase() { return currentPhase; }
    public void setCurrentPhase(String currentPhase) { this.currentPhase = currentPhase; }

    public float getRegisterComplianceScore() { return registerComplianceScore; }
    public void setRegisterComplianceScore(float registerComplianceScore) { this.registerComplianceScore = registerComplianceScore; }

    public float getDynamicStressMultiplier() { return dynamicStressMultiplier; }
    public void setDynamicStressMultiplier(float dynamicStressMultiplier) { this.dynamicStressMultiplier = dynamicStressMultiplier; }

    public String getNextPromptOrProbe() { return nextPromptOrProbe; }
    public void setNextPromptOrProbe(String nextPromptOrProbe) { this.nextPromptOrProbe = nextPromptOrProbe; }

    public boolean isConcluded() { return isConcluded; }
    public void setConcluded(boolean concluded) { isConcluded = concluded; }
}
