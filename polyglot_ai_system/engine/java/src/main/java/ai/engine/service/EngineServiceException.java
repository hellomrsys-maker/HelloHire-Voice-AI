// Engine exception types — EngineServiceException + EngineInitException

package ai.engine.service;

public class EngineServiceException extends RuntimeException {
    public EngineServiceException(String message) { super(message); }
    public EngineServiceException(String message, Throwable cause) { super(message, cause); }
}
