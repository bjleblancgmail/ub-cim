"""
Stress-Pattern Binary Analysis of ACIM Urtext 20-Syllable Couplets

The 920 twenty-syllable sentences that split cleanly into 10+10 halves.
Each half is treated as a line with 10 stress positions.
Same analysis as stress_binary.py but on this hidden data set.
"""

import re
from collections import Counter
from iambic_scan import STRESS_DICT, count_syllables, get_stress, count_sentence_syllables, get_sentence_stress, iambic_score


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


def find_10_10_split(sentence):
    """Try to split a 20-syllable sentence at the point where cumulative syllables = 10."""
    words = re.findall(r"[a-zA-Z']+", sentence)
    cumul = 0
    for idx, w in enumerate(words):
        cumul += count_syllables(w)
        if cumul == 10:
            # Split after this word
            # Rebuild from original sentence
            word_positions = list(re.finditer(r"[a-zA-Z']+", sentence))
            if idx < len(word_positions):
                split_char = word_positions[idx].end()
                first_half = sentence[:split_char].strip()
                second_half = sentence[split_char:].strip()
                second_half = re.sub(r'^[,;:\s]+', '', second_half).strip()
                # Verify
                if count_sentence_syllables(first_half) == 10 and count_sentence_syllables(second_half) == 10:
                    return first_half, second_half
            return None, None
    return None, None


def bits_to_ascii(bits):
    chars = []
    for i in range(0, len(bits) - 7, 8):
        byte = bits[i:i+8]
        val = int(byte, 2)
        if 32 <= val <= 126:
            chars.append(chr(val))
        else:
            chars.append('.')
    return ''.join(chars)


def bits_to_ascii_7bit(bits):
    chars = []
    for i in range(0, len(bits) - 6, 7):
        chunk = bits[i:i+7]
        val = int(chunk, 2)
        if 32 <= val <= 126:
            chars.append(chr(val))
        else:
            chars.append('.')
    return ''.join(chars)


def check_printable_ratio(text):
    if not text:
        return 0
    letters = sum(1 for c in text if c.isalpha() or c == ' ')
    return letters / len(text)


