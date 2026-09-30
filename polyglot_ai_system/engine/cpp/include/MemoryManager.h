// =============================================================================
// engine/cpp/include/MemoryManager.h
// Episodic, Semantic, and Working Memory Systems
// =============================================================================

#pragma once

#include "EngineCore.h"
#include <deque>
#include <unordered_map>
#include <vector>
#include <string>
#include <cstdint>
#include <optional>
#include <functional>

namespace engine {

// =============================================================================
// MemoryIndex — fast cosine-similarity retrieval over float embeddings
// =============================================================================

class MemoryIndex {
public:
    struct IndexedEntry {
        uint64_t             id;
        std::vector<float>   embedding;  ///< Normalized L2 unit vector
        std::string          payload;
    };

    explicit MemoryIndex(size_t max_entries, size_t embedding_dim);

    /// Inserts or replaces an entry. Embedding is L2-normalized internally.
    void upsert(uint64_t id, std::vector<float> embedding, std::string payload);

    /// Returns the top-k most similar entries by cosine similarity.
    std::vector<std::pair<uint64_t, float>> queryTopK(
        const std::vector<float>& query, size_t k) const;

    /// Removes an entry by id. Returns true if found.
    bool remove(uint64_t id);

    size_t size() const noexcept;
    size_t capacity() const noexcept;

private:
    size_t                     max_entries_;
    size_t                     embedding_dim_;
    std::vector<IndexedEntry>  entries_;
    mutable std::shared_mutex  mutex_;

    static void l2Normalize(std::vector<float>& v);
    static float cosineSim(const std::vector<float>& a, const std::vector<float>& b);
};

// =============================================================================
// WorkingMemory — bounded FIFO scratch pad for current task context
// =============================================================================

class WorkingMemory {
public:
    explicit WorkingMemory(size_t capacity_bytes);

    /// Writes a key-value entry. Evicts LRU entry if at capacity.
    void write(std::string key, std::string value);

    /// Reads a value by key. Returns nullopt if not found.
    std::optional<std::string> read(const std::string& key) const;

    /// Clears all working memory (e.g., at conversation reset).
    void clear();

    /// Returns all entries as a flat key-value map.
    std::unordered_map<std::string, std::string> snapshot() const;

    size_t sizeBytes() const noexcept;
    size_t capacityBytes() const noexcept;

private:
    size_t                                        capacity_bytes_;
    size_t                                        current_bytes_{0};
    std::deque<std::string>                       lru_order_;
    std::unordered_map<std::string, std::string>  store_;
    mutable std::mutex                            mutex_;
};

// =============================================================================
// EpisodicMemory — time-ordered event log for autobiographical context
// =============================================================================

class EpisodicMemory {
public:
    explicit EpisodicMemory(size_t max_slots, size_t embedding_dim);

    /**
     * @brief Records a new episodic event.
     * @param surface_text   The raw input that triggered this event.
     * @param meaning        The inferred natural meaning.
     * @param embedding      Dense vector embedding of the event (optional).
     */
    uint64_t record(
        std::string surface_text,
        std::string meaning,
        std::vector<float> embedding = {});

    /// Retrieves recent events (latest first).
    std::vector<MemoryEntry> getRecent(size_t n) const;

    /// Retrieves semantically similar events by embedding similarity.
    std::vector<MemoryEntry> queryByEmbedding(
        const std::vector<float>& query, size_t k) const;

    /// Retrieves events by keyword match.
    std::vector<MemoryEntry> queryByKeyword(
        const std::string& keyword, size_t max_results = 20) const;

    /// Marks an event as approved for long-term retention.
    void approve(uint64_t event_id);

    /// Removes non-approved events older than the given duration.
    size_t evictUnapproved(std::chrono::seconds max_age);

