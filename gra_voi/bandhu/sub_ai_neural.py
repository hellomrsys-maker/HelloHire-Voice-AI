"""
sub_ai_neural.py - Production-Grade Neural Architectures for BandhuPrime Dedicated Sub-AIs.

Implements full Transformer-based deep neural sequence models with native UTF-8
multilingual tokenization, multi-head self-attention, and specialized task heads:
- UniversalSubwordTokenizer: Multilingual character & morpheme tokenizer covering 20 languages.
- B1: WritingSubAINeural (Transformer, Clause boundaries, Completeness, Punctuation, Register)
- B2: EmailSubAINeural (Transformer, Politeness score, Salutation levels, Pragmatic transfer)
- B3: ListeningSubAINeural (Transformer, Reduction-form expansion, Boundary entropy, Rhythm)
- B4: PronunciationSubAINeural (Transformer, Ending audibility, Stress shift, Tonal alignment)
- B5: ReviewingSubAINeural (Transformer, 4-Tier error taxonomy, Hedged language, Anchoring)
- B6: BookWritingSubAINeural (Transformer, Tense collision, Reference decay, 5-Stage editing)
"""

from __future__ import annotations
import os
import math
import re
import unicodedata
from typing import Any, Dict, List, Optional, Tuple, Union

import torch
import torch.nn as nn
import torch.nn.functional as F


# ============================================================================
# MULTILINGUAL VOCABULARY & UNIVERSAL TOKENIZER
# ============================================================================

class UniversalSubwordTokenizer:
    """
    Multilingual subword/character-level tokenizer covering all 20 target languages:
    Latin, Cyrillic, Arabic, Chinese, Japanese (Kanji/Kana), Korean (Hangul),
    Greek, Devanāgarī, Thai, Vietnamese, and Hebrew scripts.
    """
    PAD_TOKEN = "<PAD>"
    UNK_TOKEN = "<UNK>"
    BOS_TOKEN = "<BOS>"
    EOS_TOKEN = "<EOS>"
    SEP_TOKEN = "<SEP>"

    def __init__(self, vocab_size: int = 4096):
        self.vocab_size = vocab_size
        self.special_tokens = [self.PAD_TOKEN, self.UNK_TOKEN, self.BOS_TOKEN, self.EOS_TOKEN, self.SEP_TOKEN]
        self.token2id: Dict[str, int] = {tok: idx for idx, tok in enumerate(self.special_tokens)}
        self.id2token: Dict[int, str] = {idx: tok for idx, tok in enumerate(self.special_tokens)}

        # Populate base multilingual character set and grammatical morphemes
        self._build_vocab()

    def _build_vocab(self):
        # ASCII printable characters
        for c in range(32, 127):
            ch = chr(c)
            self._add_token(ch)

        # High-frequency linguistic morphemes & grammatical affixes
        grammatical_morphemes = [
            # English affixes
            "ing", "ed", "tion", "sion", "ness", "ment", "able", "ible", "ize", "ise",
            "un", "re", "dis", "pre", "post", "anti", "could", "would", "should", "have",
            # Email formulas
            "dear", "regards", "sincerely", "attached", "please", "request",
            # German affixes & particles
            "ung", "heit", "keit", "schaft", "sehr", "geehrte", "könnten", "bitte",
            # French affixes
            "ment", "ation", "ez", "ons", "ont", "chais", "pas", "cordialement",
            # Spanish affixes
            "mente", "ción", "ando", "iendo", "estimado", "atentamente",
            # Japanese particles & honorifics
            "は", "が", "を", "に", "で", "へ", "と", "から", "まで", "より", "て",
            "ます", "ました", "ません", "拝啓", "敬具", "貴社", "弊社", "よろしく",
            # Chinese aspect markers & particles
            "了", "过", "着", "的", "地", "得", "吗", "呢", "吧", "啊", "yyds",
            # Russian affixes & case markers
            "ость", "ение", "ать", "ить", "ого", "его", "ому", "ему",
            # Arabic roots & markers
            "كتب", "كتاب", "مكتب", "كاتب", "السلام", "عليكم", "ورحمة", "الله",
            # Ancient Sanskrit & Greek tokens
            "asti", "bhavati", "nama", "logos", "aorist", "samasa", "sandhi"
        ]
        for m in grammatical_morphemes:
            self._add_token(m)

    def _add_token(self, token: str):
        if token not in self.token2id and len(self.token2id) < self.vocab_size:
            idx = len(self.token2id)
            self.token2id[token] = idx
            self.id2token[idx] = token

    def tokenize(self, text: str) -> List[int]:
        """Converts raw text in any script into a sequence of token IDs."""
        tokens = [self.token2id[self.BOS_TOKEN]]
        normalized = unicodedata.normalize("NFC", text)

        words = re.findall(r"\w+|[^\w\s]", normalized, re.UNICODE)
        for w in words:
            if w in self.token2id:
                tokens.append(self.token2id[w])
            else:
                # Character-level fallback for out-of-vocabulary words
                for ch in w:
                    if ch in self.token2id:
                        tokens.append(self.token2id[ch])
                    else:
                        # Dynamic token hashing for rare Unicode codepoints
                        hashed_id = (hash(ch) % (self.vocab_size - 100)) + 100
                        tokens.append(hashed_id)
        tokens.append(self.token2id[self.EOS_TOKEN])
        return tokens

    def encode(self, texts: Union[str, List[str]], max_length: int = 128) -> Tuple[torch.Tensor, torch.Tensor]:
        """Encodes a single text or batch of texts into (input_ids, attention_mask) tensors."""
        if isinstance(texts, str):
            texts = [texts]

        batch_ids = []
        batch_masks = []

        for t in texts:
            toks = self.tokenize(t)
            if len(toks) > max_length:
                toks = toks[:max_length - 1] + [self.token2id[self.EOS_TOKEN]]
            mask = [1] * len(toks)

            # Padding
            padding_len = max_length - len(toks)
            toks = toks + [self.token2id[self.PAD_TOKEN]] * padding_len
            mask = mask + [0] * padding_len

            batch_ids.append(toks)
            batch_masks.append(mask)

        return torch.tensor(batch_ids, dtype=torch.long), torch.tensor(batch_masks, dtype=torch.long)


