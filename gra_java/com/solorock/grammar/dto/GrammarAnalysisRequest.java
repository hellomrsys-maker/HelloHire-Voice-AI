package com.solorock.grammar.dto;

import java.util.List;

public class GrammarAnalysisRequest {
    private String text;
    private String language;
    private boolean verifyUniversalGrammar;
    private boolean checkCaseFilter;
    private boolean checkBindingTheory;

    public GrammarAnalysisRequest() {
        this.language = "en";
        this.verifyUniversalGrammar = true;
        this.checkCaseFilter = true;
        this.checkBindingTheory = true;
    }

    public GrammarAnalysisRequest(String text) {
        this();
        this.text = text;
    }

    public String getText() { return text; }
    public void setText(String text) { this.text = text; }

    public String getLanguage() { return language; }
    public void setLanguage(String language) { this.language = language; }

    public boolean isVerifyUniversalGrammar() { return verifyUniversalGrammar; }
    public void setVerifyUniversalGrammar(boolean verifyUniversalGrammar) { this.verifyUniversalGrammar = verifyUniversalGrammar; }

    public boolean isCheckCaseFilter() { return checkCaseFilter; }
    public void setCheckCaseFilter(boolean checkCaseFilter) { this.checkCaseFilter = checkCaseFilter; }

    public boolean isCheckBindingTheory() { return checkBindingTheory; }
    public void setCheckBindingTheory(boolean checkBindingTheory) { this.checkBindingTheory = checkBindingTheory; }
}
