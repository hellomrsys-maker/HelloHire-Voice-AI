package com.solorock.error.dto;

import java.util.List;
import java.util.Map;

public class ErrorDiagnosticResponse {
    private boolean errorDetected;
    private int errorCount;
    private List<Map<String, Object>> errorDetails;
    private String correctedUtterance;
    private String cognitiveInterlanguageProfile;

    public ErrorDiagnosticResponse() {}

    public boolean isErrorDetected() { return errorDetected; }
    public void setErrorDetected(boolean errorDetected) { this.errorDetected = errorDetected; }

    public int getErrorCount() { return errorCount; }
    public void setErrorCount(int errorCount) { this.errorCount = errorCount; }

    public List<Map<String, Object>> getErrorDetails() { return errorDetails; }
    public void setErrorDetails(List<Map<String, Object>> errorDetails) { this.errorDetails = errorDetails; }

    public String getCorrectedUtterance() { return correctedUtterance; }
    public void setCorrectedUtterance(String correctedUtterance) { this.correctedUtterance = correctedUtterance; }

    public String getCognitiveInterlanguageProfile() { return cognitiveInterlanguageProfile; }
    public void setCognitiveInterlanguageProfile(String cognitiveInterlanguageProfile) { this.cognitiveInterlanguageProfile = cognitiveInterlanguageProfile; }
}
