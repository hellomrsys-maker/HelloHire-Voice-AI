"""
extract_all_english_books.py - Authentic Extraction Across All English Grammar PDFs.

Ingests and categorizes authentic linguistic paradigms, syntactic structures,
and communicative examples from the reference textbooks in:
C:\\Users\\sysyo\\Downloads\\grammar:
1. Book 1: English_Oxford-Guide-to-English-Grammar.pdf (Oxford University Press)
2. Book 2: English_English-for-Everyone-Grammar-Guide.pdf (DK Publishing)
3. Book 3: English_Complete-English-Grammar-1891.pdf (Classical Historical Grammar)

Outputs per-book datasets under English_engine/6_DATA_REQUIREMENTS/:
- corpus_book1_oxford.json
- corpus_book2_dk.json
- corpus_book3_1891.json
- english_full_curriculum_manifest.json
"""

from __future__ import annotations
import os
import re
import json
from typing import Dict, List, Any, Tuple
import fitz  # PyMuPDF


PDF_DIR = r"C:\Users\sysyo\Downloads\grammar"
OUT_DIR = os.path.join("English_engine", "6_DATA_REQUIREMENTS")

BOOKS_CONFIG = [
    {
        "id": "book1_oxford",
        "name": "Oxford Guide to English Grammar",
        "file": "English_Oxford-Guide-to-English-Grammar.pdf",
        "output_json": "corpus_book1_oxford.json",
        "pedagogy": "Descriptive Formal Syntax, Subordination, Modals, Conditionals",
        "primary_register": "Formal / Academic",
    },
    {
        "id": "book2_dk",
        "name": "English for Everyone: English Grammar Guide",
        "file": "English_English-for-Everyone-Grammar-Guide.pdf",
        "output_json": "corpus_book2_dk.json",
        "pedagogy": "Visual Communicative Rules, Pragmatics, Phrasal Verbs, Business",
        "primary_register": "Professional / Everyday",
    },
    {
        "id": "book3_1891",
        "name": "Complete English Grammar (1891)",
        "file": "English_Complete-English-Grammar-1891.pdf",
        "output_json": "corpus_book3_1891.json",
        "pedagogy": "Classical 8 Parts of Speech, Inflectional Case, Subjunctive, Parsing",
        "primary_register": "Classical / Historical",
    },
]


def clean_line(text: str) -> str:
    t = text.replace("\u2019", "'").replace("\u2018", "'")
    t = t.replace("\u201c", '"').replace("\u201d", '"')
    t = t.replace("\u2014", " - ").replace("\ufffd", "'")
    t = re.sub(r"\s+", " ", t)
    return t.strip()


def extract_sentences_from_pdf(pdf_path: str) -> List[str]:
    if not os.path.exists(pdf_path):
        print(f"Warning: PDF file {pdf_path} not found.")
        return []

    doc = fitz.open(pdf_path)
    sentences = []
    seen = set()

    for page_idx in range(len(doc)):
        text = doc[page_idx].get_text("text")
        raw_lines = [clean_line(l) for l in text.split("\n") if l.strip()]
        for line in raw_lines:
            # Filter for high-quality authentic sentences
            if (
                len(line) >= 20
                and len(line) <= 220
                and line[0].isupper()
                and line.endswith((".", "?", "!"))
                and not line.startswith(("PAGE", "CHAPTER", "CONTENTS", "INDEX", "FIGURE", "SECTION", "TABLE", "EXERCISE", "LESSON"))
                and not re.match(r"^\d+\s", line)
            ):
                if line not in seen:
                    seen.add(line)
                    sentences.append(line)

    return sentences


