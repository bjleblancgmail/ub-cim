"""
Toggle Binary Analysis of ACIM Urtext 10-Syllable Sentences

Encoding rule:
- Walk through syllable positions 1-10
- Start in state 0
- As long as stress matches expected iambic (u/u/u/u/u/), state stays same
- When a syllable DEVIATES from expected, toggle state (0->1, 1->0)
- State stays until next deviation toggles again

Two output methods:
1. Word-level: each word produces one bit (its current state)
2. Letter-level: each letter in each word carries that word's bit

Also try inverted (swap 0s and 1s).
"""

import re
from collections import Counter
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
    """Given a 10-position stress pattern, return toggle state for each position.
    State starts at 0. Each deviation from expected iambic toggles the state."""
    ideal = [0, 1, 0, 1, 0, 1, 0, 1, 0, 1]
    state = 0
    toggle_bits = []
    for actual, expected in zip(pattern, ideal):
        if actual != expected:
            state = 1 - state  # toggle
        toggle_bits.append(state)
    return toggle_bits


def get_word_level_bits(sentence, pattern):
    """Assign one bit per word based on the toggle state at that word's FIRST syllable position."""
    words = re.findall(r"[a-zA-Z']+", sentence)
    stresses = []
    for w in words:
        stresses.append(get_stress(w))

    toggle_bits = get_toggle_bits(pattern)

    # Map each word to the toggle state at its first syllable position
    word_bits = []
    pos = 0
    for w, stress in zip(words, stresses):
        if pos < len(toggle_bits):
            word_bits.append((w, toggle_bits[pos]))
        pos += len(stress)

    return word_bits


def get_letter_level_bits(word_bits):
    """Each letter in each word carries that word's bit."""
    bits = ''
    for word, bit in word_bits:
        clean = re.sub(r'[^a-zA-Z]', '', word)
        bits += str(bit) * len(clean)
    return bits


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


def invert_bits(bits):
    return ''.join('1' if b == '0' else '0' for b in bits)


def check_printable_ratio(text):
    if not text:
        return 0
    letters = sum(1 for c in text if c.isalpha() or c == ' ')
    return letters / len(text)


def check_english_ratio(text):
    """Stricter: check for lowercase letters, spaces, and common punctuation."""
    if not text:
        return 0
    good = sum(1 for c in text if c.isalpha() or c in ' .,;:!?\'-')
    return good / len(text)


def look_for_words(text, min_len=3):
    """Search for English words in the decoded text."""
    common_words = {
        'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had',
        'her', 'was', 'one', 'our', 'out', 'has', 'his', 'how', 'its', 'may',
        'new', 'now', 'old', 'see', 'way', 'who', 'did', 'get', 'let', 'say',
        'she', 'too', 'use', 'god', 'man', 'day', 'eye', 'far', 'few', 'got',
        'him', 'hit', 'lot', 'men', 'ran', 'run', 'set', 'sit', 'top', 'try',
        'war', 'yes', 'yet', 'big', 'end', 'put', 'red', 'ten', 'ago', 'boy',
        'own', 'why', 'oil', 'ask', 'son', 'love', 'will', 'mind', 'soul',
        'fear', 'truth', 'light', 'peace', 'world', 'heart', 'death', 'dream',
        'power', 'spirit', 'father', 'brother', 'heaven', 'forgive', 'christ',
        'holy', 'miracle', 'salvation', 'eternal', 'divine', 'faith', 'hope',
        'that', 'this', 'with', 'have', 'from', 'they', 'been', 'said', 'each',
        'make', 'like', 'long', 'look', 'many', 'some', 'them', 'then', 'what',
        'when', 'come', 'made', 'find', 'here', 'know', 'take', 'want', 'give',
        'most', 'only', 'over', 'such', 'tell', 'very', 'also', 'back', 'call',
        'hand', 'high', 'keep', 'last', 'name', 'self', 'show', 'turn', 'help',
    }

    found = []
    text_lower = text.lower()
    for word in common_words:
        idx = 0
        while True:
            pos = text_lower.find(word, idx)
            if pos == -1:
                break
            found.append((pos, word))
            idx = pos + 1

    return sorted(found)


