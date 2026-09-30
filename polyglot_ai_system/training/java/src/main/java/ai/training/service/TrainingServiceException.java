package ai.training.service;

/** Thrown when the training service encounters an unrecoverable error. */
public class TrainingServiceException extends RuntimeException {
    public TrainingServiceException(String message) { super(message); }
    public TrainingServiceException(String message, Throwable cause) { super(message, cause); }
}
