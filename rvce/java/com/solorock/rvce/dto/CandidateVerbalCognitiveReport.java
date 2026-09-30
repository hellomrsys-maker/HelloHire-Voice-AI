package com.solorock.rvce.dto;

import java.io.Serializable;

/**
 * Immutable Data Transfer Object capturing a candidate's verbal cognitive scorecard
 * across all six core cognitive dimensions.
 */
public class CandidateVerbalCognitiveReport implements Serializable {
    private static final long serialVersionUID = 1L;

    private final String candidateId;
    private final int turnNumber;
    private final float thinkingScore;
    private final float concentrationScore;
    private final float recallScore;
    private final float creativityScore;
    private final float imaginationScore;
    private final float verbalScore;
    private final float compositeHireability;
    private final int recommendationCode; // 1=Strong Hire, 2=Hire, 3=Leaning, 4=No Hire
    private final String recommendationLabel;

    public CandidateVerbalCognitiveReport(
        String candidateId,
        int turnNumber,
        float thinkingScore,
        float concentrationScore,
        float recallScore,
        float creativityScore,
        float imaginationScore,
        float verbalScore,
        float compositeHireability,
        int recommendationCode,
        String recommendationLabel
    ) {
        this.candidateId = candidateId;
        this.turnNumber = turnNumber;
        this.thinkingScore = thinkingScore;
        this.concentrationScore = concentrationScore;
        this.recallScore = recallScore;
        this.creativityScore = creativityScore;
        this.imaginationScore = imaginationScore;
        this.verbalScore = verbalScore;
        this.compositeHireability = compositeHireability;
        this.recommendationCode = recommendationCode;
        this.recommendationLabel = recommendationLabel;
    }

    public String getCandidateId() { return candidateId; }
    public int getTurnNumber() { return turnNumber; }
    public float getThinkingScore() { return thinkingScore; }
    public float getConcentrationScore() { return concentrationScore; }
    public float getRecallScore() { return recallScore; }
    public float getCreativityScore() { return creativityScore; }
    public float getImaginationScore() { return imaginationScore; }
    public float getVerbalScore() { return verbalScore; }
    public float getCompositeHireability() { return compositeHireability; }
    public int getRecommendationCode() { return recommendationCode; }
    public String getRecommendationLabel() { return recommendationLabel; }

    @Override
    public String toString() {
        return String.format(
            "CandidateReport[id=%s, turn=%d, composite=%.3f, decision=%s (Think:%.2f, Focus:%.2f, Recall:%.2f, Creat:%.2f, Imagi:%.2f, Verbal:%.2f)]",
            candidateId, turnNumber, compositeHireability, recommendationLabel,
            thinkingScore, concentrationScore, recallScore, creativityScore, imaginationScore, verbalScore
        );
    }
}
