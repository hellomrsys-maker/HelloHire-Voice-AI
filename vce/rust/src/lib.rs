//! VCE Rust Real-Time Audio Streaming & Zero-Allocation Ring Buffer
//!
//! Provides lock-free Single-Producer Single-Consumer (SPSC) circular audio streaming,
//! real-time PCM frame validation, clipping detection, RMS energy calculation,
//! and zero-bridge AMSV synchronization.

use std::sync::atomic::{AtomicU64, Ordering};

pub const DEFAULT_AUDIO_CAPACITY: usize = 65536; // 64K samples (4 seconds at 16kHz)
pub const DEFAULT_BUFFER_MASK: usize = DEFAULT_AUDIO_CAPACITY - 1;

#[repr(C)]
#[derive(Debug, Clone, Copy, Default)]
pub struct PcmFrameStats {
    pub rms_energy: f32,
    pub peak_amplitude: f32,
    pub zero_crossing_rate: f32,
    pub is_clipped: bool,
    pub sample_count: usize,
}

pub struct SafeAudioRingBuffer {
    buffer: Vec<f32>,
    capacity: usize,
    mask: usize,
    write_head: AtomicU64,
    read_tail: AtomicU64,
}

impl SafeAudioRingBuffer {
    pub fn new(capacity: usize) -> Self {
        let cap = capacity.next_power_of_two();
        Self {
            buffer: vec![0.0; cap],
            capacity: cap,
            mask: cap - 1,
            write_head: AtomicU64::new(0),
            read_tail: AtomicU64::new(0),
        }
    }

    #[inline(always)]
    pub fn push(&mut self, sample: f32) -> bool {
        let head = self.write_head.load(Ordering::Relaxed);
        let tail = self.read_tail.load(Ordering::Acquire);

        if (head - tail) >= self.capacity as u64 {
            return false; // Buffer overflow
        }

        self.buffer[(head as usize) & self.mask] = sample;
        self.write_head.store(head + 1, Ordering::Release);
        true
    }

    #[inline(always)]
    pub fn pop(&mut self) -> Option<f32> {
        let tail = self.read_tail.load(Ordering::Relaxed);
        let head = self.write_head.load(Ordering::Acquire);

        if tail == head {
            return None; // Buffer underflow / empty
        }

        let sample = self.buffer[(tail as usize) & self.mask];
        self.read_tail.store(tail + 1, Ordering::Release);
        Some(sample)
    }

    pub fn available_read(&self) -> usize {
        let tail = self.read_tail.load(Ordering::Relaxed);
        let head = self.write_head.load(Ordering::Acquire);
        if head >= tail {
            (head - tail) as usize
        } else {
            0
        }
    }

    pub fn available_write(&self) -> usize {
        self.capacity - self.available_read()
    }
}

/// Validates raw PCM frame, detecting clipping, computing RMS, and zero crossings.
pub fn analyze_pcm_frame(samples: &[f32]) -> PcmFrameStats {
    if samples.is_empty() {
        return PcmFrameStats::default();
    }

    let mut sum_sq = 0.0f32;
    let mut peak = 0.0f32;
    let mut zero_crossings = 0usize;
    let mut prev_sign = samples[0] >= 0.0;
    let mut clipped = false;

    for &s in samples {
        let abs_s = s.abs();
        if abs_s > peak {
            peak = abs_s;
        }
        if abs_s >= 0.995 {
            clipped = true;
        }
        sum_sq += s * s;

        let curr_sign = s >= 0.0;
        if curr_sign != prev_sign {
            zero_crossings += 1;
            prev_sign = curr_sign;
        }
    }

    let rms = (sum_sq / (samples.len() as f32)).sqrt();
    let zcr = (zero_crossings as f32) / (samples.len() as f32);

    PcmFrameStats {
        rms_energy: rms,
        peak_amplitude: peak,
        zero_crossing_rate: zcr,
        is_clipped: clipped,
        sample_count: samples.len(),
    }
}

// ============================================================================
// C-ABI EXPORTS
// ============================================================================

#[no_mangle]
pub extern "C" fn vce_ring_buffer_create(capacity: usize) -> *mut SafeAudioRingBuffer {
    let cap = if capacity == 0 { DEFAULT_AUDIO_CAPACITY } else { capacity };
    Box::into_raw(Box::new(SafeAudioRingBuffer::new(cap)))
}

#[no_mangle]
pub extern "C" fn vce_ring_buffer_push(rb_ptr: *mut SafeAudioRingBuffer, sample: f32) -> bool {
    if rb_ptr.is_null() {
        return false;
    }
    let rb = unsafe { &mut *rb_ptr };
    rb.push(sample)
}

#[no_mangle]
pub extern "C" fn vce_ring_buffer_pop(rb_ptr: *mut SafeAudioRingBuffer, out_sample: *mut f32) -> bool {
    if rb_ptr.is_null() || out_sample.is_null() {
        return false;
    }
    let rb = unsafe { &mut *rb_ptr };
    if let Some(val) = rb.pop() {
        unsafe { *out_sample = val; }
        true
    } else {
        false
    }
}

#[no_mangle]
pub extern "C" fn vce_ring_buffer_available_read(rb_ptr: *const SafeAudioRingBuffer) -> usize {
    if rb_ptr.is_null() {
        return 0;
    }
    let rb = unsafe { &*rb_ptr };
    rb.available_read()
}

#[no_mangle]
pub extern "C" fn vce_analyze_pcm(
    samples_ptr: *const f32,
    count: usize,
    out_stats: *mut PcmFrameStats,
) -> bool {
    if samples_ptr.is_null() || count == 0 || out_stats.is_null() {
        return false;
    }
    let slice = unsafe { std::slice::from_raw_parts(samples_ptr, count) };
    let stats = analyze_pcm_frame(slice);
    unsafe { *out_stats = stats; }
    true
}

#[no_mangle]
pub extern "C" fn vce_free_ring_buffer(rb_ptr: *mut SafeAudioRingBuffer) {
    if !rb_ptr.is_null() {
        unsafe { drop(Box::from_raw(rb_ptr)); }
    }
}
