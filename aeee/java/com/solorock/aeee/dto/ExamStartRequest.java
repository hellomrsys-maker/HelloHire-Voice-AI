package com.solorock.aeee.dto;

/**
 * Request DTO to start an adaptive examination session.
 */
public class ExamStartRequest {
    private String candidateId;
    private int maxQuestions = 10;
    private float targetSem = 0.25f;

    public ExamStartRequest() {}

    public ExamStartRequest(String candidateId, int maxQuestions, float targetSem) {
        this.candidateId = candidateId;
        this.maxQuestions = maxQuestions;
        this.targetSem = targetSem;
    }

    public String getCandidateId() { return candidateId; }
    public void setCandidateId(String candidateId) { this.candidateId = candidateId; }

    public int getMaxQuestions() { return maxQuestions; }
    public void setMaxQuestions(int maxQuestions) { this.maxQuestions = maxQuestions; }

    public float getTargetSem() { return targetSem; }
    public void setTargetSem(float targetSem) { this.targetSem = targetSem; }
}
