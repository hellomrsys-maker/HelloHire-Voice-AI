package com.solorock.sla.dto;

import java.util.List;

public class SLARequest {
    private String learnerId;
    private String firstLanguage;
    private String targetLanguage;
    private List<String> observedErrors;
    private float yearsOfExposure;

    public SLARequest() {
        this.firstLanguage = "Spanish";
        this.targetLanguage = "English";
        this.yearsOfExposure = 2.0f;
    }

    public SLARequest(String learnerId, List<String> observedErrors) {
        this();
        this.learnerId = learnerId;
        this.observedErrors = observedErrors;
    }

    public String getLearnerId() { return learnerId; }
    public void setLearnerId(String learnerId) { this.learnerId = learnerId; }

    public String getFirstLanguage() { return firstLanguage; }
    public void setFirstLanguage(String firstLanguage) { this.firstLanguage = firstLanguage; }

    public String getTargetLanguage() { return targetLanguage; }
    public void setTargetLanguage(String targetLanguage) { this.targetLanguage = targetLanguage; }

    public List<String> getObservedErrors() { return observedErrors; }
    public void setObservedErrors(List<String> observedErrors) { this.observedErrors = observedErrors; }

    public float getYearsOfExposure() { return yearsOfExposure; }
    public void setYearsOfExposure(float yearsOfExposure) { this.yearsOfExposure = yearsOfExposure; }
}
