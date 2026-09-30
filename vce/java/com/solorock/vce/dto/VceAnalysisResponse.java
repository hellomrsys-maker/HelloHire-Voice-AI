package com.solorock.vce.dto;

public class VceAnalysisResponse {
    private String sessionId;
    private float articulationAccuracy;
    private float fluencyScore;
    private float fundamentalFrequencyF0;
    private float speechRateSylSec;
    private float phonationTimeRatio;
    private String diagnosticFeedback;
    private boolean amsvSynchronized;

    public VceAnalysisResponse() {}

    public String getSessionId() { return sessionId; }
    public void setSessionId(String sessionId) { this.sessionId = sessionId; }

    public float getArticulationAccuracy() { return articulationAccuracy; }
    public void setArticulationAccuracy(float articulationAccuracy) { this.articulationAccuracy = articulationAccuracy; }

    public float getFluencyScore() { return fluencyScore; }
    public void setFluencyScore(float fluencyScore) { this.fluencyScore = fluencyScore; }

    public float getFundamentalFrequencyF0() { return fundamentalFrequencyF0; }
    public void setFundamentalFrequencyF0(float fundamentalFrequencyF0) { this.fundamentalFrequencyF0 = fundamentalFrequencyF0; }

    public float getSpeechRateSylSec() { return speechRateSylSec; }
    public void setSpeechRateSylSec(float speechRateSylSec) { this.speechRateSylSec = speechRateSylSec; }

    public float getPhonationTimeRatio() { return phonationTimeRatio; }
    public void setPhonationTimeRatio(float phonationTimeRatio) { this.phonationTimeRatio = phonationTimeRatio; }

    public String getDiagnosticFeedback() { return diagnosticFeedback; }
    public void setDiagnosticFeedback(String diagnosticFeedback) { this.diagnosticFeedback = diagnosticFeedback; }

    public boolean isAmsvSynchronized() { return amsvSynchronized; }
    public void setAmsvSynchronized(boolean amsvSynchronized) { this.amsvSynchronized = amsvSynchronized; }
}
