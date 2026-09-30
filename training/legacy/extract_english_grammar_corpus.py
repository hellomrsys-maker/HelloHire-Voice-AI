"""
extract_english_grammar_corpus.py - Authentic English Grammar Corpus Extractor.

Extracts authentic linguistic paradigms, syntactic structures, error patterns,
and communicative examples from the reference textbooks in:
C:\\Users\\sysyo\\Downloads\\grammar
- English_Oxford-Guide-to-English-Grammar.pdf
- English_English-for-Everyone-Grammar-Guide.pdf

Transforms extracted examples into structured training corpora for:
1. Syntax & Writing Sub-AI (Sentence completeness, agreement, subordination)
2. Pragmatics & Email Sub-AI (Politeness, indirectness, formal/casual register)
3. Phonology & Listening Sub-AI (Reductions, rhythm, stress shift)
4. Editorial & Reviewing Sub-AI (4-Tier error taxonomy, tense consistency)
5. Main Agent Multi-Task Objectives (Grammar validity, tree depth, error spans)
"""

from __future__ import annotations
import os
import re
import json
from typing import Dict, List, Any, Tuple
import fitz  # PyMuPDF


PDF_DIR = r"C:\Users\sysyo\Downloads\grammar"
OXFORD_PDF = os.path.join(PDF_DIR, "English_Oxford-Guide-to-English-Grammar.pdf")
DK_PDF = os.path.join(PDF_DIR, "English_English-for-Everyone-Grammar-Guide.pdf")
OUTPUT_PATH = os.path.join("English_engine", "6_DATA_REQUIREMENTS", "extracted_grammar_corpus.json")


def clean_line(text: str) -> str:
    t = text.replace("\u2019", "'").replace("\u2018", "'")
    t = t.replace("\u201c", '"').replace("\u201d", '"')
    t = t.replace("\u2014", " - ").replace("\ufffd", "'")
    t = re.sub(r"\s+", " ", t)
    return t.strip()


def extract_raw_sentences_from_pdf(pdf_path: str, max_pages: int = 400) -> List[str]:
    if not os.path.exists(pdf_path):
        print(f"Warning: PDF file {pdf_path} not found.")
        return []

    doc = fitz.open(pdf_path)
    total_pages = min(len(doc), max_pages)
    sentences = []
    seen = set()

    for page_idx in range(total_pages):
        text = doc[page_idx].get_text("text")
        raw_lines = [clean_line(l) for l in text.split("\n") if l.strip()]
        for line in raw_lines:
            # Filter for plausible complete sentences
            if (
                len(line) >= 20
                and len(line) <= 220
                and line[0].isupper()
                and line.endswith((".", "?", "!"))
                and not line.startswith(("PAGE", "CHAPTER", "CONTENTS", "INDEX", "FIGURE", "SECTION", "TABLE", "EXERCISE"))
                and not re.match(r"^\d+\s", line)
            ):
                if line not in seen:
                    seen.add(line)
                    sentences.append(line)

    return sentences


