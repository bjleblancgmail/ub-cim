"""
Show the binary string for ALL methods we've tried, on the same block.
Dense block (20710-20771).
"""

import re
from iambic_scan import (STRESS_DICT, count_syllables, get_stress,
                         count_sentence_syllables, get_sentence_stress, iambic_score)


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


def get_toggle_bits(pattern):
    state = 0
    toggle = []
    for i, actual in enumerate(pattern):
        expected = i % 2
        if actual != expected:
            state = 1 - state
        toggle.append(state)
    return toggle


def syllabify_word(word):
    clean = re.sub(r'[^a-zA-Z]', '', word)
    if not clean:
        return []
    stress = get_stress(word)
    num_syls = len(stress)
    if num_syls <= 1:
        return [clean]
    n = len(clean)
    if n <= num_syls:
        return [c for c in clean] + [''] * (num_syls - n)
    groups = []
    chars_per_syl = n / num_syls
    for s in range(num_syls):
        start = int(s * chars_per_syl)
        end = int((s + 1) * chars_per_syl)
        groups.append(clean[start:end])
    return groups


def main():
    filepath = "my-book/source-material/CourseUB/urtext_extracted.txt"
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        text = f.read()

    sentences = extract_sentences(text)
    real = [(i, s) for i, s in enumerate(sentences) if is_real(s)]
    block = [(i, s) for i, s in real if 20710 <= i <= 20771]

    # Collect all methods
    m1_raw_stress = ''        # 1. Raw stress pattern
    m2_deviation = ''         # 2. Deviation from iambic (XOR)
    m3_toggle_syl = ''        # 3. Toggle, syllable level
    m4_toggle_word = ''       # 4. Toggle, word level
    m5_toggle_letter_word = '' # 5. Toggle, letter level (word's bit)
    m6_toggle_letter_syl = '' # 6. Toggle, syllable-letter level

    for idx, s in block:
        words = re.findall(r"[a-zA-Z']+", s)
        pattern = []
        stresses_per_word = []
        for w in words:
            st = get_stress(w)
            stresses_per_word.append((w, st))
            pattern.extend(st)
        if not pattern:
            continue

        # M1: Raw stress
        m1_raw_stress += ''.join(str(b) for b in pattern)

        # M2: Deviation from iambic
        for i, actual in enumerate(pattern):
            expected = i % 2
            m2_deviation += '1' if actual != expected else '0'

        # M3: Toggle syllable level
        toggle = get_toggle_bits(pattern)
        m3_toggle_syl += ''.join(str(b) for b in toggle)

        # M4: Toggle word level
        pos = 0
        for w, st in stresses_per_word:
            if pos < len(toggle):
                m4_toggle_word += str(toggle[pos])
            pos += len(st)

        # M5: Toggle letter level (word's bit)
        pos = 0
        for w, st in stresses_per_word:
            if pos < len(toggle):
                clean = re.sub(r'[^a-zA-Z]', '', w)
                m5_toggle_letter_word += str(toggle[pos]) * len(clean)
            pos += len(st)

        # M6: Toggle syllable-letter level
        pos = 0
        for w, st in stresses_per_word:
            syl_groups = syllabify_word(w)
            num_syls = len(st)
            while len(syl_groups) < num_syls:
                syl_groups.append('')
            syl_groups = syl_groups[:num_syls]
            for grp in syl_groups:
                if pos < len(toggle):
                    m6_toggle_letter_syl += str(toggle[pos]) * len(grp)
                pos += 1

    methods = [
        ("M1: RAW STRESS", m1_raw_stress,
         "Each syllable's actual stress: 0=unstressed, 1=stressed"),
        ("M2: DEVIATION FROM IAMBIC", m2_deviation,
         "XOR with expected iambic (0101...): 0=matches, 1=deviates"),
        ("M3: TOGGLE (syllable)", m3_toggle_syl,
         "State flips on each deviation, one bit per syllable"),
        ("M4: TOGGLE (word)", m4_toggle_word,
         "State flips on each deviation, one bit per word"),
        ("M5: TOGGLE (letter, word bit)", m5_toggle_letter_word,
         "Each letter carries its word's toggle state"),
        ("M6: TOGGLE (letter, syllable bit)", m6_toggle_letter_syl,
         "Each letter carries its syllable's toggle state"),
    ]

    for name, bits, desc in methods:
        print(f"{'=' * 80}")
        print(f"{name}")
        print(f"{desc}")
        print(f"Length: {len(bits)} bits")
        print(f"Ones: {bits.count('1')} ({bits.count('1')/len(bits):.1%})")
        print(f"{'=' * 80}")
        print()

        # Print in rows of 80
        for i in range(0, len(bits), 80):
            print(bits[i:i+80])

        print()
        print()


if __name__ == '__main__':
    main()
