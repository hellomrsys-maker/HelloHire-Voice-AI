// =============================================================================
// engine/java/src/main/java/ai/engine/infra/EngineLibraryBridge.java
// JNI bridge to the C++ engine_core shared library.
// Manages native library loading, engine handle lifecycle, and JNI calls.
// =============================================================================

package ai.engine.infra;

import java.io.File;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.logging.Logger;
import java.util.logging.Level;

/**
 * EngineLibraryBridge — JNI bridge to the C++ engine_core shared library.
 *
 * <p>Loads the native library, creates an opaque engine handle, and
 * exposes Java-callable methods for all C-linkage FFI functions.
 *
 * <p>Thread safety: This class itself is NOT thread-safe — callers must
 * synchronize externally (e.g., via {@link ai.engine.service.EngineService}).
 */
public class EngineLibraryBridge {

    private static final Logger LOG = Logger.getLogger(EngineLibraryBridge.class.getName());

    private final EngineConfig config;
    private long nativeHandle = 0L;  // Stores the C++ EngineHandle* as a long
    private boolean libraryLoaded = false;

    // ==========================================================================
    // JNI native method declarations
    // ==========================================================================

    /**
     * Creates a C++ EngineHandle from a JSON config string.
     * @param configJson JSON configuration string
     * @return Native pointer as long (EngineHandle*)
     */
    private native long nativeCreateEngine(String configJson);

    /**
     * Recruits all engine subsystems.
     * @param handle Native engine handle pointer
     * @return 1 on success, 0 on failure
     */
    private native int nativeRecruitSubsystems(long handle);

    /**
     * Processes a text input.
     * @param handle  Native engine handle
     * @param input   Input text string
     * @param depth   Reasoning depth (0=shallow, 1=moderate, 2=deep, 3=extended)
     * @param modality Output modality (0=text, 1=speech_pcm, 2=speech_opus)
     * @return Response text string
     */
    private native String nativeProcessText(long handle, String input, int depth, int modality);

    /**
     * Returns 1 if the engine is operational.
     */
    private native int nativeIsOperational(long handle);

    /**
     * Returns the engine's JSON health dump.
     */
    private native String nativeHealthDump(long handle);

    /**
     * Destroys the engine handle and releases all C++ resources.
     */
    private native void nativeDestroyEngine(long handle);

    // ==========================================================================
    // Static library loading
    // ==========================================================================

    static {
        // Native library is loaded on demand via loadLibrary()
    }

    // ==========================================================================
    // Constructor
    // ==========================================================================

    public EngineLibraryBridge(EngineConfig config) {
        this.config = config;
    }

    // ==========================================================================
    // Lifecycle
    // ==========================================================================

    /**
     * Loads the native engine_core shared library.
     * Must be called before any other method.
     *
     * @throws EngineInitException if the library cannot be loaded
     */
    public void loadLibrary() {
        String libPath = config.getEngineCppLibPath();

        try {
            if (libPath != null && !libPath.isEmpty()) {
                System.load(libPath);
                LOG.info("Loaded engine_core native library from: " + libPath);
            } else {
                // Try loading from system library path
                System.loadLibrary("engine_core");
                LOG.info("Loaded engine_core from system library path");
            }
            libraryLoaded = true;
        } catch (UnsatisfiedLinkError e) {
            LOG.log(Level.WARNING,
                "Native engine_core library not found — running in stub mode. " +
                "Build with: make engine-cpp", e);
            libraryLoaded = false;
        }
    }

    /**
     * Creates the engine instance.
     * @throws EngineInitException if engine creation fails
     */
    public void createEngine() {
        if (!libraryLoaded) {
            LOG.info("Running in stub mode — no native library loaded");
            nativeHandle = -1L; // Sentinel for stub mode
            return;
        }

        String configJson = buildConfigJson();
        nativeHandle = nativeCreateEngine(configJson);

        if (nativeHandle == 0L) {
            throw new EngineInitException("nativeCreateEngine returned null pointer");
        }
        LOG.info("Engine created with handle: " + nativeHandle);
    }

