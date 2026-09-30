package ai.training.service;

import ai.training.infra.TrainingConfig;
import ai.training.infra.TrainingInitException;

import java.util.Map;
import java.util.concurrent.CompletableFuture;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 * TrainingServiceMain — CLI entry point for the Java training infrastructure.
 *
 * <p>Initializes the full Java training stack:
 * <ol>
 *   <li>Load configuration from environment / args</li>
 *   <li>Initialize TrainingService (JNI bridge + IPC + scheduler)</li>
 *   <li>Submit a training job and block until complete</li>
 *   <li>Report final metrics and exit</li>
 * </ol>
 */
public class TrainingServiceMain {

    private static final Logger LOG = Logger.getLogger(TrainingServiceMain.class.getName());

    public static void main(String[] args) {
        configureLogging();

        LOG.info("=== Polyglot AI System — Java Training Infrastructure ===");

        // Load config
        TrainingConfig config = TrainingConfig.fromEnvironment();
        applyCliArgs(config, args);
        LOG.info("Config: " + config);

        // Build and initialize service
        TrainingService service = new TrainingService(config);
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            LOG.info("Shutdown hook triggered.");
            service.shutdown();
        }));

        try {
            service.initialize();
        } catch (TrainingInitException e) {
            LOG.log(Level.SEVERE, "Training service failed to initialize", e);
            System.exit(1);
        }

        // Register a progress listener
        service.addListener(new TrainingJobListener() {
            @Override
            public void onEpochComplete(int epoch, float loss) {
                LOG.info(String.format("[Java listener] Epoch %d complete, loss=%.4f", epoch + 1, loss));
            }

            @Override
            public void onEvaluationComplete(int epoch, float score) {
                LOG.info(String.format("[Java listener] Eval after epoch %d: score=%.4f", epoch + 1, score));
            }
        });

        // Build and submit job
        TrainingJobConfig jobConfig = TrainingJobConfig.builder()
            .dataPath(config.getDataPath())
            .outputDir(config.getOutputDir())
            .epochs(config.getNumEpochs())
            .batchSize(config.getBatchSize())
            .learningRate(config.getLearningRate())
            .weightDecay(config.getWeightDecay())
            .evalEveryEpochs(config.getEvalEveryEpochs())
            .saveEveryEpochs(config.getSaveEveryEpochs())
            .build();

        LOG.info("Submitting training job...");
        CompletableFuture<TrainingJobResult> jobFuture = service.submitTrainingJob(jobConfig);

        try {
            TrainingJobResult result = jobFuture.join();
            LOG.info("=== Training Complete ===");
            LOG.info(String.format("  Final loss:    %.4f",   result.finalLoss()));
            LOG.info(String.format("  Total steps:   %d",     result.totalSteps()));
            LOG.info(String.format("  Epochs:        %d",     result.epochsCompleted()));
            LOG.info(String.format("  Total time:    %.1fs",  result.totalTimeMs() / 1000.0));
            LOG.info("  Faculty losses:");
            for (Map.Entry<String, Float> e : result.facultyLosses().entrySet()) {
                LOG.info(String.format("    %-20s %.4f", e.getKey(), e.getValue()));
            }
            System.exit(0);
        } catch (Exception e) {
            LOG.log(Level.SEVERE, "Training job failed", e);
            service.shutdown();
            System.exit(1);
        }
    }

    private static void configureLogging() {
        System.setProperty("java.util.logging.SimpleFormatter.format",
            "%1$tF %1$tT [%4$s] %3$s: %5$s%6$s%n");
    }

    private static void applyCliArgs(TrainingConfig config, String[] args) {
        for (int i = 0; i < args.length - 1; i++) {
            switch (args[i]) {
                case "--data"         -> config.dataPath(args[++i]);
                case "--output"       -> config.outputDir(args[++i]);
                case "--epochs"       -> config.numEpochs(Integer.parseInt(args[++i]));
                case "--batch-size"   -> config.batchSize(Integer.parseInt(args[++i]));
                case "--lr"           -> config.learningRate(Float.parseFloat(args[++i]));
                case "--workers"      -> config.numWorkers(Integer.parseInt(args[++i]));
                case "--vocab"        -> config.vocabPath(args[++i]);
                case "--native-lib"   -> config.nativeLibPath(args[++i]);
                case "--no-cuda"      -> config.useCuda(false);
                case "--verbose"      -> config.verbose(true);
                default -> {
                    // ignore unknown args (env vars take precedence)
                }
            }
        }
    }
}
