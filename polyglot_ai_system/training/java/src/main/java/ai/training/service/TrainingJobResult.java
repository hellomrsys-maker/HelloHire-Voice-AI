package ai.training.service;

import java.util.Map;

/** Result of a completed training job. */
public record TrainingJobResult(
    float finalLoss,
    Map<String, Float> facultyLosses,
    long totalSteps,
    int epochsCompleted,
    long totalTimeMs
) {}
