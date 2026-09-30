package com.solorock.grammar.dto;

import java.util.List;
import java.util.Map;

public class GrammarAnalysisResponse {
    private boolean grammaticallyValid;
    private String clauseType;
    private int syntacticTreeDepth;
    private float structuralComplexityScore;
    private List<String> detectedErrors;
    private String universalGrammarProof;
    private Map<String, Object> featureVector;

    public GrammarAnalysisResponse() {}

    public boolean isGrammaticallyValid() { return grammaticallyValid; }
    public void setGrammaticallyValid(boolean grammaticallyValid) { this.grammaticallyValid = grammaticallyValid; }

    public String getClauseType() { return clauseType; }
    public void setClauseType(String clauseType) { this.clauseType = clauseType; }

    public int getSyntacticTreeDepth() { return syntacticTreeDepth; }
    public void setSyntacticTreeDepth(int syntacticTreeDepth) { this.syntacticTreeDepth = syntacticTreeDepth; }

    public float getStructuralComplexityScore() { return structuralComplexityScore; }
    public void setStructuralComplexityScore(float structuralComplexityScore) { this.structuralComplexityScore = structuralComplexityScore; }

    public List<String> getDetectedErrors() { return detectedErrors; }
    public void setDetectedErrors(List<String> detectedErrors) { this.detectedErrors = detectedErrors; }

    public String getUniversalGrammarProof() { return universalGrammarProof; }
    public void setUniversalGrammarProof(String universalGrammarProof) { this.universalGrammarProof = universalGrammarProof; }

    public Map<String, Object> getFeatureVector() { return featureVector; }
    public void setFeatureVector(Map<String, Object> featureVector) { this.featureVector = featureVector; }
}
