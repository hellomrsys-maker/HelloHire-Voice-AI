package com.solorock.rsse.dto;

/**
 * Request DTO for processing a candidate's turn in an active scenario.
 */
public class ScenarioTurnRequest {
    private String sessionId;
    private int turnId;
    private String candidateTranscript;
    private float speechWpm;

    public ScenarioTurnRequest() {}

    public ScenarioTurnRequest(String sessionId, int turnId, String candidateTranscript, float speechWpm) {
        this.sessionId = sessionId;
        this.turnId = turnId;
        this.candidateTranscript = candidateTranscript;
        this.speechWpm = speechWpm;
    }

    public String getSessionId() { return sessionId; }
    public void setSessionId(String sessionId) { this.sessionId = sessionId; }

    public int getTurnId() { return turnId; }
    public void setTurnId(int turnId) { this.turnId = turnId; }

    public String getCandidateTranscript() { return candidateTranscript; }
    public void setCandidateTranscript(String candidateTranscript) { this.candidateTranscript = candidateTranscript; }

    public float getSpeechWpm() { return speechWpm; }
    public void setSpeechWpm(float speechWpm) { this.speechWpm = speechWpm; }
}
