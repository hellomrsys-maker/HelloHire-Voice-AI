// =============================================================================
// engine/java/src/main/java/ai/engine/scheduler/TaskScheduler.java
// Priority-based task scheduler for engine request processing.
// =============================================================================

package ai.engine.scheduler;

import ai.engine.service.EngineRequest;

import java.util.concurrent.*;
import java.util.logging.Logger;
import java.util.concurrent.atomic.AtomicBoolean;

/**
 * TaskScheduler — priority-based scheduler for engine requests.
 *
 * <p>Uses a PriorityBlockingQueue internally so that high-priority
 * requests (larger priority value) are processed before low-priority ones.
 * Supports graceful shutdown with drain.
 */
public class TaskScheduler {

    private static final Logger LOG = Logger.getLogger(TaskScheduler.class.getName());

    private final PriorityBlockingQueue<ScheduledTask> queue;
    private final AtomicBoolean shutdown;

    public TaskScheduler(int maxCapacity) {
        this.queue    = new PriorityBlockingQueue<>(maxCapacity,
            (a, b) -> Integer.compare(b.priority, a.priority)); // Higher priority first
        this.shutdown = new AtomicBoolean(false);
    }

    /**
     * Submits a task with a given priority.
     * @param requestId  Unique request identifier
     * @param priority   Task priority (higher = more urgent)
     * @param task       The Runnable to execute
     * @return true if accepted, false if scheduler is shut down
     */
    public boolean submit(String requestId, int priority, Runnable task) {
        if (shutdown.get()) {
            LOG.warning("TaskScheduler is shut down — rejecting task: " + requestId);
            return false;
        }
        return queue.offer(new ScheduledTask(requestId, priority, task));
    }

    /**
     * Polls the next task from the queue, waiting up to timeoutMs milliseconds.
     * @return The next ScheduledTask, or null if none available within timeout.
     */
    public ScheduledTask poll(long timeoutMs) throws InterruptedException {
        return queue.poll(timeoutMs, TimeUnit.MILLISECONDS);
    }

    /**
     * Drains and cancels all pending tasks, then shuts down.
     */
    public void shutdown() {
        shutdown.set(true);
        queue.clear();
        LOG.info("TaskScheduler shut down — " + queue.size() + " pending tasks drained");
    }

    public int pendingCount() { return queue.size(); }
    public boolean isShutdown() { return shutdown.get(); }

    // ==========================================================================
    // ScheduledTask
    // ==========================================================================

    public static final class ScheduledTask {
        public final String   requestId;
        public final int      priority;
        public final Runnable task;
        public final long     enqueueTimeNs;

        public ScheduledTask(String requestId, int priority, Runnable task) {
            this.requestId      = requestId;
            this.priority       = priority;
            this.task           = task;
            this.enqueueTimeNs  = System.nanoTime();
        }

        public long waitTimeMs() {
            return (System.nanoTime() - enqueueTimeNs) / 1_000_000L;
        }

        @Override
        public String toString() {
            return "ScheduledTask{id=" + requestId + ", priority=" + priority
                   + ", waitMs=" + waitTimeMs() + "}";
        }
    }
}
