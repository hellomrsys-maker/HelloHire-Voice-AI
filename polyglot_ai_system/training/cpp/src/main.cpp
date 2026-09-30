// training/cpp/src/main.cpp
// CLI entry point for the C++ AI training system.
// Parses arguments, initializes TrainingCore, runs the full training loop,
// and exports trained model artifacts.

#include "TrainingCore.h"

#include <iostream>
#include <fstream>
#include <iomanip>
#include <string>
#include <chrono>
#include <csignal>
#include <cstring>
#include <filesystem>

namespace fs = std::filesystem;
using namespace polyglot::training;

// ─────────────────────────────────────────────────────────────────────────────
// Signal handler for graceful shutdown
// ─────────────────────────────────────────────────────────────────────────────

static volatile bool g_shutdown_requested = false;

static void signal_handler(int sig) {
    std::cerr << "\n[training] Signal " << sig << " received — requesting graceful shutdown\n";
    g_shutdown_requested = true;
}

// ─────────────────────────────────────────────────────────────────────────────
// Simple CLI argument parser
// ─────────────────────────────────────────────────────────────────────────────

struct CliArgs {
    std::string config_path;
    std::string data_path;
    std::string output_dir;
    std::string vocab_path;
    std::string checkpoint_path;  // resume from checkpoint
    int         epochs          = 10;
    int         batch_size      = 32;
    float       learning_rate   = 1e-4f;
    float       weight_decay    = 0.01f;
    float       grad_clip_norm  = 1.0f;
    int         warmup_steps    = 1000;
    int         log_interval    = 100;    // steps between log prints
    int         eval_interval   = 500;   // steps between evaluations
    int         save_interval   = 1000;  // steps between checkpoints
    bool        cuda            = true;
    bool        verbose         = false;
    bool        dry_run         = false;  // validate config only
};

static void print_usage(const char* prog) {
    std::cout << "Usage: " << prog << " [OPTIONS]\n\n"
              << "Polyglot AI System — Training Core\n\n"
              << "Options:\n"
              << "  --config       <path>    YAML training configuration file\n"
              << "  --data         <path>    JSONL training data file\n"
              << "  --output       <dir>     Output directory for checkpoints\n"
              << "  --vocab        <path>    BPE vocabulary JSON file\n"
              << "  --checkpoint   <path>    Resume from checkpoint\n"
              << "  --epochs       <int>     Number of training epochs (default: 10)\n"
              << "  --batch-size   <int>     Batch size (default: 32)\n"
              << "  --lr           <float>   Learning rate (default: 1e-4)\n"
              << "  --weight-decay <float>   Weight decay (default: 0.01)\n"
              << "  --grad-clip    <float>   Gradient clipping norm (default: 1.0)\n"
              << "  --warmup-steps <int>     LR warmup steps (default: 1000)\n"
              << "  --log-interval <int>     Steps between log lines (default: 100)\n"
              << "  --eval-interval<int>     Steps between evaluations (default: 500)\n"
              << "  --save-interval<int>     Steps between checkpoints (default: 1000)\n"
              << "  --no-cuda                Disable CUDA\n"
              << "  --verbose                Verbose logging\n"
              << "  --dry-run                Validate config and exit\n"
              << "  --help                   Print this help\n\n";
}

