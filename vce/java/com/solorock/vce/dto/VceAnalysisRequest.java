package com.solorock.vce.dto;

import java.util.List;

public class VceAnalysisRequest {
    private String sessionId;
    private String candidateId;
    private List<Float> pcmSamples;
    private int sampleRate;
    private String referenceText;

    public VceAnalysisRequest() {}

    public String getSessionId() { return sessionId; }
    public void setSessionId(String sessionId) { this.sessionId = sessionId; }

    public String getCandidateId() { return candidateId; }
    public void setCandidateId(String candidateId) { this.candidateId = candidateId; }

    public List<Float> getPcmSamples() { return pcmSamples; }
    public void setPcmSamples(List<Float> pcmSamples) { this.pcmSamples = pcmSamples; }

    public int getSampleRate() { return sampleRate; }
    public void setSampleRate(int sampleRate) { this.sampleRate = sampleRate; }

    public String getReferenceText() { return referenceText; }
    public void setReferenceText(String referenceText) { this.referenceText = referenceText; }
}
