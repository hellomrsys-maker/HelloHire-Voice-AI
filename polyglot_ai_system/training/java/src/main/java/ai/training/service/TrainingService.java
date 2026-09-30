package ai.training.service;

import ai.training.infra.TrainingConfig;
import ai.training.infra.TrainingLibraryBridge;
import ai.training.scheduler.TrainingTaskScheduler;
import ai.training.ipc.TrainingIPCChannel;

import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;
import java.util.logging.Level;
import java.util.logging.Logger;
import java.util.*;

/**
 * TrainingService — orchestrates the full AI training lifecycle.
 *
 * <p>Responsibilities:
 * <ul>
 *   <li>Submit and track training jobs across all 6 language components</li>
 *   <li>Bridge to the C++ TrainingCore via JNI</li>
 *   <li>Coordinate with the Rust data pipeline via IPC</li>
 *   <li>Report metrics to experiment tracking (Python orchestrator)</li>
 *   <li>Handle fault tolerance: retry on transient failures, abort on fatal errors</li>
 * </ul>
 */
public class TrainingService {

    private static final Logger LOG = Logger.getLogger(TrainingService.class.getName());

    private final TrainingConfig config;
    private final TrainingLibraryBridge bridge;
    private final TrainingTaskScheduler scheduler;
    private final TrainingIPCChannel ipcChannel;
    private final ExecutorService executor;

    private final AtomicBoolean running       = new AtomicBoolean(false);
    private final AtomicInteger epochCounter  = new AtomicInteger(0);
    private final AtomicLong    totalSteps    = new AtomicLong(0);
    private final AtomicLong    totalLoss     = new AtomicLong(0);  // stored as Float.floatToIntBits

    // Training job state
    private volatile TrainingJobState jobState = TrainingJobState.IDLE;
    private final List<TrainingJobListener> listeners = Collections.synchronizedList(new ArrayList<>());

    public TrainingService(TrainingConfig config) {
        this.config     = Objects.requireNonNull(config, "config must not be null");
        this.bridge     = new TrainingLibraryBridge(config);
        this.scheduler  = new TrainingTaskScheduler(config.getNumWorkers());
        this.ipcChannel = new TrainingIPCChannel(config.getIpcSocketPath());
        this.executor   = Executors.newFixedThreadPool(
            Math.max(2, config.getNumWorkers()),
            r -> {
                Thread t = new Thread(r, "training-service-worker");
                t.setDaemon(true);
                return t;
            }
        );
    }

    // ── Lifecycle ────────────────────────────────────────────────────────────

    /**
     * Initialize the training service and all its subsystems.
     * Must be called before {@link #submitTrainingJob}.
     *
     * @throws TrainingServiceException if any subsystem fails to initialize
     */
    public synchronized void initialize() throws TrainingServiceException {
        LOG.info("Initializing TrainingService...");
        try {
            bridge.initialize();
            ipcChannel.connect();
            LOG.info("TrainingService initialized successfully.");
            jobState = TrainingJobState.READY;
        } catch (Exception e) {
            throw new TrainingServiceException("TrainingService initialization failed", e);
        }
    }

