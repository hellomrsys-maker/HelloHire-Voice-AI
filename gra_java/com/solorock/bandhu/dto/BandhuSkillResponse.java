package com.solorock.bandhu.dto;

import java.util.ArrayList;
import java.util.List;

public class BandhuSkillResponse {
    private String text;
    private String skill;
    private String era;
    private float structuralScore;
    private float registerScore;
    private float consistencyScore;
    private int fatalErrorsCount;
    private int clarityErrorsCount;
    private int registerErrorsCount;
    private int stylePreferenceCount;
    private String recommendedEditingStage; // Draft, Structural, Line, Copy, Proofread
    private List<String> diagnostics = new ArrayList<>();

    public BandhuSkillResponse() {}

    public String getText() { return text; }
    public void setText(String text) { this.text = text; }

    public String getSkill() { return skill; }
    public void setSkill(String skill) { this.skill = skill; }

    public String getEra() { return era; }
    public void setEra(String era) { this.era = era; }

    public float getStructuralScore() { return structuralScore; }
    public void setStructuralScore(float structuralScore) { this.structuralScore = structuralScore; }

    public float getRegisterScore() { return registerScore; }
    public void setRegisterScore(float registerScore) { this.registerScore = registerScore; }

    public float getConsistencyScore() { return consistencyScore; }
    public void setConsistencyScore(float consistencyScore) { this.consistencyScore = consistencyScore; }

    public int getFatalErrorsCount() { return fatalErrorsCount; }
    public void setFatalErrorsCount(int fatalErrorsCount) { this.fatalErrorsCount = fatalErrorsCount; }

    public int getClarityErrorsCount() { return clarityErrorsCount; }
    public void setClarityErrorsCount(int clarityErrorsCount) { this.clarityErrorsCount = clarityErrorsCount; }

    public int getRegisterErrorsCount() { return registerErrorsCount; }
    public void setRegisterErrorsCount(int registerErrorsCount) { this.registerErrorsCount = registerErrorsCount; }

    public int getStylePreferenceCount() { return stylePreferenceCount; }
    public void setStylePreferenceCount(int stylePreferenceCount) { this.stylePreferenceCount = stylePreferenceCount; }

    public String getRecommendedEditingStage() { return recommendedEditingStage; }
    public void setRecommendedEditingStage(String recommendedEditingStage) { this.recommendedEditingStage = recommendedEditingStage; }

    public List<String> getDiagnostics() { return diagnostics; }
    public void setDiagnostics(List<String> diagnostics) { this.diagnostics = diagnostics; }
}
