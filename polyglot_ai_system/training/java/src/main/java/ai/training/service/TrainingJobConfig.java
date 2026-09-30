package ai.training.service;

import java.util.Map;

/** Configuration for one training job submission. */
public final class TrainingJobConfig {
    private final String dataPath;
    private final String outputDir;
    private final int    epochs;
    private final int    batchSize;
    private final float  learningRate;
    private final float  weightDecay;
    private final int    evalEveryEpochs;
    private final int    saveEveryEpochs;

    private TrainingJobConfig(Builder b) {
        this.dataPath        = b.dataPath;
        this.outputDir       = b.outputDir;
        this.epochs          = b.epochs;
        this.batchSize       = b.batchSize;
        this.learningRate    = b.learningRate;
        this.weightDecay     = b.weightDecay;
        this.evalEveryEpochs = b.evalEveryEpochs;
        this.saveEveryEpochs = b.saveEveryEpochs;
    }

    public String getDataPath()        { return dataPath; }
    public String getOutputDir()       { return outputDir; }
    public int    getEpochs()          { return epochs; }
    public int    getBatchSize()       { return batchSize; }
    public float  getLearningRate()    { return learningRate; }
    public float  getWeightDecay()     { return weightDecay; }
    public int    getEvalEveryEpochs() { return evalEveryEpochs; }
    public int    getSaveEveryEpochs() { return saveEveryEpochs; }

    public static Builder builder() { return new Builder(); }

    public static final class Builder {
        private String dataPath        = "";
        private String outputDir       = "output/training";
        private int    epochs          = 10;
        private int    batchSize       = 32;
        private float  learningRate    = 1e-4f;
        private float  weightDecay     = 0.01f;
        private int    evalEveryEpochs = 1;
        private int    saveEveryEpochs = 2;

        public Builder dataPath(String v)        { dataPath = v;        return this; }
        public Builder outputDir(String v)       { outputDir = v;       return this; }
        public Builder epochs(int v)             { epochs = v;          return this; }
        public Builder batchSize(int v)          { batchSize = v;       return this; }
        public Builder learningRate(float v)     { learningRate = v;    return this; }
        public Builder weightDecay(float v)      { weightDecay = v;     return this; }
        public Builder evalEveryEpochs(int v)    { evalEveryEpochs = v; return this; }
        public Builder saveEveryEpochs(int v)    { saveEveryEpochs = v; return this; }
        public TrainingJobConfig build()         { return new TrainingJobConfig(this); }
    }
}
