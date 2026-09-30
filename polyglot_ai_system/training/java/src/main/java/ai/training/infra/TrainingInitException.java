package ai.training.infra;

/** Thrown when the training library bridge fails to initialize. */
public class TrainingInitException extends Exception {
    public TrainingInitException(String message)                    { super(message); }
    public TrainingInitException(String message, Throwable cause)   { super(message, cause); }
}