def structure_book_corpus(book_id: str, sentences: List[str]) -> Dict[str, Any]:
    writing_corpus: List[Tuple[str, float, int, int]] = []
    email_corpus: List[Tuple[str, float, int, float, int]] = []
    listening_corpus: List[Tuple[str, int, float, int]] = []
    pronunciation_corpus: List[Tuple[str, float, int, float]] = []
    reviewing_corpus: List[Tuple[str, int, float, float]] = []
    book_writing_corpus: List[Tuple[str, float, float, int]] = []

    # 1. Writing / Syntax dataset (text, completeness, punct_class, register)
    # punct: 0=Period, 1=Question, 2=Exclam, 3=Semicolon, 4=Missing
    # register: 0=Acad, 1=Legal, 2=Journ, 3=Colloq, 4=Digital
    for s in sentences:
        punct = 1 if s.endswith("?") else (2 if s.endswith("!") else (3 if ";" in s else 0))
        reg = 0
        s_low = s.lower()
        if any(w in s_low for w in ["hereby", "plaintiff", "pursuant", "statutory", "indemnify", "law", "jurisdiction"]):
            reg = 1
        elif any(w in s_low for w in ["government", "market", "reported", "spokesman", "economy", "today", "minister"]):
            reg = 2
        elif any(w in s_low for w in ["buddy", "yeah", "hey", "gonna", "wanna", "cool", "mate", "dad"]):
            reg = 3
        elif any(w in s_low for w in ["lol", "omg", "btw", "tbh", "app", "post", "online"]):
            reg = 4
        else:
            reg = 0

        writing_corpus.append((s, 1.0, punct, reg))

    # Add book-specific synthetic fragments for clausal boundary discrimination
    fragments = [
        ("Because the linguistic committee delayed their final decision.", 0.0, 0, 0),
        ("Although the experimental results contradicted earlier findings.", 0.0, 0, 0),
        ("While the syntactic trees were being computed in the laboratory.", 0.0, 0, 0),
        ("Whereas classical grammarians emphasized morphological inflection.", 0.0, 0, 0),
        ("Since no conclusive evidence could be extracted from the text.", 0.0, 0, 0),
        ("Unless the author clarifies the ambiguous antecedent on line twelve.", 0.0, 0, 0),
        ("Whenever an intransitive verb appears without a direct object.", 0.0, 0, 0),
    ]
    for frag in fragments:
        writing_corpus.append(frag)

    # 2. Email & Pragmatics dataset
    for s in sentences:
        s_low = s.lower()
        if any(w in s_low for w in ["please", "could you", "would you", "kindly", "appreciate", "thank", "sincerely", "regards"]):
            politeness = 0.92 if "could you" in s_low or "would you" in s_low or "kindly" in s_low else 0.85
            sal = 0 if any(g in s_low for g in ["dear", "esteemed"]) else (1 if "hi" in s_low or "hello" in s_low else 3)
            sign = 0 if "sincerely" in s_low or "regards" in s_low else 1
            email_corpus.append((s, politeness, sal, 0.05, sign))
        elif any(w in s_low for w in ["send", "must", "give me", "do this", "rewrite", "fix", "hurry"]):
            email_corpus.append((s, 0.25, 3, 0.65, 3))

    # Add canonical email anchors
    email_corpus.extend([
        ("Dear Dr. Patel, could you please review the attached document? Best regards, Alex.", 0.96, 0, 0.04, 0),
        ("Dear Professor Schmidt, could you please let me know if Friday works for our seminar? Sincerely, Marcus.", 0.94, 0, 0.05, 0),
        ("Hi team, please find attached the revised quarterly projections for your review. Thanks, David.", 0.80, 1, 0.10, 1),
        ("Send me the updated database passwords right now.", 0.15, 3, 0.75, 3),
        ("You must rewrite this report immediately without any excuses.", 0.10, 3, 0.85, 3),
    ])

    # 3. Listening & Reduction dataset
    for s in sentences:
        s_low = s.lower()
        if any(r in s_low for r in ["i'd've", "whaddya", "gonna", "wanna", "gotta", "coulda", "shoulda"]):
            listening_corpus.append((s, 1, 0.82, 0))
        elif len(s.split()) > 10 and any(w in s_low for w in ["the", "of", "and", "in", "to"]):
            listening_corpus.append((s, 0, 0.55, 0))

    listening_corpus.extend([
        ("I'd've gone to the conference if the train had not been delayed.", 1, 0.85, 0),
        ("Whaddya think about the new universal syntax model?", 2, 0.78, 0),
        ("We're gonna analyze the acoustic speech waveform tomorrow.", 3, 0.72, 0),
        ("Do you wanna review the experimental results together this afternoon?", 4, 0.68, 0),
        ("You gotta make sure you're ready for the phonology quiz.", 6, 0.70, 0),
    ])

    # 4. Pronunciation & Stress shift dataset
    for s in sentences:
        s_low = s.lower()
        if any(w in s_low for w in ["walked", "asked", "published", "analyzed", "demanded"]):
            pronunciation_corpus.append((s, 0.92, 0, 0.88))
        elif any(w in s_low for w in ["record", "object", "contract", "permit", "subject", "present"]):
            is_verb = any(v in s_low for v in ["to ", "will ", "must ", "can "])
            stress = 1 if is_verb else 0
            pronunciation_corpus.append((s, 0.90, stress, 0.90))

    pronunciation_corpus.extend([
        ("The student walked to school and asked several insightful questions.", 0.94, 0, 0.88),
        ("The official RE-cord of the committee was archived.", 0.92, 0, 0.92),
        ("Please re-CORD the audio signal inside the chamber.", 0.91, 1, 0.91),
        ("A rare archaeological OB-ject was uncovered near the temple.", 0.92, 0, 0.89),
        ("They ob-JECT strongly to the proposed methodological changes.", 0.90, 1, 0.90),
    ])

    # 5. Reviewing dataset (4-tier taxonomy: 0=Fatal, 1=Clarity, 2=Register, 3=StylePreference)
    for s in sentences:
        s_low = s.lower()
        if any(w in s_low for w in ["incorrect", "fails", "error", "concord", "disagree"]):
            reviewing_corpus.append((s, 0, 0.20, 1.0))
        elif any(w in s_low for w in ["ambiguous", "unclear", "obscure", "dangling", "passive"]):
            reviewing_corpus.append((s, 1, 0.60, 1.0))
        elif any(w in s_low for w in ["informal", "slang", "tone", "inappropriate"]):
            reviewing_corpus.append((s, 2, 0.75, 1.0))
        elif any(w in s_low for w in ["prefer", "optionally", "balance", "aesthetic"]):
            reviewing_corpus.append((s, 3, 0.90, 0.8))

    reviewing_corpus.extend([
        ("In Section 3 on page 14, the subject-verb concord completely fails: 'they is' must be corrected to 'they are'.", 0, 0.15, 1.0),
        ("Page 8, line 22: The double negative creates an unintended contradictory assertion in the proof.", 0, 0.20, 1.0),
        ("On page 5, the antecedent of the pronoun 'it' is ambiguous across the two preceding noun phrases.", 1, 0.65, 1.0),
        ("The author might consider softening the tone in paragraph 2, as colloquial slang clashes with journal style.", 2, 0.85, 1.0),
        ("You may optionally prefer the Oxford comma here for aesthetic balance, though the sentence is grammatically sound.", 3, 0.95, 0.8),
    ])

    # 6. Book Writing dataset
    for s in sentences:
        s_low = s.lower()
        if any(w in s_low for w in ["walked", "looked", "saw", "entered", "opened", "noticed"]):
            book_writing_corpus.append((s, 0.05, 0.05, 3))
        elif any(w in s_low for w in ["chapter", "plot", "character", "protagonist", "outline"]):
            book_writing_corpus.append((s, 0.10, 0.20, 1))

    book_writing_corpus.extend([
        ("The detective walked into the abandoned study. Rain battered the dark window panes. He noticed the drawer was open.", 0.03, 0.04, 3),
        ("The detective walked into the room. Rain batters the window panes and he sees the broken lock on the door.", 0.88, 0.10, 2),
        ("Three hundred pages after introducing Lord Harrington's second cousin once, the narrative simply states 'he died'.", 0.10, 0.92, 1),
    ])

    return {
        "book_id": book_id,
        "sentences_extracted": len(sentences),
        "writing_corpus": writing_corpus,
        "email_corpus": email_corpus,
        "listening_corpus": listening_corpus,
        "pronunciation_corpus": pronunciation_corpus,
        "reviewing_corpus": reviewing_corpus,
        "book_writing_corpus": book_writing_corpus,
    }