def main():
    filepath = "my-book/source-material/CourseUB/urtext_extracted.txt"

    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        text = f.read()

    sentences = extract_sentences(text)

    # Get 10-syllable sentences IN ORDER
    ten_syl = []
    for s in sentences:
        if not is_real(s):
            continue
        if count_sentence_syllables(s) == 10:
            pattern, word_boundaries = get_sentence_stress(s)
            if len(pattern) == 10:
                ten_syl.append((s, pattern))

    print(f"Total 10-syllable sentences: {len(ten_syl)}")

    # === Show first 30 with toggle patterns ===
    print(f"\n{'=' * 70}")
    print("FIRST 30 SENTENCES WITH TOGGLE PATTERNS")
    print("=" * 70)

    for i, (s, pattern) in enumerate(ten_syl[:30], 1):
        ideal = [0, 1, 0, 1, 0, 1, 0, 1, 0, 1]
        toggle = get_toggle_bits(pattern)
        stress_str = ''.join(['/' if b == 1 else 'u' for b in pattern])
        ideal_str = ''.join(['/' if b == 1 else 'u' for b in ideal])
        toggle_str = ''.join(str(b) for b in toggle)
        devs = ''.join(['^' if p != e else ' ' for p, e in zip(pattern, ideal)])

        word_bits = get_word_level_bits(s, pattern)
        wb_str = ' '.join([f"{w}({b})" for w, b in word_bits])

        print(f"\n{i}. {s}")
        print(f"   Stress:   {stress_str}")
        print(f"   Ideal:    {ideal_str}")
        print(f"   Deviate:  {devs}")
        print(f"   Toggle:   {toggle_str}")
        print(f"   Words:    {wb_str}")

    # === Collect all bits ===
    print(f"\n{'=' * 70}")
    print("WORD-LEVEL BINARY (one bit per word)")
    print("=" * 70)

    all_word_bits = []
    for s, pattern in ten_syl:
        wb = get_word_level_bits(s, pattern)
        all_word_bits.extend(wb)

    word_bit_str = ''.join(str(b) for w, b in all_word_bits)
    word_bit_inv = invert_bits(word_bit_str)

    print(f"\nTotal word-bits: {len(word_bit_str)}")
    print(f"Ones: {word_bit_str.count('1')} ({word_bit_str.count('1')/len(word_bit_str):.1%})")
    print(f"Zeros: {word_bit_str.count('0')} ({word_bit_str.count('0')/len(word_bit_str):.1%})")

    # Decode as ASCII
    w_ascii = bits_to_ascii(word_bit_str)
    w_ascii_inv = bits_to_ascii(word_bit_inv)

    print(f"\n8-bit ASCII (normal):")
    print(f"  {w_ascii[:300]}")
    print(f"  Printable ratio: {check_printable_ratio(w_ascii):.1%}")

    print(f"\n8-bit ASCII (inverted):")
    print(f"  {w_ascii_inv[:300]}")
    print(f"  Printable ratio: {check_printable_ratio(w_ascii_inv):.1%}")

    # Look for English words in decoded text
    print(f"\n  Words found in normal decode:")
    found_normal = look_for_words(w_ascii[:500])
    for pos, word in found_normal[:30]:
        context = w_ascii[max(0,pos-3):pos+len(word)+3]
        print(f"    pos {pos}: '{word}' in context '...{context}...'")

    print(f"\n  Words found in inverted decode:")
    found_inv = look_for_words(w_ascii_inv[:500])
    for pos, word in found_inv[:30]:
        context = w_ascii_inv[max(0,pos-3):pos+len(word)+3]
        print(f"    pos {pos}: '{word}' in context '...{context}...'")

    # === LETTER-LEVEL BINARY ===
    print(f"\n{'=' * 70}")
    print("LETTER-LEVEL BINARY (each letter carries its word's bit)")
    print("=" * 70)

    all_letter_bits = ''
    for s, pattern in ten_syl:
        wb = get_word_level_bits(s, pattern)
        all_letter_bits += get_letter_level_bits(wb)

    letter_bit_inv = invert_bits(all_letter_bits)

    print(f"\nTotal letter-bits: {len(all_letter_bits)}")
    print(f"Ones: {all_letter_bits.count('1')} ({all_letter_bits.count('1')/len(all_letter_bits):.1%})")

    l_ascii = bits_to_ascii(all_letter_bits)
    l_ascii_inv = bits_to_ascii(letter_bit_inv)

    print(f"\n8-bit ASCII (normal):")
    print(f"  {l_ascii[:300]}")
    print(f"  Printable ratio: {check_printable_ratio(l_ascii):.1%}")

    print(f"\n8-bit ASCII (inverted):")
    print(f"  {l_ascii_inv[:300]}")
    print(f"  Printable ratio: {check_printable_ratio(l_ascii_inv):.1%}")

    # Look for words
    print(f"\n  Words found in normal decode:")
    found = look_for_words(l_ascii[:500])
    for pos, word in found[:30]:
        context = l_ascii[max(0,pos-3):pos+len(word)+3]
        print(f"    pos {pos}: '{word}' in context '...{context}...'")

    print(f"\n  Words found in inverted decode:")
    found = look_for_words(l_ascii_inv[:500])
    for pos, word in found[:30]:
        context = l_ascii_inv[max(0,pos-3):pos+len(word)+3]
        print(f"    pos {pos}: '{word}' in context '...{context}...'")

    # === TOGGLE BITS PER SYLLABLE (10 bits per line) ===
    print(f"\n{'=' * 70}")
    print("SYLLABLE-LEVEL TOGGLE (10 toggle bits per line)")
    print("=" * 70)

    syl_toggle_bits = ''
    for s, pattern in ten_syl:
        toggle = get_toggle_bits(pattern)
        syl_toggle_bits += ''.join(str(b) for b in toggle)

    syl_toggle_inv = invert_bits(syl_toggle_bits)

    print(f"\nTotal bits: {len(syl_toggle_bits)}")
    print(f"Ones: {syl_toggle_bits.count('1')} ({syl_toggle_bits.count('1')/len(syl_toggle_bits):.1%})")

    s_ascii = bits_to_ascii(syl_toggle_bits)
    s_ascii_inv = bits_to_ascii(syl_toggle_inv)

    print(f"\n8-bit ASCII (normal):")
    print(f"  {s_ascii[:300]}")
    print(f"  Printable ratio: {check_printable_ratio(s_ascii):.1%}")

    print(f"\n8-bit ASCII (inverted):")
    print(f"  {s_ascii_inv[:300]}")
    print(f"  Printable ratio: {check_printable_ratio(s_ascii_inv):.1%}")

    # Look for words
    print(f"\n  Words found in normal decode:")
    found = look_for_words(s_ascii[:500])
    for pos, word in found[:30]:
        context = s_ascii[max(0,pos-3):pos+len(word)+3]
        print(f"    pos {pos}: '{word}' in context '...{context}...'")

    print(f"\n  Words found in inverted decode:")
    found = look_for_words(s_ascii_inv[:500])
    for pos, word in found[:30]:
        context = s_ascii_inv[max(0,pos-3):pos+len(word)+3]
        print(f"    pos {pos}: '{word}' in context '...{context}...'")

    # === TRY 5-BIT ENCODING (A=00001 ... Z=11010) ===
    print(f"\n{'=' * 70}")
    print("5-BIT LETTER ENCODING (Bacon cipher style, A=1 ... Z=26)")
    print("=" * 70)

    for label, bits in [("Syllable toggle", syl_toggle_bits),
                        ("Syllable toggle inverted", syl_toggle_inv),
                        ("Word-level", word_bit_str),
                        ("Word-level inverted", word_bit_inv)]:
        chars = []
        for i in range(0, len(bits) - 4, 5):
            chunk = bits[i:i+5]
            val = int(chunk, 2)
            if 1 <= val <= 26:
                chars.append(chr(64 + val))  # A=1, B=2, ...
            elif val == 0:
                chars.append('_')
            else:
                chars.append('.')
        decoded = ''.join(chars)
        print(f"\n{label}:")
        print(f"  {decoded[:200]}")
        # Check for words
        found = look_for_words(decoded[:300])
        if found:
            print(f"  Words found: ", end='')
            for pos, word in found[:15]:
                print(f"'{word}'@{pos} ", end='')
            print()

    # === SUMMARY TABLE ===
    print(f"\n{'=' * 70}")
    print("SUMMARY: Printable ratios for all methods")
    print("=" * 70)

    results = [
        ("Word-level (8-bit, normal)", check_printable_ratio(w_ascii)),
        ("Word-level (8-bit, inverted)", check_printable_ratio(w_ascii_inv)),
        ("Letter-level (8-bit, normal)", check_printable_ratio(l_ascii)),
        ("Letter-level (8-bit, inverted)", check_printable_ratio(l_ascii_inv)),
        ("Syllable toggle (8-bit, normal)", check_printable_ratio(s_ascii)),
        ("Syllable toggle (8-bit, inverted)", check_printable_ratio(s_ascii_inv)),
    ]

    print(f"\n{'Method':<45} {'Ratio':>8}  Verdict")
    print("-" * 70)
    for name, ratio in results:
        verdict = "INVESTIGATE" if ratio > 0.60 else "random-like"
        print(f"  {name:<43} {ratio:>7.1%}  {verdict}")

    print(f"\nEnglish text would show ~85%+. Random noise shows ~37%.")
    print(f"Anything above 60% warrants deeper investigation.")


if __name__ == '__main__':
    main()
