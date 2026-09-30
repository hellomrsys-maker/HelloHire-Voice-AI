package ai.training.infra;

import java.util.Objects;

/**
 * Configuration for the AI training system.
 * Loaded from YAML/environment at startup.
 */
public class TrainingConfig {

    // ── Data ────────────────────────────────────────────────────────────────
    private String dataPath          = "";
    private String vocabPath         = "";
    private String outputDir         = "output/training";

    // ── Model ────────────────────────────────────────────────────────────────
    private int    vocabSize         = 32_000;
    private int    hiddenDim         = 1024;
    private int    numHeads          = 16;
    private int    numLayers         = 24;
    private int    maxSeqLen         = 2048;

    // ── Training ─────────────────────────────────────────────────────────────
    private int    numEpochs         = 10;
    private int    batchSize         = 32;
    private float  learningRate      = 1e-4f;
    private float  weightDecay       = 0.01f;
    private float  gradClipNorm      = 1.0f;
    private int    warmupSteps       = 1_000;
    private int    evalEveryEpochs   = 1;
    private int    saveEveryEpochs   = 2;

    // ── Infrastructure ───────────────────────────────────────────────────────
    private int    numWorkers        = 4;
    private String ipcSocketPath     = "/tmp/polyglot_training.sock";
    private String cppLibPath        = "";
    private boolean useCuda          = true;
    private boolean verbose          = false;

    // ── Native library ───────────────────────────────────────────────────────
    private String nativeLibPath     = "";

    public TrainingConfig() {}

    // ── Fluent builder methods ───────────────────────────────────────────────

    public TrainingConfig dataPath(String v)       { this.dataPath = v;        return this; }
    public TrainingConfig vocabPath(String v)      { this.vocabPath = v;       return this; }
    public TrainingConfig outputDir(String v)      { this.outputDir = v;       return this; }
    public TrainingConfig numEpochs(int v)         { this.numEpochs = v;       return this; }
    public TrainingConfig batchSize(int v)         { this.batchSize = v;       return this; }
    public TrainingConfig learningRate(float v)    { this.learningRate = v;    return this; }
    public TrainingConfig weightDecay(float v)     { this.weightDecay = v;     return this; }
    public TrainingConfig gradClipNorm(float v)    { this.gradClipNorm = v;    return this; }
    public TrainingConfig warmupSteps(int v)       { this.warmupSteps = v;     return this; }
    public TrainingConfig numWorkers(int v)        { this.numWorkers = v;      return this; }
    public TrainingConfig ipcSocketPath(String v)  { this.ipcSocketPath = v;   return this; }
    public TrainingConfig cppLibPath(String v)     { this.cppLibPath = v;      return this; }
    public TrainingConfig nativeLibPath(String v)  { this.nativeLibPath = v;   return this; }
    public TrainingConfig useCuda(boolean v)       { this.useCuda = v;         return this; }
    public TrainingConfig verbose(boolean v)       { this.verbose = v;         return this; }
    public TrainingConfig evalEveryEpochs(int v)   { this.evalEveryEpochs = v; return this; }
    public TrainingConfig saveEveryEpochs(int v)   { this.saveEveryEpochs = v; return this; }

    // ── Getters ─────────────────────────────────────────────────────────────

    public String  getDataPath()         { return dataPath; }
    public String  getVocabPath()        { return vocabPath; }
    public String  getOutputDir()        { return outputDir; }
    public int     getVocabSize()        { return vocabSize; }
    public int     getHiddenDim()        { return hiddenDim; }
    public int     getNumHeads()         { return numHeads; }
    public int     getNumLayers()        { return numLayers; }
    public int     getMaxSeqLen()        { return maxSeqLen; }
    public int     getNumEpochs()        { return numEpochs; }
    public int     getBatchSize()        { return batchSize; }
    public float   getLearningRate()     { return learningRate; }
    public float   getWeightDecay()      { return weightDecay; }
    public float   getGradClipNorm()     { return gradClipNorm; }
    public int     getWarmupSteps()      { return warmupSteps; }
    public int     getNumWorkers()       { return numWorkers; }
    public String  getIpcSocketPath()    { return ipcSocketPath; }
    public String  getCppLibPath()       { return cppLibPath; }
    public String  getNativeLibPath()    { return nativeLibPath; }
    public boolean isUseCuda()           { return useCuda; }
    public boolean isVerbose()           { return verbose; }
    public int     getEvalEveryEpochs()  { return evalEveryEpochs; }
    public int     getSaveEveryEpochs()  { return saveEveryEpochs; }

    /** Load configuration from environment variables, falling back to defaults. */
    public static TrainingConfig fromEnvironment() {
        TrainingConfig c = new TrainingConfig();
        c.dataPath       = env("TRAINING_DATA_PATH",    c.dataPath);
        c.vocabPath      = env("TRAINING_VOCAB_PATH",   c.vocabPath);
        c.outputDir      = env("TRAINING_OUTPUT_DIR",   c.outputDir);
        c.numEpochs      = envInt("TRAINING_EPOCHS",    c.numEpochs);
        c.batchSize      = envInt("TRAINING_BATCH",     c.batchSize);
        c.learningRate   = envFloat("TRAINING_LR",      c.learningRate);
        c.weightDecay    = envFloat("TRAINING_WD",      c.weightDecay);
        c.numWorkers     = envInt("TRAINING_WORKERS",   c.numWorkers);
        c.ipcSocketPath  = env("TRAINING_IPC_SOCKET",   c.ipcSocketPath);
        c.cppLibPath     = env("TRAINING_CPP_LIB",      c.cppLibPath);
        c.nativeLibPath  = env("TRAINING_NATIVE_LIB",   c.nativeLibPath);
        c.useCuda        = envBool("TRAINING_USE_CUDA", c.useCuda);
        c.verbose        = envBool("TRAINING_VERBOSE",  c.verbose);
        return c;
    }

    private static String  env(String key, String  def) { var v = System.getenv(key); return v != null ? v : def; }
    private static int     envInt(String key, int   def) { var v = System.getenv(key); return v != null ? Integer.parseInt(v) : def; }
    private static float   envFloat(String key, float def) { var v = System.getenv(key); return v != null ? Float.parseFloat(v) : def; }
    private static boolean envBool(String key, boolean def) { var v = System.getenv(key); return v != null ? Boolean.parseBoolean(v) : def; }

    @Override
    public String toString() {
        return String.format(
            "TrainingConfig{epochs=%d, batch=%d, lr=%e, workers=%d, cuda=%b}",
            numEpochs, batchSize, learningRate, numWorkers, useCuda);
    }
}
