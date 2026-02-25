"""
Toggle Binary Analysis on a BLOCK of text (all sentence lengths).

Uses the dense section near the end of the urtext (sentences 20710-20771).
Every sentence is analyzed, not just 10-syllable ones.
The toggle method: start at state 0, walk through each syllable,
toggle whenever stress deviates from expected iambic (u/u/u/...).
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


def get_toggle_bits_variable(pattern):
    """Toggle encoding for any length pattern.
    Expected iambic: u/u/u/u/... (0,1,0,1,0,1...)
    State starts at 0. Each deviation from expected toggles the state."""
    state = 0
    toggle_bits = []
    for i, actual in enumerate(pattern):
        expected = i % 2  # 0,1,0,1,0,1...
        if actual != expected:
            state = 1 - state
        toggle_bits.append(state)
    return toggle_bits


def get_full_stress_pattern(sentence):
    """Get stress pattern for any sentence (any length)."""
    words = re.findall(r"[a-zA-Z']+", sentence)
    pattern = []
    word_list = []
    for w in words:
        stress = get_stress(w)
        word_list.append((w, stress))
        pattern.extend(stress)
    return pattern, word_list


def get_word_level_bits(sentence, pattern):
    """One bit per word based on toggle state at word's first syllable."""
    words = re.findall(r"[a-zA-Z']+", sentence)
    stresses = [get_stress(w) for w in words]
    toggle_bits = get_toggle_bits_variable(pattern)

    word_bits = []
    pos = 0
    for w, stress in zip(words, stresses):
        if pos < len(toggle_bits):
            word_bits.append((w, toggle_bits[pos]))
        pos += len(stress)
    return word_bits


def get_letter_level_bits(word_bits):
    """Each letter carries its word's toggle bit."""
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


