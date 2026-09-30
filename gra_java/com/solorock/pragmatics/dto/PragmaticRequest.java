package com.solorock.pragmatics.dto;

public class PragmaticRequest {
    private String utterance;
    private String conversationalContext;
    private String speakerStatus; // Peer, Subordinate, Superior

    public PragmaticRequest() {
        this.speakerStatus = "Peer";
    }

    public PragmaticRequest(String utterance, String conversationalContext) {
        this();
        this.utterance = utterance;
        this.conversationalContext = conversationalContext;
    }

    public String getUtterance() { return utterance; }
    public void setUtterance(String utterance) { this.utterance = utterance; }

    public String getConversationalContext() { return conversationalContext; }
    public void setConversationalContext(String conversationalContext) { this.conversationalContext = conversationalContext; }

    public String getSpeakerStatus() { return speakerStatus; }
    public void setSpeakerStatus(String speakerStatus) { this.speakerStatus = speakerStatus; }
}
