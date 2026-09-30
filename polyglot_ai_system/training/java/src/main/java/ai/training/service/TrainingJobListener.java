package ai.training.service;

/** Listener interface for training lifecycle events. */
public interface TrainingJobListener {
    void onEpochComplete(int epoch, float loss);
    void onEvaluationComplete(int epoch, float score);
}
