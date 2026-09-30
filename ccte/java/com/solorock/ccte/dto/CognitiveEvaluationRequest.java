package com.solorock.ccte.dto;

import java.util.Map;

public class CognitiveEvaluationRequest {
    private String candidateId;
    private String capabilityName; // e.g., "thinking", "focus", "all"
    private Map<String, Object> parameters;

    public CognitiveEvaluationRequest() {}

    public String getCandidateId() { return candidateId; }
    public void setCandidateId(String candidateId) { this.candidateId = candidateId; }

    public String getCapabilityName() { return capabilityName; }
    public void setCapabilityName(String capabilityName) { this.capabilityName = capabilityName; }

    public Map<String, Object> getParameters() { return parameters; }
    public void setParameters(Map<String, Object> parameters) { this.parameters = parameters; }
}
