/**
 * train.js - Master Single-Screen Universal Language Trainer in JavaScript (Node.js).
 * 
 * Consolidates all training routines into a single screen runner:
 * - Runs pure JavaScript engines directly.
 * - Single file per language (e.g. English_engine/train.js, Hindustani_engine/train.js).
 * - Enforces the 64-byte Zero-Bridge AMSV physical hardware sync.
 * 
 * Usage:
 *   node train.js                     (Trains default English engine)
 *   node train.js --language English
 *   node train.js --language Hindustani
 *   node train.js --all
 */

const fs = require('fs');
const path = require('path');

const AVAILABLE_ENGINES = {
  English: path.join(__dirname, 'English_engine', 'train.js'),
  Hindustani: path.join(__dirname, 'Hindustani_engine', 'train.js'),
  Telugu: path.join(__dirname, 'Telugu_engine', 'train.js')
};

function main() {
  const args = process.argv.slice(2);
  let targetLang = 'English';
  let runAll = false;
  let runObservational2000 = false;
  let iterations = 3;

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--language' || args[i] === '-l') {
      targetLang = args[i + 1] || 'English';
      i++;
    } else if (args[i] === '--iterations' || args[i] === '-i') {
      iterations = parseInt(args[i + 1], 10) || 3;
      i++;
    } else if (args[i] === '--all' || args[i] === '-a') {
      runAll = true;
    } else if (args[i] === '--observational-2000' || args[i] === '--observational' || args[i] === '-o') {
      runObservational2000 = true;
    }
  }

  console.clear ? console.clear() : void 0;
  console.log("=".repeat(80));
  console.log("  SOLO ROCK VOCAL INTELLIGENCE — UNIFIED JAVASCRIPT MASTER TRAINER");
  console.log("  Single-Screen Unified Execution | Zero-Bridge 64-Byte AMSV Protocol");
  console.log("=".repeat(80));

  if (runObservational2000) {
    // Train English and Hindustani separately and sequentially on observational speech dyads
    console.log("\n>>> RUNNING OBSERVATIONAL SPEECH TRAINING SEPARATELY PER LANGUAGE ENGINE (2000 ITERS) <<<\n");
    const { EnglishUnifiedTrainerJS } = require(AVAILABLE_ENGINES.English);
    const { HindustaniUnifiedTrainerJS } = require(AVAILABLE_ENGINES.Hindustani);
    
    console.log("\n[STEP 1/2] TRAINING ENGLISH ENGINE WITH 2000 ITERATIONS...");
    const engTrainer = new EnglishUnifiedTrainerJS({ iterations: 2000 });
    engTrainer.runFullTraining();

    console.log("\n[STEP 2/2] TRAINING HINDUSTANI ENGINE WITH 2000 ITERATIONS...");
    const hinTrainer = new HindustaniUnifiedTrainerJS({ iterations: 2000 });
    hinTrainer.runFullTraining();
    return;
  }

  if (runAll) {
    for (const [lang, scriptPath] of Object.entries(AVAILABLE_ENGINES)) {
      if (fs.existsSync(scriptPath)) {
        const module = require(scriptPath);
        const TrainerClass = Object.values(module)[0];
        if (TrainerClass) {
          const trainer = new TrainerClass({ iterations });
          trainer.runFullTraining();
        }
      }
    }
  } else {
    const scriptPath = AVAILABLE_ENGINES[targetLang];
    if (!scriptPath || !fs.existsSync(scriptPath)) {
      console.error(`[ERROR] Engine '${targetLang}' not found or train.js missing.`);
      console.log(`Available engines: ${Object.keys(AVAILABLE_ENGINES).join(', ')}`);
      process.exit(1);
    }

    const module = require(scriptPath);
    const TrainerClass = Object.values(module)[0];
    if (TrainerClass) {
      const trainer = new TrainerClass({ iterations });
      trainer.runFullTraining();
    }
  }
}

if (require.main === module) {
  main();
}

module.exports = { AVAILABLE_ENGINES };
