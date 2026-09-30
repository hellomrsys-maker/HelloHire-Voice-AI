package ai.training.infra;

import ai.training.service.EvaluationResult;
import ai.training.service.TrainingStepResult;

import java.util.*;
import java.util.logging.Logger;

/**
 * JNI bridge to the native C++ training library (libpolyglot_training.so).
 * Provides Java wrappers for all C++ TrainingCore functions:
 * training steps, checkpoint save/load, evaluation, and parameter access.
 */
public class TrainingLibraryBridge {

    private static final Logger LOG = Logger.getLogger(TrainingLibraryBridge.class.getName());

    private final TrainingConfig config;
    private volatile boolean initialized = false;
    private long nativeHandle = 0L;  // opaque pointer to C++ TrainingCore

    static {
        // Attempt to load native library at class load time
        try {
            System.loadLibrary("polyglot_training_jni");
            LOG.info("Loaded native library: polyglot_training_jni");
        } catch (UnsatisfiedLinkError e) {
            LOG.warning("Could not load polyglot_training_jni: " + e.getMessage() +
                        " — JNI calls will be stubbed.");
        }
    }

    public TrainingLibraryBridge(TrainingConfig config) {
        this.config = Objects.requireNonNull(config);
    }

    // ── Lifecycle ────────────────────────────────────────────────────────────

    /**
     * Initialize the C++ training core and allocate native resources.
     *
     * @throws TrainingInitException if native initialization fails
     */
    public synchronized void initialize() throws TrainingInitException {
        if (initialized) return;
        LOG.info("Initializing TrainingLibraryBridge (native TrainingCore)...");
        try {
            nativeHandle = nativeInit(
                config.getDataPath(),
                config.getVocabPath(),
                config.getBatchSize(),
                config.getLearningRate(),
                config.getWeightDecay(),
                config.getGradClipNorm(),
                config.getWarmupSteps(),
                config.isUseCuda() ? 1 : 0,
                config.isVerbose() ? 1 : 0
            );
            if (nativeHandle == 0L) {
                throw new TrainingInitException("nativeInit returned null handle");
            }
            initialized = true;
            LOG.info("TrainingLibraryBridge initialized. nativeHandle=" + nativeHandle);
        } catch (TrainingInitException e) {
            throw e;
        } catch (Exception e) {
            throw new TrainingInitException("TrainingLibraryBridge init failed", e);
        }
    }

    /** Release native resources. */
    public synchronized void shutdown() {
        if (!initialized) return;
        try {
            nativeShutdown(nativeHandle);
        } catch (Exception e) {
            LOG.warning("Error during native shutdown: " + e.getMessage());
        } finally {
            nativeHandle = 0L;
            initialized = false;
        }
    }

    // ── Training operations ──────────────────────────────────────────────────

    /**
     * Execute one training step for a given batch.
     *
     * @param epoch       current epoch (0-based)
     * @param batchIdx    batch index within the epoch
     * @param tokenIds    flat array of token IDs [record_count × max_seq_len]
     * @param seqLengths  per-sequence lengths [record_count]
     * @param maxSeqLen   maximum sequence length in this batch
     * @param lr          effective learning rate for this step
     * @param wd          weight decay
     * @return TrainingStepResult with loss and per-faculty losses
     */
    public TrainingStepResult trainingStep(
        int epoch,
        int batchIdx,
        int[] tokenIds,
        int[] seqLengths,
        int maxSeqLen,
        float lr,
        float wd
    ) {
        if (!initialized) {
            return TrainingStepResult.failure("Not initialized");
        }
        try {
            float[] result = nativeTrainingStep(
                nativeHandle, epoch, batchIdx, tokenIds, seqLengths, maxSeqLen, lr, wd
            );
            // result[0] = total loss, result[1..] = per-faculty losses (8 faculties)
            float loss = result.length > 0 ? result[0] : Float.NaN;
            Map<String, Float> facultyLosses = parseFacultyLosses(result);
            return TrainingStepResult.success(batchIdx, loss, facultyLosses);
        } catch (Exception e) {
            LOG.warning("Training step error: " + e.getMessage());
            return TrainingStepResult.failure(e.getMessage());
        }
    }

    /**
     * Run evaluation on the current model state.
     * @return EvaluationResult with overall score and per-faculty scores
     */
    public EvaluationResult runEvaluation() {
        if (!initialized) return new EvaluationResult(0.0f, Collections.emptyMap());
        try {
            float[] scores = nativeEvaluate(nativeHandle);
            // scores[0] = overall, scores[1..8] = per-faculty
            float overall = scores.length > 0 ? scores[0] : 0.0f;
            Map<String, Float> facultyScores = parseFacultyScores(scores);
            return new EvaluationResult(overall, facultyScores);
        } catch (Exception e) {
            LOG.warning("Evaluation error: " + e.getMessage());
            return new EvaluationResult(0.0f, Collections.emptyMap());
        }
    }

    /**
     * Save current model checkpoint to the specified path.
     * @return true if saved successfully
     */
    public boolean saveCheckpoint(String path) {
        if (!initialized) return false;
        try {
            return nativeSaveCheckpoint(nativeHandle, path) == 1;
        } catch (Exception e) {
            LOG.warning("Checkpoint save error: " + e.getMessage());
            return false;
        }
    }

    /**
     * Load a model checkpoint from the specified path.
     * @return true if loaded successfully
     */
    public boolean loadCheckpoint(String path) {
        if (!initialized) return false;
        try {
            return nativeLoadCheckpoint(nativeHandle, path) == 1;
        } catch (Exception e) {
            LOG.warning("Checkpoint load error: " + e.getMessage());
            return false;
        }
    }

    // ── Private helpers ──────────────────────────────────────────────────────

    private static final String[] FACULTY_NAMES = {
        "thinking", "attention", "memory", "creativity",
        "imagination", "metacognition", "associative", "curiosity"
    };

    private Map<String, Float> parseFacultyLosses(float[] result) {
        Map<String, Float> map = new LinkedHashMap<>();
        for (int i = 0; i < FACULTY_NAMES.length && (i + 1) < result.length; i++) {
            map.put(FACULTY_NAMES[i], result[i + 1]);
        }
        return map;
    }

    private Map<String, Float> parseFacultyScores(float[] scores) {
        Map<String, Float> map = new LinkedHashMap<>();
        for (int i = 0; i < FACULTY_NAMES.length && (i + 1) < scores.length; i++) {
            map.put(FACULTY_NAMES[i], scores[i + 1]);
        }
        return map;
    }

    // ── JNI declarations ─────────────────────────────────────────────────────

    private native long nativeInit(
        String dataPath, String vocabPath,
        int batchSize, float lr, float wd, float gradClip,
        int warmupSteps, int useCuda, int verbose
    );

    private native void nativeShutdown(long handle);

    private native float[] nativeTrainingStep(
        long handle, int epoch, int batchIdx,
        int[] tokenIds, int[] seqLengths, int maxSeqLen,
        float lr, float wd
    );

    private native float[] nativeEvaluate(long handle);

    private native int nativeSaveCheckpoint(long handle, String path);

    private native int nativeLoadCheckpoint(long handle, String path);
}
