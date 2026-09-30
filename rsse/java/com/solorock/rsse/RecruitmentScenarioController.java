package com.solorock.rsse;

import com.solorock.rsse.dto.ScenarioStartRequest;
import com.solorock.rsse.dto.ScenarioTurnRequest;
import com.solorock.rsse.dto.ScenarioTurnResponse;

import java.nio.ByteBuffer;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Enterprise Service Layer Controller for Recruitment Scenario Simulation Engine (RSSE).
 * Coordinates interview sessions, manages dynamic stage transitions,
 * and interfaces with the AMSV zero-bridge shared memory state vector.
 */
public class RecruitmentScenarioController {

    private final ByteBuffer amsvDirectBuffer;
    private final Map<String, ActiveScenarioSession> activeSessions = new ConcurrentHashMap<>();

    private static class ActiveScenarioSession {
        String sessionId;
        int formatCode;
        int scenarioId;
        int currentTurn;
        String currentPhase;
        float stressMultiplier;

        ActiveScenarioSession(String sessionId, int formatCode, int scenarioId) {
            this.sessionId = sessionId;
            this.formatCode = formatCode;
            this.scenarioId = scenarioId;
            this.currentTurn = 0;
            this.currentPhase = "WarmupIntroduction";
            this.stressMultiplier = 1.0f;
        }
    }

    public RecruitmentScenarioController(ByteBuffer amsvDirectBuffer) {
        this.amsvDirectBuffer = amsvDirectBuffer;
    }

    /**
     * Starts a new recruitment simulation session.
     */
    public ScenarioTurnResponse startScenario(ScenarioStartRequest request) {
        String sessionId = UUID.randomUUID().toString();
        ActiveScenarioSession session = new ActiveScenarioSession(sessionId, request.getFormatCode(), request.getScenarioId());
        activeSessions.put(sessionId, session);

        String openingPrompt = getOpeningPromptForFormat(request.getFormatCode());

        // Update AMSV state vector if direct buffer is present
        syncToAmsv(request.getScenarioId(), 0, 1.0f, 1);

        return new ScenarioTurnResponse(
            sessionId,
            0,
            session.currentPhase,
            1.0f,
            session.stressMultiplier,
            openingPrompt,
            false
        );
    }

    /**
     * Evaluates a candidate turn, advances phase, and returns next dynamic probe.
     */
    public ScenarioTurnResponse processTurn(ScenarioTurnRequest request) {
        ActiveScenarioSession session = activeSessions.get(request.getSessionId());
        if (session == null) {
            throw new IllegalArgumentException("Invalid session ID: " + request.getSessionId());
        }

        session.currentTurn++;

        // Calculate heuristic register compliance
        float compliance = calculateRegisterCompliance(request.getCandidateTranscript(), request.getSpeechWpm());

        // Dynamic phase advancement
        boolean concluded = false;
        int phaseCode = 1;
        if (session.currentTurn >= 6) {
            session.currentPhase = "Concluded";
            concluded = true;
            phaseCode = 6;
        } else if (session.currentTurn >= 5) {
            session.currentPhase = "SynthesisDebrief";
            phaseCode = 5;
        } else if (session.currentTurn >= 3) {
            session.currentPhase = "StressChallenge";
            session.stressMultiplier = Math.min(2.0f, session.stressMultiplier * 1.15f);
            phaseCode = 4;
        } else if (session.currentTurn >= 2) {
            session.currentPhase = "DepthProbing";
            phaseCode = 3;
        } else {
            session.currentPhase = "CoreExploration";
            phaseCode = 2;
        }

        String nextProbe = generateNextProbe(session.currentPhase, session.formatCode);

        // Sync to AMSV state vector at offset 0x20
        syncToAmsv(session.scenarioId, session.currentTurn, compliance, phaseCode);

        return new ScenarioTurnResponse(
            session.sessionId,
            session.currentTurn,
            session.currentPhase,
            compliance,
            session.stressMultiplier,
            nextProbe,
            concluded
        );
    }

    private float calculateRegisterCompliance(String transcript, float wpm) {
        if (transcript == null || transcript.trim().isEmpty()) {
            return 0.0f;
        }
        float wpmTarget = 135.0f;
        float wpmError = Math.abs(wpm - wpmTarget) / wpmTarget;
        float wpmScore = Math.max(0.0f, 1.0f - wpmError);

        float lengthScore = Math.min(1.0f, (float) transcript.length() / 100.0f);
        return (wpmScore * 0.4f) + (lengthScore * 0.6f);
    }

    private String getOpeningPromptForFormat(int formatCode) {
        switch (formatCode) {
            case 1: return "Technical Architecture: Design an ultra-low-latency distributed consensus cluster handling 10M tx/sec with sub-50us p99 latency.";
            case 2: return "Behavioral Incident: Walk me through a catastrophic production outage where key leaders were unavailable using STAR.";
            case 3: return "Competency Alignment: How do you reconcile a sales demand for immediate feature delivery against critical tech debt refactoring?";
            case 4: return "Case Study: Evaluate the market entry of 5,000 autonomous delivery vehicles into Germany, detailing unit economics.";
            case 5: return "Group Consensus: Synthesize agreement across clinicians and vendor-backed executives on a 42-hospital health record system.";
            case 6: return "HR Screening: Why our firm, why this practice, and what ethical philosophy guides you through intense ambiguity?";
            case 7: return "Executive Leadership: Present your 5-year capital allocation and sovereign defense AI roadmap for our $250M fund.";
            case 8:
            default: return "Panel Defense: Address conflicting mandates from the CFO, CSO, and COO regarding your $1.2B network modernization.";
        }
    }

    private String generateNextProbe(String phase, int formatCode) {
        switch (phase) {
            case "DepthProbing":
                return "Explain the exact data structures and algorithmic complexity of your critical path.";
            case "StressChallenge":
                return "Your primary dependency just encountered an unrecoverable failure under peak load. How do you respond?";
            case "SynthesisDebrief":
                return "Provide your final 60-second summary highlighting value, risk mitigation, and next steps.";
            case "Concluded":
                return "Simulation complete. Results logged to central telemetry.";
            default:
                return "Elaborate further on the implementation details.";
        }
    }

    private void syncToAmsv(int scenarioId, int turn, float compliance, int phase) {
        if (amsvDirectBuffer == null || amsvDirectBuffer.capacity() < 64) {
            return;
        }
        // Offset 0x20 is byte offset 32 in AMSV state vector
        // [Bits 0-15: scenario_id | Bits 16-31: turn | Bits 32-47: comp Q16 | Bits 48-63: phase]
        int compQ16 = (int) (Math.max(0.0f, Math.min(1.0f, compliance)) * 65535.0f);
        long packedU64 = ((long) (scenarioId & 0xFFFF))
                       | (((long) (turn & 0xFFFF)) << 16)
                       | (((long) (compQ16 & 0xFFFF)) << 32)
                       | (((long) (phase & 0xFFFF)) << 48);

        amsvDirectBuffer.putLong(32, packedU64);
    }
}
