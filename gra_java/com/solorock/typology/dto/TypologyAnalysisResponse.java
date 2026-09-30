package com.solorock.typology.dto;

import java.util.List;
import java.util.Map;

public class TypologyAnalysisResponse {
    private String text;
    private String languageFamily;
    private String morphologicalType; // Isolating, Agglutinative, Fusional, Polysynthetic
    private String grammaticalAlignment; // NominativeAccusative, ErgativeAbsolutive, etc.
    private String headDirectionality; // HeadInitial, HeadFinal
    private float synthesisIndex;
    private float greenbergHarmony;
    private Map<String, Float> pillarScores; // P1..P8
    private List<String> transferFrictions;
    private String diagnosticSummary;

    public TypologyAnalysisResponse() {}

    public String getText() { return text; }
    public void setText(String text) { this.text = text; }

    public String getLanguageFamily() { return languageFamily; }
    public void setLanguageFamily(String languageFamily) { this.languageFamily = languageFamily; }

    public String getMorphologicalType() { return morphologicalType; }
    public void setMorphologicalType(String morphologicalType) { this.morphologicalType = morphologicalType; }

    public String getGrammaticalAlignment() { return grammaticalAlignment; }
    public void setGrammaticalAlignment(String grammaticalAlignment) { this.grammaticalAlignment = grammaticalAlignment; }

    public String getHeadDirectionality() { return headDirectionality; }
    public void setHeadDirectionality(String headDirectionality) { this.headDirectionality = headDirectionality; }

    public float getSynthesisIndex() { return synthesisIndex; }
    public void setSynthesisIndex(float synthesisIndex) { this.synthesisIndex = synthesisIndex; }

    public float getGreenbergHarmony() { return greenbergHarmony; }
    public void setGreenbergHarmony(float greenbergHarmony) { this.greenbergHarmony = greenbergHarmony; }

    public Map<String, Float> getPillarScores() { return pillarScores; }
    public void setPillarScores(Map<String, Float> pillarScores) { this.pillarScores = pillarScores; }

    public List<String> getTransferFrictions() { return transferFrictions; }
    public void setTransferFrictions(List<String> transferFrictions) { this.transferFrictions = transferFrictions; }

    public String getDiagnosticSummary() { return diagnosticSummary; }
    public void setDiagnosticSummary(String diagnosticSummary) { this.diagnosticSummary = diagnosticSummary; }
}
