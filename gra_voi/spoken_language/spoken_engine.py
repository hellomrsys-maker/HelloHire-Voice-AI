"""
Listening and Spoken Language Intelligence Engine.

Investigates the distinctive grammar of oral spoken communication:
  - Disfluency parsing: False starts, self-repairs, hesitation fillers
  - Spoken syntax constructions: Left-dislocation (heads), Right-dislocation (tails), Situational ellipsis
  - Discourse markers and pragmatic turn-taking signals
  - Real-time online incremental acoustic parsing and predictive grammar
  - Cross-linguistic spoken vs written register divergence.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import re


@dataclass
class SpokenDiscourseAnalysis:
    raw_transcript: str
    cleaned_canonical_syntax: str
    detected_disfluencies: List[Dict[str, Any]]
    discourse_markers: List[Dict[str, str]]
    spoken_grammatical_structures: List[Dict[str, str]]
    turn_taking_and_interactional_cues: List[str]
    online_incremental_parsing_steps: List[str]
    listening_comprehension_guidance: str


class SpokenLanguageEngine:
    """
    Analyzes oral spoken discourse, contrasting spoken grammar with written syntax,
    and coaching listeners on grammatical acoustic decoding.
    """

    def __init__(self):
        self._fillers = {"um", "uh", "er", "ah", "like", "you know", "i mean", "sort of", "kind of"}
        self._discourse_markers = {
            "well": "Framing Marker: Signals deliberation, qualification, or non-straightforward response.",
            "now": "Topic Initiator: Directs attention to a new conversational focus or sequential argument.",
            "anyway": "Topic Resumption: Terminates a digression and returns to the primary conversational thread.",
            "mind you": "Hedging / Qualification: Introduces an important caveat or concession.",
            "look": "Assertive Direct: Demands direct attention to a crucial perspective.",
            "so": "Summary / Consequential Marker: Prepares the interlocutor for a conclusion or question.",
            "actually": "Contrasting Marker: Corrects a prior assumption or presents surprising information."
        }

        self._cross_linguistic_spoken_registers = {
            "English": {
                "phenomena": "Situational ellipsis ('Heading out?', 'Sounds great'), Left-dislocation ('My uncle, he lives in Bristol'), Contractions ('gonna', 'wanna').",
                "listener_challenge": "Reduced vowel quality and elision require listeners to rely heavily on grammatical predictability rather than acoustic acoustic completeness."
            },
            "French": {
                "phenomena": "Obligatory dropping of negative particle 'ne' in spoken communication ('Je sais pas' instead of written 'Je ne sais pas'); dislocation and heavy use of 'on' for 'nous'.",
                "listener_challenge": "Listeners must identify negation solely from the postverbal marker 'pas' / 'rien'."
            },
            "Spanish": {
                "phenomena": "Pervasive clitic doubling ('A Juan lo vi ayer'), conversational pro-drop, and discourse tags ('¿vale?', '¿no?').",
                "listener_challenge": "Rapid syllable-timed articulation requires tracking agreement inflections on the verb rather than listening for subject pronouns."
            },
            "Japanese": {
                "phenomena": "Omission of case particles (が ga, を o) in casual speech, adoption of plain short forms, and reliance on sentence-final particles (ね ne, よ yo, さ sa) for pragmatic stance.",
                "listener_challenge": "Semantic roles must be inferred from context, word order, and intonational pitch accent rather than explicit particle markers."
            }
        }

    def analyze_spoken_discourse(self, transcript: str) -> SpokenDiscourseAnalysis:
        """
        Deconstruct a spoken transcript into its syntactic, disfluent, and discourse elements.
        """
        raw = transcript.strip()
        tokens = raw.split()

        detected_disfluencies: List[Dict[str, Any]] = []
        discourse_markers_found: List[Dict[str, str]] = []
        spoken_structures: List[Dict[str, str]] = []
        turn_cues: List[str] = []

        # 1. Detect fillers and hesitations (single-token and multi-token phrases)
        for filler in self._fillers:
            for match in re.finditer(rf"\b{re.escape(filler)}\b", raw, re.IGNORECASE):
                detected_disfluencies.append({
                    "token": match.group(0),
                    "position": match.start(),
                    "type": "Hesitation Filler / Filled Pause",
                    "function": "Holds conversational floor while cognitive lexical search or syntactic planning occurs."
                })

        # 2. Detect self-repair and false starts (e.g., "I went— I saw", "She had... she had been")
        if re.search(r"\b([a-z]+)\s+([a-z]+)—\s*\1\b", raw, re.I):
            detected_disfluencies.append({
                "token": "Repeated restart",
                "type": "Self-Repair / False Start",
                "function": "Speaker abandons initial syntactic trajectory and restarts to re-formulate grammatical structure."
            })

        # 3. Detect discourse markers
        for dm, explanation in self._discourse_markers.items():
            if re.search(rf"\b{dm}\b", raw, re.I):
                discourse_markers_found.append({
                    "marker": dm,
                    "pragmatic_function": explanation
                })

        # 4. Spoken grammatical structures: Left dislocation (heads) and Right dislocation (tails)
        # e.g., "that ancient manuscript, I studied it" or "my friend, he said"
        m_head = re.search(r"(?:^|,\s*)((?:that|this|my|the)?\s*[a-z\s]+),\s*(i|he|she|they|we)\s+([a-z]+)\s+(it|them|him|her)\b", raw, re.I)
        if not m_head:
            m_head = re.search(r"(?:^|,\s*)(my\s+[a-z]+|that\s+[a-z]+|[a-z]+),\s*(he|she|they|it)\s+([a-z]+)\b", raw, re.I)

        if m_head:
            spoken_structures.append({
                "construction": "Left-Dislocation / Topic Fronting ('Head')",
                "snippet": m_head.group(0).lstrip(", "),
                "syntactic_role": "Fronts the discourse topic to reduce listener processing load before the matrix proposition unfolds."
            })

        # Situational ellipsis: "Coffee?", "Seen John?", "Sounds good"
        if re.match(r"^(seen|heard|got|heading|sounds|looks|no)\b", raw, re.I):
            spoken_structures.append({
                "construction": "Situational Ellipsis",
                "snippet": raw,
                "syntactic_role": "Omission of subject pronoun and auxiliary verb when obvious from immediate physical context."
            })

        # 5. Cleaned canonical syntax reconstruction
        cleaned_syntax = raw
        for f in self._fillers:
            cleaned_syntax = re.sub(rf"\b{f}\b[,]?\s*", "", cleaned_syntax, flags=re.I)
        cleaned_syntax = re.sub(r"\s+", " ", cleaned_syntax).strip()
        if cleaned_syntax and not cleaned_syntax[-1] in ".?!":
            cleaned_syntax += "."
        cleaned_syntax = cleaned_syntax[0].upper() + cleaned_syntax[1:] if cleaned_syntax else ""

        # 6. Turn taking signals
        if raw.strip().endswith("?") or any(w in raw.lower() for w in ["right?", "you know?", "isn't it?"]):
            turn_cues.append("Turn-Yielding Signal: Interrogative tag or rising intonation prompts listener to take the conversational floor.")
        else:
            turn_cues.append("Floor-Holding / Collaborative Continuation: Sustained cadence maintains speaker authority.")

        # 7. Incremental parsing trace
        incremental_steps = [
            f"T1 (Acoustic Reception): Interlocutor parses incoming continuous acoustic waveform.",
            f"T2 (Disfluency Filtering): Filler tokens ({', '.join([d['token'] for d in detected_disfluencies]) if detected_disfluencies else 'None'}) are routed to pragmatic monitoring without stalling syntactic parsing.",
            f"T3 (Structural Prediction): First content word activates grammatical expectation frame.",
            f"T4 (Semantic Integration): Proposition is synthesized into active discourse memory."
        ]

        guidance = (
            "Listening Accuracy Strategy: Native listeners do not wait for a sentence to complete before comprehending. "
            "They deploy real-time predictive grammar to anticipate upcoming grammatical heads, using prosodic pauses "
            "and discourse markers as structural punctuation to filter out verbal repairs and extract the semantic core."
        )

        return SpokenDiscourseAnalysis(
            raw_transcript=raw,
            cleaned_canonical_syntax=cleaned_syntax,
            detected_disfluencies=detected_disfluencies,
            discourse_markers=discourse_markers_found,
            spoken_grammatical_structures=spoken_structures,
            turn_taking_and_interactional_cues=turn_cues,
            online_incremental_parsing_steps=incremental_steps,
            listening_comprehension_guidance=guidance
        )

    def get_cross_linguistic_spoken_profile(self, language: str) -> Dict[str, str]:
        """Return spoken vs written register dynamics for a specified language."""
        return self._cross_linguistic_spoken_registers.get(language, {
            "phenomena": "Spoken informal register displays reduced grammatical inflection and increased contextual ellipsis.",
            "listener_challenge": "Requires pragmatic inference and familiarity with connected speech reductions."
        })
