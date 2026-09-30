/**
 * @file amsv_core.cpp
 * @brief Core implementation of the Advanced Multi-language Shared Memory (AMSV) Manager.
 *
 * Implements OS-level shared memory segments (Windows FileMapping / POSIX shm),
 * initialization of the 64-byte Atomic Memory State Vector, and zero-bridge
 * memory access interfaces.
 */

#include "../include/amsv_layout.h"
#include <iostream>
#include <cstring>
#include <chrono>

#if defined(_WIN32)
    #include <windows.h>
#else
    #include <sys/mman.h>
    #include <sys/stat.h>
    #include <fcntl.h>
    #include <unistd.h>
#endif

namespace solorock::amsv {

class AMSVManager {
public:
    static constexpr const char* DEFAULT_SHM_NAME = "SoloRock_AMSV_SharedMemory";

    AMSVManager() : shared_segment_(nullptr), is_creator_(false) {}

    ~AMSVManager() {
        cleanup();
    }

    bool initialize(bool create_if_missing = true, size_t custom_size = sizeof(MasterSharedMemorySegment)) {
        size_t total_size = (custom_size < sizeof(MasterSharedMemorySegment)) ? sizeof(MasterSharedMemorySegment) : custom_size;

#if defined(_WIN32)
        // Windows Named Shared Memory Mapping
        HANDLE hMapFile = CreateFileMappingA(
            INVALID_HANDLE_VALUE,
            nullptr,
            PAGE_READWRITE,
            0,
            static_cast<DWORD>(total_size),
            DEFAULT_SHM_NAME
        );

        if (hMapFile == nullptr) {
            std::cerr << "[AMSV Core Error] CreateFileMapping failed: " << GetLastError() << "\n";
            return false;
        }

        is_creator_ = (GetLastError() != ERROR_ALREADY_EXISTS);

        void* pBuf = MapViewOfFile(
            hMapFile,
            FILE_MAP_ALL_ACCESS,
            0,
            0,
            total_size
        );

        if (pBuf == nullptr) {
            std::cerr << "[AMSV Core Error] MapViewOfFile failed: " << GetLastError() << "\n";
            CloseHandle(hMapFile);
            return false;
        }

        shared_segment_ = reinterpret_cast<MasterSharedMemorySegment*>(pBuf);
        handle_ = hMapFile;
#else
        // POSIX shm_open
        int shm_fd = shm_open(DEFAULT_SHM_NAME, O_CREAT | O_RDWR, 0666);
        if (shm_fd == -1) {
            std::cerr << "[AMSV Core Error] shm_open failed.\n";
            return false;
        }

        struct stat sb;
        fstat(shm_fd, &sb);
        is_creator_ = (sb.st_size == 0);

        if (is_creator_) {
            ftruncate(shm_fd, total_size);
        }

        void* pBuf = mmap(nullptr, total_size, PROT_READ | PROT_WRITE, MAP_SHARED, shm_fd, 0);
        if (pBuf == MAP_FAILED) {
            std::cerr << "[AMSV Core Error] mmap failed.\n";
            close(shm_fd);
            return false;
        }

        shared_segment_ = reinterpret_cast<MasterSharedMemorySegment*>(pBuf);
        shm_fd_ = shm_fd;
#endif

        if (is_creator_) {
            // Initialize Master Header
            std::memset(shared_segment_, 0, sizeof(MasterSharedMemorySegment));
            shared_segment_->magic_header = AMSV_MAGIC_HEADER;
            shared_segment_->protocol_version = AMSV_PROTOCOL_VERSION;
            shared_segment_->init_timestamp_ns = std::chrono::duration_cast<std::chrono::nanoseconds>(
                std::chrono::system_clock::now().time_since_epoch()
            ).count();
            shared_segment_->sequence_counter = 1;
            shared_segment_->active_engines_bitmask = 0x1F; // All 5 engines active
            shared_segment_->system_status_code = 200;       // OK

            std::cout << "[AMSV Core] Initialized new Master Shared Memory Segment ("
                      << sizeof(MasterSharedMemorySegment) << " bytes) at physical address: "
                      << static_cast<void*>(shared_segment_) << "\n";
            std::cout << "[AMSV Core] 64-Byte Atomic State Vector aligned at: "
                      << static_cast<void*>(&shared_segment_->state_vector) << "\n";
        } else {
            std::cout << "[AMSV Core] Attached to existing Master Shared Memory Segment at: "
                      << static_cast<void*>(shared_segment_) << "\n";
        }

        return true;
    }

    MasterSharedMemorySegment* get_segment() const noexcept {
        return shared_segment_;
    }

    AtomicStateVector* get_state_vector() const noexcept {
        return shared_segment_ ? &shared_segment_->state_vector : nullptr;
    }

    LockFreeAudioRingBuffer* get_audio_ring_buffer() const noexcept {
        return shared_segment_ ? &shared_segment_->audio_ring_buffer : nullptr;
    }

    void cleanup() {
        if (shared_segment_) {
#if defined(_WIN32)
            UnmapViewOfFile(shared_segment_);
            if (handle_) {
                CloseHandle(handle_);
                handle_ = nullptr;
            }
#else
            munmap(shared_segment_, sizeof(MasterSharedMemorySegment));
            if (shm_fd_ >= 0) {
                close(shm_fd_);
                shm_fd_ = -1;
            }
#endif
            shared_segment_ = nullptr;
        }
    }

private:
    MasterSharedMemorySegment* shared_segment_;
    bool is_creator_;
#if defined(_WIN32)
    HANDLE handle_{nullptr};
#else
    int shm_fd_{-1};
#endif
};

} // namespace solorock::amsv

// Standalone C entry points for FFI binding
extern "C" {
    void* amsv_get_master_segment() {
        static solorock::amsv::AMSVManager manager;
        if (!manager.get_segment()) {
            manager.initialize();
        }
        return manager.get_segment();
    }

    void* amsv_get_atomic_state_vector() {
        static solorock::amsv::AMSVManager manager;
        if (!manager.get_segment()) {
            manager.initialize();
        }
        return manager.get_state_vector();
    }

    void* amsv_get_audio_ring_buffer() {
        static solorock::amsv::AMSVManager manager;
        if (!manager.get_segment()) {
            manager.initialize();
        }
        return manager.get_audio_ring_buffer();
    }
}
