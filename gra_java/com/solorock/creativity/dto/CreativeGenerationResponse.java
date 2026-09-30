package com.solorock.creativity.dto;

import java.util.List;
import java.util.Map;

public class CreativeGenerationResponse {
    private String genre;
    private String register;
    private String generatedArtifact;
    private float noveltyIndex;
    private float metaphoricalTension;
    private float rhythmRegularity;
    private List<String> rhetoricalFigures;
    private Map<String, Object> metricProfile;

    public CreativeGenerationResponse() {}

    public String getGenre() { return genre; }
    public void setGenre(String genre) { this.genre = genre; }

    public String getRegister() { return register; }
    public void setRegister(String register) { this.register = register; }

    public String getGeneratedArtifact() { return generatedArtifact; }
    public void setGeneratedArtifact(String generatedArtifact) { this.generatedArtifact = generatedArtifact; }

    public float getNoveltyIndex() { return noveltyIndex; }
    public void setNoveltyIndex(float noveltyIndex) { this.noveltyIndex = noveltyIndex; }

    public float getMetaphoricalTension() { return metaphoricalTension; }
    public void setMetaphoricalTension(float metaphoricalTension) { this.metaphoricalTension = metaphoricalTension; }

    public float getRhythmRegularity() { return rhythmRegularity; }
    public void setRhythmRegularity(float rhythmRegularity) { this.rhythmRegularity = rhythmRegularity; }

    public List<String> getRhetoricalFigures() { return rhetoricalFigures; }
    public void setRhetoricalFigures(List<String> rhetoricalFigures) { this.rhetoricalFigures = rhetoricalFigures; }

    public Map<String, Object> getMetricProfile() { return metricProfile; }
    public void setMetricProfile(Map<String, Object> metricProfile) { this.metricProfile = metricProfile; }
}
