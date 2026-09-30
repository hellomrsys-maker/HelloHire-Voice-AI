package com.solorock.rsse.dto;

/**
 * Request DTO for starting a recruitment simulation scenario.
 */
public class ScenarioStartRequest {
    private int formatCode;      // 1-8
    private int scenarioId;      // e.g. 101, 201
    private String candidateId;
    private float targetWpm;

    public ScenarioStartRequest() {}

    public ScenarioStartRequest(int formatCode, int scenarioId, String candidateId, float targetWpm) {
        this.formatCode = formatCode;
        this.scenarioId = scenarioId;
        this.candidateId = candidateId;
        this.targetWpm = targetWpm;
    }

    public int getFormatCode() { return formatCode; }
    public void setFormatCode(int formatCode) { this.formatCode = formatCode; }

    public int getScenarioId() { return scenarioId; }
    public void setScenarioId(int scenarioId) { this.scenarioId = scenarioId; }

    public String getCandidateId() { return candidateId; }
    public void setCandidateId(String candidateId) { this.candidateId = candidateId; }

    public float getTargetWpm() { return targetWpm; }
    public void setTargetWpm(float targetWpm) { this.targetWpm = targetWpm; }
}
