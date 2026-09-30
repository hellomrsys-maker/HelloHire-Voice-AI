package com.solorock.creativity.dto;

public class CreativeGenerationRequest {
    private String genre; // ShakespeareanSonnet, Haiku, PersuasiveOration
    private String theme;
    private String register; // Academic, CorporateExecutive, VictorianElevated, PoeticLyrical
    private float targetNovelty;

    public CreativeGenerationRequest() {
        this.genre = "Haiku";
        this.theme = "nature and cosmos";
        this.register = "PoeticLyrical";
        this.targetNovelty = 0.85f;
    }

    public CreativeGenerationRequest(String genre, String theme, String register) {
        this.genre = genre;
        this.theme = theme;
        this.register = register;
        this.targetNovelty = 0.85f;
    }

    public String getGenre() { return genre; }
    public void setGenre(String genre) { this.genre = genre; }

    public String getTheme() { return theme; }
    public void setTheme(String theme) { this.theme = theme; }

    public String getRegister() { return register; }
    public void setRegister(String register) { this.register = register; }

    public float getTargetNovelty() { return targetNovelty; }
    public void setTargetNovelty(float targetNovelty) { this.targetNovelty = targetNovelty; }
}
