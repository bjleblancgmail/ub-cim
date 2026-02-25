"""
Stress-Pattern Binary Analysis of ACIM Urtext 10-Syllable Sentences

Each 10-syllable sentence has 10 stress positions (0=unstressed, 1=stressed).
Perfect iambic pentameter = 0101010101.

This script:
1. Extracts stress patterns IN ORDER OF APPEARANCE (not sorted by score)
2. Reads the raw 10-bit stress pattern as binary
3. Reads the DEVIATION from perfect iambic as binary (where does it differ?)
4. Attempts to decode as ASCII text
5. Checks for statistical patterns in the bits
"""

import re
from collections import Counter

# Import stress analysis from iambic_scan
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


def bits_to_ascii(bits):
    """Convert a string of 0s and 1s to ASCII text, 8 bits at a time."""
    chars = []
    for i in range(0, len(bits) - 7, 8):
        byte = bits[i:i+8]
        val = int(byte, 2)
        if 32 <= val <= 126:  # printable ASCII
            chars.append(chr(val))
        else:
            chars.append('.')
    return ''.join(chars)


def bits_to_ascii_7bit(bits):
    """Try 7-bit ASCII."""
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
    """What percentage of decoded characters are printable letters/spaces?"""
    if not text:
        return 0
    letters = sum(1 for c in text if c.isalpha() or c == ' ')
    return letters / len(text)


