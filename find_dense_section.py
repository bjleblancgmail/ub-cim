"""
Find the section near the end of the urtext with the highest density of 10-syllable sentences.
Show the surrounding text so we can pick a good block.
"""

import re
from iambic_scan import count_syllables, count_sentence_syllables


def extract_sentences(text):
    text = text.replace('\t', ' ')
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]


def is_real(s):
    clean = re.sub(r'[^a-zA-Z\s]', '', s).strip()
    words = clean.split()
    if len(words) < 3:
        return False
    alpha = sum(1 for c in s if c.isalpha() or c.isspace())
    return alpha >= len(s) * 0.7


def main():
    filepath = "my-book/source-material/CourseUB/urtext_extracted.txt"

    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        text = f.read()

    sentences = extract_sentences(text)
    real = [(i, s) for i, s in enumerate(sentences) if is_real(s)]

    print(f"Total real sentences: {len(real)}")
    print(f"Last sentence index: {real[-1][0]}")

    # Look at the last 20% of text
    cutoff = int(len(real) * 0.80)
    last_section = real[cutoff:]

    # Sliding window: find the densest 100-sentence window
    print(f"\nSearching last {len(last_section)} sentences for dense 10-syllable windows...\n")

    best_density = 0
    best_start = 0
    window_size = 100

    for start in range(len(last_section) - window_size):
        window = last_section[start:start + window_size]
        tens = sum(1 for idx, s in window if count_sentence_syllables(s) == 10)
        density = tens / window_size
        if density > best_density:
            best_density = density
            best_start = start

    best_window = last_section[best_start:best_start + window_size]
    print(f"Best 100-sentence window: density = {best_density:.1%}")
    print(f"Starts at real-sentence index {best_window[0][0]}, ends at {best_window[-1][0]}")

    # Show the window
    print(f"\n{'=' * 70}")
    print(f"DENSEST WINDOW ({window_size} sentences)")
    print(f"{'=' * 70}\n")

    for idx, s in best_window:
        syl = count_sentence_syllables(s)
        marker = " <<<< 10-SYL" if syl == 10 else ""
        print(f"[{idx:>5}] ({syl:>2} syl) {s[:100]}{marker}")

    # Also check: densest 50-sentence window
    best50_density = 0
    best50_start = 0
    for start in range(len(last_section) - 50):
        window = last_section[start:start + 50]
        tens = sum(1 for idx, s in window if count_sentence_syllables(s) == 10)
        density = tens / 50
        if density > best50_density:
            best50_density = density
            best50_start = start

    best50 = last_section[best50_start:best50_start + 50]
    print(f"\n{'=' * 70}")
    print(f"DENSEST 50-SENTENCE WINDOW: density = {best50_density:.1%}")
    print(f"{'=' * 70}\n")

    for idx, s in best50:
        syl = count_sentence_syllables(s)
        marker = " <<<< 10-SYL" if syl == 10 else ""
        print(f"[{idx:>5}] ({syl:>2} syl) {s[:120]}{marker}")

    # Show the very last 80 sentences
    print(f"\n{'=' * 70}")
    print(f"LAST 80 SENTENCES OF THE TEXT")
    print(f"{'=' * 70}\n")

    for idx, s in real[-80:]:
        syl = count_sentence_syllables(s)
        marker = " <<<< 10-SYL" if syl == 10 else ""
        print(f"[{idx:>5}] ({syl:>2} syl) {s[:120]}{marker}")


if __name__ == '__main__':
    main()
