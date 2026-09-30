package com.solorock.writing.dto;

public class WritingCritiqueRequest {
    private String documentText;
    private String targetAudience;
    private String documentType; // AcademicEssay, ExecutiveMemo, TechnicalProposal, CreativeProse

    public WritingCritiqueRequest() {
        this.targetAudience = "Executive";
        this.documentType = "ExecutiveMemo";
    }

    public WritingCritiqueRequest(String documentText, String documentType) {
        this();
        this.documentText = documentText;
        this.documentType = documentType;
    }

    public String getDocumentText() { return documentText; }
    public void setDocumentText(String documentText) { this.documentText = documentText; }

    public String getTargetAudience() { return targetAudience; }
    public void setTargetAudience(String targetAudience) { this.targetAudience = targetAudience; }

    public String getDocumentType() { return documentType; }
    public void setDocumentType(String documentType) { this.documentType = documentType; }
}
