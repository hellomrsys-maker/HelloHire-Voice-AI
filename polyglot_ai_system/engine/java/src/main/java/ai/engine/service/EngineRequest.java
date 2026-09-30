// =============================================================================
// engine/java/src/main/java/ai/engine/service/EngineRequest.java
// Engine/java/src/main/java/ai/engine/service/EngineResponse.java
// Request/response value objects for the Java engine service
// =============================================================================

package ai.engine.service;

import java.util.UUID;
import java.util.Objects;

/**
 * EngineRequest — immutable value object representing a text processing request.
 */
public final class EngineRequest {

    private final String requestId;
    private final String inputText;
    private final String outputModality;  // "text" | "speech_pcm" | "speech_opus"
    private final String reasoningDepth;  // "shallow" | "moderate" | "deep" | "extended"
    private final long   timestampNs;
    private final int    priority;        // Higher = more urgent

    private EngineRequest(Builder b) {
        this.requestId       = b.requestId;
        this.inputText       = b.inputText;
        this.outputModality  = b.outputModality;
        this.reasoningDepth  = b.reasoningDepth;
        this.timestampNs     = System.nanoTime();
        this.priority        = b.priority;
    }

    public String getRequestId()      { return requestId; }
    public String getInputText()      { return inputText; }
    public String getOutputModality() { return outputModality; }
    public String getReasoningDepth() { return reasoningDepth; }
    public long   getTimestampNs()    { return timestampNs; }
    public int    getPriority()       { return priority; }

    public static Builder builder(String inputText) {
        return new Builder(inputText);
    }

    public static class Builder {
        private final String inputText;
        private String requestId      = UUID.randomUUID().toString();
        private String outputModality = "text";
        private String reasoningDepth = "moderate";
        private int    priority       = 5;

        public Builder(String inputText) {
            this.inputText = Objects.requireNonNull(inputText, "inputText must not be null");
        }

        public Builder requestId(String v)      { this.requestId = v; return this; }
        public Builder outputModality(String v) { this.outputModality = v; return this; }
        public Builder reasoningDepth(String v) { this.reasoningDepth = v; return this; }
        public Builder priority(int v)          { this.priority = v; return this; }
        public EngineRequest build()            { return new EngineRequest(this); }
    }

    @Override
    public String toString() {
        return "EngineRequest{id=" + requestId + ", text='" +
               inputText.substring(0, Math.min(40, inputText.length())) + "...'}";
    }
}
