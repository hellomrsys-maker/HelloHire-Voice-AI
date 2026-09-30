package ai.training.service;

/** Current state of a training job. */
public enum TrainingJobState {
    IDLE, READY, RUNNING, COMPLETE, FAILED
}