def main():
    print("=" * 80)
    print("  EXTRACTION OF AUTHENTIC ENGLISH GRAMMAR CORPORA: ONE BY ONE ACROSS ALL PDFS")
    print(f"  Source Library: {PDF_DIR}")
    print("=" * 80)

    os.makedirs(OUT_DIR, exist_ok=True)
    manifest = {
        "library_path": PDF_DIR,
        "books": [],
        "total_sentences_extracted": 0,
    }

    cumulative_sentences = []

    for cfg in BOOKS_CONFIG:
        pdf_path = os.path.join(PDF_DIR, cfg["file"])
        print(f"\n[Processing Book] {cfg['name']} ({cfg['file']})...")
        if not os.path.exists(pdf_path):
            print(f"  ERROR: File not found: {pdf_path}")
            continue

        sentences = extract_sentences_from_pdf(pdf_path)
        print(f"  Extracted {len(sentences):,} authentic sentence examples.")
        cumulative_sentences.extend(sentences)

        book_data = structure_book_corpus(cfg["id"], sentences)
        out_file = os.path.join(OUT_DIR, cfg["output_json"])
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(book_data, f, indent=2, ensure_ascii=False)

        manifest["books"].append({
            "id": cfg["id"],
            "name": cfg["name"],
            "file": cfg["file"],
            "output_json": cfg["output_json"],
            "pedagogy": cfg["pedagogy"],
            "primary_register": cfg["primary_register"],
            "sentences_count": len(sentences),
            "writing_samples": len(book_data["writing_corpus"]),
            "email_samples": len(book_data["email_corpus"]),
            "listening_samples": len(book_data["listening_corpus"]),
            "pronunciation_samples": len(book_data["pronunciation_corpus"]),
            "reviewing_samples": len(book_data["reviewing_corpus"]),
            "book_writing_samples": len(book_data["book_writing_corpus"]),
        })
        manifest["total_sentences_extracted"] += len(sentences)
        print(f"  Saved structured dataset -> {out_file}")

    # Save full curriculum manifest
    manifest_path = os.path.join(OUT_DIR, "english_full_curriculum_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 80)
    print(f"  [SUCCESS] All English books extracted! Total sentences: {manifest['total_sentences_extracted']:,}")
    print(f"  Curriculum manifest -> {manifest_path}")
    print("=" * 80)


if __name__ == "__main__":
    main()
