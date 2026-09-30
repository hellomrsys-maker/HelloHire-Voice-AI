package com.solorock.sla;

import com.solorock.sla.dto.SLARequest;
import com.solorock.sla.dto.SLAResponse;
import com.solorock.amsv.AMSVBridge;

import java.util.ArrayList;
import java.util.List;

/**
 * Enterprise Service Layer for Second Language Acquisition (SLA) & Pedagogical Interventions.
 * Evaluates Pienemann Processability hierarchies and fossilization risks.
 */
public class SLAPedagogyController {

    public SLAResponse diagnoseLearner(SLARequest request) {
        if (request == null) {
            request = new SLARequest();
        }

        List<String> errors = request.getObservedErrors() != null ? request.getObservedErrors() : new ArrayList<>();
        int level = 4; // Default to Stage 4 (S-Procedure)
        float fossilization = 0.25f;

        for (String err : errors) {
            String lower = err.toLowerCase();
            if (lower.contains("concord") || lower.contains("agreement")) {
                level = Math.min(level, 3); // Phrasal agreement
            }
            if (lower.contains("stative") || lower.contains("aspect")) {
                level = Math.min(level, 4);
            }
        }

        if (request.getYearsOfExposure() > 5.0f && !errors.isEmpty()) {
            fossilization = 0.65f;
        }

        List<String> drills = new ArrayList<>();
        drills.add("Stage-Appropriate Processing Drill: Fast-paced Subject-Verb Concord Inversion");
        drills.add("Cognitive Scaffolding: Visual Aspect Matrix for Stative vs Dynamic Predicates");

        SLAResponse response = new SLAResponse();
        response.setInterlanguageStage("Stage " + level + ": Transitional Interlanguage");
        response.setPienemannProcessabilityLevel(level);
        response.setFossilizationRisk(fossilization);
        response.setZoneOfProximalDevelopment("Target Stage " + (level + 1) + " (Krashen i+1 Subordinate Clausal Control)");
        response.setTargetedPedagogicalDrills(drills);

        return response;
    }
}
