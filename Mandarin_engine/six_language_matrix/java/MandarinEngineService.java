package mandarin_engine;

import java.util.concurrent.*;
import java.util.List;
import java.util.ArrayList;

/**
 * Java 21 Distributed Execution Service for Mandarin Engine.
 * Uses Project Loom Virtual Threads for ultra-high concurrency request routing.
 */
public class MandarinEngineService {

    private final ExecutorService virtualThreadExecutor;

    public MandarinEngineService() {
        this.virtualThreadExecutor = Executors.newVirtualThreadPerTaskExecutor();
    }

    public record MandarinProcessingResult(
        String requestId,
        String originalText,
        int tokenCount,
        boolean success,
        long executionTimeMs
    ) {}

    public CompletableFuture<MandarinProcessingResult> processMandarinRequestAsync(String requestId, String text) {
        return CompletableFuture.supplyAsync(() -> {
            long start = System.currentTimeMillis();
            // Maximum matching & segmentation token estimation
            int tokens = text != null ? (int) Math.ceil(text.length() * 0.65) : 0;
            long elapsed = System.currentTimeMillis() - start;
            return new MandarinProcessingResult(requestId, text, tokens, true, elapsed);
        }, virtualThreadExecutor);
    }

    public List<MandarinProcessingResult> processBatch(List<String> texts) throws InterruptedException, ExecutionException {
        List<CompletableFuture<MandarinProcessingResult>> futures = new ArrayList<>();
        int id = 0;
        for (String t : texts) {
            futures.add(processMandarinRequestAsync("req-zh-" + (++id), t));
        }
        CompletableFuture.allOf(futures.toArray(new CompletableFuture[0])).join();
        List<MandarinProcessingResult> results = new ArrayList<>();
        for (var f : futures) {
            results.add(f.get());
        }
        return results;
    }

    public void shutdown() {
        virtualThreadExecutor.shutdown();
    }
}