def look_for_words(text, min_len=3):
    common_words = {
        'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had',
        'her', 'was', 'one', 'our', 'out', 'has', 'his', 'how', 'its', 'may',
        'god', 'man', 'son', 'love', 'will', 'mind', 'soul', 'fear', 'truth',
        'light', 'peace', 'world', 'heart', 'death', 'dream', 'power', 'spirit',
        'father', 'brother', 'heaven', 'forgive', 'christ', 'holy', 'miracle',
        'that', 'this', 'with', 'have', 'from', 'they', 'been', 'said', 'each',
        'make', 'like', 'long', 'look', 'many', 'some', 'them', 'then', 'what',
        'when', 'come', 'made', 'find', 'here', 'know', 'take', 'want', 'give',
        'most', 'only', 'over', 'such', 'tell', 'very', 'also', 'back', 'call',
        'done', 'self', 'free', 'true', 'real', 'word', 'life', 'body', 'eyes',
        'see', 'way', 'new', 'old', 'sin', 'joy', 'ask', 'say', 'let', 'put',
        'own', 'set', 'run', 'use', 'try', 'end', 'far', 'yet', 'why', 'who',
        'save', 'seek', 'teach', 'learn', 'hear', 'child', 'name',
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
    real = [(i, s) for i, s in enumerate(sentences) if is_real(s)]

    # Use the dense section: real-sentence indices roughly 20710-20771
    # But let's get by position in the real array
    block = [(i, s) for i, s in real if 20710 <= i <= 20771]

    print(f"Block: {len(block)} sentences (indices {block[0][0]}-{block[-1][0]})")
    print()

    # === Show every sentence with its toggle pattern ===
    print("=" * 80)
    print("ALL SENTENCES IN BLOCK WITH TOGGLE PATTERNS")
    print("=" * 80)

    all_syl_toggle_bits = ''
    all_word_bits = []
    all_letter_bits = ''

    for idx, s in block:
        pattern, word_list = get_full_stress_pattern(s)
        syl_count = len(pattern)
        toggle = get_toggle_bits_variable(pattern)
        wb = get_word_level_bits(s, pattern)

        stress_str = ''.join(['/' if b == 1 else 'u' for b in pattern])
        toggle_str = ''.join(str(b) for b in toggle)
        wb_str = ' '.join([f"{w}({b})" for w, b in wb])

        is_ten = " *** 10-SYL ***" if syl_count == 10 else ""

        print(f"\n[{idx}] ({syl_count} syl){is_ten}")
        print(f"  {s[:120]}")
        print(f"  Stress: {stress_str}")
        print(f"  Toggle: {toggle_str}")
        print(f"  Words:  {wb_str}")

        all_syl_toggle_bits += toggle_str
        all_word_bits.extend(wb)
        all_letter_bits += get_letter_level_bits(wb)

    # === Decode all methods ===
    word_bit_str = ''.join(str(b) for w, b in all_word_bits)
    word_bit_inv = invert_bits(word_bit_str)
    syl_inv = invert_bits(all_syl_toggle_bits)
    letter_inv = invert_bits(all_letter_bits)

    print(f"\n\n{'=' * 80}")
    print("DECODING RESULTS")
    print("=" * 80)

    # Syllable-level toggle
    print(f"\n--- SYLLABLE-LEVEL TOGGLE ---")
    print(f"Total bits: {len(all_syl_toggle_bits)}")
    print(f"Ones: {all_syl_toggle_bits.count('1')} ({all_syl_toggle_bits.count('1')/len(all_syl_toggle_bits):.1%})")
    s_ascii = bits_to_ascii(all_syl_toggle_bits)
    s_ascii_inv = bits_to_ascii(syl_inv)
    print(f"\n8-bit ASCII (normal):   {s_ascii}")
    print(f"Printable ratio: {check_printable_ratio(s_ascii):.1%}")
    print(f"\n8-bit ASCII (inverted): {s_ascii_inv}")
    print(f"Printable ratio: {check_printable_ratio(s_ascii_inv):.1%}")

    # Word-level
    print(f"\n--- WORD-LEVEL ---")
    print(f"Total bits: {len(word_bit_str)}")
    w_ascii = bits_to_ascii(word_bit_str)
    w_ascii_inv = bits_to_ascii(word_bit_inv)
    print(f"\n8-bit ASCII (normal):   {w_ascii}")
    print(f"Printable ratio: {check_printable_ratio(w_ascii):.1%}")
    print(f"\n8-bit ASCII (inverted): {w_ascii_inv}")
    print(f"Printable ratio: {check_printable_ratio(w_ascii_inv):.1%}")

    # Letter-level
    print(f"\n--- LETTER-LEVEL ---")
    print(f"Total bits: {len(all_letter_bits)}")
    l_ascii = bits_to_ascii(all_letter_bits)
    l_ascii_inv = bits_to_ascii(letter_inv)
    print(f"\n8-bit ASCII (normal):   {l_ascii[:300]}")
    print(f"Printable ratio: {check_printable_ratio(l_ascii):.1%}")
    print(f"\n8-bit ASCII (inverted): {l_ascii_inv[:300]}")
    print(f"Printable ratio: {check_printable_ratio(l_ascii_inv):.1%}")

    # 5-bit Bacon cipher
    print(f"\n--- 5-BIT BACON CIPHER ---")
    for label, bits in [("Syllable toggle", all_syl_toggle_bits),
                        ("Syllable inverted", syl_inv),
                        ("Word-level", word_bit_str),
                        ("Word-level inverted", word_bit_inv)]:
        chars = []
        for i in range(0, len(bits) - 4, 5):
            chunk = bits[i:i+5]
            val = int(chunk, 2)
            if 1 <= val <= 26:
                chars.append(chr(64 + val))
            elif val == 0:
                chars.append('_')
            else:
                chars.append('.')
        print(f"\n{label}: {''.join(chars)}")

    # Word search in all decodes
    print(f"\n--- WORD SEARCH ---")
    for label, decoded in [("Syl normal", s_ascii), ("Syl inverted", s_ascii_inv),
                           ("Word normal", w_ascii), ("Word inverted", w_ascii_inv),
                           ("Letter normal", l_ascii), ("Letter inverted", l_ascii_inv)]:
        found = look_for_words(decoded)
        if found:
            print(f"\n  {label}:")
            for pos, word in found:
                context = decoded[max(0, pos-3):pos+len(word)+3]
                print(f"    '{word}' at pos {pos}: ...{context}...")

    # === SUMMARY ===
    print(f"\n{'=' * 80}")
    print("SUMMARY")
    print("=" * 80)

    results = [
        ("Syllable toggle (normal)", check_printable_ratio(s_ascii)),
        ("Syllable toggle (inverted)", check_printable_ratio(s_ascii_inv)),
        ("Word-level (normal)", check_printable_ratio(w_ascii)),
        ("Word-level (inverted)", check_printable_ratio(w_ascii_inv)),
        ("Letter-level (normal)", check_printable_ratio(l_ascii)),
        ("Letter-level (inverted)", check_printable_ratio(l_ascii_inv)),
    ]

    print(f"\n{'Method':<40} {'Ratio':>8}  Verdict")
    print("-" * 65)
    for name, ratio in results:
        verdict = "INVESTIGATE" if ratio > 0.60 else "random-like"
        print(f"  {name:<38} {ratio:>7.1%}  {verdict}")


if __name__ == '__main__':
    main()
