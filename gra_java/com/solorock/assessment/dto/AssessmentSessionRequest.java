package com.solorock.assessment.dto;

import java.util.Map;

public class AssessmentSessionRequest {
    private String learnerId;
    private String targetCefrLevel;
    private Map<String, String> answers;

    public AssessmentSessionRequest() {
        this.targetCefrLevel = "B1";
    }

    public AssessmentSessionRequest(String learnerId, String targetCefrLevel, Map<String, String> answers) {
        this.learnerId = learnerId;
        this.targetCefrLevel = targetCefrLevel;
        this.answers = answers;
    }

    public String getLearnerId() { return learnerId; }
    public void setLearnerId(String learnerId) { this.learnerId = learnerId; }

    public String getTargetCefrLevel() { return targetCefrLevel; }
    public void setTargetCefrLevel(String targetCefrLevel) { this.targetCefrLevel = targetCefrLevel; }

    public Map<String, String> getAnswers() { return answers; }
    public void setAnswers(Map<String, String> answers) { this.answers = answers; }
}
