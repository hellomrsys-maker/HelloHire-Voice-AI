package com.solorock.metrics.dto;

public class GrammarMetricRequest {
    private String text;
    private String targetGenre; // Essay, Report, Email, Letter, Academic
    private boolean deepChecklistAnalysis;

    public GrammarMetricRequest() {
        this.targetGenre = "Essay";
        this.deepChecklistAnalysis = true;
    }

    public GrammarMetricRequest(String text, String targetGenre) {
        this();
        this.text = text;
        this.targetGenre = targetGenre;
    }

    public String getText() { return text; }
    public void setText(String text) { this.text = text; }

    public String getTargetGenre() { return targetGenre; }
    public void setTargetGenre(String targetGenre) { this.targetGenre = targetGenre; }

    public boolean isDeepChecklistAnalysis() { return deepChecklistAnalysis; }
    public void setDeepChecklistAnalysis(boolean deepChecklistAnalysis) { this.deepChecklistAnalysis = deepChecklistAnalysis; }
}
