package ai.training.ipc;

import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.*;
import java.net.StandardProtocolFamily;
import java.net.UnixDomainSocketAddress;
import java.nio.ByteBuffer;
import java.nio.channels.SocketChannel;
import java.nio.charset.StandardCharsets;
import java.util.Map;
import java.util.Objects;
import java.util.concurrent.locks.ReentrantLock;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 * TrainingIPCChannel — Unix domain socket IPC channel for training coordination.
 *
 * <p>Provides JSON-over-Unix-socket communication between:
 * <ul>
 *   <li>Java training infrastructure → Rust data pipeline (batch requests)</li>
 *   <li>Java training infrastructure → Python orchestrator (metric reporting)</li>
 *   <li>Java training infrastructure → C++ engine (lightweight status queries)</li>
 * </ul>
 *
 * <p>Protocol: 4-byte little-endian length prefix + UTF-8 JSON payload.
 */
public class TrainingIPCChannel {

    private static final Logger LOG = Logger.getLogger(TrainingIPCChannel.class.getName());

    private static final int MAX_MESSAGE_BYTES = 64 * 1024 * 1024;  // 64 MB

    private final String socketPath;
    private final ObjectMapper json;
    private final ReentrantLock lock = new ReentrantLock();

    private volatile SocketChannel channel;
    private volatile boolean connected = false;

    public TrainingIPCChannel(String socketPath) {
        this.socketPath = Objects.requireNonNull(socketPath);
        this.json = new ObjectMapper();
    }

    // ── Lifecycle ────────────────────────────────────────────────────────────

    /**
     * Connect to the Unix domain socket at the configured path.
     * The server (Rust pipeline or Python orchestrator) must already be listening.
     *
     * @throws IOException if connection fails
     */
    public void connect() throws IOException {
        lock.lock();
        try {
            if (connected) return;
            LOG.info("Connecting to IPC socket: " + socketPath);

            UnixDomainSocketAddress addr = UnixDomainSocketAddress.of(socketPath);
            channel = SocketChannel.open(StandardProtocolFamily.UNIX);
            channel.connect(addr);
            channel.configureBlocking(true);
            connected = true;
            LOG.info("IPC channel connected: " + socketPath);
        } catch (UnsupportedOperationException e) {
            // Java < 16 fallback: log and continue (IPC will be stubbed)
            LOG.warning("Unix domain sockets not supported on this JVM — IPC disabled: " + e.getMessage());
        } finally {
            lock.unlock();
        }
    }

    /**
     * Close the IPC channel and release resources.
     */
    public void close() {
        lock.lock();
        try {
            if (channel != null) {
                try { channel.close(); } catch (IOException e) { /* ignore */ }
                channel = null;
            }
            connected = false;
            LOG.info("IPC channel closed.");
        } finally {
            lock.unlock();
        }
    }

    // ── Request / Response ───────────────────────────────────────────────────

    /**
     * Send a JSON request and receive a JSON response.
     * Thread-safe (uses lock). Blocks until response is received.
     *
     * @param request  map representing the JSON request
     * @return deserialized JSON response object
     * @throws IOException if I/O fails
     */
    public Object sendReceive(Map<String, Object> request) throws IOException {
        lock.lock();
        try {
            if (!connected || channel == null) {
                LOG.warning("IPC channel not connected — returning empty response");
                return Map.of();
            }

            // Serialize request to JSON bytes
            byte[] requestBytes = json.writeValueAsBytes(request);

            // Write 4-byte length prefix + payload
            ByteBuffer header = ByteBuffer.allocate(4).order(java.nio.ByteOrder.LITTLE_ENDIAN);
            header.putInt(requestBytes.length);
            header.flip();
            while (header.hasRemaining()) channel.write(header);

            ByteBuffer payload = ByteBuffer.wrap(requestBytes);
            while (payload.hasRemaining()) channel.write(payload);

            // Read 4-byte response length
            ByteBuffer respHeader = ByteBuffer.allocate(4).order(java.nio.ByteOrder.LITTLE_ENDIAN);
            readFully(channel, respHeader);
            respHeader.flip();
            int respLen = respHeader.getInt();

            if (respLen < 0 || respLen > MAX_MESSAGE_BYTES) {
                throw new IOException("Invalid response length: " + respLen);
            }

            // Read response payload
            ByteBuffer respPayload = ByteBuffer.allocate(respLen);
            readFully(channel, respPayload);
            String respJson = new String(respPayload.array(), StandardCharsets.UTF_8);

            return json.readValue(respJson, Object.class);

        } finally {
            lock.unlock();
        }
    }

    /**
     * Send a notification without waiting for a response (fire-and-forget).
     * Used for metric reporting to the Python orchestrator.
     *
     * @param message the JSON message to send
     */
    public void sendAsync(Map<String, Object> message) {
        if (!connected) return;
        lock.lock();
        try {
            byte[] bytes = json.writeValueAsBytes(message);
            ByteBuffer header = ByteBuffer.allocate(4).order(java.nio.ByteOrder.LITTLE_ENDIAN);
            header.putInt(bytes.length);
            header.flip();
            while (header.hasRemaining()) channel.write(header);
            ByteBuffer payload = ByteBuffer.wrap(bytes);
            while (payload.hasRemaining()) channel.write(payload);
        } catch (Exception e) {
            LOG.log(Level.FINE, "sendAsync failed (non-critical)", e);
        } finally {
            lock.unlock();
        }
    }

    /** Report training metrics to the Python orchestrator. */
    public void reportMetrics(int epoch, int step, float loss, Map<String, Float> facultyLosses) {
        Map<String, Object> msg = Map.of(
            "action",         "report_metrics",
            "epoch",          epoch,
            "step",           step,
            "loss",           loss,
            "faculty_losses", facultyLosses
        );
        sendAsync(msg);
    }

    public boolean isConnected() { return connected; }

    // ── Internal helpers ─────────────────────────────────────────────────────

    private void readFully(SocketChannel ch, ByteBuffer buf) throws IOException {
        while (buf.hasRemaining()) {
            int n = ch.read(buf);
            if (n == -1) throw new EOFException("IPC channel closed by peer");
        }
    }
}
