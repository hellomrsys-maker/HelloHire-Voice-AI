// training/rust/src/main.rs
//! CLI entry point for the polyglot training data pipeline.
//! Run as: polyglot-data-pipeline --data <path.jsonl> [options]

use clap::Parser;
use polyglot_training::{
    batch::DataSource,
    pipeline::{DataPipeline, PipelineConfig},
};
use tracing::info;
use tracing_subscriber::EnvFilter;

#[derive(Parser, Debug)]
#[command(name = "polyglot-data-pipeline")]
#[command(about = "High-throughput training data pipeline for the polyglot AI system")]
struct Args {
    /// Path to JSONL training data file
    #[arg(short, long)]
    data: String,

    /// Path to BPE vocabulary JSON file (optional)
    #[arg(short, long)]
    vocab: Option<String>,

    /// Batch size
    #[arg(short, long, default_value = "32")]
    batch_size: usize,

    /// Minimum quality score for records
    #[arg(short, long, default_value = "0.5")]
    min_quality: f64,

    /// Number of worker threads
    #[arg(short, long, default_value = "4")]
    workers: usize,

    /// Number of epochs to process
    #[arg(short, long, default_value = "1")]
    epochs: usize,

    /// Print per-batch statistics
    #[arg(long)]
    verbose: bool,
}

fn main() {
    tracing_subscriber::fmt()
        .with_env_filter(EnvFilter::from_default_env().add_directive(
            "polyglot_training=info".parse().unwrap(),
        ))
        .init();

    let args = Args::parse();

    info!("Starting polyglot training data pipeline");
    info!("  data:        {}", args.data);
    info!("  batch_size:  {}", args.batch_size);
    info!("  min_quality: {}", args.min_quality);
    info!("  workers:     {}", args.workers);
    info!("  epochs:      {}", args.epochs);

    let config = PipelineConfig {
        batch_size: args.batch_size,
        shuffle: true,
        min_quality_score: args.min_quality,
        vocab_path: args.vocab.clone(),
        max_seq_len: 512,
        num_workers: args.workers,
    };

    let source = DataSource::jsonl(&args.data);
    let mut pipeline = DataPipeline::new(config, vec![source])
        .expect("Failed to create data pipeline");

    info!("Vocabulary size: {}", pipeline.vocab_size());

    for epoch in 0..args.epochs {
        info!("=== Epoch {}/{} ===", epoch + 1, args.epochs);
        let batches = pipeline.epoch().expect("Pipeline epoch failed");
        info!("Epoch {} complete: {} batches", epoch + 1, batches.len());

        if args.verbose {
            for batch in &batches {
                info!(
                    "  Batch {}: {} records, max_len={}",
                    batch.batch_idx,
                    batch.len(),
                    batch.max_len()
                );
            }
        }
    }

    let metrics = pipeline.metrics();
    let snap = metrics.snapshot();
    info!("Pipeline complete.");
    info!("  Epochs:    {}", snap.epochs);
    info!("  Batches:   {}", snap.total_batches);
    info!("  Processed: {}", polyglot_training::processed_count());
    info!("  Rejected:  {}", polyglot_training::rejected_count());
}
