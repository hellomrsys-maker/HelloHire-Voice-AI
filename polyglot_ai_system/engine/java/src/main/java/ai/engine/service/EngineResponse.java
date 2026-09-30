// =============================================================================
// engine/java/src/main/java/ai/engine/service/EngineResponse.java
// Immutable response value object
// =============================================================================

package ai.engine.service;

import java.util.Objects;

/**
 * EngineResponse — immutable value object containing engine processing results.
 */
public final class EngineResponse {

    private final String  requestId;
    private final String  text;
    private final byte[]  speechPcm;      // Non-null if modality = speech
    private final long    latencyMs;
    private final float   confidence;
    private final String  reasoningTrace;
    private final boolean success;
    private final String  errorMessage;

    private EngineResponse(Builder b) {
        this.requestId      = b.requestId;
        this.text           = b.text;
        this.speechPcm      = b.speechPcm;
        this.latencyMs      = b.latencyMs;
        this.confidence     = b.confidence;
        this.reasoningTrace = b.reasoningTrace;
        this.success        = b.success;
        this.errorMessage   = b.errorMessage;
    }

    public String  getRequestId()      { return requestId; }
    public String  getText()           { return text; }
    public byte[]  getSpeechPcm()      { return speechPcm; }
    public long    getLatencyMs()      { return latencyMs; }
    public float   getConfidence()     { return confidence; }
    public String  getReasoningTrace() { return reasoningTrace; }
    public boolean isSuccess()         { return success; }
    public String  getErrorMessage()   { return errorMessage; }

    public static EngineResponse errorResponse(String requestId, String error) {
        return EngineResponse.builder()
            .requestId(requestId)
            .text("")
            .success(false)
            .errorMessage(error)
            .build();
    }

    public static Builder builder() { return new Builder(); }

    public static class Builder {
        private String  requestId      = "";
        private String  text           = "";
        private byte[]  speechPcm      = null;
        private long    latencyMs      = 0L;
        private float   confidence     = 0.0f;
        private String  reasoningTrace = "";
        private boolean success        = false;
        private String  errorMessage   = "";

        public Builder requestId(String v)      { this.requestId = v; return this; }
        public Builder text(String v)           { this.text = v; return this; }
        public Builder speechPcm(byte[] v)      { this.speechPcm = v; return this; }
        public Builder latencyMs(long v)        { this.latencyMs = v; return this; }
        public Builder confidence(float v)      { this.confidence = v; return this; }
        public Builder reasoningTrace(String v) { this.reasoningTrace = v; return this; }
        public Builder success(boolean v)       { this.success = v; return this; }
        public Builder errorMessage(String v)   { this.errorMessage = v; return this; }
        public EngineResponse build()           { return new EngineResponse(this); }
    }

    @Override
    public String toString() {
        return "EngineResponse{id=" + requestId +
               ", success=" + success +
               ", latencyMs=" + latencyMs +
               ", text='" + (text != null ? text.substring(0, Math.min(60, text.length())) : "") + "'}";
    }
}