static CliArgs parse_args(int argc, char** argv) {
    CliArgs args;
    for (int i = 1; i < argc; ++i) {
        std::string a = argv[i];
        auto next = [&]() -> std::string {
            if (i + 1 >= argc) {
                std::cerr << "Missing value for " << a << "\n";
                std::exit(1);
            }
            return argv[++i];
        };

        if (a == "--help" || a == "-h")  { print_usage(argv[0]); std::exit(0); }
        else if (a == "--config")        args.config_path     = next();
        else if (a == "--data")          args.data_path       = next();
        else if (a == "--output")        args.output_dir      = next();
        else if (a == "--vocab")         args.vocab_path      = next();
        else if (a == "--checkpoint")    args.checkpoint_path = next();
        else if (a == "--epochs")        args.epochs          = std::stoi(next());
        else if (a == "--batch-size")    args.batch_size      = std::stoi(next());
        else if (a == "--lr")            args.learning_rate   = std::stof(next());
        else if (a == "--weight-decay")  args.weight_decay    = std::stof(next());
        else if (a == "--grad-clip")     args.grad_clip_norm  = std::stof(next());
        else if (a == "--warmup-steps")  args.warmup_steps    = std::stoi(next());
        else if (a == "--log-interval")  args.log_interval    = std::stoi(next());
        else if (a == "--eval-interval") args.eval_interval   = std::stoi(next());
        else if (a == "--save-interval") args.save_interval   = std::stoi(next());
        else if (a == "--no-cuda")       args.cuda            = false;
        else if (a == "--verbose")       args.verbose         = true;
        else if (a == "--dry-run")       args.dry_run         = true;
        else {
            std::cerr << "Unknown option: " << a << "\n";
            print_usage(argv[0]);
            std::exit(1);
        }
    }
    return args;
}

// ─────────────────────────────────────────────────────────────────────────────
// Training loop — uses TrainingCore public API from TrainingCore.h
// ─────────────────────────────────────────────────────────────────────────────

static void run_training_loop(
    TrainingCore& core,
    const CliArgs& args)
{
    auto total_start = std::chrono::high_resolution_clock::now();
    uint64_t last_logged_step = 0;

    std::cout << "[training] Starting training loop\n"
              << "  epochs:          " << args.epochs        << "\n"
              << "  batch_size:      " << args.batch_size    << "\n"
              << "  learning_rate:   " << args.learning_rate << "\n"
              << "  weight_decay:    " << args.weight_decay  << "\n"
              << "  grad_clip_norm:  " << args.grad_clip_norm << "\n"
              << "  warmup_steps:    " << args.warmup_steps  << "\n\n";

    // Run the configured number of epochs.
    // TrainingCore::train() runs the full loop internally and calls back
    // via metrics. We run it epoch by epoch using step() here for fine control.
    for (int epoch = 0; epoch < args.epochs && !g_shutdown_requested; ++epoch) {
        auto epoch_start = std::chrono::high_resolution_clock::now();
        double epoch_loss = 0.0;
        int steps_this_epoch = 0;

        // Run steps until epoch boundary (TrainingCore tracks this internally)
        while (!g_shutdown_requested) {
            TrainingMetrics m = core.step();

            epoch_loss += m.loss;
            ++steps_this_epoch;

            // Log at interval
            if (args.verbose && (m.global_step - last_logged_step) >= (uint64_t)args.log_interval) {
                std::cout << "[step " << m.global_step << "]"
                          << "  loss=" << std::fixed << std::setprecision(4) << m.loss
                          << "  lr="   << std::scientific << std::setprecision(3) << m.learning_rate
                          << "  grad=" << std::fixed << std::setprecision(3) << m.gradient_norm
                          << "\n";
                last_logged_step = m.global_step;
            }

            // Evaluate at interval
            if (m.global_step % (uint64_t)args.eval_interval == 0) {
                TrainingMetrics eval_m = core.evaluate();
                std::cout << "[eval step " << m.global_step << "]"
                          << "  loss=" << std::fixed << std::setprecision(4) << eval_m.loss
                          << "  thinking=" << eval_m.thinking_loss
                          << "  memory="   << eval_m.memory_loss
                          << "\n";
            }

            // Save checkpoint at interval
            if (!args.output_dir.empty() && m.global_step % (uint64_t)args.save_interval == 0) {
                fs::create_directories(args.output_dir);
                std::string tag = "step" + std::to_string(m.global_step);
                core.saveCheckpoint(tag);
                std::cout << "[checkpoint] Saved checkpoint: " << tag << "\n";
            }

            // Check if epoch is complete (TrainingCore uses max_steps / epoch tracking)
            if (steps_this_epoch >= static_cast<int>(core.config().max_steps / args.epochs)) {
                break;
            }
        }

        auto epoch_end = std::chrono::high_resolution_clock::now();
        double epoch_ms = std::chrono::duration<double, std::milli>(epoch_end - epoch_start).count();
        double avg_loss = steps_this_epoch > 0 ? epoch_loss / steps_this_epoch : 0.0;

        std::cout << "[epoch " << epoch + 1 << "/" << args.epochs << "]"
                  << "  avg_loss=" << std::fixed << std::setprecision(4) << avg_loss
                  << "  steps=" << steps_this_epoch
                  << "  time=" << std::fixed << std::setprecision(0) << epoch_ms << "ms"
                  << "\n";
    }

    // Final evaluation
    std::cout << "\n[training] Training complete — running final evaluation\n";
    TrainingMetrics final_m = core.evaluate();
    std::cout << "[final eval]"
              << "  loss="         << std::fixed << std::setprecision(4) << final_m.loss
              << "  thinking="     << final_m.thinking_loss
              << "  attention="    << final_m.attention_loss
              << "  memory="       << final_m.memory_loss
              << "  creativity="   << final_m.creativity_loss
              << "  imagination="  << final_m.imagination_loss
              << "  metacognition=" << final_m.metacognition_loss
              << "\n";

    // Final checkpoint
    if (!args.output_dir.empty()) {
        fs::create_directories(args.output_dir);
        core.saveCheckpoint("final");
        std::cout << "[checkpoint] Final checkpoint saved: " << args.output_dir << "/final\n";
    }

    auto total_end = std::chrono::high_resolution_clock::now();
    double total_ms = std::chrono::duration<double, std::milli>(total_end - total_start).count();
    std::cout << "\n[training] Total time:    " << total_ms / 1000.0 << " seconds\n";
    std::cout << "[training] Global steps:  " << core.globalStep() << "\n";
}

