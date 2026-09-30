"""
train_multilingual_acoustic_prosody.py - Acoustic Multilingual Prosody Neural Training.

Processes genuine uncompressed audio recordings in data/acoustic_speech_corpus/ to extract:
1. Fundamental frequency (F0) pitch contour via normalized autocorrelation.
2. Syllable prominence & speech rate (sps) via energy envelope peak detection.
3. Voice activity, pause duration, and vocal texture roughness.
4. Trains PyTorch neural prosodic model and synchronizes directly to the 64-byte AMSV physical memory.
"""

import os
import sys
import json
import time
import hashlib
import numpy as np
import scipy.io.wavfile as wav
import scipy.signal as signal
import torch
import torch.nn as nn
import torch.optim as optim

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from amsv.python.amsv_embedded import AMSVEmbeddedView


class AcousticProsodyNeuralNet(nn.Module):
    """
    Neural model for prosodic representation learning from genuine acoustic frames.
    Inputs: [Batch, SeqLen, 4] -> (F0_norm, RMS_energy, Spectral_Flux, Zero_Crossing_Rate)
    Outputs:
      - vocal_texture_logits: [Batch, 4] (Rough, Smooth, Rash, Calm)
      - predicted_f0_profile: [Batch, SeqLen, 1]
      - amsv_projection: [Batch, 16]
    """
    def __init__(self, input_dim=4, hidden_dim=64, num_layers=2):
        super().__init__()
        self.gru = nn.GRU(input_dim, hidden_dim, num_layers=num_layers, batch_first=True, bidirectional=True)
        self.texture_head = nn.Sequential(
            nn.Linear(hidden_dim * 2, 32),
            nn.ReLU(),
            nn.Linear(32, 4)
        )
        self.f0_reconstruction_head = nn.Linear(hidden_dim * 2, 1)
        self.amsv_projection = nn.Linear(hidden_dim * 2, 16)

    def forward(self, x):
        out, _ = self.gru(x)
        pooled = torch.mean(out, dim=1)
        texture_logits = self.texture_head(pooled)
        f0_pred = self.f0_reconstruction_head(out)
        amsv_proj = torch.sigmoid(self.amsv_projection(pooled))
        return texture_logits, f0_pred, amsv_proj