def main():
    filepath = "my-book/source-material/CourseUB/urtext_extracted.txt"

    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        text = f.read()

    sentences = extract_sentences(text)

    # Find 20-syllable sentences that split into 10+10, IN ORDER
    couplets = []
    for s in sentences:
        if not is_real(s):
            continue
        if count_sentence_syllables(s) == 20:
            first, second = find_10_10_split(s)
            if first and second:
                pat1, wb1 = get_sentence_stress(first)
                pat2, wb2 = get_sentence_stress(second)
                if len(pat1) == 10 and len(pat2) == 10:
                    couplets.append((s, first, second, pat1, pat2))

    print(f"Total 20-syllable sentences that split into 10+10: {len(couplets)}")
    print(f"Total half-lines (each 10 syllables): {len(couplets) * 2}")
    print()

    # Collect all half-line patterns in order (first half, second half, first half, second half...)
    all_patterns = []
    for s, first, second, pat1, pat2 in couplets:
        all_patterns.append(('A', first, pat1))  # first half
        all_patterns.append(('B', second, pat2))  # second half

    # Also try: just first halves, just second halves
    first_patterns = [(first, pat1) for s, first, second, pat1, pat2 in couplets]
    second_patterns = [(second, pat2) for s, first, second, pat1, pat2 in couplets]

    # === METHOD 1: Raw stress patterns as binary ===
    print("=" * 70)
    print("METHOD 1: Raw stress patterns as binary (all half-lines interleaved)")
    print("=" * 70)

    raw_bits = ''
    for label, sent, pattern in all_patterns:
        raw_bits += ''.join(str(b) for b in pattern)

    print(f"\nTotal bits: {len(raw_bits)}")
    ascii_8 = bits_to_ascii(raw_bits)
    print(f"8-bit ASCII (first 200 chars): {ascii_8[:200]}")
    print(f"Printable letter ratio: {check_printable_ratio(ascii_8):.1%}")

    # First halves only
    raw_bits_first = ''.join(''.join(str(b) for b in pat) for sent, pat in first_patterns)
    ascii_8_first = bits_to_ascii(raw_bits_first)
    print(f"\nFirst halves only - 8-bit ASCII (first 200 chars): {ascii_8_first[:200]}")
    print(f"Printable letter ratio: {check_printable_ratio(ascii_8_first):.1%}")

    # Second halves only
    raw_bits_second = ''.join(''.join(str(b) for b in pat) for sent, pat in second_patterns)
    ascii_8_second = bits_to_ascii(raw_bits_second)
    print(f"\nSecond halves only - 8-bit ASCII (first 200 chars): {ascii_8_second[:200]}")
    print(f"Printable letter ratio: {check_printable_ratio(ascii_8_second):.1%}")

    # === METHOD 2: Deviation from perfect iambic ===
    print(f"\n{'=' * 70}")
    print("METHOD 2: Deviation bits (XOR with perfect iambic)")
    print("=" * 70)

    ideal = [0, 1, 0, 1, 0, 1, 0, 1, 0, 1]
    dev_bits = ''
    for label, sent, pattern in all_patterns:
        for actual, expected in zip(pattern, ideal):
            dev_bits += '1' if actual != expected else '0'

    dev_ascii = bits_to_ascii(dev_bits)
    ones = dev_bits.count('1')
    print(f"\nDeviation rate: {ones}/{len(dev_bits)} = {ones/len(dev_bits):.1%}")
    print(f"8-bit ASCII (first 200 chars): {dev_ascii[:200]}")
    print(f"Printable letter ratio: {check_printable_ratio(dev_ascii):.1%}")

    # === METHOD 3: One bit per half-line ===
    print(f"\n{'=' * 70}")
    print("METHOD 3: One bit per half-line")
    print("=" * 70)

    # 3a: Word-count parity
    wp_bits = ''
    for label, sent, pattern in all_patterns:
        words = re.findall(r"[a-zA-Z']+", sent)
        wp_bits += '1' if len(words) % 2 == 1 else '0'
    wp_ascii = bits_to_ascii(wp_bits)
    print(f"\n3a. Word parity: {wp_ascii[:100]}")
    print(f"    Printable ratio: {check_printable_ratio(wp_ascii):.1%}")

    # 3b: Letter-count parity
    lp_bits = ''
    for label, sent, pattern in all_patterns:
        letters = sum(1 for c in sent if c.isalpha())
        lp_bits += '1' if letters % 2 == 1 else '0'
    lp_ascii = bits_to_ascii(lp_bits)
    print(f"\n3b. Letter parity: {lp_ascii[:100]}")
    print(f"    Printable ratio: {check_printable_ratio(lp_ascii):.1%}")

    # 3c: First letter A-M=0, N-Z=1
    fl_bits = ''
    for label, sent, pattern in all_patterns:
        first = ''
        for c in sent:
            if c.isalpha():
                first = c.upper()
                break
        if first:
            fl_bits += '0' if first <= 'M' else '1'
    fl_ascii = bits_to_ascii(fl_bits)
    print(f"\n3c. First letter: {fl_ascii[:100]}")
    print(f"    Printable ratio: {check_printable_ratio(fl_ascii):.1%}")

    # 3d: Iambic score >= 0.8
    ib_bits = ''
    for label, sent, pattern in all_patterns:
        score = iambic_score(pattern)
        ib_bits += '1' if score >= 0.8 else '0'
    ib_ascii = bits_to_ascii(ib_bits)
    print(f"\n3d. Iambic quality: {ib_ascii[:100]}")
    print(f"    Printable ratio: {check_printable_ratio(ib_ascii):.1%}")

    # === METHOD 4: Position-specific stress ===
    print(f"\n{'=' * 70}")
    print("METHOD 4: Position-specific stress frequency")
    print("=" * 70)

    total_lines = len(all_patterns)

    # All half-lines
    pos_all = [0] * 10
    for label, sent, pattern in all_patterns:
        for i, bit in enumerate(pattern):
            pos_all[i] += bit

    print(f"\nAll {total_lines} half-lines:")
    print(f"Position:  1    2    3    4    5    6    7    8    9    10")
    print(f"Ideal:     u    /    u    /    u    /    u    /    u    /")
    print(f"Stressed: ", end='')
    for c in pos_all:
        print(f"{c/total_lines:.0%}  ", end='')
    print()

    # First halves only
    pos_first = [0] * 10
    for sent, pat in first_patterns:
        for i, bit in enumerate(pat):
            pos_first[i] += bit

    n_first = len(first_patterns)
    print(f"\nFirst halves only ({n_first}):")
    print(f"Stressed: ", end='')
    for c in pos_first:
        print(f"{c/n_first:.0%}  ", end='')
    print()

    # Second halves only
    pos_second = [0] * 10
    for sent, pat in second_patterns:
        for i, bit in enumerate(pat):
            pos_second[i] += bit

    n_second = len(second_patterns)
    print(f"\nSecond halves only ({n_second}):")
    print(f"Stressed: ", end='')
    for c in pos_second:
        print(f"{c/n_second:.0%}  ", end='')
    print()

    # === METHOD 5: Compare first-half vs second-half patterns ===
    print(f"\n{'=' * 70}")
    print("METHOD 5: Do first and second halves have different stress profiles?")
    print("=" * 70)

    # Most common patterns for each half
    first_pat_strs = [''.join(str(b) for b in pat) for sent, pat in first_patterns]
    second_pat_strs = [''.join(str(b) for b in pat) for sent, pat in second_patterns]

    first_counts = Counter(first_pat_strs)
    second_counts = Counter(second_pat_strs)

    print(f"\nFirst halves - unique patterns: {len(first_counts)}")
    print("Top 10:")
    for pat, count in first_counts.most_common(10):
        visual = ''.join(['/' if c == '1' else 'u' for c in pat])
        print(f"  {visual}  {count:>4} ({count/n_first*100:.1f}%)")

    print(f"\nSecond halves - unique patterns: {len(second_counts)}")
    print("Top 10:")
    for pat, count in second_counts.most_common(10):
        visual = ''.join(['/' if c == '1' else 'u' for c in pat])
        print(f"  {visual}  {count:>4} ({count/n_second*100:.1f}%)")

    # === METHOD 6: Couplet-level encoding ===
    print(f"\n{'=' * 70}")
    print("METHOD 6: Couplet-level encoding (20 bits per sentence)")
    print("Concatenate both halves = 20 bits per original sentence")
    print("=" * 70)

    couplet_bits = ''
    for s, first, second, pat1, pat2 in couplets:
        couplet_bits += ''.join(str(b) for b in pat1) + ''.join(str(b) for b in pat2)

    print(f"\nTotal bits: {len(couplet_bits)}")
    # 20 bits per couplet = 2.5 bytes. Try reading as continuous stream
    c_ascii = bits_to_ascii(couplet_bits)
    print(f"8-bit ASCII (first 200 chars): {c_ascii[:200]}")
    print(f"Printable letter ratio: {check_printable_ratio(c_ascii):.1%}")

    # === SUMMARY ===
    print(f"\n{'=' * 70}")
    print("SUMMARY")
    print("=" * 70)

    methods = [
        ("All half-lines interleaved (8-bit)", check_printable_ratio(ascii_8)),
        ("First halves only (8-bit)", check_printable_ratio(ascii_8_first)),
        ("Second halves only (8-bit)", check_printable_ratio(ascii_8_second)),
        ("Deviation from iambic (8-bit)", check_printable_ratio(dev_ascii)),
        ("Word parity (8-bit)", check_printable_ratio(wp_ascii)),
        ("Letter parity (8-bit)", check_printable_ratio(lp_ascii)),
        ("First letter binary (8-bit)", check_printable_ratio(fl_ascii)),
        ("Iambic quality (8-bit)", check_printable_ratio(ib_ascii)),
        ("Full 20-bit couplets (8-bit)", check_printable_ratio(c_ascii)),
    ]

    print(f"\nPrintable text ratios (English ~85%+, random ~37%):\n")
    for name, ratio in methods:
        indicator = "INTERESTING" if ratio > 0.6 else "random-like"
        print(f"  {name:<45} {ratio:.1%}  [{indicator}]")

    # === SAMPLE COUPLETS WITH PATTERNS ===
    print(f"\n{'=' * 70}")
    print("FIRST 20 COUPLETS WITH STRESS PATTERNS")
    print("=" * 70)

    for i, (s, first, second, pat1, pat2) in enumerate(couplets[:20], 1):
        v1 = ''.join(['/' if b == 1 else 'u' for b in pat1])
        v2 = ''.join(['/' if b == 1 else 'u' for b in pat2])
        b1 = ''.join(str(b) for b in pat1)
        b2 = ''.join(str(b) for b in pat2)
        s1 = iambic_score(pat1)
        s2 = iambic_score(pat2)
        print(f"\n{i}. {first}")
        print(f"   {v1}  [{s1:.0%}]")
        print(f"   {second}")
        print(f"   {v2}  [{s2:.0%}]")

    print(f"\n{'=' * 70}")
    print("LAST 20 COUPLETS WITH STRESS PATTERNS")
    print("=" * 70)

    for i, (s, first, second, pat1, pat2) in enumerate(couplets[-20:], len(couplets) - 19):
        v1 = ''.join(['/' if b == 1 else 'u' for b in pat1])
        v2 = ''.join(['/' if b == 1 else 'u' for b in pat2])
        s1 = iambic_score(pat1)
        s2 = iambic_score(pat2)
        print(f"\n{i}. {first}")
        print(f"   {v1}  [{s1:.0%}]")
        print(f"   {second}")
        print(f"   {v2}  [{s2:.0%}]")


if __name__ == '__main__':
    main()
