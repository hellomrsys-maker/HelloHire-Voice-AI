// =============================================================================
// engine/java/src/main/java/ai/engine/service/EngineService.java
// Java service layer for the Verbal Communication Engine.
// Provides gRPC and REST service facades over the C++ engine core.
// =============================================================================

package ai.engine.service;

import ai.engine.infra.EngineLibraryBridge;
import ai.engine.infra.EngineConfig;
import ai.engine.scheduler.TaskScheduler;
import ai.engine.ipc.IPCChannel;

import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicLong;
import java.util.logging.Logger;
import java.util.logging.Level;
import java.util.*;

/**
 * EngineService — Java service facade for the Verbal Communication Engine.
 *
 * <p>Provides:
 * <ul>
 *   <li>Thread-safe text processing via a bounded ExecutorService</li>
 *   <li>Health check and status monitoring</li>
 *   <li>Request scheduling with priority queues</li>
 *   <li>IPC channel management for multi-process coordination</li>
 * </ul>
 *
 * <p>Thread safety: All public methods are thread-safe.
 * The underlying C++ engine is called via JNI through {@link EngineLibraryBridge}.
 */
public class EngineService implements AutoCloseable {

    private static final Logger LOG = Logger.getLogger(EngineService.class.getName());

    private final EngineConfig           config;
    private final EngineLibraryBridge    bridge;
    private final ExecutorService        executor;
    private final TaskScheduler          scheduler;
    private final AtomicBoolean          operational;
    private final AtomicLong             requestCount;
    private final AtomicLong             successCount;
    private final AtomicLong             failureCount;
    private final AtomicLong             totalLatencyNs;

    // ==========================================================================
    // Construction
    // ==========================================================================

    /**
     * Creates an EngineService with the given configuration.
     * Does NOT start the engine — call {@link #start()} explicitly.
     *
     * @param config Engine configuration
     */
    public EngineService(EngineConfig config) {
        this.config         = Objects.requireNonNull(config, "config must not be null");
        this.bridge         = new EngineLibraryBridge(config);
        this.executor       = createExecutor(config.getThreadPoolSize());
        this.scheduler      = new TaskScheduler(config.getMaxQueueDepth());
        this.operational    = new AtomicBoolean(false);
        this.requestCount   = new AtomicLong(0);
        this.successCount   = new AtomicLong(0);
        this.failureCount   = new AtomicLong(0);
        this.totalLatencyNs = new AtomicLong(0);
    }

    private static ExecutorService createExecutor(int poolSize) {
        return new ThreadPoolExecutor(
            poolSize,
            poolSize,
            60L,
            TimeUnit.SECONDS,
            new LinkedBlockingQueue<>(10_000),
            r -> {
                Thread t = new Thread(r, "engine-worker-" + System.nanoTime());
                t.setDaemon(true);
                return t;
            },
            new ThreadPoolExecutor.CallerRunsPolicy()
        );
    }

    // ==========================================================================
    // Lifecycle
    // ==========================================================================

    /**
     * Starts the engine service: loads the C++ library, recruits subsystems,
     * and marks the service as operational.
     *
     * @throws EngineServiceException if startup fails
     */
    public synchronized void start() {
        LOG.info("Starting EngineService: " + config.getEngineId());
        try {
            bridge.loadLibrary();
            bridge.createEngine();
            bridge.recruitSubsystems();

            if (!bridge.isOperational()) {
                throw new EngineServiceException(
                    "Engine reported non-operational status after recruitment");
            }

            operational.set(true);
            LOG.info("EngineService started and operational");
        } catch (Exception e) {
            LOG.log(Level.SEVERE, "EngineService startup failed", e);
            throw new EngineServiceException("Engine startup failed: " + e.getMessage(), e);
        }
    }

    /**
     * Returns true if the engine service is operational.
     */
    public boolean isOperational() {
        return operational.get() && bridge.isOperational();
    }

    // ==========================================================================
    // Core processing
    // ==========================================================================

    /**
     * Processes a text request asynchronously.
     *
     * @param request The text request to process
     * @return CompletableFuture resolving to the engine response
     */
    public CompletableFuture<EngineResponse> processAsync(EngineRequest request) {
        Objects.requireNonNull(request, "request must not be null");

        if (!operational.get()) {
            return CompletableFuture.failedFuture(
                new EngineServiceException("Engine is not operational"));
        }

        return CompletableFuture.supplyAsync(() -> processSync(request), executor);
    }

