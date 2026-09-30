package ai.engine.infra;

public class EngineInitException extends RuntimeException {
    public EngineInitException(String message) { super(message); }
    public EngineInitException(String message, Throwable cause) { super(message, cause); }
}