// ─────────────────────────────────────────────────────────────────────────────
// main
// ─────────────────────────────────────────────────────────────────────────────

int main(int argc, char** argv) {
    // Register signal handlers
    std::signal(SIGINT,  signal_handler);
    std::signal(SIGTERM, signal_handler);

    CliArgs args = parse_args(argc, argv);

    if (args.data_path.empty() && args.config_path.empty()) {
        std::cerr << "[error] At least one of --data or --config is required.\n";
        print_usage(argv[0]);
        return 1;
    }

    // Build TrainingConfig (fields that exist in the header)
    TrainingConfig config;
    config.data_dir         = args.data_path.empty() ? "data/" : args.data_path;
    config.checkpoint_dir   = args.output_dir.empty() ? "checkpoints/" : args.output_dir + "/";
    config.batch_size       = static_cast<uint32_t>(args.batch_size);
    config.learning_rate    = args.learning_rate;
    config.weight_decay     = args.weight_decay;
    config.gradient_clip_norm = args.grad_clip_norm;
    config.num_epochs       = static_cast<uint32_t>(args.epochs);
    config.use_gpu          = args.cuda;
    config.max_steps        = static_cast<uint32_t>(args.epochs) * 10000u;  // estimate

    if (args.dry_run) {
        std::cout << "[dry-run] Configuration validated. Exiting.\n";
        std::cout << "  data_dir:      " << config.data_dir    << "\n";
        std::cout << "  num_epochs:    " << config.num_epochs  << "\n";
        std::cout << "  batch_size:    " << config.batch_size  << "\n";
        std::cout << "  learning_rate: " << config.learning_rate << "\n";
        std::cout << "  use_gpu:       " << (config.use_gpu ? "yes" : "no") << "\n";
        return 0;
    }

    // Initialize TrainingCore
    TrainingCore core(config);
    std::cout << "[training] TrainingCore initialized.\n";

    // Resume from checkpoint if provided
    if (!args.checkpoint_path.empty()) {
        try {
            core.loadCheckpoint(args.checkpoint_path);
            std::cout << "[checkpoint] Resumed from: " << args.checkpoint_path << "\n";
        } catch (const std::exception& e) {
            std::cerr << "[warning] Failed to load checkpoint '" << args.checkpoint_path
                      << "': " << e.what() << "\n";
        }
    }

    // Run training
    run_training_loop(core, args);

    core.requestStop();
    std::cout << "[training] Shutdown complete.\n";
    return 0;
}
