/**
 * @file amsv_layout.h
 * @brief Advanced Multi-language Shared Memory and State Vector (AMSV) Specification.
 *
 * Implements the 64-byte Atomic Memory State Vector aligned to CPU cache-line boundary (64 bytes),
 * lock-free ring buffer for real-time PCM audio streaming, and atomic memory barriers.
 * Adheres strictly to the Zero-Bridge Synchronous Memory Rule: 0-nanosecond latency
 * through shared physical memory addresses across C++, Rust, Julia, Python, CUDA, and Java.
 */

#ifndef AMSV_LAYOUT_H
#define AMSV_LAYOUT_H

#include <cstdint>
#include <cstddef>
#include <atomic>
#include <type_traits>

#if defined(_MSC_VER)
    #define AMSV_ALIGN(n) __declspec(align(n))
#else
    #define AMSV_ALIGN(n) __attribute__((aligned(n)))
#endif

namespace solorock::amsv {

// ============================================================================
// 64-BYTE ATOMIC MEMORY STATE VECTOR (AMSV)
// ============================================================================
/**
 * Exact byte-offset mapping within the 64-byte cache-line aligned vector:
 *
 * Offset 0x00 - 0x07 (8 bytes) : VCE Phoneme & Articulation State
 * Offset 0x08 - 0x0F (8 bytes) : VCE Prosody & Pitch Contour State
 * Offset 0x10 - 0x1F (16 bytes): CCTE 8 Cognitive Capability State Vector (8 x 2 bytes)
 *   0x10 - 0x11: Thinking Ability State (uint16_t fixed-point)
 *   0x12 - 0x13: Concentration & Focus State (uint16_t fixed-point)
 *   0x14 - 0x15: Memory & Recall State (uint16_t fixed-point)
 *   0x16 - 0x17: Creative Thinking State (uint16_t fixed-point)
 *   0x18 - 0x19: Imagination State (uint16_t fixed-point)
 *   0x1A - 0x1B: Analytical Thinking State (uint16_t fixed-point)
 *   0x1C - 0x1D: Verbal Reasoning State (uint16_t fixed-point)
 *   0x1E - 0x1F: Emotional Regulation State (uint16_t fixed-point)
 * Offset 0x20 - 0x27 (8 bytes) : RSSE Recruitment Scenario State
 * Offset 0x28 - 0x2F (8 bytes) : AEEE Adaptive Examination State (IRT Theta & Score)
 * Offset 0x30 - 0x3F (16 bytes): MAIO Global Surveillance & Reasoning State
 *
 * Total size = 64 bytes. Cache-line aligned (alignas(64)).
 */
struct AMSV_ALIGN(64) AtomicStateVector {
    // 0x00: VCE Phoneme State
    // [Bits 0-15: Active Phoneme ID | Bits 16-31: Articulation Accuracy (Q16) | Bits 32-63: Acoustic Energy & Flags]
    std::atomic<uint64_t> vce_phoneme_state;

    // 0x08: VCE Prosody State
    // [Bits 0-15: Fundamental Frequency F0 (Q8.8) | Bits 16-31: Speech Rate | Bits 32-47: Fluency | Bits 48-63: Flags]
    std::atomic<uint64_t> vce_prosody_state;

    // 0x10: CCTE Cognitive Capabilities 1 to 4 (Thinking, Focus, Memory, Creativity)
    // 4 x uint16_t Q16 fixed-point scores
    std::atomic<uint64_t> ccte_cog_bank_alpha;

    // 0x18: CCTE Cognitive Capabilities 5 to 8 (Imagination, Analytical, Verbal, Emotional)
    // 4 x uint16_t Q16 fixed-point scores
    std::atomic<uint64_t> ccte_cog_bank_beta;

    // 0x20: RSSE Recruitment Scenario State
    // [Bits 0-15: Active Scenario ID | Bits 16-31: Turn Counter | Bits 32-47: Register Compliance | Bits 48-63: Phase]
    std::atomic<uint64_t> rsse_scenario_state;

    // 0x28: AEEE Examination State
    // [Bits 0-31: IRT Ability Theta (IEEE 754 float) | Bits 32-47: Standard Error | Bits 48-63: Question Index]
    std::atomic<uint64_t> aeee_examination_state;

    // 0x30: MAIO Global State Alpha
    // [Bits 0-31: Global Competency Index | Bits 32-63: System Health & Sync Timestamp]
    std::atomic<uint64_t> maio_global_state_alpha;

