package com.solorock.aeee.dto;

import java.util.Map;

/**
 * Response DTO returning updated IRT ability, SEM, rubric score, and next question.
 */
public class ExamEvaluationResponse {
    private String sessionId;
    private int questionIndex;
    private float abilityTheta;
    private float standardError;
    private float compositeScore;
    private Map<String, Float> dimensionScores;
    private String nextQuestion;
    private boolean examCompleted;

    public ExamEvaluationResponse() {}

    public ExamEvaluationResponse(String sessionId, int questionIndex, float abilityTheta,
                                float standardError, float compositeScore,
                                Map<String, Float> dimensionScores, String nextQuestion,
                                boolean examCompleted) {
        this.sessionId = sessionId;
        this.questionIndex = questionIndex;
        this.abilityTheta = abilityTheta;
        this.standardError = standardError;
        this.compositeScore = compositeScore;
        this.dimensionScores = dimensionScores;
        this.nextQuestion = nextQuestion;
        this.examCompleted = examCompleted;
    }

    public String getSessionId() { return sessionId; }
    public void setSessionId(String sessionId) { this.sessionId = sessionId; }

    public int getQuestionIndex() { return questionIndex; }
    public void setQuestionIndex(int questionIndex) { this.questionIndex = questionIndex; }

    public float getAbilityTheta() { return abilityTheta; }
    public void setAbilityTheta(float abilityTheta) { this.abilityTheta = abilityTheta; }

    public float getStandardError() { return standardError; }
    public void setStandardError(float standardError) { this.standardError = standardError; }

    public float getCompositeScore() { return compositeScore; }
    public void setCompositeScore(float compositeScore) { this.compositeScore = compositeScore; }

    public Map<String, Float> getDimensionScores() { return dimensionScores; }
    public void setDimensionScores(Map<String, Float> dimensionScores) { this.dimensionScores = dimensionScores; }

    public String getNextQuestion() { return nextQuestion; }
    public void setNextQuestion(String nextQuestion) { this.nextQuestion = nextQuestion; }

    public boolean isExamCompleted() { return examCompleted; }
    public void setExamCompleted(boolean examCompleted) { this.examCompleted = examCompleted; }
}
