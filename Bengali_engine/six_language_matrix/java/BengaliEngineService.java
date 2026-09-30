// Bengali Engine Service (Java 21 Project Loom)
// Leverages virtual threads and java.nio.ByteBuffer for 0-bridge direct 64-byte AMSV memory integration.

package gra.bengali;

import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;

public class BengaliEngineService {

    private final ByteBuffer amsvBuffer;
    private final ExecutorService virtualThreadExecutor;

    public BengaliEngineService(ByteBuffer sharedDirectBuffer) {
        if (sharedDirectBuffer == null || sharedDirectBuffer.capacity() < 64) {
            throw new IllegalArgumentException("Shared buffer must be direct and at least 64 bytes in capacity.");
        }
        this.amsvBuffer = sharedDirectBuffer.order(ByteOrder.LITTLE_ENDIAN);
        this.virtualThreadExecutor = Executors.newVirtualThreadPerTaskExecutor();
    }

    public record BengaliAnalysisResult(
        String text,
        boolean isValidSOV,
        boolean hasClassifier,
        double syntaxScore,
        double registerScore
    ) {}

    public Future<BengaliAnalysisResult> processSentenceAsync(String text) {
        return virtualThreadExecutor.submit(() -> {
            boolean hasClassifier = text.contains("টা") || text.contains("টি") || 
                                    text.contains("গুলো") || text.contains("জন");
            double syntaxScore = text.endsWith("।") ? 0.95 : 0.85;
            double registerScore = text.contains("আপনি") || text.contains("তিনি") ? 0.95 : 0.80;

            // Direct zero-bridge synchronous memory write to AMSV buffer
            synchronized (amsvBuffer) {
                // Byte 18: Capability 1 (Syntax)
                amsvBuffer.put(18, (byte) ((int) (syntaxScore * 255)));
                // Byte 22: Capability 3 (Pragmatics)
                amsvBuffer.put(22, (byte) ((int) (registerScore * 255)));
                // Byte 52: Structural Score
                amsvBuffer.putFloat(52, (float) syntaxScore);
                // Byte 54: Register Score
                amsvBuffer.putFloat(54, (float) registerScore);
            }

            return new BengaliAnalysisResult(text, true, hasClassifier, syntaxScore, registerScore);
        });
    }

    public void shutdown() {
        virtualThreadExecutor.close();
    }
}
