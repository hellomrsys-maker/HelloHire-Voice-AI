package com.solorock.writing.dto;

import java.util.List;
import java.util.Map;

public class WritingCritiqueResponse {
    private float overallQualityScore;
    private float coherenceScore;
    private float cohesionScore;
    private float fleschKincaidGradeLevel;
    private float automatedReadabilityIndex;
    private List<String> paragraphTransitions;
    private List<String> stylisticRecommendations;
    private Map<String, Object> lexicalDensityMap;

    public WritingCritiqueResponse() {}

    public float getOverallQualityScore() { return overallQualityScore; }
    public void setOverallQualityScore(float overallQualityScore) { this.overallQualityScore = overallQualityScore; }

    public float getCoherenceScore() { return coherenceScore; }
    public void setCoherenceScore(float coherenceScore) { this.coherenceScore = coherenceScore; }

    public float getCohesionScore() { return cohesionScore; }
    public void setCohesionScore(float cohesionScore) { this.cohesionScore = cohesionScore; }

    public float getFleschKincaidGradeLevel() { return fleschKincaidGradeLevel; }
    public void setFleschKincaidGradeLevel(float fleschKincaidGradeLevel) { this.fleschKincaidGradeLevel = fleschKincaidGradeLevel; }

    public float getAutomatedReadabilityIndex() { return automatedReadabilityIndex; }
    public void setAutomatedReadabilityIndex(float automatedReadabilityIndex) { this.automatedReadabilityIndex = automatedReadabilityIndex; }

    public List<String> getParagraphTransitions() { return paragraphTransitions; }
    public void setParagraphTransitions(List<String> paragraphTransitions) { this.paragraphTransitions = paragraphTransitions; }

    public List<String> getStylisticRecommendations() { return stylisticRecommendations; }
    public void setStylisticRecommendations(List<String> stylisticRecommendations) { this.stylisticRecommendations = stylisticRecommendations; }

    public Map<String, Object> getLexicalDensityMap() { return lexicalDensityMap; }
    public void setLexicalDensityMap(Map<String, Object> lexicalDensityMap) { this.lexicalDensityMap = lexicalDensityMap; }
}
