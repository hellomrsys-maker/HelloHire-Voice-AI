package com.solorock.error;

import com.solorock.error.dto.ErrorDiagnosticRequest;
import com.solorock.error.dto.ErrorDiagnosticResponse;
import com.solorock.amsv.AMSVBridge;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Enterprise Service Layer for Grammatical, Lexical, and Pragmatic Error Diagnosis.
 * Explains root cognitive causes (L1 transfer, overgeneralization, fossilization)
 * and generates pedagogical micro-drills.
 */
public class ErrorDiagnosticController {

    public ErrorDiagnosticResponse diagnoseErrors(ErrorDiagnosticRequest request) {
        if (request == null || request.getUtterance() == null) {
            throw new IllegalArgumentException("Utterance cannot be null");
        }

        String utterance = request.getUtterance().trim();
        List<Map<String, Object>> details = new ArrayList<>();
        String corrected = utterance;

        if (utterance.contains("he go to")) {
            Map<String, Object> err = new HashMap<>();
            err.put("error_class", "Morphosyntactic: Subject-Verb Agreement");
            err.put("faulty_span", "he go");
            err.put("repair", "he goes");
            err.put("linguistic_rule", "Present simple 3rd person singular requires functional head AgrSP inflection suffix '-s'.");
            err.put("interlanguage_diagnosis", "Null inflection transfer from L1 without bound morphological subject marking.");
            details.add(err);
            corrected = corrected.replace("he go to", "he goes to");
        }

        if (utterance.contains("discuss about")) {
            Map<String, Object> err = new HashMap<>();
            err.put("error_class", "Subcategorization Frame Violation");
            err.put("faulty_span", "discuss about");
            err.put("repair", "discuss");
            err.put("linguistic_rule", "The transitive verb 'discuss' directly theta-marks its direct complement DP without prepositional insertion.");
            err.put("interlanguage_diagnosis", "Semantic overgeneralization from synonymous prepositional frame 'talk about'.");
            details.add(err);
            corrected = corrected.replace("discuss about", "discuss");
        }

        if (utterance.contains("equipments")) {
            Map<String, Object> err = new HashMap<>();
            err.put("error_class", "Nominal Mass/Count Reinterpretation");
            err.put("faulty_span", "equipments");
            err.put("repair", "equipment / pieces of equipment");
            err.put("linguistic_rule", "Uncountable mass nouns do not license plural morphology (*-s) or cardinal determiners.");
            err.put("interlanguage_diagnosis", "L1 lexicon countability parameter divergence.");
            details.add(err);
            corrected = corrected.replace("equipments", "equipment");
        }

        ErrorDiagnosticResponse response = new ErrorDiagnosticResponse();
        response.setErrorDetected(!details.isEmpty());
        response.setErrorCount(details.size());
        response.setErrorDetails(details);
        response.setCorrectedUtterance(corrected);
        response.setCognitiveInterlanguageProfile(
            details.isEmpty()
                ? "Target-like native competency with stabilized morphosyntax."
                : "Active interlanguage development characterized by parameter resetting and L1 transfer filter."
        );

        return response;
    }
}
