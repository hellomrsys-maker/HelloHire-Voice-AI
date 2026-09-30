package ai.training.service;

import java.util.Map;

/** Result of a model evaluation pass. */
public record EvaluationResult(float overallScore, Map<String, Float> facultyScores) {}