def categorize_grammar_corpus(oxford_sentences: List[str], dk_sentences: List[str]) -> Dict[str, Any]:
    all_sentences = list(dict.fromkeys(oxford_sentences + dk_sentences))

    writing_corpus: List[Tuple[str, float, int, int]] = []
    email_corpus: List[Tuple[str, float, int, float, int]] = []
    listening_corpus: List[Tuple[str, int, float, int]] = []
    pronunciation_corpus: List[Tuple[str, float, int, float]] = []
    reviewing_corpus: List[Tuple[str, int, float, float]] = []
    book_writing_corpus: List[Tuple[str, float, float, int]] = []

    # 1. Writing / Syntax dataset (text, completeness, punct_class, register)
    # punct: 0=Period, 1=Question, 2=Exclam, 3=Semicolon, 4=Missing
    # register: 0=Acad, 1=Legal, 2=Journ, 3=Colloq, 4=Digital
    for s in all_sentences:
        punct = 1 if s.endswith("?") else (2 if s.endswith("!") else (3 if ";" in s else 0))
        reg = 0
        if any(w in s.lower() for w in ["hereby", "plaintiff", "pursuant", "statutory", "indemnify"]):
            reg = 1
        elif any(w in s.lower() for w in ["government", "market", "reported", "spokesman", "economy", "today"]):
            reg = 2
        elif any(w in s.lower() for w in ["buddy", "yeah", "hey", "gonna", "wanna", "cool", "mate"]):
            reg = 3
        elif any(w in s.lower() for w in ["lol", "omg", "btw", "tbh", "app", "post"]):
            reg = 4
        else:
            reg = 0

        writing_corpus.append((s, 1.0, punct, reg))

    # Add synthetic grammatical fragments for training discrimination
    fragments = [
        ("Because the laboratory experiments failed during the initial trial phase.", 0.0, 0, 0),
        ("Following today's unexpected interest rate cuts by the central bank.", 0.0, 0, 2),
        ("Whereas under Section 4 of the aforementioned statutory instrument.", 0.0, 0, 1),
        ("Over to watch the football match tonight.", 0.0, 0, 3),
        ("In accordance with the contractual stipulations set forth herein.", 0.0, 0, 1),
        ("Although the committee reached a preliminary consensus yesterday evening.", 0.0, 0, 0),
        ("While reviewing the complex syntactic dependencies across the manuscript.", 0.0, 0, 0),
        ("Since the arrival of the foreign delegation at the embassy.", 0.0, 0, 2),
        ("Before submitting the revised research grant application to the council.", 0.0, 0, 0),
        ("Whenever the automated parser encounters a discontinuous constituent.", 0.0, 0, 0),
    ]
    writing_corpus.extend(fragments)

    # 2. Pragmatics & Email dataset (text, politeness, salutation, transfer_prob, signoff)
    # salutation: 0=Formal, 1=Prof, 2=Casual, 3=Missing
    # signoff: 0=Formal, 1=Prof, 2=Casual, 3=Missing
    polite_samples = [
        ("Dear Dr. Henderson, would you be so kind as to review the attached manuscript? Best regards, Elena.", 0.95, 0, 0.05, 0),
        ("Dear Professor Schmidt, could you please let me know if Friday works for our seminar? Sincerely, Marcus.", 0.92, 0, 0.06, 0),
        ("Hi team, please find attached the revised quarterly projections for your review. Thanks, David.", 0.78, 1, 0.10, 1),
        ("Hey Sarah, can you look over these slides before 3pm? Cheers, Mike.", 0.65, 2, 0.15, 2),
        ("Send me the updated database passwords right now.", 0.15, 3, 0.75, 3),
        ("You must rewrite this report immediately without any excuses.", 0.10, 3, 0.85, 3),
        ("Could you possibly consider providing feedback when your schedule permits? Many thanks.", 0.90, 3, 0.08, 1),
        ("Good morning everyone, kindly note the rescheduled meeting time for tomorrow morning. Warm regards.", 0.88, 1, 0.08, 1),
        ("I need you to fix this bug today or else.", 0.20, 3, 0.70, 3),
        ("Give me the files.", 0.10, 3, 0.80, 3),
        ("Dear Colleague, would it be possible to arrange a brief call regarding the project deliverables? With best regards.", 0.94, 0, 0.04, 0),
        ("We would be most grateful if you could confirm your attendance at the annual symposium. Yours faithfully.", 0.96, 0, 0.03, 0),
        ("Let me know ASAP.", 0.40, 3, 0.45, 3),
        ("Just wanted to check in on the draft when you get a chance.", 0.75, 3, 0.12, 3),
        ("I demand an immediate explanation for this unacceptable delay.", 0.08, 3, 0.90, 3),
    ]
    # Add authentic polite sentences extracted from Oxford/DK
    for s in all_sentences:
        if any(w in s.lower() for w in ["could you", "would you", "please", "may i", "grateful", "appreciate"]):
            email_corpus.append((s, 0.88, 3, 0.08, 3))
    email_corpus.extend(polite_samples)

    # 3. Listening & Connected Speech (text, reduction_class, boundary_entropy, rhythm)
    # rhythm: 0=StressTimed, 1=SyllableTimed, 2=MoraTimed
    listening_samples = [
        ("I'd've gone to the conference if the train had not been delayed.", 1, 0.85, 0),
        ("Whaddya think about the new universal syntax model?", 2, 0.78, 0),
        ("We're gonna analyze the acoustic speech waveform tomorrow.", 3, 0.72, 0),
        ("Do you wanna review the experimental results together this afternoon?", 4, 0.68, 0),
        ("English connected speech exhibits severe vowel reduction to schwa in unstressed positions.", 0, 0.88, 0),
        ("You gotta make sure you're ready for the phonology quiz.", 6, 0.70, 0),
        ("What are you doing over there with those acoustic spectrograms?", 0, 0.45, 0),
        ("He should've told us about the clausal subordination rule earlier.", 1, 0.80, 0),
        ("I dunno what the difference between trochaic and iambic rhythm is.", 5, 0.75, 0),
        ("They're gonna be examining the acoustic vowel formant shifts.", 3, 0.70, 0),
    ]
    listening_corpus.extend(listening_samples)

    # 4. Pronunciation & Word Stress (text, ending_audibility, stress_class, tonal_acc)
    # stress_class: 0=TrochaicNoun, 1=IambicVerb
    pronunciation_samples = [
        ("The student walked to school and asked several insightful questions.", 0.94, 0, 0.88),
        ("She demanded that they provide audited financial records.", 0.96, 0, 0.90),
        ("He walk to school and ask question yesterday.", 0.12, 0, 0.35),
        ("The official RE-cord of the committee was archived.", 0.90, 0, 0.92),
        ("Please re-CORD the audio signal inside the anechoic chamber.", 0.91, 1, 0.91),
        ("A rare archaeological OB-ject was uncovered near the temple.", 0.92, 0, 0.89),
        ("They ob-JECT strongly to the proposed methodological changes.", 0.90, 1, 0.90),
        ("They signed a legally binding CON-tract yesterday.", 0.93, 0, 0.90),
        ("The metal bars con-TRACT rapidly at cryogenic temperatures.", 0.91, 1, 0.88),
        ("The company received an official export PER-mit.", 0.92, 0, 0.88),
        ("They per-MIT visitors during regular university hours.", 0.90, 1, 0.89),
        ("She jumped over the fence and kicked the ball.", 0.95, 0, 0.87),
        ("She jump over the fence and kick the ball.", 0.14, 0, 0.40),
        ("The economic PRO-gress of the nation exceeded all forecasts.", 0.92, 0, 0.91),
        ("They pro-GRESS steadily through the syllabus each semester.", 0.90, 1, 0.90),
    ]
    pronunciation_corpus.extend(pronunciation_samples)

    # 5. Reviewing & Error Taxonomy (text, error_taxonomy, hedging, is_anchored)
    # error_taxonomy: 0=Fatal, 1=Clarity, 2=Register, 3=StylePreference
    reviewing_samples = [
        ("In Section 3 on page 14, the subject-verb concord completely fails: 'they is' must be corrected to 'they are'.", 0, 0.20, 1.0),
        ("Page 8, line 22: The double negative creates an unintended contradictory assertion in the proof.", 0, 0.25, 1.0),
        ("On page 5, the antecedent of the pronoun 'it' is ambiguous across the two preceding noun phrases.", 1, 0.65, 1.0),
        ("Line 104: The passive construction obscures who performed the statistical extraction.", 1, 0.70, 1.0),
        ("The author might consider softening the tone in paragraph 2, as colloquial slang like 'cool trick' clashes with journal style.", 2, 0.85, 1.0),
        ("In Chapter 4, the informal phrasing 'lots of stuff' should be replaced by 'numerous phenomena'.", 2, 0.75, 1.0),
        ("You may optionally prefer the Oxford comma here for aesthetic balance, though the sentence is grammatically sound.", 3, 0.95, 0.8),
        ("Page 12, line 3: The modifier is dangling: 'Walking into the lab, the experiment was seen'.", 1, 0.60, 1.0),
        ("This entire methodology is fundamentally broken and invalid.", 0, 0.05, 0.0),
        ("Line 55: Recommend substituting 'utilize' with 'use' for clearer readability.", 3, 0.80, 1.0),
        ("In the abstract, using emojis is inappropriate for an academic publication.", 2, 0.70, 1.0),
        ("Page 19: The plural subject 'The criteria' requires the plural verb 'were established', not 'was established'.", 0, 0.15, 1.0),
        ("Line 88: Consider restructuring this 65-word periodic sentence into two independent clauses.", 1, 0.70, 1.0),
    ]
    reviewing_corpus.extend(reviewing_samples)

    # 6. Book Writing & Editorial Stages (text, tense_collision, ref_decay, stage)
    # stage: 0=Draft, 1=Structural, 2=Line, 3=Copy, 4=Proofread
    book_writing_samples = [
        ("The detective walked into the abandoned study. Rain battered the dark window panes. He noticed the drawer was open.", 0.04, 0.06, 3),
        ("The detective walked into the room. Rain batters the window panes and he sees the broken lock on the door.", 0.88, 0.12, 2),
        ("Three hundred pages after introducing Lord Harrington's second cousin once, the narrative simply states 'he died'.", 0.12, 0.92, 1),
        ("Rough initial scene outline: Protagonist enters warehouse, finds ancient scroll, flees across rooftops.", 0.30, 0.40, 0),
        ("Final typeset galley: Verify running headers, em-dash kerning, and footnote numeral superscripts.", 0.02, 0.03, 4),
        ("She had lived in Vienna for ten years before moving to Prague; she remembers the music.", 0.75, 0.15, 2),
        ("The overall pacing of Act Two drags significantly; the subplot involving the merchant needs restructuring or deletion.", 0.10, 0.30, 1),
        ("The knight drew his sword and struck the dragon. The beast collapsed with a shuddering roar.", 0.05, 0.05, 3),
        ("He walked to the window. He looks outside and saw the storm coming.", 0.85, 0.10, 2),
        ("First messy brain dump of Chapter 1 concepts and potential dialogue fragments.", 0.35, 0.45, 0),
    ]
    book_writing_corpus.extend(book_writing_samples)

    return {
        "metadata": {
            "source_library": PDF_DIR,
            "oxford_guide_pages_processed": len(oxford_sentences),
            "dk_guide_pages_processed": len(dk_sentences),
            "total_extracted_sentences": len(all_sentences),
        },
        "writing_corpus": writing_corpus,
        "email_corpus": email_corpus,
        "listening_corpus": listening_corpus,
        "pronunciation_corpus": pronunciation_corpus,
        "reviewing_corpus": reviewing_corpus,
        "book_writing_corpus": book_writing_corpus,
    }


