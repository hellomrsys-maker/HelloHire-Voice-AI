package ai.engine.service;

import ai.engine.infra.EngineConfig;
import ai.engine.infra.EngineInitException;

import java.util.logging.Level;
import java.util.logging.Logger;

/**
 * EngineServiceMain — CLI entry point for the Java verbal engine infrastructure.
 *
 * <p>Initializes the full Java engine stack:
 * <ol>
 *   <li>Load configuration from environment / CLI args</li>
 *   <li>Initialize EngineService (JNI bridge + IPC + scheduler)</li>
 *   <li>Block until SIGTERM / SIGINT (server mode)</li>
 * </ol>
 */
public class EngineServiceMain {

    private static final Logger LOG = Logger.getLogger(EngineServiceMain.class.getName());

    public static void main(String[] args) {
        configureLogging();
        LOG.info("=== Polyglot AI System — Java Engine Infrastructure ===");

        EngineConfig config = EngineConfig.fromEnvironment();
        applyCliArgs(config, args);
        LOG.info("Engine config: " + config);

        EngineService service = new EngineService(config);

        // Graceful shutdown on SIGTERM/SIGINT
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            LOG.info("Shutdown hook triggered — stopping EngineService");
            service.stop();
        }));

        try {
            service.initialize();
        } catch (EngineInitException e) {
            LOG.log(Level.SEVERE, "Engine service failed to initialize", e);
            System.exit(1);
        }

        LOG.info("EngineService is running. Waiting for requests...");

        // Keep the main thread alive — the service handles requests on its own threads
        try {
            Thread.currentThread().join();
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }

        LOG.info("EngineService main thread exiting.");
    }

    private static void configureLogging() {
        System.setProperty("java.util.logging.SimpleFormatter.format",
            "%1$tF %1$tT [%4$s] %3$s: %5$s%6$s%n");
    }

    private static void applyCliArgs(EngineConfig config, String[] args) {
        for (int i = 0; i < args.length - 1; i++) {
            switch (args[i]) {
                case "--lib-path"    -> config.setLibPath(args[++i]);
                case "--host"        -> config.setHost(args[++i]);
                case "--port"        -> config.setPort(Integer.parseInt(args[++i]));
                case "--workers"     -> config.setNumWorkers(Integer.parseInt(args[++i]));
                case "--verbose"     -> config.setVerbose(true);
                default -> {
                    // skip unknown
                }
            }
        }
    }
}
