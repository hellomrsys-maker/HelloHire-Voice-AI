package com.solorock.pragmatics.dto;

import java.util.List;
import java.util.Map;

public class PragmaticResponse {
    private String primarySpeechAct;
    private String illocutionaryForce;
    private Map<String, Boolean> griceanMaxims;
    private List<String> conversationalImplicatures;
    private String politenessStrategy;
    private float appropriatenessIndex;

    public PragmaticResponse() {}

    public String getPrimarySpeechAct() { return primarySpeechAct; }
    public void setPrimarySpeechAct(String primarySpeechAct) { this.primarySpeechAct = primarySpeechAct; }

    public String getIllocutionaryForce() { return illocutionaryForce; }
    public void setIllocutionaryForce(String illocutionaryForce) { this.illocutionaryForce = illocutionaryForce; }

    public Map<String, Boolean> getGriceanMaxims() { return griceanMaxims; }
    public void setGriceanMaxims(Map<String, Boolean> griceanMaxims) { this.griceanMaxims = griceanMaxims; }

    public List<String> getConversationalImplicatures() { return conversationalImplicatures; }
    public void setConversationalImplicatures(List<String> conversationalImplicatures) { this.conversationalImplicatures = conversationalImplicatures; }

    public String getPolitenessStrategy() { return politenessStrategy; }
    public void setPolitenessStrategy(String politenessStrategy) { this.politenessStrategy = politenessStrategy; }

    public float getAppropriatenessIndex() { return appropriatenessIndex; }
    public void setAppropriatenessIndex(float appropriatenessIndex) { this.appropriatenessIndex = appropriatenessIndex; }
}