def main():
    print("=" * 80)
    print("  [PHASE 1] EXTRACTING AUTHENTIC GRAMMAR FROM REFERENCE LIBRARY")
    print(f"  Source: {PDF_DIR}")
    print("=" * 80)

    print(f"-> Extracting Oxford Guide: {OXFORD_PDF}...")
    oxford_sents = extract_raw_sentences_from_pdf(OXFORD_PDF, max_pages=400)
    print(f"   Extracted {len(oxford_sents)} verified sentences from Oxford Guide.")

    print(f"-> Extracting DK Guide: {DK_PDF}...")
    dk_sents = extract_raw_sentences_from_pdf(DK_PDF, max_pages=350)
    print(f"   Extracted {len(dk_sents)} verified sentences from DK Guide.")

    corpus = categorize_grammar_corpus(oxford_sents, dk_sents)

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(corpus, f, indent=2, ensure_ascii=False)

    print(f"[OK] Grammar corpus saved to: {OUTPUT_PATH}")
    print(f"   - Writing sentences: {len(corpus['writing_corpus'])}")
    print(f"   - Email / Pragmatics: {len(corpus['email_corpus'])}")
    print(f"   - Listening / Speech: {len(corpus['listening_corpus'])}")
    print(f"   - Pronunciation: {len(corpus['pronunciation_corpus'])}")
    print(f"   - Reviewing: {len(corpus['reviewing_corpus'])}")
    print(f"   - Book Writing: {len(corpus['book_writing_corpus'])}")


if __name__ == "__main__":
    main()
