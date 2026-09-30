// =============================================================================
// engine/java/src/main/java/ai/engine/infra/EngineConfig.java
// Engine configuration object for the Java infrastructure layer
// =============================================================================

package ai.engine.infra;

import java.util.List;
import java.util.ArrayList;
import java.util.Objects;

/**
 * EngineConfig — complete configuration for the Java engine infrastructure.
 * Mirrors the EngineConfig struct from the C++ layer.
 */
public class EngineConfig {

    private String engineId           = "verbal_comm_engine_v1";
    private String engineVersion      = "1.0.0";
    private String defaultLanguage    = "en";
    private List<String> supportedLanguages = new ArrayList<>(List.of("en", "fr", "de", "ja", "es", "ar", "ta"));

    private int     threadPoolSize    = 8;
    private int     maxQueueDepth     = 10000;
    private int     maxBatchSize      = 64;
    private int     maxSeqLength      = 8192;
    private boolean enableGpu         = true;
    private int     gpuDeviceId       = 0;

    private long    workingMemoryBytes    = 1L << 30;   // 1 GB
    private long    episodicMemorySlots   = 65536L;
    private long    semanticMemorySlots   = 1048576L;

    private int     attentionHeads    = 16;
    private int     attentionDim      = 1024;
    private float   attentionDropout  = 0.1f;

    private String  reasoningDepth    = "moderate";
    private int     maxReasoningSteps = 32;

    private boolean enableSafetyFilter = true;
    private boolean enablePrivacyGuard = true;
    private float   safetyThreshold    = 0.85f;

    // Paths
    private String engineCppLibPath     = "";
    private String trainingFilePath     = "language_engines/English_engine.training.yaml";

    // Timeouts
    private long    batchTimeoutSeconds = 30L;
    private long    requestTimeoutMs    = 5000L;

    // Private constructor — use Builder
    private EngineConfig() {}

    // ==========================================================================
    // Builder
    // ==========================================================================

    public static Builder builder() { return new Builder(); }

    public static class Builder {
        private final EngineConfig config = new EngineConfig();

        public Builder engineId(String v)           { config.engineId = v; return this; }
        public Builder defaultLanguage(String v)    { config.defaultLanguage = v; return this; }
        public Builder threadPoolSize(int v)        { config.threadPoolSize = v; return this; }
        public Builder maxQueueDepth(int v)         { config.maxQueueDepth = v; return this; }
        public Builder maxBatchSize(int v)          { config.maxBatchSize = v; return this; }
        public Builder maxSeqLength(int v)          { config.maxSeqLength = v; return this; }
        public Builder enableGpu(boolean v)         { config.enableGpu = v; return this; }
        public Builder attentionHeads(int v)        { config.attentionHeads = v; return this; }
        public Builder attentionDim(int v)          { config.attentionDim = v; return this; }
        public Builder reasoningDepth(String v)     { config.reasoningDepth = v; return this; }
        public Builder engineCppLibPath(String v)   { config.engineCppLibPath = v; return this; }
        public Builder trainingFilePath(String v)   { config.trainingFilePath = v; return this; }
        public Builder batchTimeoutSeconds(long v)  { config.batchTimeoutSeconds = v; return this; }

        public EngineConfig build() { return config; }
    }

    // ==========================================================================
    // Getters
    // ==========================================================================

    public String  getEngineId()           { return engineId; }
    public String  getEngineVersion()      { return engineVersion; }
    public String  getDefaultLanguage()    { return defaultLanguage; }
    public List<String> getSupportedLanguages() { return supportedLanguages; }
    public int     getThreadPoolSize()     { return threadPoolSize; }
    public int     getMaxQueueDepth()      { return maxQueueDepth; }
    public int     getMaxBatchSize()       { return maxBatchSize; }
    public int     getMaxSeqLength()       { return maxSeqLength; }
    public boolean isEnableGpu()           { return enableGpu; }
    public int     getGpuDeviceId()        { return gpuDeviceId; }
    public long    getWorkingMemoryBytes() { return workingMemoryBytes; }
    public long    getEpisodicMemorySlots(){ return episodicMemorySlots; }
    public long    getSemanticMemorySlots(){ return semanticMemorySlots; }
    public int     getAttentionHeads()     { return attentionHeads; }
    public int     getAttentionDim()       { return attentionDim; }
    public float   getAttentionDropout()   { return attentionDropout; }
    public String  getReasoningDepth()     { return reasoningDepth; }
    public int     getMaxReasoningSteps()  { return maxReasoningSteps; }
    public boolean isEnableSafetyFilter()  { return enableSafetyFilter; }
    public boolean isEnablePrivacyGuard()  { return enablePrivacyGuard; }
    public float   getSafetyThreshold()    { return safetyThreshold; }
    public String  getEngineCppLibPath()   { return engineCppLibPath; }
    public String  getTrainingFilePath()   { return trainingFilePath; }
    public long    getBatchTimeoutSeconds(){ return batchTimeoutSeconds; }
    public long    getRequestTimeoutMs()   { return requestTimeoutMs; }

    @Override
    public String toString() {
        return "EngineConfig{" +
               "engineId='" + engineId + '\'' +
               ", defaultLanguage='" + defaultLanguage + '\'' +
               ", threadPoolSize=" + threadPoolSize +
               ", enableGpu=" + enableGpu +
               ", attentionHeads=" + attentionHeads +
               ", attentionDim=" + attentionDim +
               ", reasoningDepth='" + reasoningDepth + '\'' +
               '}';
    }
}
