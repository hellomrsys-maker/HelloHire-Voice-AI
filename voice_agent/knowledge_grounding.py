"""
voice_agent/knowledge_grounding.py - Free Knowledge Grounding Engine via Wikipedia REST API.

Enriches candidate evaluation and grammatical recruiter dialogue generation
by retrieving factual summaries for engineering concepts, architectures, and protocols
from Wikipedia's open REST API (free, zero API key required).
"""

from __future__ import annotations
import urllib.request
import urllib.parse
import json
import re
from typing import Optional, Dict, Any, List

# In-memory LRU cache for 0ms repeated entity lookups
_KNOWLEDGE_CACHE: Dict[str, Dict[str, Any]] = {}

# Common technical term mappings to canonical Wikipedia page titles
CONCEPT_CANONICAL_MAP: Dict[str, str] = {
    "rdma": "Remote_direct_memory_access",
    "kernel bypass": "Kernel_bypass",
    "raft": "Raft_(algorithm)",
    "consensus": "Consensus_(computer_science)",
    "paxos": "Paxos_(computer_science)",
    "vector clock": "Vector_clock",
    "vector clocks": "Vector_clock",
    "zero copy": "Zero-copy",
    "zero-copy": "Zero-copy",
    "kafka": "Apache_Kafka",
    "redis": "Redis",
    "kubernetes": "Kubernetes",
    "k8s": "Kubernetes",
    "docker": "Docker_(software)",
    "microservices": "Microservices",
    "pcie": "PCI_Express",
    "item response theory": "Item_response_theory",
    "transformer": "Transformer_(deep_learning_architecture)",
    "backpressure": "Backpressure",
    "concurrency": "Concurrency_(computer_science)",
    "star method": "Situation,_task,_action,_result",
    "star": "Situation,_task,_action,_result",
    "distributed systems": "Distributed_computing",
    "distributed architecture": "Distributed_computing",
    "sql": "SQL",
    "postgresql": "PostgreSQL",
    "rust": "Rust_(programming_language)",
    "c++": "C%2B%2B",
    "python": "Python_(programming_language)",
    "grpc": "GRPC",
    "graphql": "GraphQL"
}


def extract_technical_terms(text: str) -> List[str]:
    """Extracts candidate technical keywords from an utterance."""
    text_lower = text.lower()
    matched_terms = []

    for key in sorted(CONCEPT_CANONICAL_MAP.keys(), key=len, reverse=True):
        # Match whole words or phrases
        pattern = r"\b" + re.escape(key) + r"\b"
        if re.search(pattern, text_lower):
            matched_terms.append(key)

    return matched_terms


def fetch_wikipedia_summary(concept_key: str, timeout: float = 2.0) -> Optional[Dict[str, Any]]:
    """
    Fetches the page summary from Wikipedia's free REST API.
    Returns: { "title": str, "extract": str, "url": str, "concept": str }
    """
    canonical_title = CONCEPT_CANONICAL_MAP.get(concept_key.lower())
    if not canonical_title:
        # Fallback to capitalized title
        canonical_title = urllib.parse.quote(concept_key.replace(" ", "_").capitalize())

    if canonical_title in _KNOWLEDGE_CACHE:
        return _KNOWLEDGE_CACHE[canonical_title]

    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{canonical_title}"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "HelloHireVoiceAI/1.0 (Autonomous Recruiter AI; https://github.com/hellomrsys-maker/HelloHire-Voice-AI)",
            "Accept": "application/json"
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                result = {
                    "concept": concept_key,
                    "title": data.get("title", concept_key),
                    "extract": data.get("extract", ""),
                    "description": data.get("description", ""),
                    "url": data.get("content_urls", {}).get("desktop", {}).get("page", f"https://en.wikipedia.org/wiki/{canonical_title}")
                }
                _KNOWLEDGE_CACHE[canonical_title] = result
                return result
    except Exception as e:
        # Silently fail without impacting real-time pipeline latency
        return None

    return None


def fetch_duckduckgo_summary(query: str, timeout: float = 2.0) -> Optional[Dict[str, Any]]:
    """
    Fetches instant answers and abstract definitions from DuckDuckGo's free open API.
    Zero API key required.
    """
    encoded_query = urllib.parse.quote_plus(query)
    url = f"https://api.duckduckgo.com/?q={encoded_query}&format=json"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "HelloHireVoiceAI/1.0",
            "Accept": "application/json"
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                abstract = data.get("AbstractText") or data.get("Abstract")
                heading = data.get("Heading") or query
                if abstract:
                    return {
                        "concept": query,
                        "title": heading,
                        "extract": abstract,
                        "source": "DuckDuckGo",
                        "url": data.get("AbstractURL", f"https://duckduckgo.com/?q={encoded_query}")
                    }
    except Exception:
        pass
    return None


def ground_candidate_speech(text: str) -> Optional[Dict[str, Any]]:
    """
    Scans the candidate's speech for technical entities and returns the primary grounded concept
    from Wikipedia (Primary) or DuckDuckGo Instant Answer (Fallback).
    """
    terms = extract_technical_terms(text)
    if not terms:
        return None

    primary_term = terms[0]
    
    # 1. Primary: Wikipedia REST API
    wiki_res = fetch_wikipedia_summary(primary_term)
    if wiki_res and wiki_res.get("extract"):
        wiki_res["source"] = "Wikipedia"
        return wiki_res

    # 2. Fallback: DuckDuckGo Instant Answer API
    ddg_res = fetch_duckduckgo_summary(primary_term)
    if ddg_res:
        return ddg_res

    return wiki_res
