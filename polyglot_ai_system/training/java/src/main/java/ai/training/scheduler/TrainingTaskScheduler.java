package ai.training.scheduler;

import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.logging.Level;
import java.util.logging.Logger;
import java.util.*;
import java.util.function.Supplier;

/**
 * TrainingTaskScheduler — manages prioritized task scheduling for training jobs.
 *
 * <p>Supports:
 * <ul>
 *   <li>Priority queue for training steps (NORMAL), evaluations (HIGH), checkpoints (LOW)</li>
 *   <li>Concurrent execution with configurable thread count</li>
 *   <li>Task retry with exponential backoff on transient failure</li>
 *   <li>Graceful shutdown with drain</li>
 * </ul>
 */
public class TrainingTaskScheduler {

    private static final Logger LOG = Logger.getLogger(TrainingTaskScheduler.class.getName());

    /** Task priority levels. */
    public enum Priority { LOW, NORMAL, HIGH }

    /** Represents a schedulable training task with retry semantics. */
    public static class TrainingTask<T> implements Comparable<TrainingTask<T>> {
        public final String    name;
        public final Priority  priority;
        public final Supplier<T> action;
        public final int       maxRetries;
        private int            retriesUsed = 0;

        public TrainingTask(String name, Priority priority, Supplier<T> action, int maxRetries) {
            this.name       = name;
            this.priority   = priority;
            this.action     = action;
            this.maxRetries = maxRetries;
        }

        public TrainingTask(String name, Priority priority, Supplier<T> action) {
            this(name, priority, action, 3);
        }

        @Override
        public int compareTo(TrainingTask<T> other) {
            // Higher priority → lower value in PQ (max-priority first)
            return Integer.compare(other.priority.ordinal(), this.priority.ordinal());
        }

        public boolean canRetry() { return retriesUsed < maxRetries; }
        public void incrementRetry() { retriesUsed++; }
        public int getRetriesUsed() { return retriesUsed; }
    }

    // ── State ────────────────────────────────────────────────────────────────

    private final ThreadPoolExecutor threadPool;
    private final PriorityBlockingQueue<Runnable> taskQueue;
    private final AtomicInteger submittedCount = new AtomicInteger(0);
    private final AtomicInteger completedCount = new AtomicInteger(0);
    private final AtomicInteger failedCount    = new AtomicInteger(0);
    private volatile boolean shuttingDown = false;

    // ── Construction ─────────────────────────────────────────────────────────

    public TrainingTaskScheduler(int numWorkers) {
        this.taskQueue = new PriorityBlockingQueue<>(256);
        this.threadPool = new ThreadPoolExecutor(
            numWorkers,
            numWorkers * 2,
            60L,
            TimeUnit.SECONDS,
            taskQueue,
            r -> {
                Thread t = new Thread(r, "training-scheduler-" + submittedCount.get());
                t.setDaemon(true);
                return t;
            },
            new ThreadPoolExecutor.AbortPolicy()
        );
        LOG.info("TrainingTaskScheduler started with " + numWorkers + " workers");
    }

    // ── API ──────────────────────────────────────────────────────────────────

    /**
     * Submit a task with given priority. Returns a CompletableFuture for the result.
     */
    public <T> CompletableFuture<T> submit(TrainingTask<T> task) {
        if (shuttingDown) {
            return CompletableFuture.failedFuture(
                new RejectedExecutionException("Scheduler is shutting down")
            );
        }

        submittedCount.incrementAndGet();
        CompletableFuture<T> future = new CompletableFuture<>();

        // Wrap in a Runnable that handles retries and priority
        Runnable runnable = createRetryableRunnable(task, future, 0);
        try {
            threadPool.execute(runnable);
        } catch (RejectedExecutionException e) {
            future.completeExceptionally(e);
        }
        return future;
    }

    /**
     * Submit a training step task (NORMAL priority).
     */
    public CompletableFuture<Void> submitStep(String name, Runnable step) {
        return submit(new TrainingTask<>(name, Priority.NORMAL, () -> {
            step.run();
            return null;
        }));
    }

    /**
     * Submit an evaluation task (HIGH priority — preempts training steps).
     */
    public <T> CompletableFuture<T> submitEvaluation(String name, Supplier<T> eval) {
        return submit(new TrainingTask<>(name, Priority.HIGH, eval));
    }

    /**
     * Submit a checkpoint save task (LOW priority — runs after current batch).
     */
    public CompletableFuture<Void> submitCheckpoint(String name, Runnable save) {
        return submit(new TrainingTask<>(name, Priority.LOW, () -> {
            save.run();
            return null;
        }));
    }

    /**
     * Wait for all currently queued tasks to complete.
     * @param timeoutMs maximum wait time in milliseconds
     * @return true if all tasks drained within the timeout
     */
    public boolean awaitDrain(long timeoutMs) throws InterruptedException {
        long deadline = System.currentTimeMillis() + timeoutMs;
        while (System.currentTimeMillis() < deadline) {
            if (threadPool.getActiveCount() == 0 && taskQueue.isEmpty()) {
                return true;
            }
            Thread.sleep(50);
        }
        return taskQueue.isEmpty() && threadPool.getActiveCount() == 0;
    }

    /** Graceful shutdown — stops accepting new tasks and drains queue. */
    public void shutdown() {
        shuttingDown = true;
        threadPool.shutdown();
        try {
            if (!threadPool.awaitTermination(30, TimeUnit.SECONDS)) {
                LOG.warning("Scheduler did not drain in 30s — forcing shutdown");
                threadPool.shutdownNow();
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            threadPool.shutdownNow();
        }
        LOG.info(String.format(
            "Scheduler shutdown. submitted=%d, completed=%d, failed=%d",
            submittedCount.get(), completedCount.get(), failedCount.get()
        ));
    }

    // ── Metrics ──────────────────────────────────────────────────────────────

    public int getQueueDepth()    { return taskQueue.size(); }
    public int getActiveWorkers() { return threadPool.getActiveCount(); }
    public int getSubmitted()     { return submittedCount.get(); }
    public int getCompleted()     { return completedCount.get(); }
    public int getFailed()        { return failedCount.get(); }

    // ── Private helpers ──────────────────────────────────────────────────────

    private <T> Runnable createRetryableRunnable(
        TrainingTask<T> task,
        CompletableFuture<T> future,
        int attemptNum
    ) {
        return () -> {
            try {
                T result = task.action.get();
                completedCount.incrementAndGet();
                future.complete(result);
            } catch (Exception e) {
                task.incrementRetry();
                if (task.canRetry() && !shuttingDown) {
                    long backoffMs = (long)(Math.pow(2, task.getRetriesUsed()) * 100);
                    LOG.log(Level.WARNING,
                        String.format("Task '%s' failed (attempt %d/%d), retrying in %dms: %s",
                            task.name, task.getRetriesUsed(), task.maxRetries, backoffMs,
                            e.getMessage()));
                    try { Thread.sleep(backoffMs); } catch (InterruptedException ie) {
                        Thread.currentThread().interrupt();
                    }
                    if (!shuttingDown) {
                        try {
                            threadPool.execute(createRetryableRunnable(task, future, attemptNum + 1));
                        } catch (RejectedExecutionException rje) {
                            failedCount.incrementAndGet();
                            future.completeExceptionally(rje);
                        }
                    }
                } else {
                    failedCount.incrementAndGet();
                    LOG.log(Level.SEVERE,
                        "Task '" + task.name + "' failed after " + task.getRetriesUsed() + " retries", e);
                    future.completeExceptionally(e);
                }
            }
        };
    }
}
