package com.solorock.metrics.dto;

import java.util.List;
import java.util.Map;

public class GrammarMetricResponse {
    private String text;
    private String targetGenre;
    private float compositeScore;
    private boolean isGrammaticallyAcceptable;
    private Map<String, Float> checklistScores; // A..G
    private List<String> detectedViolations;
    private List<String> genreRecommendations;

    public GrammarMetricResponse() {}

    public String getText() { return text; }
    public void setText(String text) { this.text = text; }

    public String getTargetGenre() { return targetGenre; }
    public void setTargetGenre(String targetGenre) { this.targetGenre = targetGenre; }

    public float getCompositeScore() { return compositeScore; }
    public void setCompositeScore(float compositeScore) { this.compositeScore = compositeScore; }

    public boolean isGrammaticallyAcceptable() { return isGrammaticallyAcceptable; }
    public void setGrammaticallyAcceptable(boolean grammaticallyAcceptable) { isGrammaticallyAcceptable = grammaticallyAcceptable; }

    public Map<String, Float> getChecklistScores() { return checklistScores; }
    public void setChecklistScores(Map<String, Float> checklistScores) { this.checklistScores = checklistScores; }

    public List<String> getDetectedViolations() { return detectedViolations; }
    public void setDetectedViolations(List<String> detectedViolations) { this.detectedViolations = detectedViolations; }

    public List<String> getGenreRecommendations() { return genreRecommendations; }
    public void setGenreRecommendations(List<String> genreRecommendations) { this.genreRecommendations = genreRecommendations; }
}
