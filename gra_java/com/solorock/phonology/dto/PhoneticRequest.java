package com.solorock.phonology.dto;

public class PhoneticRequest {
    private String utterance;
    private String grammaticalRole;
    private String targetAccent;

    public PhoneticRequest() {
        this.grammaticalRole = "noun";
        this.targetAccent = "GeneralAmerican";
    }

    public PhoneticRequest(String utterance, String grammaticalRole) {
        this();
        this.utterance = utterance;
        this.grammaticalRole = grammaticalRole;
    }

    public String getUtterance() { return utterance; }
    public void setUtterance(String utterance) { this.utterance = utterance; }

    public String getGrammaticalRole() { return grammaticalRole; }
    public void setGrammaticalRole(String grammaticalRole) { this.grammaticalRole = grammaticalRole; }

    public String getTargetAccent() { return targetAccent; }
    public void setTargetAccent(String targetAccent) { this.targetAccent = targetAccent; }
}
