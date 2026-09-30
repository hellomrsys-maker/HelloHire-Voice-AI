package com.solorock.ccte.dto;

import java.util.Map;

public class CognitiveEvaluationResponse {
    private String candidateId;
    private float globalCognitiveIndex;
    private Map<String, Float> capabilityScores;
    private boolean amsvSynchronized;
    private String cognitiveProfileSummary;

    public CognitiveEvaluationResponse() {}

    public String getCandidateId() { return candidateId; }
    public void setCandidateId(String candidateId) { this.candidateId = candidateId; }

    public float getGlobalCognitiveIndex() { return globalCognitiveIndex; }
    public void setGlobalCognitiveIndex(float globalCognitiveIndex) { this.globalCognitiveIndex = globalCognitiveIndex; }

    public Map<String, Float> getCapabilityScores() { return capabilityScores; }
    public void setCapabilityScores(Map<String, Float> capabilityScores) { this.capabilityScores = capabilityScores; }

    public boolean isAmsvSynchronized() { return amsvSynchronized; }
    public void setAmsvSynchronized(boolean amsvSynchronized) { this.amsvSynchronized = amsvSynchronized; }

    public String getCognitiveProfileSummary() { return cognitiveProfileSummary; }
    public void setCognitiveProfileSummary(String cognitiveProfileSummary) { this.cognitiveProfileSummary = cognitiveProfileSummary; }
}
