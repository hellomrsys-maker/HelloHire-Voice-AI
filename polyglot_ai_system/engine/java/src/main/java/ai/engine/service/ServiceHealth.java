// =============================================================================
// engine/java/src/main/java/ai/engine/service/ServiceHealth.java
// engine/java/src/main/java/ai/engine/service/EngineServiceException.java
// engine/java/src/main/java/ai/engine/infra/EngineInitException.java
// Service health and exception types
// =============================================================================

package ai.engine.service;

/**
 * ServiceHealth — immutable health status snapshot.
 */
public final class ServiceHealth {

    private final String  engineId;
    private final boolean operational;
    private final long    totalRequests;
    private final long    successfulRequests;
    private final long    failedRequests;
    private final double  successRate;
    private final double  averageLatencyMs;
    private final int     activeWorkers;
    private final int     queueDepth;
    private final String  engineHealthDump;

    private ServiceHealth(Builder b) {
        this.engineId          = b.engineId;
        this.operational       = b.operational;
        this.totalRequests     = b.totalRequests;
        this.successfulRequests = b.successfulRequests;
        this.failedRequests    = b.failedRequests;
        this.successRate       = b.successRate;
        this.averageLatencyMs  = b.averageLatencyMs;
        this.activeWorkers     = b.activeWorkers;
        this.queueDepth        = b.queueDepth;
        this.engineHealthDump  = b.engineHealthDump;
    }

    public String  getEngineId()           { return engineId; }
    public boolean isOperational()         { return operational; }
    public long    getTotalRequests()      { return totalRequests; }
    public long    getSuccessfulRequests() { return successfulRequests; }
    public long    getFailedRequests()     { return failedRequests; }
    public double  getSuccessRate()        { return successRate; }
    public double  getAverageLatencyMs()   { return averageLatencyMs; }
    public int     getActiveWorkers()      { return activeWorkers; }
    public int     getQueueDepth()         { return queueDepth; }
    public String  getEngineHealthDump()   { return engineHealthDump; }

    public static Builder builder() { return new Builder(); }

    public static class Builder {
        private String  engineId = "";
        private boolean operational = false;
        private long    totalRequests = 0L;
        private long    successfulRequests = 0L;
        private long    failedRequests = 0L;
        private double  successRate = 0.0;
        private double  averageLatencyMs = 0.0;
        private int     activeWorkers = 0;
        private int     queueDepth = 0;
        private String  engineHealthDump = "{}";

        public Builder engineId(String v)           { this.engineId = v; return this; }
        public Builder operational(boolean v)       { this.operational = v; return this; }
        public Builder totalRequests(long v)        { this.totalRequests = v; return this; }
        public Builder successfulRequests(long v)   { this.successfulRequests = v; return this; }
        public Builder failedRequests(long v)       { this.failedRequests = v; return this; }
        public Builder successRate(double v)        { this.successRate = v; return this; }
        public Builder averageLatencyMs(double v)   { this.averageLatencyMs = v; return this; }
        public Builder activeWorkers(int v)         { this.activeWorkers = v; return this; }
        public Builder queueDepth(int v)            { this.queueDepth = v; return this; }
        public Builder engineHealthDump(String v)   { this.engineHealthDump = v; return this; }
        public ServiceHealth build()                { return new ServiceHealth(this); }
    }

    @Override
    public String toString() {
        return String.format(
            "ServiceHealth{engine=%s, operational=%b, requests=%d, successRate=%.2f, avgLatency=%.1fms}",
            engineId, operational, totalRequests, successRate, averageLatencyMs);
    }
}