    /**
     * Processes a text request synchronously.
     *
     * @param request The text request to process
     * @return EngineResponse with the result
     * @throws EngineServiceException if processing fails
     */
    public EngineResponse processSync(EngineRequest request) {
        Objects.requireNonNull(request, "request must not be null");

        if (!operational.get()) {
            throw new EngineServiceException("Engine is not operational");
        }

        requestCount.incrementAndGet();
        final long startNs = System.nanoTime();

        try {
            final String responseText = bridge.processText(
                request.getInputText(),
                request.getOutputModality(),
                request.getReasoningDepth()
            );

            final long latencyNs = System.nanoTime() - startNs;
            successCount.incrementAndGet();
            totalLatencyNs.addAndGet(latencyNs);

            return EngineResponse.builder()
                .requestId(request.getRequestId())
                .text(responseText)
                .latencyMs(latencyNs / 1_000_000L)
                .success(true)
                .build();

        } catch (Exception e) {
            failureCount.incrementAndGet();
            LOG.log(Level.WARNING, "processSync failed for request: " + request.getRequestId(), e);
            throw new EngineServiceException("Text processing failed: " + e.getMessage(), e);
        }
    }

    /**
     * Processes a batch of requests concurrently.
     *
     * @param requests List of requests to process
     * @return List of responses in the same order as the input
     */
    public List<EngineResponse> processBatch(List<EngineRequest> requests) {
        Objects.requireNonNull(requests, "requests must not be null");
        if (requests.isEmpty()) return Collections.emptyList();

        List<CompletableFuture<EngineResponse>> futures = new ArrayList<>(requests.size());
        for (EngineRequest req : requests) {
            futures.add(processAsync(req));
        }

        CompletableFuture<Void> allDone = CompletableFuture.allOf(
            futures.toArray(new CompletableFuture[0])
        );

        try {
            allDone.get(config.getBatchTimeoutSeconds(), TimeUnit.SECONDS);
        } catch (TimeoutException e) {
            LOG.warning("Batch processing timed out after "
                        + config.getBatchTimeoutSeconds() + "s");
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        } catch (ExecutionException e) {
            LOG.log(Level.WARNING, "Batch processing had failures", e.getCause());
        }

        List<EngineResponse> results = new ArrayList<>(requests.size());
        for (int i = 0; i < requests.size(); i++) {
            try {
                results.add(futures.get(i).getNow(
                    EngineResponse.errorResponse(requests.get(i).getRequestId(),
                                                 "Batch processing failed or timed out")
                ));
            } catch (Exception e) {
                results.add(EngineResponse.errorResponse(
                    requests.get(i).getRequestId(), e.getMessage()));
            }
        }
        return results;
    }

    // ==========================================================================
    // Health and metrics
    // ==========================================================================

    /**
     * Returns the current service health status.
     */
    public ServiceHealth getHealth() {
        long total = requestCount.get();
        long succ  = successCount.get();
        double avgLatencyMs = (total > 0)
            ? (totalLatencyNs.get() / 1_000_000.0) / total
            : 0.0;

        return ServiceHealth.builder()
            .engineId(config.getEngineId())
            .operational(isOperational())
            .totalRequests(total)
            .successfulRequests(succ)
            .failedRequests(failureCount.get())
            .successRate(total > 0 ? (double) succ / total : 1.0)
            .averageLatencyMs(avgLatencyMs)
            .activeWorkers(((ThreadPoolExecutor) executor).getActiveCount())
            .queueDepth(((ThreadPoolExecutor) executor).getQueue().size())
            .engineHealthDump(bridge.isOperational() ? bridge.getHealthDump() : "{}")
            .build();
    }

    // ==========================================================================
    // Lifecycle close
    // ==========================================================================

    @Override
    public synchronized void close() {
        LOG.info("Shutting down EngineService: " + config.getEngineId());
        operational.set(false);

        executor.shutdown();
        try {
            if (!executor.awaitTermination(30, TimeUnit.SECONDS)) {
                executor.shutdownNow();
            }
        } catch (InterruptedException e) {
            executor.shutdownNow();
            Thread.currentThread().interrupt();
        }

        bridge.destroyEngine();
        scheduler.shutdown();
        LOG.info("EngineService shut down cleanly");
    }
}