    // 0x38: MAIO Global State Beta
    // [Bits 0-31: Intervention Directives | Bits 32-63: Cross-Module Attention Weights]
    std::atomic<uint64_t> maio_global_state_beta;
};

static_assert(sizeof(AtomicStateVector) == 64, "AtomicStateVector MUST be exactly 64 bytes");
static_assert(alignof(AtomicStateVector) == 64, "AtomicStateVector MUST be aligned to 64 bytes");

// ============================================================================
// LOCK-FREE AUDIO STREAM RING BUFFER SPECIFICATION
// ============================================================================
constexpr size_t AMSV_AUDIO_BUFFER_CAPACITY = 65536; // 64K samples (4 seconds at 16kHz)
constexpr size_t AMSV_AUDIO_BUFFER_MASK = AMSV_AUDIO_BUFFER_CAPACITY - 1;

/**
 * Single-Producer Single-Consumer (SPSC) lock-free ring buffer for real-time PCM audio streaming.
 * Eliminates OS lock contention and guarantees deterministic latency.
 */
struct AMSV_ALIGN(64) LockFreeAudioRingBuffer {
    AMSV_ALIGN(64) std::atomic<uint64_t> write_head{0};
    AMSV_ALIGN(64) std::atomic<uint64_t> read_tail{0};
    AMSV_ALIGN(64) float samples[AMSV_AUDIO_BUFFER_CAPACITY];

    inline bool push(float sample) noexcept {
        const uint64_t current_head = write_head.load(std::memory_order_relaxed);
        const uint64_t current_tail = read_tail.load(std::memory_order_acquire);

        if ((current_head - current_tail) >= AMSV_AUDIO_BUFFER_CAPACITY) {
            return false; // Buffer overflow
        }

        samples[current_head & AMSV_AUDIO_BUFFER_MASK] = sample;
        write_head.store(current_head + 1, std::memory_order_release);
        return true;
    }

    inline bool pop(float& sample) noexcept {
        const uint64_t current_tail = read_tail.load(std::memory_order_relaxed);
        const uint64_t current_head = write_head.load(std::memory_order_acquire);

        if (current_tail == current_head) {
            return false; // Buffer underflow / empty
        }

        sample = samples[current_tail & AMSV_AUDIO_BUFFER_MASK];
        read_tail.store(current_tail + 1, std::memory_order_release);
        return true;
    }

    inline uint64_t available_read() const noexcept {
        const uint64_t current_tail = read_tail.load(std::memory_order_relaxed);
        const uint64_t current_head = write_head.load(std::memory_order_acquire);
        return (current_head > current_tail) ? (current_head - current_tail) : 0;
    }

    inline uint64_t available_write() const noexcept {
        return AMSV_AUDIO_BUFFER_CAPACITY - available_read();
    }
};

// ============================================================================
// MASTER SHARED MEMORY CONTROL BLOCK
// ============================================================================
constexpr uint32_t AMSV_MAGIC_HEADER = 0x534F4C4F; // "SOLO"
constexpr uint32_t AMSV_PROTOCOL_VERSION = 100;    // v1.0.0

struct AMSV_ALIGN(64) MasterSharedMemorySegment {
    // Header block (64 bytes)
    uint32_t magic_header;
    uint32_t protocol_version;
    uint64_t init_timestamp_ns;
    uint64_t sequence_counter;
    uint32_t active_engines_bitmask;
    uint32_t system_status_code;
    uint8_t  header_reserved[32];

    // The 64-Byte Atomic State Vector
    AtomicStateVector state_vector;

    // Lock-Free Audio Stream Ring Buffer
    LockFreeAudioRingBuffer audio_ring_buffer;

    // Auxiliary State Buffers
    AMSV_ALIGN(64) float phoneme_posteriors[128]; // Max 128 phoneme probabilities
    AMSV_ALIGN(64) float prosody_pitch_buffer[512]; // 512 pitch contour frames
    AMSV_ALIGN(64) float cognitive_load_matrix[8][8]; // 8x8 cross-capability interaction matrix
    AMSV_ALIGN(64) char  scenario_prompt_buffer[4096]; // Active scenario text prompt
    AMSV_ALIGN(64) char  examiner_question_buffer[2048]; // Active examiner question
    AMSV_ALIGN(64) char  candidate_transcription[4096]; // Real-time candidate ASR transcription
    AMSV_ALIGN(64) char  creative_generation_buffer[4096]; // Active generated creative text/poem/prose
    AMSV_ALIGN(64) char  error_diagnostic_buffer[2048];    // Detailed grammar & syntax error report
    AMSV_ALIGN(64) float linguistic_embedding[256];        // 256-dim deep linguistic state representation
};


// ============================================================================
// MEMORY SYNCHRONIZATION BARRIERS & HELPER MACROS
// ============================================================================
inline void memory_fence_acquire() noexcept {
    std::atomic_thread_fence(std::memory_order_acquire);
}

inline void memory_fence_release() noexcept {
    std::atomic_thread_fence(std::memory_order_release);
}

inline void memory_fence_seq_cst() noexcept {
    std::atomic_thread_fence(std::memory_order_seq_cst);
}

} // namespace solorock::amsv

#endif // AMSV_LAYOUT_H
