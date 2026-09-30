package com.solorock.sla.dto;

import java.util.List;

public class SLAResponse {
    private String interlanguageStage;
    private int pienemannProcessabilityLevel;
    private float fossilizationRisk;
    private String zoneOfProximalDevelopment;
    private List<String> targetedPedagogicalDrills;

    public SLAResponse() {}

    public String getInterlanguageStage() { return interlanguageStage; }
    public void setInterlanguageStage(String interlanguageStage) { this.interlanguageStage = interlanguageStage; }

    public int getPienemannProcessabilityLevel() { return pienemannProcessabilityLevel; }
    public void setPienemannProcessabilityLevel(int pienemannProcessabilityLevel) { this.pienemannProcessabilityLevel = pienemannProcessabilityLevel; }

    public float getFossilizationRisk() { return fossilizationRisk; }
    public void setFossilizationRisk(float fossilizationRisk) { this.fossilizationRisk = fossilizationRisk; }

    public String getZoneOfProximalDevelopment() { return zoneOfProximalDevelopment; }
    public void setZoneOfProximalDevelopment(String zoneOfProximalDevelopment) { this.zoneOfProximalDevelopment = zoneOfProximalDevelopment; }

    public List<String> getTargetedPedagogicalDrills() { return targetedPedagogicalDrills; }
    public void setTargetedPedagogicalDrills(List<String> targetedPedagogicalDrills) { this.targetedPedagogicalDrills = targetedPedagogicalDrills; }
}