# ============================================================================
# POSITIONAL ENCODING & SHARED TRANSFORMER BACKBONE
# ============================================================================

class PositionalEncoding(nn.Module):
    def __init__(self, d_model: int, max_len: int = 512):
        super().__init__()
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        self.register_buffer("pe", pe.unsqueeze(0))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: [Batch, SeqLen, d_model]
        return x + self.pe[:, :x.size(1)]


class TransformerSequenceEncoder(nn.Module):
    """Deep bidirectional Transformer encoder for sub-AI linguistic modeling."""
    def __init__(self, vocab_size: int = 4096, d_model: int = 128, nhead: int = 4, num_layers: int = 3, dim_feedforward: int = 256):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, d_model, padding_idx=0)
        self.pos_encoder = PositionalEncoding(d_model)
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=dim_feedforward,
            dropout=0.1,
            activation="gelu",
            batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.norm = nn.LayerNorm(d_model)

    def forward(self, input_ids: torch.Tensor, attention_mask: Optional[torch.Tensor] = None) -> Tuple[torch.Tensor, torch.Tensor]:
        # input_ids: [Batch, SeqLen]
        h = self.embedding(input_ids)
        h = self.pos_encoder(h)

        key_padding_mask = (attention_mask == 0) if attention_mask is not None else None
        seq_features = self.transformer(h, src_key_padding_mask=key_padding_mask)
        seq_features = self.norm(seq_features)

        # Pooled representation (masked average over sequence)
        if attention_mask is not None:
            mask_exp = attention_mask.unsqueeze(-1).float()
            pooled = (seq_features * mask_exp).sum(dim=1) / (mask_exp.sum(dim=1) + 1e-9)
        else:
            pooled = seq_features.mean(dim=1)

        return seq_features, pooled


# ============================================================================
# B1: WRITING SUB-AI NEURAL MODEL
# ============================================================================