def main():
    filepath = "my-book/source-material/CourseUB/urtext_extracted.txt"

    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        text = f.read()

    sentences = extract_sentences(text)

    # Get 10-syllable sentences IN ORDER OF APPEARANCE
    ten_syl = []
    for s in sentences:
        if not is_real(s):
            continue
        if count_sentence_syllables(s) == 10:
            pattern, word_boundaries = get_sentence_stress(s)
            if len(pattern) == 10:
                ten_syl.append((s, pattern))

    print(f"Total 10-syllable sentences (in order): {len(ten_syl)}")
    print()

    # === METHOD 1: Raw stress patterns as binary ===
    print("=" * 70)
    print("METHOD 1: Raw stress patterns as binary")
    print("Each line's 10 stress positions read as bits (0/1)")
    print("=" * 70)

    raw_bits = ''
    for s, pattern in ten_syl:
        raw_bits += ''.join(str(b) for b in pattern)

    print(f"\nTotal bits: {len(raw_bits)}")
    print(f"First 100 bits: {raw_bits[:100]}")
    print(f"Last 100 bits:  {raw_bits[-100:]}")

    # Decode as 8-bit ASCII
    ascii_8 = bits_to_ascii(raw_bits)
    print(f"\n8-bit ASCII decode (first 200 chars):")
    print(f"  {ascii_8[:200]}")
    print(f"\nPrintable letter ratio: {check_printable_ratio(ascii_8):.1%}")

    # Decode as 7-bit ASCII
    ascii_7 = bits_to_ascii_7bit(raw_bits)
    print(f"\n7-bit ASCII decode (first 200 chars):")
    print(f"  {ascii_7[:200]}")
    print(f"\nPrintable letter ratio: {check_printable_ratio(ascii_7):.1%}")

    # === METHOD 2: Deviation from perfect iambic ===
    print(f"\n{'=' * 70}")
    print("METHOD 2: Deviation bits (XOR with perfect iambic 0101010101)")
    print("0 = matches iambic, 1 = deviates from iambic")
    print("=" * 70)

    ideal = [0, 1, 0, 1, 0, 1, 0, 1, 0, 1]
    deviation_bits = ''
    for s, pattern in ten_syl:
        for actual, expected in zip(pattern, ideal):
            deviation_bits += '1' if actual != expected else '0'

    print(f"\nTotal deviation bits: {len(deviation_bits)}")
    print(f"First 100 bits: {deviation_bits[:100]}")

    # What percentage are deviations?
    ones = deviation_bits.count('1')
    print(f"Deviation rate: {ones}/{len(deviation_bits)} = {ones/len(deviation_bits):.1%}")
    print(f"(50% would be random, 0% would be all perfect iambic)")

    # Decode deviations as ASCII
    dev_ascii_8 = bits_to_ascii(deviation_bits)
    print(f"\n8-bit ASCII decode of deviations (first 200 chars):")
    print(f"  {dev_ascii_8[:200]}")
    print(f"\nPrintable letter ratio: {check_printable_ratio(dev_ascii_8):.1%}")

    # === METHOD 3: One bit per line (majority stress) ===
    print(f"\n{'=' * 70}")
    print("METHOD 3: One bit per line")
    print("Various single-bit encodings per sentence")
    print("=" * 70)

    # 3a: Odd/even word count
    word_parity_bits = ''
    for s, pattern in ten_syl:
        words = re.findall(r"[a-zA-Z']+", s)
        word_parity_bits += '1' if len(words) % 2 == 1 else '0'

    print(f"\n3a. Word-count parity (odd=1, even=0):")
    print(f"    Bits: {word_parity_bits[:80]}")
    wa_8 = bits_to_ascii(word_parity_bits)
    print(f"    ASCII: {wa_8[:100]}")
    print(f"    Printable ratio: {check_printable_ratio(wa_8):.1%}")

    # 3b: Letter-count parity
    letter_parity_bits = ''
    for s, pattern in ten_syl:
        letters = sum(1 for c in s if c.isalpha())
        letter_parity_bits += '1' if letters % 2 == 1 else '0'

    print(f"\n3b. Letter-count parity (odd=1, even=0):")
    print(f"    Bits: {letter_parity_bits[:80]}")
    la_8 = bits_to_ascii(letter_parity_bits)
    print(f"    ASCII: {la_8[:100]}")
    print(f"    Printable ratio: {check_printable_ratio(la_8):.1%}")

    # 3c: First letter A-M=0, N-Z=1
    first_letter_bits = ''
    for s, pattern in ten_syl:
        first = ''
        for c in s:
            if c.isalpha():
                first = c.upper()
                break
        if first:
            first_letter_bits += '0' if first <= 'M' else '1'

    print(f"\n3c. First-letter binary (A-M=0, N-Z=1):")
    print(f"    Bits: {first_letter_bits[:80]}")
    fl_8 = bits_to_ascii(first_letter_bits)
    print(f"    ASCII: {fl_8[:100]}")
    print(f"    Printable ratio: {check_printable_ratio(fl_8):.1%}")

    # 3d: Iambic score >= 0.8 = 1, else 0
    iambic_bits = ''
    for s, pattern in ten_syl:
        score = iambic_score(pattern)
        iambic_bits += '1' if score >= 0.8 else '0'

    print(f"\n3d. Iambic quality (score >= 80% = 1, else 0):")
    print(f"    Bits: {iambic_bits[:80]}")
    ib_8 = bits_to_ascii(iambic_bits)
    print(f"    ASCII: {ib_8[:100]}")
    print(f"    Printable ratio: {check_printable_ratio(ib_8):.1%}")

    # === METHOD 4: Position-specific analysis ===
    print(f"\n{'=' * 70}")
    print("METHOD 4: Position-specific stress frequency")
    print("How often is each of the 10 positions stressed?")
    print("=" * 70)

    pos_counts = [0] * 10
    for s, pattern in ten_syl:
        for i, bit in enumerate(pattern):
            pos_counts[i] += bit

    total = len(ten_syl)
    print(f"\nPosition:  1    2    3    4    5    6    7    8    9    10")
    print(f"Ideal:     u    /    u    /    u    /    u    /    u    /")
    print(f"Stressed: ", end='')
    for c in pos_counts:
        print(f"{c/total:.0%}  ", end='')
    print()
    print(f"Counts:   ", end='')
    for c in pos_counts:
        print(f"{c:<5}", end='')
    print()

    # === METHOD 5: Check for repeating patterns ===
    print(f"\n{'=' * 70}")
    print("METHOD 5: Pattern frequency (most common stress patterns)")
    print("=" * 70)

    pattern_strs = []
    for s, pattern in ten_syl:
        pat_str = ''.join(str(b) for b in pattern)
        pattern_strs.append(pat_str)

    pat_counts = Counter(pattern_strs)
    print(f"\nUnique patterns: {len(pat_counts)} out of 1024 possible")
    print(f"\nTop 20 most common patterns:")
    for pat, count in pat_counts.most_common(20):
        visual = ''.join(['/' if c == '1' else 'u' for c in pat])
        pct = count / total * 100
        is_iambic = pat == '0101010101'
        marker = " <<< PERFECT IAMBIC" if is_iambic else ""
        print(f"  {visual}  ({pat})  {count:>4} times ({pct:.1f}%){marker}")

    # === METHOD 6: Entropy analysis ===
    print(f"\n{'=' * 70}")
    print("METHOD 6: Statistical tests")
    print("=" * 70)

    import math

    # Bit balance
    total_bits = len(raw_bits)
    ones_raw = raw_bits.count('1')
    zeros_raw = raw_bits.count('0')
    print(f"\nRaw stress bits: {ones_raw} ones ({ones_raw/total_bits:.3f}), {zeros_raw} zeros ({zeros_raw/total_bits:.3f})")
    print(f"  Perfect random would be 0.500/0.500")
    print(f"  Perfect iambic would be 0.500/0.500 (but in strict alternation)")

    # Check for runs (consecutive same bits)
    runs = 1
    for i in range(1, len(raw_bits)):
        if raw_bits[i] != raw_bits[i-1]:
            runs += 1
    expected_runs = (total_bits + 1) / 2  # expected for random
    print(f"\n  Number of runs (bit transitions): {runs}")
    print(f"  Expected for random: {expected_runs:.0f}")
    print(f"  Expected for perfect iambic: {total_bits} (alternates every bit)")
    print(f"  Ratio to random expectation: {runs/expected_runs:.3f}")

    # Check consecutive line patterns
    print(f"\n  Consecutive identical patterns:")
    consecutive = 0
    for i in range(1, len(pattern_strs)):
        if pattern_strs[i] == pattern_strs[i-1]:
            consecutive += 1
    expected_consec = total / len(pat_counts)  # rough expectation
    print(f"    Found: {consecutive} pairs of identical consecutive patterns")

    # === SUMMARY ===
    print(f"\n{'=' * 70}")
    print("SUMMARY: Is there a hidden binary message?")
    print("=" * 70)

    methods = [
        ("Raw stress (8-bit)", check_printable_ratio(ascii_8)),
        ("Raw stress (7-bit)", check_printable_ratio(ascii_7)),
        ("Deviation from iambic (8-bit)", check_printable_ratio(dev_ascii_8)),
        ("Word parity (8-bit)", check_printable_ratio(wa_8)),
        ("Letter parity (8-bit)", check_printable_ratio(la_8)),
        ("First letter binary (8-bit)", check_printable_ratio(fl_8)),
        ("Iambic quality (8-bit)", check_printable_ratio(ib_8)),
    ]

    print(f"\nPrintable text ratios (English text would be ~85%+, random ~37%):\n")
    for name, ratio in methods:
        indicator = "INTERESTING" if ratio > 0.6 else "random-like"
        print(f"  {name:<40} {ratio:.1%}  [{indicator}]")

    print(f"\nIf any method shows >60% printable ratio, it warrants deeper investigation.")
    print(f"If all are near ~37%, the stress patterns do not encode ASCII text.")

    # Save first 50 lines with their patterns for manual inspection
    print(f"\n{'=' * 70}")
    print("FIRST 30 SENTENCES WITH STRESS PATTERNS")
    print("(for manual inspection)")
    print("=" * 70)

    for i, (s, pattern) in enumerate(ten_syl[:30], 1):
        pat_str = ''.join(['/' if b == 1 else 'u' for b in pattern])
        binary = ''.join(str(b) for b in pattern)
        val = int(binary, 2)
        print(f"\n{i}. {s}")
        print(f"   Stress:  {pat_str}")
        print(f"   Binary:  {binary} = {val} (0x{val:03X})")

    # Also show last 30
    print(f"\n{'=' * 70}")
    print("LAST 30 SENTENCES WITH STRESS PATTERNS")
    print("=" * 70)

    for i, (s, pattern) in enumerate(ten_syl[-30:], len(ten_syl) - 29):
        pat_str = ''.join(['/' if b == 1 else 'u' for b in pattern])
        binary = ''.join(str(b) for b in pattern)
        val = int(binary, 2)
        print(f"\n{i}. {s}")
        print(f"   Stress:  {pat_str}")
        print(f"   Binary:  {binary} = {val} (0x{val:03X})")


if __name__ == '__main__':
    main()
