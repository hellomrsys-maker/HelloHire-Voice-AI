package com.solorock.maio.dto;

import java.util.List;
import java.util.Map;

/**
 * Response DTO providing holistic multi-agent evaluation report and prescriptive curriculum.
 */
public class HolisticReportResponse {
    private String candidateId;
    private String sessionId;
    private float globalCompetencyIndex;
    private float irtAbilityTheta;
    private Map<String, Float> radarDimensions;
    private List<String> rootCauseDiagnoses;
    private List<String> activeInterventions;
    private List<String> prescriptiveCurriculum;
    private boolean systemIntegrityVerified;

    public HolisticReportResponse() {}

    public HolisticReportResponse(String candidateId, String sessionId, float globalCompetencyIndex,
                                  float irtAbilityTheta, Map<String, Float> radarDimensions,
                                  List<String> rootCauseDiagnoses, List<String> activeInterventions,
                                  List<String> prescriptiveCurriculum, boolean systemIntegrityVerified) {
        this.candidateId = candidateId;
        this.sessionId = sessionId;
        this.globalCompetencyIndex = globalCompetencyIndex;
        this.irtAbilityTheta = irtAbilityTheta;
        this.radarDimensions = radarDimensions;
        this.rootCauseDiagnoses = rootCauseDiagnoses;
        this.activeInterventions = activeInterventions;
        this.prescriptiveCurriculum = prescriptiveCurriculum;
        this.systemIntegrityVerified = systemIntegrityVerified;
    }

    public String getCandidateId() { return candidateId; }
    public void setCandidateId(String candidateId) { this.candidateId = candidateId; }

    public String getSessionId() { return sessionId; }
    public void setSessionId(String sessionId) { this.sessionId = sessionId; }

    public float getGlobalCompetencyIndex() { return globalCompetencyIndex; }
    public void setGlobalCompetencyIndex(float globalCompetencyIndex) { this.globalCompetencyIndex = globalCompetencyIndex; }

    public float getIrtAbilityTheta() { return irtAbilityTheta; }
    public void setIrtAbilityTheta(float irtAbilityTheta) { this.irtAbilityTheta = irtAbilityTheta; }

    public Map<String, Float> getRadarDimensions() { return radarDimensions; }
    public void setRadarDimensions(Map<String, Float> radarDimensions) { this.radarDimensions = radarDimensions; }

    public List<String> getRootCauseDiagnoses() { return rootCauseDiagnoses; }
    public void setRootCauseDiagnoses(List<String> rootCauseDiagnoses) { this.rootCauseDiagnoses = rootCauseDiagnoses; }

    public List<String> getActiveInterventions() { return activeInterventions; }
    public void setActiveInterventions(List<String> activeInterventions) { this.activeInterventions = activeInterventions; }

    public List<String> getPrescriptiveCurriculum() { return prescriptiveCurriculum; }
    public void setPrescriptiveCurriculum(List<String> prescriptiveCurriculum) { this.prescriptiveCurriculum = prescriptiveCurriculum; }

    public boolean isSystemIntegrityVerified() { return systemIntegrityVerified; }
    public void setSystemIntegrityVerified(boolean systemIntegrityVerified) { this.systemIntegrityVerified = systemIntegrityVerified; }
}