class WritingSubAINeural(nn.Module):
    """
    Dedicated Sub-AI Neural Architecture for Writing Skill.
    Predicts:
    1. Sentence completeness probability (subject + finite verb nexus)
    2. Clause boundaries (per-token coordinate and subordinate markers)
    3. Terminal punctuation classification
    4. Register formality index (0.0 to 1.0)
    """
    def __init__(self, vocab_size: int = 4096, d_model: int = 128):
        super().__init__()
        self.tokenizer = UniversalSubwordTokenizer(vocab_size=vocab_size)
        self.encoder = TransformerSequenceEncoder(vocab_size=vocab_size, d_model=d_model, num_layers=3)

        # Token-level clause boundary head: [None=0, Coord=1, Subord=2]
        self.clause_boundary_head = nn.Linear(d_model, 3)

        # Sentence-level heads
        self.completeness_head = nn.Sequential(
            nn.Linear(d_model, 64),
            nn.GELU(),
            nn.Linear(64, 1),
            nn.Sigmoid()
        )
        self.punctuation_head = nn.Linear(d_model, 5)  # [Period=0, Question=1, Exclamation=2, Semicolon=3, Missing=4]
        self.register_head = nn.Sequential(
            nn.Linear(d_model, 64),
            nn.GELU(),
            nn.Linear(64, 5)  # [Academic=0, Legal=1, Journalistic=2, Colloquial=3, Digital=4]
        )

    def forward(self, input_ids: torch.Tensor, attention_mask: Optional[torch.Tensor] = None) -> Dict[str, torch.Tensor]:
        seq_feats, pooled = self.encoder(input_ids, attention_mask)
        return {
            "token_clause_boundaries": self.clause_boundary_head(seq_feats),
            "sentence_completeness": self.completeness_head(pooled),
            "terminal_punctuation_logits": self.punctuation_head(pooled),
            "register_logits": self.register_head(pooled),
            "pooled_embedding": pooled
        }

    def analyze_text(self, text: str) -> Dict[str, Any]:
        self.eval()
        with torch.no_grad():
            input_ids, attention_mask = self.tokenizer.encode(text)
            out = self.forward(input_ids, attention_mask)
            completeness = out["sentence_completeness"].item()
            punct_class = out["terminal_punctuation_logits"].argmax(dim=-1).item()
            register_class = out["register_logits"].argmax(dim=-1).item()

            register_names = ["Academic", "Legal", "Journalistic", "Colloquial", "Digital"]
            punct_names = ["Period", "Question", "Exclamation", "Semicolon", "Missing"]

            fatal_errors = []
            clarity_errors = []
            subord_cues = ["because ", "although ", "while ", "whereas ", "since ", "unless ", "weil ", "bien que ", "a pesar de que "]
            text_lower = text.strip().lower()
            is_subord_fragment = any(text_lower.startswith(c) for c in subord_cues) and ("," not in text and ";" not in text)
            if completeness < 0.65 or is_subord_fragment:
                fatal_errors.append("Sentence fragment detected: Subject-finite verb nexus incomplete.")
            if punct_names[punct_class] == "Missing":
                clarity_errors.append("Missing terminal clause punctuation glyph.")

            return {
                "skill": "Writing",
                "sentence_completeness_score": round(completeness, 4),
                "terminal_punctuation": punct_names[punct_class],
                "detected_register": register_names[register_class],
                "structural_score": round(completeness if not clarity_errors else completeness * 0.8, 4),
                "fatal_errors": fatal_errors,
                "clarity_errors": clarity_errors,
                "recommended_stage": "CopyEdit" if not fatal_errors else "StructuralEdit"
            }


# ============================================================================
# B2: EMAIL SUB-AI NEURAL MODEL
# ============================================================================