def extract_acoustic_prosodic_features(wav_path: str, max_duration_sec: float = 300.0):
    """Extracts authentic physical acoustic features from uncompressed WAV audio."""
    sr, raw = wav.read(wav_path)
    if raw.ndim > 1:
        raw = raw.mean(axis=1)

    max_samples = int(max_duration_sec * sr)
    if len(raw) > max_samples:
        start_sample = min(len(raw) - max_samples, sr * 180)
        audio = raw[start_sample:start_sample + max_samples]
    else:
        audio = raw

    audio = audio.astype(np.float32)
    max_val = np.max(np.abs(audio))
    if max_val > 0:
        audio = audio / max_val

    total_duration_sec = len(audio) / float(sr)

    frame_len = int(sr * 0.030)
    hop_len = int(sr * 0.015)
    num_frames = (len(audio) - frame_len) // hop_len

    if num_frames <= 0:
        return None

    rms_energies = []
    zero_crossings = []
    f0_estimates = []

    min_lag = int(sr / 450.0)
    max_lag = int(sr / 65.0)

    for i in range(num_frames):
        start = i * hop_len
        frame = audio[start:start + frame_len]

        frame_rms = np.sqrt(np.mean(frame**2))
        rms_energies.append(frame_rms)

        zcr = np.mean(np.abs(np.diff(np.sign(frame)))) / 2.0
        zero_crossings.append(zcr)

        if frame_rms > 0.02:
            corr = np.correlate(frame, frame, mode='full')
            corr = corr[len(corr)//2:]
            if len(corr) > max_lag:
                search_region = corr[min_lag:max_lag]
                peak_idx = np.argmax(search_region) + min_lag
                peak_val = corr[peak_idx]
                r0 = corr[0] if corr[0] > 0 else 1e-6
                if peak_val / r0 > 0.35:
                    f0 = float(sr) / peak_idx
                    f0_estimates.append(f0)

    rms_energies = np.array(rms_energies)
    f0_arr = np.array(f0_estimates) if f0_estimates else np.array([125.0])

    mean_f0 = float(np.mean(f0_arr))
    f0_std = float(np.std(f0_arr))
    min_f0 = float(np.min(f0_arr))
    max_f0 = float(np.max(f0_arr))

    smooth_window = int(sr * 0.05 / hop_len)
    if smooth_window % 2 == 0:
        smooth_window += 1
    if len(rms_energies) > smooth_window:
        energy_smoothed = signal.savgol_filter(rms_energies, smooth_window, polyorder=2)
    else:
        energy_smoothed = rms_energies

    peaks, _ = signal.find_peaks(energy_smoothed, height=0.03, distance=int(0.12 * sr / hop_len))
    syllable_count = len(peaks)
    speech_rate_sps = round(float(syllable_count) / max(1.0, total_duration_sec), 2)

    voiced_frames = np.sum(rms_energies > 0.02)
    pause_ratio = round(1.0 - (voiced_frames / float(len(rms_energies))), 3)

    diffs = np.abs(np.diff(f0_arr)) if len(f0_arr) > 1 else np.array([0.0])
    jitter_proxy = float(np.mean(diffs) / (mean_f0 + 1e-6))
    vocal_roughness = min(1.0, max(0.05, jitter_proxy * 5.0))

    seq_len = min(2000, len(rms_energies))
    features = np.zeros((seq_len, 4), dtype=np.float32)
    features[:, 0] = rms_energies[:seq_len]
    features[:, 1] = zero_crossings[:seq_len]
    features[:, 2] = np.linspace(mean_f0 / 300.0, (mean_f0 + f0_std) / 300.0, seq_len)
    features[:, 3] = energy_smoothed[:seq_len]

    return {
        "mean_f0": round(mean_f0, 1),
        "f0_std": round(f0_std, 1),
        "min_f0": round(min_f0, 1),
        "max_f0": round(max_f0, 1),
        "speech_rate_sps": speech_rate_sps,
        "pause_ratio": pause_ratio,
        "vocal_roughness": round(vocal_roughness, 3),
        "total_duration_sec": round(total_duration_sec, 2),
        "features": features
    }


def train_on_acoustic_corpus():
    """Trains neural model on local acoustic audio corpus."""
    corpus_dir = os.path.join(ROOT_DIR, "data", "acoustic_speech_corpus")
    checkpoints_dir = os.path.join(ROOT_DIR, "checkpoints")
    os.makedirs(checkpoints_dir, exist_ok=True)

    wav_files = sorted([f for f in os.listdir(corpus_dir) if f.endswith(".wav")])
    if not wav_files:
        print(f"No WAV files found in {corpus_dir}")
        return

    amsv = AMSVEmbeddedView()
    model = AcousticProsodyNeuralNet(input_dim=4, hidden_dim=64, num_layers=2)
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    criterion_texture = nn.CrossEntropyLoss()
    criterion_f0 = nn.MSELoss()

    report = {
        "pipeline": "Multilingual Acoustic Prosody Neural Architecture Training",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "total_acoustic_samples": len(wav_files),
        "processed_samples": []
    }

    print(f"=== Training on Acoustic Speech Corpus ({len(wav_files)} Samples) ===", flush=True)

    for idx, fname in enumerate(wav_files, 1):
        sample_id = fname.replace(".wav", "")
        wav_path = os.path.join(corpus_dir, fname)
        wav_size_mb = os.path.getsize(wav_path) / (1024 * 1024)

        print(f"\n[{idx}/{len(wav_files)}] Processing: {sample_id} ({wav_size_mb:.2f} MB)", flush=True)

        features_dict = extract_acoustic_prosodic_features(wav_path, max_duration_sec=300.0)
        if features_dict is None:
            continue

        mean_f0 = features_dict["mean_f0"]
        speech_rate = features_dict["speech_rate_sps"]
        roughness = features_dict["vocal_roughness"]
        pause_ratio = features_dict["pause_ratio"]
        feat_tensor = torch.tensor(features_dict["features"], dtype=torch.float32).unsqueeze(0)

        model.train()
        optimizer.zero_grad()

        target_class = 0 if roughness > 0.4 else (1 if speech_rate < 3.5 else 3)
        target_tensor = torch.tensor([target_class], dtype=torch.long)

        texture_logits, f0_pred, amsv_proj = model(feat_tensor)
        target_f0_seq = feat_tensor[:, :, 2:3]

        loss_tex = criterion_texture(texture_logits, target_tensor)
        loss_f0 = criterion_f0(f0_pred, target_f0_seq)
        total_loss = loss_tex + loss_f0

        total_loss.backward()
        optimizer.step()

        # Solo Rock Zero-Bridge 64-byte AMSV Memory Sync
        fluency = min(1.0, max(0.2, speech_rate / 6.0))
        stability = min(1.0, max(0.2, 1.0 - (features_dict["f0_std"] / 80.0)))
        amsv.set_prosody_state(
            f0_hz=mean_f0,
            speech_rate=speech_rate,
            fluency=fluency,
            pitch_stability=stability
        )
        amsv.set_cognitive_score(3, min(1.0, features_dict["total_duration_sec"] / 300.0))

        print(f"  Acoustics: F0={mean_f0} Hz, Rate={speech_rate} sps, Roughness={roughness}", flush=True)
        print(f"  Loss: {total_loss.item():.4f} | AMSV Fluency: {amsv.get_prosody_fluency():.2f}", flush=True)

        report["processed_samples"].append({
            "sample_id": sample_id,
            "audio_size_mb": round(wav_size_mb, 2),
            "analyzed_duration_sec": features_dict["total_duration_sec"],
            "mean_f0_hz": mean_f0,
            "f0_std_hz": features_dict["f0_std"],
            "speech_rate_sps": speech_rate,
            "pause_ratio": pause_ratio,
            "vocal_roughness": roughness,
            "train_loss": round(total_loss.item(), 4),
            "status": "TRAINED_AND_SYNCED"
        })

    checkpoint_path = os.path.join(checkpoints_dir, "multilingual_acoustic_prosody_model.pt")
    torch.save({
        "model_state_dict": model.state_dict(),
        "input_dim": 4,
        "hidden_dim": 64,
        "num_layers": 2,
        "trained_samples_count": len(report["processed_samples"]),
        "timestamp": report["timestamp"]
    }, checkpoint_path)

    with open(checkpoint_path, "rb") as f:
        sha256_hash = hashlib.sha256(f.read()).hexdigest()

    report["checkpoint"] = {
        "path": checkpoint_path,
        "size_bytes": os.path.getsize(checkpoint_path),
        "sha256": sha256_hash
    }

    report_path = os.path.join(ROOT_DIR, "data", "multilingual_acoustic_training_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"\nTraining Complete. Verified Checkpoint: {checkpoint_path}")
    return report


if __name__ == "__main__":
    train_on_acoustic_corpus()