    /**
     * Gracefully shut down the training service.
     * Waits for any running training job to complete or timeout.
     */
    public synchronized void shutdown() {
        if (!running.get()) {
            return;
        }
        LOG.info("Shutting down TrainingService...");
        running.set(false);

        scheduler.shutdown();
        try {
            executor.shutdown();
            if (!executor.awaitTermination(30, TimeUnit.SECONDS)) {
                executor.shutdownNow();
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            executor.shutdownNow();
        }

        ipcChannel.close();
        bridge.shutdown();
        jobState = TrainingJobState.IDLE;
        LOG.info("TrainingService shutdown complete.");
    }

    // ── Job submission ───────────────────────────────────────────────────────

    /**
     * Submit a training job and return a CompletableFuture for its result.
     * The job runs all training epochs on all cognitive faculties.
     *
     * @param jobConfig configuration for this specific job
     * @return future resolving to the final TrainingJobResult
     */
    public CompletableFuture<TrainingJobResult> submitTrainingJob(TrainingJobConfig jobConfig) {
        if (jobState != TrainingJobState.READY) {
            return CompletableFuture.failedFuture(
                new TrainingServiceException("Service not in READY state: " + jobState)
            );
        }

        jobState = TrainingJobState.RUNNING;
        running.set(true);

        LOG.info(String.format("Submitting training job: epochs=%d, batch_size=%d",
            jobConfig.getEpochs(), jobConfig.getBatchSize()));

        return CompletableFuture.supplyAsync(() -> {
            try {
                return runTrainingJob(jobConfig);
            } catch (Exception e) {
                jobState = TrainingJobState.FAILED;
                throw new RuntimeException("Training job failed", e);
            } finally {
                if (jobState == TrainingJobState.RUNNING) {
                    jobState = TrainingJobState.COMPLETE;
                }
            }
        }, executor);
    }

    // ── Core training loop ───────────────────────────────────────────────────

    private TrainingJobResult runTrainingJob(TrainingJobConfig jobConfig) throws Exception {
        long jobStart = System.currentTimeMillis();
        float finalLoss = Float.MAX_VALUE;
        Map<String, Float> finalFacultyLosses = new HashMap<>();

        for (int epoch = 0; epoch < jobConfig.getEpochs() && running.get(); epoch++) {
            long epochStart = System.currentTimeMillis();
            epochCounter.set(epoch);

            LOG.fine("Starting epoch " + (epoch + 1) + "/" + jobConfig.getEpochs());

            // 1. Request next batch set from Rust data pipeline via IPC
            List<TrainingBatch> batches = requestBatchesFromRust(epoch, jobConfig);

            // 2. Submit batches to C++ TrainingCore via JNI
            EpochResult epochResult = runEpochBatches(epoch, batches, jobConfig);

            // 3. Update metrics
            totalSteps.addAndGet(epochResult.steps);
            totalLoss.set(Float.floatToRawIntBits(epochResult.totalLoss));
            finalLoss = epochResult.totalLoss;
            finalFacultyLosses = epochResult.facultyLosses;

            long epochMs = System.currentTimeMillis() - epochStart;
            LOG.info(String.format("Epoch %d/%d: loss=%.4f, steps=%d, time=%dms",
                epoch + 1, jobConfig.getEpochs(), epochResult.totalLoss, epochResult.steps, epochMs));

            // 4. Notify listeners
            notifyEpochComplete(epoch, epochResult);

            // 5. Periodic evaluation
            if ((epoch + 1) % jobConfig.getEvalEveryEpochs() == 0) {
                EvaluationResult evalResult = runEvaluation();
                LOG.info("Eval score: " + evalResult.overallScore);
                notifyEvalComplete(epoch, evalResult);
            }

            // 6. Save checkpoint
            if (!jobConfig.getOutputDir().isEmpty() &&
                (epoch + 1) % jobConfig.getSaveEveryEpochs() == 0) {
                String ckptPath = jobConfig.getOutputDir() + "/checkpoint_epoch" + (epoch + 1) + ".bin";
                boolean saved = bridge.saveCheckpoint(ckptPath);
                LOG.info("Checkpoint " + (saved ? "saved: " : "FAILED: ") + ckptPath);
            }
        }

        long totalMs = System.currentTimeMillis() - jobStart;
        return new TrainingJobResult(
            finalLoss,
            finalFacultyLosses,
            totalSteps.get(),
            epochCounter.get() + 1,
            totalMs
        );
    }

    // ── Internal helpers ─────────────────────────────────────────────────────

    private List<TrainingBatch> requestBatchesFromRust(int epoch, TrainingJobConfig cfg) {
        try {
            // Send epoch request to Rust pipeline via IPC socket
            Map<String, Object> req = new HashMap<>();
            req.put("action", "get_batches");
            req.put("epoch", epoch);
            req.put("batch_size", cfg.getBatchSize());
            req.put("data_path", cfg.getDataPath());

            @SuppressWarnings("unchecked")
            List<Map<String, Object>> rawBatches =
                (List<Map<String, Object>>) ipcChannel.sendReceive(req);

            List<TrainingBatch> batches = new ArrayList<>();
            for (Map<String, Object> raw : rawBatches) {
                batches.add(TrainingBatch.fromMap(raw));
            }
            LOG.fine("Received " + batches.size() + " batches from Rust pipeline");
            return batches;
        } catch (Exception e) {
            LOG.log(Level.WARNING, "IPC batch request failed, using empty epoch", e);
            return Collections.emptyList();
        }
    }

    private EpochResult runEpochBatches(
        int epoch,
        List<TrainingBatch> batches,
        TrainingJobConfig cfg
    ) {
        float totalLoss = 0.0f;
        int steps = 0;
        Map<String, Float> facultyLossAccum = new HashMap<>();

        for (TrainingBatch batch : batches) {
            if (!running.get()) break;

            // Submit batch to C++ core via JNI bridge
            TrainingStepResult stepResult = bridge.trainingStep(
                epoch,
                batch.getBatchIndex(),
                batch.getTokenIds(),
                batch.getSeqLengths(),
                batch.getMaxSeqLen(),
                cfg.getLearningRate(),
                cfg.getWeightDecay()
            );

            if (stepResult.isSuccess()) {
                totalLoss += stepResult.getLoss();
                steps++;
                for (Map.Entry<String, Float> e : stepResult.getFacultyLosses().entrySet()) {
                    facultyLossAccum.merge(e.getKey(), e.getValue(), Float::sum);
                }
            } else {
                LOG.warning("Training step failed: " + stepResult.getErrorMsg());
            }
        }

        // Average faculty losses
        final int finalSteps = steps;
        Map<String, Float> avgFacultyLosses = new HashMap<>();
        facultyLossAccum.forEach((k, v) ->
            avgFacultyLosses.put(k, finalSteps > 0 ? v / finalSteps : 0.0f)
        );

        return new EpochResult(
            steps > 0 ? totalLoss / steps : Float.NaN,
            avgFacultyLosses,
            steps
        );
    }

    private EvaluationResult runEvaluation() {
        try {
            return bridge.runEvaluation();
        } catch (Exception e) {
            LOG.log(Level.WARNING, "Evaluation failed", e);
            return new EvaluationResult(0.0f, Collections.emptyMap());
        }
    }

    // ── Listener management ──────────────────────────────────────────────────

    public void addListener(TrainingJobListener listener) {
        listeners.add(listener);
    }

    public void removeListener(TrainingJobListener listener) {
        listeners.remove(listener);
    }

    private void notifyEpochComplete(int epoch, EpochResult result) {
        for (TrainingJobListener l : listeners) {
            try {
                l.onEpochComplete(epoch, result.totalLoss);
            } catch (Exception e) {
                LOG.log(Level.FINE, "Listener error", e);
            }
        }
    }

    private void notifyEvalComplete(int epoch, EvaluationResult result) {
        for (TrainingJobListener l : listeners) {
            try {
                l.onEvaluationComplete(epoch, result.overallScore);
            } catch (Exception e) {
                LOG.log(Level.FINE, "Listener error", e);
            }
        }
    }

    // ── Status accessors ─────────────────────────────────────────────────────

    public TrainingJobState getJobState()   { return jobState; }
    public long getTotalSteps()             { return totalSteps.get(); }
    public int  getCurrentEpoch()           { return epochCounter.get(); }
    public float getLastLoss() {
        return Float.intBitsToFloat((int) totalLoss.get());
    }

    // ─────────────────────────────────────────────────────────────────────────
    // Inner record types
    // ─────────────────────────────────────────────────────────────────────────

    /** Aggregated result of one epoch. */
    record EpochResult(float totalLoss, Map<String, Float> facultyLosses, int steps) {}

    /** Result of a model evaluation pass. */
    record EvaluationResult(float overallScore, Map<String, Float> facultyScores) {}
}