    size_t size() const noexcept;

private:
    size_t                         max_slots_;
    std::atomic<uint64_t>          next_id_{1};
    std::deque<MemoryEntry>        events_;          ///< Ordered newest-first
    MemoryIndex                    index_;
    mutable std::shared_mutex      mutex_;
};

// =============================================================================
// SemanticMemory — persistent concept graph for world knowledge
// =============================================================================

class SemanticMemory {
public:
    struct Concept {
        uint64_t             id;
        std::string          name;
        std::string          definition;
        std::vector<float>   embedding;
        std::vector<uint64_t> related_ids;   ///< Links to related concepts
        std::string          domain;          ///< e.g. "grammar", "world", "task"
        float                salience;
        bool                 approved;
    };

    explicit SemanticMemory(size_t max_slots, size_t embedding_dim);

    /// Inserts or updates a concept. Returns concept id.
    uint64_t upsertConcept(Concept concept);

    /// Looks up concept by name (exact match).
    std::optional<Concept> lookupByName(const std::string& name) const;

    /// Looks up top-k related concepts by embedding similarity.
    std::vector<Concept> querySimilar(
        const std::vector<float>& query, size_t k) const;

    /// Adds a typed relation between two concepts.
    void addRelation(uint64_t from_id, uint64_t to_id, std::string relation_type);

    /// Returns all concepts related to a given concept by relation type.
    std::vector<Concept> getRelated(uint64_t concept_id,
                                    const std::string& relation_type = "") const;

    size_t size() const noexcept;

private:
    size_t                                       max_slots_;
    std::atomic<uint64_t>                        next_id_{1};
    std::unordered_map<uint64_t, Concept>        concepts_;
    std::unordered_map<std::string, uint64_t>    name_index_;

    // Adjacency: from_id → [(to_id, relation_type)]
    std::unordered_map<uint64_t, std::vector<std::pair<uint64_t, std::string>>> edges_;

    MemoryIndex                                  embedding_index_;
    mutable std::shared_mutex                    mutex_;
};

// =============================================================================
// MemoryManager — unified facade over all memory subsystems
// =============================================================================

class MemoryManager {
public:
    explicit MemoryManager(const EngineConfig& config);

    // -------------------------------------------------------------------------
    // Working memory operations
    // -------------------------------------------------------------------------

    void   writeWorking(std::string key, std::string value);
    std::optional<std::string> readWorking(const std::string& key) const;
    void   clearWorking();

    // -------------------------------------------------------------------------
    // Episodic memory operations
    // -------------------------------------------------------------------------

    uint64_t recordEpisodicEvent(
        std::string surface_text,
        std::string meaning,
        std::vector<float> embedding = {});

    std::vector<MemoryEntry> getRecentEpisodes(size_t n) const;
    std::vector<MemoryEntry> queryEpisodicByEmbedding(
        const std::vector<float>& query, size_t k) const;
    std::vector<MemoryEntry> queryEpisodicByKeyword(
        const std::string& keyword, size_t max_results = 20) const;
    void approveEpisodicEvent(uint64_t event_id);

    // -------------------------------------------------------------------------
    // Semantic memory operations
    // -------------------------------------------------------------------------

    uint64_t upsertConcept(SemanticMemory::Concept concept);
    std::optional<SemanticMemory::Concept> lookupConcept(const std::string& name) const;
    std::vector<SemanticMemory::Concept> querySimilarConcepts(
        const std::vector<float>& query, size_t k) const;
    void addConceptRelation(uint64_t from_id, uint64_t to_id,
                            std::string relation_type);

    // -------------------------------------------------------------------------
    // Consolidated retrieval — fuses episodic + semantic results
    // -------------------------------------------------------------------------

    struct MemoryRecall {
        std::vector<MemoryEntry>          episodic_hits;
        std::vector<SemanticMemory::Concept> semantic_hits;
    };

    MemoryRecall recall(const std::vector<float>& query_embedding,
                        size_t k_episodic = 5,
                        size_t k_semantic = 5) const;

    // -------------------------------------------------------------------------
    // Diagnostics
    // -------------------------------------------------------------------------

    size_t workingSizeBytes()  const noexcept;
    size_t episodicEventCount() const noexcept;
    size_t semanticConceptCount() const noexcept;
    std::string dumpStats() const;

private:
    WorkingMemory   working_;
    EpisodicMemory  episodic_;
    SemanticMemory  semantic_;
};

} // namespace engine
