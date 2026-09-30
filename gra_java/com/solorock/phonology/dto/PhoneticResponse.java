package com.solorock.phonology.dto;

import java.util.List;

public class PhoneticResponse {
    private String utterance;
    private String ipaTranscription;
    private boolean hasStressShift;
    private String primaryStressPattern;
    private List<String> connectedSpeechPhenomena;
    private float articulationPrecisionScore;

    public PhoneticResponse() {}

    public String getUtterance() { return utterance; }
    public void setUtterance(String utterance) { this.utterance = utterance; }

    public String getIpaTranscription() { return ipaTranscription; }
    public void setIpaTranscription(String ipaTranscription) { this.ipaTranscription = ipaTranscription; }

    public boolean isHasStressShift() { return hasStressShift; }
    public void setHasStressShift(boolean hasStressShift) { this.hasStressShift = hasStressShift; }

    public String getPrimaryStressPattern() { return primaryStressPattern; }
    public void setPrimaryStressPattern(String primaryStressPattern) { this.primaryStressPattern = primaryStressPattern; }

    public List<String> getConnectedSpeechPhenomena() { return connectedSpeechPhenomena; }
    public void setConnectedSpeechPhenomena(List<String> connectedSpeechPhenomena) { this.connectedSpeechPhenomena = connectedSpeechPhenomena; }

    public float getArticulationPrecisionScore() { return articulationPrecisionScore; }
    public void setArticulationPrecisionScore(float articulationPrecisionScore) { this.articulationPrecisionScore = articulationPrecisionScore; }
}