    /**
     * Recruits all engine subsystems.
     * @throws EngineInitException if recruitment fails
     */
    public void recruitSubsystems() {
        if (!libraryLoaded) return; // Stub mode: always succeed

        int result = nativeRecruitSubsystems(nativeHandle);
        if (result != 1) {
            throw new EngineInitException("nativeRecruitSubsystems returned failure code: " + result);
        }
        LOG.info("Engine subsystems recruited successfully");
    }

    /**
     * Processes a text input.
     *
     * @param inputText Input text string
     * @param modality  "text" | "speech_pcm" | "speech_opus"
     * @param depth     "shallow" | "moderate" | "deep" | "extended"
     * @return Response text
     */
    public String processText(String inputText, String modality, String depth) {
        if (inputText == null || inputText.isBlank()) return "";

        if (!libraryLoaded || nativeHandle <= 0L) {
            // Stub mode response
            return stubResponse(inputText);
        }

        int depthCode    = parseDepth(depth);
        int modalityCode = parseModality(modality);

        String result = nativeProcessText(nativeHandle, inputText, depthCode, modalityCode);
        return result != null ? result : "";
    }

    /**
     * Returns true if the engine is operational.
     */
    public boolean isOperational() {
        if (!libraryLoaded || nativeHandle <= 0L) {
            return nativeHandle == -1L; // Stub mode: -1 = stub operational
        }
        return nativeIsOperational(nativeHandle) == 1;
    }

    /**
     * Returns the engine's JSON health dump.
     */
    public String getHealthDump() {
        if (!libraryLoaded || nativeHandle <= 0L) {
            return "{\"stub_mode\": true}";
        }
        String dump = nativeHealthDump(nativeHandle);
        return dump != null ? dump : "{}";
    }

    /**
     * Destroys the native engine and releases all C++ resources.
     */
    public void destroyEngine() {
        if (libraryLoaded && nativeHandle > 0L) {
            nativeDestroyEngine(nativeHandle);
            nativeHandle = 0L;
            LOG.info("Native engine destroyed");
        }
    }

    // ==========================================================================
    // Private helpers
    // ==========================================================================

    private String buildConfigJson() {
        return String.format(
            "{" +
            "\"engine_id\": \"%s\", " +
            "\"default_language\": \"%s\", " +
            "\"enable_gpu\": %b, " +
            "\"thread_pool_size\": %d, " +
            "\"attention_heads\": %d, " +
            "\"attention_dim\": %d, " +
            "\"max_seq_length\": %d" +
            "}",
            config.getEngineId(),
            config.getDefaultLanguage(),
            config.isEnableGpu(),
            config.getThreadPoolSize(),
            config.getAttentionHeads(),
            config.getAttentionDim(),
            config.getMaxSeqLength()
        );
    }

    private static int parseDepth(String depth) {
        if (depth == null) return 1;
        return switch (depth.toLowerCase()) {
            case "shallow"  -> 0;
            case "moderate" -> 1;
            case "deep"     -> 2;
            case "extended" -> 3;
            default         -> 1;
        };
    }

    private static int parseModality(String modality) {
        if (modality == null) return 0;
        return switch (modality.toLowerCase()) {
            case "text"       -> 0;
            case "speech_pcm" -> 1;
            case "speech_opus"-> 2;
            default           -> 0;
        };
    }

    private static String stubResponse(String inputText) {
        String lower = inputText.toLowerCase();
        if (lower.contains("hi") || lower.contains("hello") || lower.contains("hey")) {
            return "Nice to meet you.";
        }
        if (lower.contains("bye") || lower.contains("goodbye")) {
            return "Goodbye!";
        }
        if (inputText.contains("?")) {
            return "That's an interesting question.";
        }
        return "I understand.";
    }
}
