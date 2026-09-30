package com.solorock.typology.dto;

public class TypologyAnalysisRequest {
    private String text;
    private String languageFamily; // e.g. "Turkic", "SinoTibetan", "IndoEuropean"
    private String languageIso;    // e.g. "tur", "cmn", "eng"
    private String nativeL1;       // e.g. "IndoEuropean"

    public TypologyAnalysisRequest() {}

    public TypologyAnalysisRequest(String text, String languageFamily, String languageIso, String nativeL1) {
        this.text = text;
        this.languageFamily = languageFamily;
        this.languageIso = languageIso;
        this.nativeL1 = nativeL1;
    }

    public String getText() { return text; }
    public void setText(String text) { this.text = text; }

    public String getLanguageFamily() { return languageFamily; }
    public void setLanguageFamily(String languageFamily) { this.languageFamily = languageFamily; }

    public String getLanguageIso() { return languageIso; }
    public void setLanguageIso(String languageIso) { this.languageIso = languageIso; }

    public String getNativeL1() { return nativeL1; }
    public void setNativeL1(String nativeL1) { this.nativeL1 = nativeL1; }
}
