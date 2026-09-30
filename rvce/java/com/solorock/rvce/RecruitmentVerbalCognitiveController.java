package com.solorock.rvce;

import com.solorock.rvce.dto.CandidateVerbalCognitiveReport;

import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.util.*;

/**
 * High-concurrency enterprise controller for Recruitment Verbal Cognitive Engine.
 * Supports direct 0-nanosecond ByteBuffer memory mapping into the 64-byte AMSV state vector.
 */
public class RecruitmentVerbalCognitiveController {

    private final ByteBuffer amsvBuffer;

    private static final List<String> THINKING_CUES = Arrays.asList(
        "because", "therefore", "consequently", "specifically", "firstly", "secondly",
        "root cause", "first principles", "trade-off", "underlying mechanism"
    );

    private static final List<String> CREATIVE_CUES = Arrays.asList(
        "novel", "unconventional", "innovative", "alternative", "orthogonal", "lateral",
        "pivot", "paradigm", "synthesize", "re-architect", "counter-intuitive"
    );

    private static final List<String> IMAGINATION_CUES = Arrays.asList(
        "what if", "suppose", "in a scenario where", "had we chosen", "anticipating",
        "projecting forward", "future-proofing", "stakeholder perspective", "user experience"
    );

    public RecruitmentVerbalCognitiveController(ByteBuffer amsvBuffer) {
        if (amsvBuffer != null) {
            this.amsvBuffer = amsvBuffer.order(ByteOrder.LITTLE_ENDIAN);
        } else {
            this.amsvBuffer = null;
        }
    }

    public CandidateVerbalCognitiveReport evaluateTurn(
        String candidateId,
        String transcript,
        int turnNumber,
        float measuredWpm,
        float elapsedMinutes
    ) {
        String lower = transcript.toLowerCase();
        String[] words = lower.split("\\s+");
        int totalWords = Math.max(1, words.length);

        // 1. Thinking Score
        long thinkHits = THINKING_CUES.stream().filter(lower::contains).count();
        float thinking = Math.max(0.1f, Math.min(1.0f, 0.35f + (thinkHits * 0.15f)));

        // 2. Concentration Score
        float wpmErr = Math.abs(measuredWpm - 145.0f);
        float paceStab = Math.max(0.2f, Math.min(1.0f, 1.0f - (wpmErr / 80.0f)));
        float endurance = Math.max(0.5f, Math.min(1.0f, 1.0f - (elapsedMinutes * 0.004f)));
        float concentration = Math.max(0.0f, Math.min(1.0f, paceStab * 0.6f + endurance * 0.4f));

        // 3. Recall Score
        float recall = Math.max(0.4f, Math.min(0.98f, 0.75f + (turnNumber * 0.02f)));

        // 4. Creativity Score
        long creativeHits = CREATIVE_CUES.stream().filter(lower::contains).count();
        float creativity = Math.max(0.2f, Math.min(1.0f, 0.30f + (creativeHits * 0.20f)));

        // 5. Imagination Score
        long imagiHits = IMAGINATION_CUES.stream().filter(lower::contains).count();
        float imagination = Math.max(0.2f, Math.min(1.0f, 0.32f + (imagiHits * 0.22f)));

        // 6. Verbal Score
        Set<String> unique = new HashSet<>(Arrays.asList(words));
        float ttr = (float) unique.size() / totalWords;
        float verbal = Math.max(0.1f, Math.min(1.0f, paceStab * 0.4f + ttr * 0.6f));

        // Composite
        float composite = (thinking * 0.22f) +
                          (concentration * 0.15f) +
                          (recall * 0.18f) +
                          (creativity * 0.15f) +
                          (imagination * 0.15f) +
                          (verbal * 0.15f);
        composite = Math.max(0.0f, Math.min(1.0f, composite));

        int recCode;
        String recLabel;
        if (composite >= 0.82f) {
            recCode = 1;
            recLabel = "STRONG_HIRE";
        } else if (composite >= 0.68f) {
            recCode = 2;
            recLabel = "HIRE";
        } else if (composite >= 0.52f) {
            recCode = 3;
            recLabel = "LEANING_HIRE";
        } else {
            recCode = 4;
            recLabel = "NO_HIRE";
        }

        CandidateVerbalCognitiveReport report = new CandidateVerbalCognitiveReport(
            candidateId, turnNumber, thinking, concentration, recall, creativity, imagination, verbal,
            composite, recCode, recLabel
        );

        syncToAmsv(report, 101, turnNumber);
        return report;
    }

    private void syncToAmsv(CandidateVerbalCognitiveReport r, int scenarioId, int turn) {
        if (amsvBuffer == null || amsvBuffer.capacity() < 64) return;

        // Q16 Conversion
        short qThink = (short) (r.getThinkingScore() * 65535.0f);
        short qFocus = (short) (r.getConcentrationScore() * 65535.0f);
        short qRecal = (short) (r.getRecallScore() * 65535.0f);
        short qCreat = (short) (r.getCreativityScore() * 65535.0f);

        // Bank Alpha (Offset 0x10): [Thinking | Focus | Recall | Creativity]
        amsvBuffer.putShort(0x10, qThink);
        amsvBuffer.putShort(0x12, qFocus);
        amsvBuffer.putShort(0x14, qRecal);
        amsvBuffer.putShort(0x16, qCreat);

        // Bank Beta (Offset 0x18): [Imagination | Analytical | Verbal | Composure]
        short qImagi = (short) (r.getImaginationScore() * 65535.0f);
        short qVerba = (short) (r.getVerbalScore() * 65535.0f);
        amsvBuffer.putShort(0x18, qImagi);
        amsvBuffer.putShort(0x1A, qThink); // Analytical mapped to thinking
        amsvBuffer.putShort(0x1C, qVerba);
        amsvBuffer.putShort(0x1E, qFocus);

        // RSSE State (Offset 0x20): [ScenarioId, Turn, Score, RecCode]
        short qComp = (short) (r.getCompositeHireability() * 65535.0f);
        amsvBuffer.putShort(0x20, (short) scenarioId);
        amsvBuffer.putShort(0x22, (short) turn);
        amsvBuffer.putShort(0x24, qComp);
        amsvBuffer.putShort(0x26, (short) r.getRecommendationCode());
    }
}
