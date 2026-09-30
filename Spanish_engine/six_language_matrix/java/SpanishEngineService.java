package spanish_engine;

import java.util.concurrent.*;
import java.util.List;
import java.util.ArrayList;

/**
 * Java 21 Distributed Execution Service for Spanish Engine.
 * Uses Project Loom Virtual Threads for ultra-high concurrency request routing.
 */
public class SpanishEngineService {

    private final ExecutorService virtualThreadExecutor;

    public SpanishEngineService() {
        this.virtualThreadExecutor = Executors.newVirtualThreadPerTaskExecutor();
    }

    public record SpanishProcessingResult(
        String requestId,
        String originalText,
        int tokenCount,
        boolean success,
        long executionTimeMs
    ) {}

    public CompletableFuture<SpanishProcessingResult> processSpanishRequestAsync(String requestId, String text) {
        return CompletableFuture.supplyAsync(() -> {
            long start = System.currentTimeMillis();
            int tokens = text != null ? text.split("\\s+").length : 0;
            long elapsed = System.currentTimeMillis() - start;
            return new SpanishProcessingResult(requestId, text, tokens, true, elapsed);
        }, virtualThreadExecutor);
    }

    public List<SpanishProcessingResult> processBatch(List<String> texts) throws InterruptedException, ExecutionException {
        List<CompletableFuture<SpanishProcessingResult>> futures = new ArrayList<>();
        int id = 0;
        for (String t : texts) {
            futures.add(processSpanishRequestAsync("req-es-" + (++id), t));
        }
        CompletableFuture.allOf(futures.toArray(new CompletableFuture[0])).join();
        List<SpanishProcessingResult> results = new ArrayList<>();
        for (var f : futures) {
            results.add(f.get());
        }
        return results;
    }

    public void shutdown() {
        virtualThreadExecutor.shutdown();
    }
}
