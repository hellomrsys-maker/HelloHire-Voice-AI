# Japanese TTS Pipeline Hardware and Acoustic Specification
[hardware]
target_accelerator = "NVIDIA Tensor Core (CUDA compute capability >= 8.0) or AVX-512 CPU"
streaming_latency_budget_ms = 18.0
real_time_factor_rtf_max = 0.07
memory_footprint_mb_max = 480.0

[acoustic_spec]
native_sampling_rate_hz = 24000
audio_encoding = "LINEAR_PCM_16BIT"
channels = 1 # Monaural
vocoder_architecture = "HiFi-GAN V1 Universal / VITS Japanese Neural Vocoder"
hop_length_samples = 256
win_length_samples = 1024
n_fft = 1024
n_mels = 80
f_min_hz = 0.0
f_max_hz = 8000.0

[prosody_spec]
mora_timing_isochrony = true
pitch_accent_system = "Tokyo Japanese (Heiban, Atamadaka, Nakadaka, Odaka)"
pitch_f0_bounds_hz = [70.0, 420.0]
duration_mora_bounds_ms = [60.0, 220.0]
energy_normalization = "dB_FS (-24.0 LUFS target)"
silence_boundary_padding_ms = 40.0
