package com.solorock.maio.dto;

/**
 * Request DTO to generate a holistic candidate report.
 */
public class HolisticReportRequest {
    private String candidateId;
    private String sessionId;
    private boolean includeCurriculum;

    public HolisticReportRequest() {}

    public HolisticReportRequest(String candidateId, String sessionId, boolean includeCurriculum) {
        this.candidateId = candidateId;
        this.sessionId = sessionId;
        this.includeCurriculum = includeCurriculum;
    }

    public String getCandidateId() { return candidateId; }
    public void setCandidateId(String candidateId) { this.candidateId = candidateId; }

    public String getSessionId() { return sessionId; }
    public void setSessionId(String sessionId) { this.sessionId = sessionId; }

    public boolean isIncludeCurriculum() { return includeCurriculum; }
    public void setIncludeCurriculum(boolean includeCurriculum) { this.includeCurriculum = includeCurriculum; }
}
