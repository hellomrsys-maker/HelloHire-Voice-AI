// =============================================================================
// engine/java/src/main/java/ai/engine/ipc/IPCChannel.java
// Inter-process communication channel for distributed coordination
// between the Java service layer and other language components.
// =============================================================================

package ai.engine.ipc;

import java.io.*;
import java.net.*;
import java.nio.ByteBuffer;
import java.nio.channels.*;
import java.util.concurrent.*;
import java.util.function.Consumer;
import java.util.logging.Logger;
import java.util.logging.Level;
import java.util.concurrent.atomic.AtomicBoolean;

/**
 * IPCChannel — TCP-based IPC channel for cross-process coordination.
 *
 * <p>Supports both server-side (listening) and client-side (connecting) modes.
 * Messages are length-prefixed JSON payloads.
 *
 * <p>Message format: [4-byte big-endian length][UTF-8 JSON payload]
 */
public class IPCChannel implements AutoCloseable {

    private static final Logger LOG = Logger.getLogger(IPCChannel.class.getName());

    private final String           host;
    private final int              port;
    private final boolean          serverMode;
    private final AtomicBoolean    running;
    private final ExecutorService  ioExecutor;

    private ServerSocketChannel    serverChannel;
    private SocketChannel          clientChannel;
    private Consumer<String>       messageHandler;

    private static final int MAX_MESSAGE_SIZE = 16 * 1024 * 1024; // 16 MB

    // ==========================================================================
    // Construction
    // ==========================================================================

    /**
     * Creates an IPC channel.
     * @param host       Hostname or IP to listen on (server) or connect to (client)
     * @param port       Port number
     * @param serverMode true = listen for connections; false = connect to server
     */
    public IPCChannel(String host, int port, boolean serverMode) {
        this.host       = host;
        this.port       = port;
        this.serverMode = serverMode;
        this.running    = new AtomicBoolean(false);
        this.ioExecutor = Executors.newCachedThreadPool(r -> {
            Thread t = new Thread(r, "ipc-io-" + System.nanoTime());
            t.setDaemon(true);
            return t;
        });
    }

    /**
     * Sets the message handler callback.
     * @param handler Consumer called with each received JSON string
     */
    public void onMessage(Consumer<String> handler) {
        this.messageHandler = handler;
    }

    // ==========================================================================
    // Lifecycle
    // ==========================================================================

    /**
     * Starts the IPC channel (opens the socket and begins listening/connecting).
     * @throws IOException if the socket cannot be opened
     */
    public void start() throws IOException {
        running.set(true);

        if (serverMode) {
            serverChannel = ServerSocketChannel.open();
            serverChannel.socket().bind(new InetSocketAddress(host, port));
            serverChannel.configureBlocking(false);
            LOG.info("IPCChannel listening on " + host + ":" + port);
            ioExecutor.submit(this::acceptLoop);
        } else {
            clientChannel = SocketChannel.open();
            clientChannel.connect(new InetSocketAddress(host, port));
            clientChannel.configureBlocking(true);
            LOG.info("IPCChannel connected to " + host + ":" + port);
            ioExecutor.submit(() -> receiveLoop(clientChannel));
        }
    }

    // ==========================================================================
    // Send / receive
    // ==========================================================================

    /**
     * Sends a JSON message over the IPC channel.
     *
     * @param jsonMessage UTF-8 JSON string to send
     * @throws IOException if sending fails
     * @throws IllegalStateException if no connection is established
     */
    public synchronized void send(String jsonMessage) throws IOException {
        SocketChannel channel = clientChannel;
        if (channel == null || !channel.isConnected()) {
            throw new IllegalStateException("IPC channel is not connected");
        }

        byte[] payload = jsonMessage.getBytes("UTF-8");
        if (payload.length > MAX_MESSAGE_SIZE) {
            throw new IllegalArgumentException(
                "Message too large: " + payload.length + " > " + MAX_MESSAGE_SIZE);
        }

        ByteBuffer header = ByteBuffer.allocate(4);
        header.putInt(payload.length);
        header.flip();

        ByteBuffer body = ByteBuffer.wrap(payload);

        // Write header then body
        while (header.hasRemaining()) channel.write(header);
        while (body.hasRemaining())   channel.write(body);
    }

    // ==========================================================================
    // Private I/O loops
    // ==========================================================================

    private void acceptLoop() {
        while (running.get()) {
            try {
                SocketChannel accepted = serverChannel.accept();
                if (accepted != null) {
                    LOG.info("IPC client connected: " + accepted.getRemoteAddress());
                    clientChannel = accepted;
                    accepted.configureBlocking(true);
                    ioExecutor.submit(() -> receiveLoop(accepted));
                }
                Thread.sleep(10);
            } catch (IOException e) {
                if (running.get()) {
                    LOG.log(Level.WARNING, "IPC accept error", e);
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            }
        }
    }

    private void receiveLoop(SocketChannel channel) {
        ByteBuffer lenBuf = ByteBuffer.allocate(4);

        while (running.get() && channel.isOpen()) {
            try {
                // Read 4-byte length header
                lenBuf.clear();
                int read = 0;
                while (lenBuf.hasRemaining()) {
                    int n = channel.read(lenBuf);
                    if (n < 0) {
                        LOG.info("IPC remote closed connection");
                        return;
                    }
                    read += n;
                }

                lenBuf.flip();
                int msgLen = lenBuf.getInt();

                if (msgLen <= 0 || msgLen > MAX_MESSAGE_SIZE) {
                    LOG.warning("IPC received invalid message length: " + msgLen);
                    continue;
                }

                // Read message body
                ByteBuffer bodyBuf = ByteBuffer.allocate(msgLen);
                while (bodyBuf.hasRemaining()) {
                    int n = channel.read(bodyBuf);
                    if (n < 0) return;
                }
                bodyBuf.flip();

                String message = new String(bodyBuf.array(), 0, msgLen, "UTF-8");

                if (messageHandler != null) {
                    try {
                        messageHandler.accept(message);
                    } catch (Exception e) {
                        LOG.log(Level.WARNING, "IPC message handler threw exception", e);
                    }
                }

            } catch (IOException e) {
                if (running.get()) {
                    LOG.log(Level.WARNING, "IPC receive error", e);
                }
                return;
            }
        }
    }

    // ==========================================================================
    // Lifecycle close
    // ==========================================================================

    @Override
    public void close() {
        running.set(false);
        ioExecutor.shutdown();
        try {
            if (serverChannel != null) serverChannel.close();
            if (clientChannel != null) clientChannel.close();
        } catch (IOException e) {
            LOG.log(Level.WARNING, "IPC channel close error", e);
        }
        LOG.info("IPCChannel closed");
    }
}
