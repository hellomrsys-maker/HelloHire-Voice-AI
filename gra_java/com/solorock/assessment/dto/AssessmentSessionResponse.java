package com.solorock.assessment.dto;

import java.util.List;
import java.util.Map;

public class AssessmentSessionResponse {
    private String learnerId;
    private String estimatedCefrLevel;
    private float percentageScore;
    private float irtTheta;
    private float standardError;
    private Map<String, Float> domainScores;
    private List<String> personalizedRoadmap;

    public AssessmentSessionResponse() {}

    public String getLearnerId() { return learnerId; }
    public void setLearnerId(String learnerId) { this.learnerId = learnerId; }

    public String getEstimatedCefrLevel() { return estimatedCefrLevel; }
    public void setEstimatedCefrLevel(String estimatedCefrLevel) { this.estimatedCefrLevel = estimatedCefrLevel; }

    public float getPercentageScore() { return percentageScore; }
    public void setPercentageScore(float percentageScore) { this.percentageScore = percentageScore; }

    public float getIrtTheta() { return irtTheta; }
    public void setIrtTheta(float irtTheta) { this.irtTheta = irtTheta; }

    public float getStandardError() { return standardError; }
    public void setStandardError(float standardError) { this.standardError = standardError; }

    public Map<String, Float> getDomainScores() { return domainScores; }
    public void setDomainScores(Map<String, Float> domainScores) { this.domainScores = domainScores; }

    public List<String> getPersonalizedRoadmap() { return personalizedRoadmap; }
    public void setPersonalizedRoadmap(List<String> personalizedRoadmap) { this.personalizedRoadmap = personalizedRoadmap; }
}
