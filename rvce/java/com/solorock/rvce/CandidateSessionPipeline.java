package com.solorock.rvce;

import com.solorock.rvce.dto.CandidateVerbalCognitiveReport;

import java.nio.ByteBuffer;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * Enterprise multi-threaded pipeline for processing batched candidate verbal turns.
 */
public class CandidateSessionPipeline {

    private final ExecutorService executor;
    private final RecruitmentVerbalCognitiveController controller;
    private final ConcurrentHashMap<String, AtomicInteger> candidateTurnTracker;

    public CandidateSessionPipeline(int threadPoolSize, ByteBuffer amsvBuffer) {
        this.executor = Executors.newFixedThreadPool(threadPoolSize);
        this.controller = new RecruitmentVerbalCognitiveController(amsvBuffer);
        this.candidateTurnTracker = new ConcurrentHashMap<>();
    }

    public CompletableFuture<CandidateVerbalCognitiveReport> submitCandidateTurn(
        String candidateId,
        String transcript,
        float measuredWpm,
        float elapsedMinutes
    ) {
        return CompletableFuture.supplyAsync(() -> {
            int turn = candidateTurnTracker.computeIfAbsent(candidateId, k -> new AtomicInteger(0)).incrementAndGet();
            return controller.evaluateTurn(candidateId, transcript, turn, measuredWpm, elapsedMinutes);
        }, executor);
    }

    public void shutdown() {
        executor.shutdown();
    }
}
