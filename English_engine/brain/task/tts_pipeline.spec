# TTS Pipeline Hardware and Acoustic Specification
[hardware]
target_accelerator = "NVIDIA Tensor Core (CUDA compute capability >= 8.0) or AVX-512 CPU"
streaming_latency_budget_ms = 20.0
real_time_factor_rtf_max = 0.08
memory_footprint_mb_max = 450.0

[acoustic_spec]
native_sampling_rate_hz = 24000
audio_encoding = "LINEAR_PCM_16BIT"
channels = 1 # Monaural
vocoder_architecture = "HiFi-GAN V1 Universal / Vocos Neural Vocoder"
hop_length_samples = 256
win_length_samples = 1024
n_fft = 1024
n_mels = 80
f_min_hz = 0.0
f_max_hz = 8000.0

[prosody_spec]
pitch_f0_bounds_hz = [65.0, 380.0]
duration_phoneme_bounds_ms = [25.0, 450.0]
energy_normalization = "dB_FS (-24.0 LUFS target)"
silence_boundary_padding_ms = 40.0
