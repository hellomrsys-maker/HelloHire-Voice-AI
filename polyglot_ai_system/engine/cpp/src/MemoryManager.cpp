// =============================================================================
// engine/cpp/src/MemoryManager.cpp
// Full implementation of episodic, semantic, and working memory systems
// =============================================================================

#include "MemoryManager.h"

#include <algorithm>
#include <numeric>
#include <cmath>
#include <sstream>
#include <stdexcept>
#include <cassert>
#include <chrono>

namespace engine {

// =============================================================================
// MemoryIndex — vector similarity index
// =============================================================================

MemoryIndex::MemoryIndex(size_t max_entries, size_t embedding_dim)
    : max_entries_(max_entries)
    , embedding_dim_(embedding_dim)
{
    entries_.reserve(std::min(max_entries, size_t{65536}));
}

void MemoryIndex::l2Normalize(std::vector<float>& v) {
    float norm = 0.0f;
    for (float x : v) norm += x * x;
    norm = std::sqrt(norm);
    if (norm > 1e-9f) {
        for (float& x : v) x /= norm;
    }
}

float MemoryIndex::cosineSim(const std::vector<float>& a, const std::vector<float>& b) {
    assert(a.size() == b.size());
    float dot = 0.0f;
    for (size_t i = 0; i < a.size(); ++i) dot += a[i] * b[i];
    // Assumes both vectors are already L2-normalized
    return dot;
}

void MemoryIndex::upsert(uint64_t id, std::vector<float> embedding, std::string payload) {
    std::unique_lock lock(mutex_);

    if (embedding.size() != embedding_dim_ && !embedding.empty()) {
        throw std::invalid_argument("Embedding dimension mismatch in MemoryIndex::upsert");
    }
    if (!embedding.empty()) l2Normalize(embedding);

    // Check if id already exists and update
    for (auto& entry : entries_) {
        if (entry.id == id) {
            entry.embedding = std::move(embedding);
            entry.payload   = std::move(payload);
            return;
        }
    }

    // Evict oldest entry if at capacity
    if (entries_.size() >= max_entries_) {
        entries_.erase(entries_.begin()); // FIFO eviction
    }

    entries_.push_back({id, std::move(embedding), std::move(payload)});
}

std::vector<std::pair<uint64_t, float>> MemoryIndex::queryTopK(
    const std::vector<float>& query, size_t k) const
{
    std::shared_lock lock(mutex_);

    if (entries_.empty() || query.empty()) return {};

    auto norm_query = query;
    l2Normalize(norm_query);

    // Compute similarities
    std::vector<std::pair<float, uint64_t>> scored;
    scored.reserve(entries_.size());
    for (const auto& e : entries_) {
        if (e.embedding.size() != norm_query.size()) continue;
        float sim = cosineSim(norm_query, e.embedding);
        scored.emplace_back(sim, e.id);
    }

    // Partial sort to get top-k
    k = std::min(k, scored.size());
    std::partial_sort(scored.begin(), scored.begin() + static_cast<ptrdiff_t>(k),
                      scored.end(),
                      [](const auto& a, const auto& b) { return a.first > b.first; });
    scored.resize(k);

    std::vector<std::pair<uint64_t, float>> result;
    result.reserve(k);
    for (auto& [sim, id] : scored) result.emplace_back(id, sim);
    return result;
}

bool MemoryIndex::remove(uint64_t id) {
    std::unique_lock lock(mutex_);
    auto it = std::find_if(entries_.begin(), entries_.end(),
                           [id](const auto& e) { return e.id == id; });
    if (it == entries_.end()) return false;
    entries_.erase(it);
    return true;
}

size_t MemoryIndex::size() const noexcept {
    std::shared_lock lock(mutex_);
    return entries_.size();
}
size_t MemoryIndex::capacity() const noexcept { return max_entries_; }

// =============================================================================
// WorkingMemory
// =============================================================================

WorkingMemory::WorkingMemory(size_t capacity_bytes)
    : capacity_bytes_(capacity_bytes)
{}

void WorkingMemory::write(std::string key, std::string value) {
    std::unique_lock lock(mutex_);

    const size_t entry_bytes = key.size() + value.size() + 2;

    // Evict LRU entries until there is room
    while (current_bytes_ + entry_bytes > capacity_bytes_ && !lru_order_.empty()) {
        const auto& evict_key = lru_order_.front();
        auto it = store_.find(evict_key);
        if (it != store_.end()) {
            current_bytes_ -= evict_key.size() + it->second.size() + 2;
            store_.erase(it);
        }
        lru_order_.pop_front();
    }

    // Remove existing entry for this key (if any)
    auto existing = store_.find(key);
    if (existing != store_.end()) {
        current_bytes_ -= existing->first.size() + existing->second.size() + 2;
        store_.erase(existing);
        auto lru_it = std::find(lru_order_.begin(), lru_order_.end(), key);
        if (lru_it != lru_order_.end()) lru_order_.erase(lru_it);
    }

    store_.emplace(key, value);
    lru_order_.push_back(key);
    current_bytes_ += entry_bytes;
}

std::optional<std::string> WorkingMemory::read(const std::string& key) const {
    std::unique_lock lock(mutex_);
    auto it = store_.find(key);
    if (it == store_.end()) return std::nullopt;
    return it->second;
}

void WorkingMemory::clear() {
    std::unique_lock lock(mutex_);
    store_.clear();
    lru_order_.clear();
    current_bytes_ = 0;
}

std::unordered_map<std::string, std::string> WorkingMemory::snapshot() const {
    std::unique_lock lock(mutex_);
    return store_;
}

size_t WorkingMemory::sizeBytes()     const noexcept { return current_bytes_; }
size_t WorkingMemory::capacityBytes() const noexcept { return capacity_bytes_; }

// =============================================================================
// EpisodicMemory
// =============================================================================

EpisodicMemory::EpisodicMemory(size_t max_slots, size_t embedding_dim)
    : max_slots_(max_slots)
    , index_(max_slots, embedding_dim)
{}

uint64_t EpisodicMemory::record(
    std::string surface_text,
    std::string meaning,
    std::vector<float> embedding)
{
    std::unique_lock lock(mutex_);

    const uint64_t id = next_id_.fetch_add(1, std::memory_order_relaxed);
    const auto now    = std::chrono::system_clock::now();

    MemoryEntry entry{
        .id            = id,
        .content       = surface_text + " | " + meaning,
        .memory_type   = "episodic",
        .salience      = 1.0f,
        .created_at    = now,
        .last_accessed = now,
        .access_count  = 0,
        .approved      = false
    };

    // Evict oldest if at capacity
    if (events_.size() >= max_slots_) {
        events_.pop_back(); // Remove oldest (back of deque)
    }

    events_.push_front(std::move(entry)); // Newest first

    // Index embedding if provided
    if (!embedding.empty()) {
        lock.unlock(); // Unlock before calling index_ (it has its own lock)
        index_.upsert(id, std::move(embedding), surface_text);
    }

    return id;
}

std::vector<MemoryEntry> EpisodicMemory::getRecent(size_t n) const {
    std::shared_lock lock(mutex_);
    n = std::min(n, events_.size());
    return std::vector<MemoryEntry>(events_.begin(), events_.begin() + static_cast<ptrdiff_t>(n));
}

std::vector<MemoryEntry> EpisodicMemory::queryByEmbedding(
    const std::vector<float>& query, size_t k) const
{
    auto hits = index_.queryTopK(query, k);
    std::shared_lock lock(mutex_);

    std::vector<MemoryEntry> results;
    results.reserve(hits.size());
    for (auto& [id, sim] : hits) {
        for (auto& e : events_) {
            if (e.id == id) {
                results.push_back(e);
                break;
            }
        }
    }
    return results;
}

std::vector<MemoryEntry> EpisodicMemory::queryByKeyword(
    const std::string& keyword, size_t max_results) const
{
    std::shared_lock lock(mutex_);
    std::vector<MemoryEntry> results;
    for (const auto& e : events_) {
        if (e.content.find(keyword) != std::string::npos) {
            results.push_back(e);
            if (results.size() >= max_results) break;
        }
    }
    return results;
}

void EpisodicMemory::approve(uint64_t event_id) {
    std::unique_lock lock(mutex_);
    for (auto& e : events_) {
        if (e.id == event_id) {
            e.approved = true;
            return;
        }
    }
}

size_t EpisodicMemory::evictUnapproved(std::chrono::seconds max_age) {
    std::unique_lock lock(mutex_);
    const auto cutoff = std::chrono::system_clock::now() - max_age;
    size_t removed = 0;
    for (auto it = events_.begin(); it != events_.end(); ) {
        if (!it->approved && it->created_at < cutoff) {
            it = events_.erase(it);
            ++removed;
        } else {
            ++it;
        }
    }
    return removed;
}

size_t EpisodicMemory::size() const noexcept {
    std::shared_lock lock(mutex_);
    return events_.size();
}

// =============================================================================
// SemanticMemory
// =============================================================================

SemanticMemory::SemanticMemory(size_t max_slots, size_t embedding_dim)
    : max_slots_(max_slots)
    , embedding_index_(max_slots, embedding_dim)
{}

uint64_t SemanticMemory::upsertConcept(Concept concept) {
    std::unique_lock lock(mutex_);

    // If name already exists, update in-place
    auto name_it = name_index_.find(concept.name);
    if (name_it != name_index_.end()) {
        uint64_t existing_id = name_it->second;
        concept.id = existing_id;
        concepts_[existing_id] = concept;
        lock.unlock();
        if (!concept.embedding.empty()) {
            embedding_index_.upsert(existing_id, concept.embedding, concept.name);
        }
        return existing_id;
    }

    // New concept
    if (concepts_.size() >= max_slots_) {
        throw std::runtime_error("SemanticMemory at capacity");
    }

    const uint64_t id = next_id_.fetch_add(1, std::memory_order_relaxed);
    concept.id = id;
    name_index_[concept.name] = id;
    concepts_[id] = concept;

    lock.unlock();
    if (!concept.embedding.empty()) {
        embedding_index_.upsert(id, concept.embedding, concept.name);
    }
    return id;
}

std::optional<SemanticMemory::Concept> SemanticMemory::lookupByName(
    const std::string& name) const
{
    std::shared_lock lock(mutex_);
    auto it = name_index_.find(name);
    if (it == name_index_.end()) return std::nullopt;
    auto cit = concepts_.find(it->second);
    if (cit == concepts_.end()) return std::nullopt;
    return cit->second;
}

std::vector<SemanticMemory::Concept> SemanticMemory::querySimilar(
    const std::vector<float>& query, size_t k) const
{
    auto hits = embedding_index_.queryTopK(query, k);
    std::shared_lock lock(mutex_);
    std::vector<Concept> results;
    results.reserve(hits.size());
    for (auto& [id, sim] : hits) {
        auto it = concepts_.find(id);
        if (it != concepts_.end()) results.push_back(it->second);
    }
    return results;
}

void SemanticMemory::addRelation(uint64_t from_id, uint64_t to_id,
                                  std::string relation_type)
{
    std::unique_lock lock(mutex_);
    edges_[from_id].emplace_back(to_id, std::move(relation_type));
}

std::vector<SemanticMemory::Concept> SemanticMemory::getRelated(
    uint64_t concept_id, const std::string& relation_type) const
{
    std::shared_lock lock(mutex_);
    auto edge_it = edges_.find(concept_id);
    if (edge_it == edges_.end()) return {};

    std::vector<Concept> results;
    for (auto& [to_id, rel] : edge_it->second) {
        if (relation_type.empty() || rel == relation_type) {
            auto cit = concepts_.find(to_id);
            if (cit != concepts_.end()) results.push_back(cit->second);
        }
    }
    return results;
}

size_t SemanticMemory::size() const noexcept {
    std::shared_lock lock(mutex_);
    return concepts_.size();
}

// =============================================================================
// MemoryManager — unified facade
// =============================================================================

MemoryManager::MemoryManager(const EngineConfig& config)
    : working_ (config.working_memory_bytes)
    , episodic_(config.episodic_memory_slots, config.attention_dim)
    , semantic_(config.semantic_memory_slots, config.attention_dim)
{}

void MemoryManager::writeWorking(std::string key, std::string value) {
    working_.write(std::move(key), std::move(value));
}
std::optional<std::string> MemoryManager::readWorking(const std::string& key) const {
    return working_.read(key);
}
void MemoryManager::clearWorking() { working_.clear(); }

uint64_t MemoryManager::recordEpisodicEvent(
    std::string surface_text, std::string meaning, std::vector<float> embedding)
{
    return episodic_.record(std::move(surface_text), std::move(meaning),
                            std::move(embedding));
}

std::vector<MemoryEntry> MemoryManager::getRecentEpisodes(size_t n) const {
    return episodic_.getRecent(n);
}
std::vector<MemoryEntry> MemoryManager::queryEpisodicByEmbedding(
    const std::vector<float>& query, size_t k) const
{
    return episodic_.queryByEmbedding(query, k);
}
std::vector<MemoryEntry> MemoryManager::queryEpisodicByKeyword(
    const std::string& keyword, size_t max_results) const
{
    return episodic_.queryByKeyword(keyword, max_results);
}
void MemoryManager::approveEpisodicEvent(uint64_t event_id) {
    episodic_.approve(event_id);
}

uint64_t MemoryManager::upsertConcept(SemanticMemory::Concept concept) {
    return semantic_.upsertConcept(std::move(concept));
}
std::optional<SemanticMemory::Concept> MemoryManager::lookupConcept(
    const std::string& name) const
{
    return semantic_.lookupByName(name);
}
std::vector<SemanticMemory::Concept> MemoryManager::querySimilarConcepts(
    const std::vector<float>& query, size_t k) const
{
    return semantic_.querySimilar(query, k);
}
void MemoryManager::addConceptRelation(uint64_t from_id, uint64_t to_id,
                                       std::string relation_type)
{
    semantic_.addRelation(from_id, to_id, std::move(relation_type));
}

MemoryManager::MemoryRecall MemoryManager::recall(
    const std::vector<float>& query_embedding,
    size_t k_episodic, size_t k_semantic) const
{
    MemoryRecall result;
    result.episodic_hits = episodic_.queryByEmbedding(query_embedding, k_episodic);
    result.semantic_hits = semantic_.querySimilar(query_embedding, k_semantic);
    return result;
}

size_t MemoryManager::workingSizeBytes()   const noexcept { return working_.sizeBytes(); }
size_t MemoryManager::episodicEventCount() const noexcept { return episodic_.size(); }
size_t MemoryManager::semanticConceptCount() const noexcept { return semantic_.size(); }

std::string MemoryManager::dumpStats() const {
    std::ostringstream oss;
    oss << "MemoryManager{\n"
        << "  working_bytes=" << workingSizeBytes()
        << "/" << working_.capacityBytes() << "\n"
        << "  episodic_events=" << episodicEventCount() << "\n"
        << "  semantic_concepts=" << semanticConceptCount() << "\n"
        << "}";
    return oss.str();
}

} // namespace engine
