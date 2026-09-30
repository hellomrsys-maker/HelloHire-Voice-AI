package com.solorock.bandhu.dto;

public class BandhuSkillRequest {
    private String text;
    private String targetSkill; // Writing, Emailing, Listening, Pronouncing, Reviewing, BookWriting
    private String targetLanguage;
    private String historicalEra; // Ancient, Historical, Modern, Digital

    public BandhuSkillRequest() {}

    public BandhuSkillRequest(String text, String targetSkill, String targetLanguage, String historicalEra) {
        this.text = text;
        this.targetSkill = targetSkill;
        this.targetLanguage = targetLanguage;
        this.historicalEra = historicalEra;
    }

    public String getText() { return text; }
    public void setText(String text) { this.text = text; }

    public String getTargetSkill() { return targetSkill; }
    public void setTargetSkill(String targetSkill) { this.targetSkill = targetSkill; }

    public String getTargetLanguage() { return targetLanguage; }
    public void setTargetLanguage(String targetLanguage) { this.targetLanguage = targetLanguage; }

    public String getHistoricalEra() { return historicalEra; }
    public void setHistoricalEra(String historicalEra) { this.historicalEra = historicalEra; }
}
