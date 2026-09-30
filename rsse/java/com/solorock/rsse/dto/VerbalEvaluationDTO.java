package com.solorock.rsse.dto;

import java.io.Serializable;

/**
 * Data Transfer Object for Recruitment Verbal Communication Evaluation.
 */
public class VerbalEvaluationDTO implements Serializable {
    private static final long serialVersionUID = 1L;

    private String candidateId;
    private int formatCode;
    private float measuredWpm;
    private float registerCompliance;
    private float situationScore;
    private float taskScore;
    private float actionScore;
    private float resultScore;
    private float starCoherence;
    private float jargonDensity;
    private float fillerPenalty;
    private float compositeScore;
    private boolean passed;

    public VerbalEvaluationDTO() {}

    public VerbalEvaluationDTO(
        String candidateId,
        int formatCode,
        float measuredWpm,
        float registerCompliance,
        float situationScore,
        float taskScore,
        float actionScore,
        float resultScore,
        float starCoherence,
        float jargonDensity,
        float fillerPenalty,
        float compositeScore,
        boolean passed
    ) {
        this.candidateId = candidateId;
        this.formatCode = formatCode;
        this.measuredWpm = measuredWpm;
        this.registerCompliance = registerCompliance;
        this.situationScore = situationScore;
        this.taskScore = taskScore;
        this.actionScore = actionScore;
        this.resultScore = resultScore;
        this.starCoherence = starCoherence;
        this.jargonDensity = jargonDensity;
        this.fillerPenalty = fillerPenalty;
        this.compositeScore = compositeScore;
        this.passed = passed;
    }

    public String getCandidateId() { return candidateId; }
    public void setCandidateId(String candidateId) { this.candidateId = candidateId; }

    public int getFormatCode() { return formatCode; }
    public void setFormatCode(int formatCode) { this.formatCode = formatCode; }

    public float getMeasuredWpm() { return measuredWpm; }
    public void setMeasuredWpm(float measuredWpm) { this.measuredWpm = measuredWpm; }

    public float getRegisterCompliance() { return registerCompliance; }
    public void setRegisterCompliance(float registerCompliance) { this.registerCompliance = registerCompliance; }

    public float getSituationScore() { return situationScore; }
    public void setSituationScore(float situationScore) { this.situationScore = situationScore; }

    public float getTaskScore() { return taskScore; }
    public void setTaskScore(float taskScore) { this.taskScore = taskScore; }

    public float getActionScore() { return actionScore; }
    public void setActionScore(float actionScore) { this.actionScore = actionScore; }

    public float getResultScore() { return resultScore; }
    public void setResultScore(float resultScore) { this.resultScore = resultScore; }

    public float getStarCoherence() { return starCoherence; }
    public void setStarCoherence(float starCoherence) { this.starCoherence = starCoherence; }

    public float getJargonDensity() { return jargonDensity; }
    public void setJargonDensity(float jargonDensity) { this.jargonDensity = jargonDensity; }

    public float getFillerPenalty() { return fillerPenalty; }
    public void setFillerPenalty(float fillerPenalty) { this.fillerPenalty = fillerPenalty; }

    public float getCompositeScore() { return compositeScore; }
    public void setCompositeScore(float compositeScore) { this.compositeScore = compositeScore; }

    public boolean isPassed() { return passed; }
    public void setPassed(boolean passed) { this.passed = passed; }
}
