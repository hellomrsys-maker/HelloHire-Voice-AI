package com.solorock.error.dto;

public class ErrorDiagnosticRequest {
    private String utterance;
    private String nativeLanguage;
    private boolean deepDiagnosticExplanation;

    public ErrorDiagnosticRequest() {
        this.nativeLanguage = "es";
        this.deepDiagnosticExplanation = true;
    }

    public ErrorDiagnosticRequest(String utterance) {
        this();
        this.utterance = utterance;
    }

    public String getUtterance() { return utterance; }
    public void setUtterance(String utterance) { this.utterance = utterance; }

    public String getNativeLanguage() { return nativeLanguage; }
    public void setNativeLanguage(String nativeLanguage) { this.nativeLanguage = nativeLanguage; }

    public boolean isDeepDiagnosticExplanation() { return deepDiagnosticExplanation; }
    public void setDeepDiagnosticExplanation(boolean deepDiagnosticExplanation) { this.deepDiagnosticExplanation = deepDiagnosticExplanation; }
}