class EmailSubAINeural(nn.Module):
    """
    Dedicated Sub-AI Neural Architecture for Email Skill.
    Predicts:
    1. Politeness Index score in [0, 1]
    2. Salutation appropriateness classification
    3. Negative pragmatic transfer friction probability
    4. Bullet list syntactic parallelism score
    """
    def __init__(self, vocab_size: int = 4096, d_model: int = 128):
        super().__init__()
        self.tokenizer = UniversalSubwordTokenizer(vocab_size=vocab_size)
        self.encoder = TransformerSequenceEncoder(vocab_size=vocab_size, d_model=d_model, num_layers=3)

        self.politeness_head = nn.Sequential(
            nn.Linear(d_model, 64),
            nn.GELU(),
            nn.Linear(64, 1),
            nn.Sigmoid()
        )
        self.salutation_head = nn.Linear(d_model, 4)  # [Formal=0, Professional=1, Casual=2, Missing=3]
        self.pragmatic_transfer_head = nn.Sequential(
            nn.Linear(d_model, 32),
            nn.GELU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
        self.signoff_head = nn.Linear(d_model, 4)     # [Formal=0, Professional=1, Casual=2, Missing=3]

    def forward(self, input_ids: torch.Tensor, attention_mask: Optional[torch.Tensor] = None) -> Dict[str, torch.Tensor]:
        _, pooled = self.encoder(input_ids, attention_mask)
        return {
            "politeness_score": self.politeness_head(pooled),
            "salutation_logits": self.salutation_head(pooled),
            "pragmatic_transfer_prob": self.pragmatic_transfer_head(pooled),
            "signoff_logits": self.signoff_head(pooled)
        }

    def analyze_text(self, email_text: str, target_culture: str = "Western") -> Dict[str, Any]:
        self.eval()
        with torch.no_grad():
            input_ids, attention_mask = self.tokenizer.encode(email_text)
            out = self.forward(input_ids, attention_mask)
            politeness = out["politeness_score"].item()
            salutation_idx = out["salutation_logits"].argmax(dim=-1).item()
            transfer_prob = out["pragmatic_transfer_prob"].item()

            sal_names = ["Formal", "Professional", "Casual", "Missing"]
            notes = []
            if sal_names[salutation_idx] == "Missing":
                notes.append("Email lacks conventional salutation greeting.")
            if politeness < 0.6:
                notes.append("Direct unhedged imperative detected; recommend conditional modal mitigation.")
            if target_culture.lower() in ("japanese", "korean") and transfer_prob > 0.4:
                notes.append("Pragmatic Transfer Warning: Requires negative conditional honorific machinery.")

            return {
                "skill": "Emailing",
                "politeness_index": round(politeness, 4),
                "salutation_level": sal_names[salutation_idx],
                "pragmatic_transfer_risk": round(transfer_prob, 4),
                "register_score": round(politeness, 4),
                "diagnostic_notes": notes
            }


# ============================================================================
# B3: LISTENING & ACOUSTIC SEGMENTATION SUB-AI NEURAL MODEL
# ============================================================================

class ListeningSubAINeural(nn.Module):
    """
    Dedicated Sub-AI Neural Architecture for Listening & Spoken Segmentation.
    Predicts:
    1. Spoken reduction-form expansion mappings (I'd've -> I would have, chais pas -> je ne sais pas)
    2. Acoustic word boundary transition entropy
    3. Speech rhythm typology classification (Stress-timed, Syllable-timed, Mora-timed)
    """
    def __init__(self, vocab_size: int = 4096, d_model: int = 128):
        super().__init__()
        self.tokenizer = UniversalSubwordTokenizer(vocab_size=vocab_size)
        self.encoder = TransformerSequenceEncoder(vocab_size=vocab_size, d_model=d_model, num_layers=3)

        self.reduction_head = nn.Linear(d_model, 16)  # 16 reduction classes
        self.boundary_entropy_head = nn.Sequential(
            nn.Linear(d_model, 32),
            nn.GELU(),
            nn.Linear(32, 1),
            nn.Softplus()
        )
        self.rhythm_head = nn.Linear(d_model, 3)      # [StressTimed=0, SyllableTimed=1, MoraTimed=2]

    def forward(self, input_ids: torch.Tensor, attention_mask: Optional[torch.Tensor] = None) -> Dict[str, torch.Tensor]:
        seq_feats, pooled = self.encoder(input_ids, attention_mask)
        return {
            "reduction_logits": self.reduction_head(pooled),
            "boundary_entropy": self.boundary_entropy_head(pooled),
            "rhythm_logits": self.rhythm_head(pooled)
        }

    def analyze_text(self, transcript: str) -> Dict[str, Any]:
        self.eval()
        with torch.no_grad():
            input_ids, attention_mask = self.tokenizer.encode(transcript)
            out = self.forward(input_ids, attention_mask)
            entropy = out["boundary_entropy"].item()
            rhythm_idx = out["rhythm_logits"].argmax(dim=-1).item()
            rhythm_types = ["StressTimed", "SyllableTimed", "MoraTimed"]

            return {
                "skill": "Listening",
                "segmentation_entropy": round(entropy, 4),
                "predicted_rhythm_typology": rhythm_types[rhythm_idx],
                "comprehension_salience": round(max(0.2, 1.0 - (entropy * 0.1)), 4)
            }


# ============================================================================
# B4: PRONUNCIATION SUB-AI NEURAL MODEL
# ============================================================================

class PronunciationSubAINeural(nn.Module):
    """
    Dedicated Sub-AI Neural Architecture for Pronunciation & Articulatory Phonology.
    Predicts:
    1. Word-final consonant cluster audibility score (audible past tense -ed, plural -s)
    2. Morphosyntactic stress shift classification (trochaic noun vs iambic verb)
    3. Tonal contour alignment score in [0, 1]
    """
    def __init__(self, vocab_size: int = 4096, d_model: int = 128):
        super().__init__()
        self.tokenizer = UniversalSubwordTokenizer(vocab_size=vocab_size)
        self.encoder = TransformerSequenceEncoder(vocab_size=vocab_size, d_model=d_model, num_layers=3)

        self.audibility_head = nn.Sequential(
            nn.Linear(d_model, 64),
            nn.GELU(),
            nn.Linear(64, 1),
            nn.Sigmoid()
        )
        self.stress_head = nn.Linear(d_model, 2)       # [TrochaicNoun=0, IambicVerb=1]
        self.tonal_head = nn.Sequential(
            nn.Linear(d_model, 32),
            nn.GELU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )

    def forward(self, input_ids: torch.Tensor, attention_mask: Optional[torch.Tensor] = None) -> Dict[str, torch.Tensor]:
        _, pooled = self.encoder(input_ids, attention_mask)
        return {
            "ending_audibility": self.audibility_head(pooled),
            "stress_logits": self.stress_head(pooled),
            "tonal_accuracy": self.tonal_head(pooled)
        }

    def analyze_text(self, word_or_sentence: str) -> Dict[str, Any]:
        self.eval()
        with torch.no_grad():
            input_ids, attention_mask = self.tokenizer.encode(word_or_sentence)
            out = self.forward(input_ids, attention_mask)
            audibility = out["ending_audibility"].item()
            stress_idx = out["stress_logits"].argmax(dim=-1).item()
            stress_names = ["Trochaic (Initial Stress - Noun)", "Iambic (Final Stress - Verb)"]

            return {
                "skill": "Pronouncing",
                "grammar_ending_audibility": round(audibility, 4),
                "predicted_stress_class": stress_names[stress_idx],
                "tonal_accuracy": round(out["tonal_accuracy"].item(), 4),
                "seven_step_correction_path": [
                    "Step 1: Minimal-pair acoustic perception discrimination.",
                    "Step 2: Explicit articulatory biomechanics modeling (tongue-alveolar contact).",
                    "Step 3: Slow-to-fast drill progression (phoneme -> word -> sentential frame).",
                    "Step 4: Recording and native spectrogram waveform alignment.",
                    "Step 5: Full-sentence rhythm shadowing matching clausal stress peaks.",
                    "Step 6: Daily dedicated oral reading aloud.",
                    "Step 7: Targeted single-pattern feedback loop."
                ]
            }


# ============================================================================
# B5: REVIEWING & VERIFICATION SUB-AI NEURAL MODEL
# ============================================================================

class ReviewingSubAINeural(nn.Module):
    """
    Dedicated Sub-AI Neural Architecture for Editorial Reviewing.
    Predicts:
    1. 4-Tier Error Taxonomy classification (Fatal, Clarity, Register, StylePreference)
    2. Professional modal hedging index in [0, 1]
    3. Location anchoring detection (verifying line/page citations)
    """
    def __init__(self, vocab_size: int = 4096, d_model: int = 128):
        super().__init__()
        self.tokenizer = UniversalSubwordTokenizer(vocab_size=vocab_size)
        self.encoder = TransformerSequenceEncoder(vocab_size=vocab_size, d_model=d_model, num_layers=3)

        self.error_taxonomy_head = nn.Linear(d_model, 4)  # [Fatal=0, Clarity=1, Register=2, Style=3]
        self.hedging_head = nn.Sequential(
            nn.Linear(d_model, 32),
            nn.GELU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
        self.anchored_head = nn.Sequential(
            nn.Linear(d_model, 32),
            nn.GELU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )

    def forward(self, input_ids: torch.Tensor, attention_mask: Optional[torch.Tensor] = None) -> Dict[str, torch.Tensor]:
        _, pooled = self.encoder(input_ids, attention_mask)
        return {
            "error_taxonomy_logits": self.error_taxonomy_head(pooled),
            "hedging_score": self.hedging_head(pooled),
            "is_anchored": self.anchored_head(pooled)
        }

    def analyze_text(self, critique_text: str) -> Dict[str, Any]:
        self.eval()
        with torch.no_grad():
            input_ids, attention_mask = self.tokenizer.encode(critique_text)
            out = self.forward(input_ids, attention_mask)
            tax_idx = out["error_taxonomy_logits"].argmax(dim=-1).item()
            tax_names = ["Fatal", "Clarity", "Register", "StylePreference"]
            hedging = out["hedging_score"].item()
            anchored = out["is_anchored"].item()

            return {
                "skill": "Reviewing",
                "dominant_error_tier": tax_names[tax_idx],
                "hedging_score": round(hedging, 4),
                "is_location_anchored": anchored > 0.5,
                "recommended_action": "Mandatory Rewrite" if tax_names[tax_idx] == "Fatal" else "Suggest Polish"
            }


# ============================================================================
# B6: BOOK WRITING SUB-AI NEURAL MODEL
# ============================================================================

class BookWritingSubAINeural(nn.Module):
    """
    Dedicated Sub-AI Neural Architecture for Book-Scale Writing.
    Predicts:
    1. Tense collision probability between narrative past and present
    2. Long-horizon reference decay probability (distant pronoun antecedents)
    3. 5-Stage Editorial Classification (Draft, Structural, Line, Copy, Proofread)
    """
    def __init__(self, vocab_size: int = 4096, d_model: int = 128):
        super().__init__()
        self.tokenizer = UniversalSubwordTokenizer(vocab_size=vocab_size)
        self.encoder = TransformerSequenceEncoder(vocab_size=vocab_size, d_model=d_model, num_layers=3)

        self.tense_collision_head = nn.Sequential(
            nn.Linear(d_model, 64),
            nn.GELU(),
            nn.Linear(64, 1),
            nn.Sigmoid()
        )
        self.reference_decay_head = nn.Sequential(
            nn.Linear(d_model, 64),
            nn.GELU(),
            nn.Linear(64, 1),
            nn.Sigmoid()
        )
        self.editing_stage_head = nn.Linear(d_model, 5)  # [Draft=0, Structural=1, Line=2, Copy=3, Proofread=4]

    def forward(self, input_ids: torch.Tensor, attention_mask: Optional[torch.Tensor] = None) -> Dict[str, torch.Tensor]:
        _, pooled = self.encoder(input_ids, attention_mask)
        return {
            "tense_collision_prob": self.tense_collision_head(pooled),
            "reference_decay_prob": self.reference_decay_head(pooled),
            "editing_stage_logits": self.editing_stage_head(pooled)
        }

    def analyze_text(self, manuscript_excerpt: str) -> Dict[str, Any]:
        self.eval()
        with torch.no_grad():
            input_ids, attention_mask = self.tokenizer.encode(manuscript_excerpt)
            out = self.forward(input_ids, attention_mask)
            tense_prob = out["tense_collision_prob"].item()
            decay_prob = out["reference_decay_prob"].item()
            stage_idx = out["editing_stage_logits"].argmax(dim=-1).item()
            stages = ["Draft", "StructuralEdit", "LineEdit", "CopyEdit", "Proofread"]

            return {
                "skill": "BookWriting",
                "tense_collision_risk": round(tense_prob, 4),
                "reference_decay_risk": round(decay_prob, 4),
                "current_editing_stage": stages[stage_idx],
                "consistency_score": round(max(0.1, 1.0 - (tense_prob * 0.5 + decay_prob * 0.3)), 4)
            }


# ============================================================================
# COMPOSITE DEDICATED SUB-AI CLUSTER & CHECKPOINT LOADER
# ============================================================================

class BandhuDedicatedSubAICluster:
    """
    Unified cluster manager for all dedicated Transformer Sub-AIs.
    Loads and manages trained weights across:
    - B1: WritingSubAINeural
    - B2: EmailSubAINeural
    - B3: ListeningSubAINeural
    - B4: PronunciationSubAINeural
    - B5: ReviewingSubAINeural
    - B6: BookWritingSubAINeural
    - B7: RecruitmentVerbalSubAINeural (RVCE / RSSE Verbal Matrix)
    """
    def __init__(self, checkpoint_path: Optional[str] = None):
        self.writing = WritingSubAINeural()
        self.email = EmailSubAINeural()
        self.listening = ListeningSubAINeural()
        self.pronunciation = PronunciationSubAINeural()
        self.reviewing = ReviewingSubAINeural()
        self.book_writing = BookWritingSubAINeural()
        self.recruitment_verbal = None
        try:
            from rsse.python.verbal_sub_ai_neural import RecruitmentVerbalSubAINeural
            self.recruitment_verbal = RecruitmentVerbalSubAINeural()
        except ImportError:
            pass

        self.is_trained = False

        if checkpoint_path and os.path.exists(checkpoint_path):
            self.load_checkpoints(checkpoint_path)

    def load_checkpoints(self, checkpoint_path: str) -> bool:
        try:
            bundle = torch.load(checkpoint_path, map_location="cpu", weights_only=True)
            if "writing" in bundle:
                self.writing.load_state_dict(bundle["writing"])
            if "email" in bundle:
                self.email.load_state_dict(bundle["email"])
            if "listening" in bundle:
                self.listening.load_state_dict(bundle["listening"])
            if "pronunciation" in bundle:
                self.pronunciation.load_state_dict(bundle["pronunciation"])
            if "reviewing" in bundle:
                self.reviewing.load_state_dict(bundle["reviewing"])
            if "book_writing" in bundle:
                self.book_writing.load_state_dict(bundle["book_writing"])
            if "recruitment_verbal" in bundle and self.recruitment_verbal is not None:
                self.recruitment_verbal.load_state_dict(bundle["recruitment_verbal"])
            self.is_trained = True
            return True
        except Exception as e:
            print(f"Warning: Could not load Sub-AI checkpoints: {e}")
            return False

    def dispatch(self, skill: str, text: str, **kwargs) -> Dict[str, Any]:
        skill_clean = skill.strip().lower()
        if "email" in skill_clean:
            return self.email.analyze_text(text, target_culture=kwargs.get("target_culture", "Western"))
        elif "listen" in skill_clean:
            return self.listening.analyze_text(text)
        elif "pronounc" in skill_clean:
            return self.pronunciation.analyze_text(text)
        elif "review" in skill_clean:
            return self.reviewing.analyze_text(text)
        elif "book" in skill_clean:
            return self.book_writing.analyze_text(text)
        elif "recruitment" in skill_clean or "verbal" in skill_clean:
            if self.recruitment_verbal is not None:
                return self.recruitment_verbal.analyze_verbal_response(
                    text, format_code=kwargs.get("format_code", 1), wpm=kwargs.get("wpm", 135.0)
                )
            return {"skill": "RecruitmentVerbal", "error": "RecruitmentVerbalSubAINeural not initialized"}
        else:
            return self.writing.analyze_text(text)


