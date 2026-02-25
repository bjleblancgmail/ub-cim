"""
Toggle Binary Analysis on the FULL last chapter of the urtext.
Sentences 20509-20771 (July 16, 1968 through end of real text).
ALL sentence lengths included in sequence.
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
    words = re.findall(r"[a-zA-Z']+", sentence)
    pattern = []
    word_list = []
    for w in words:
        stress = get_stress(w)
        word_list.append((w, stress))
        pattern.extend(stress)
    return pattern, word_list


def get_word_level_bits(sentence, pattern):
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


def look_for_words(text):
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
        'save', 'seek', 'teach', 'learn', 'hear', 'child', 'name', 'open',
        'still', 'keep', 'hold', 'turn', 'help', 'walk', 'born', 'rest',
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

    # Full last chapter: 20509 to 20771
    block = [(i, s) for i, s in real if 20509 <= i <= 20771]

    print(f"Full last chapter: {len(block)} sentences")
    print(f"Range: indices {block[0][0]}-{block[-1][0]}")

    ten_count = sum(1 for i, s in block if count_sentence_syllables(s) == 10)
    print(f"10-syllable sentences in block: {ten_count} ({ten_count/len(block)*100:.1f}%)")
    print()

    # Collect all toggle bits
    all_syl_toggle = ''
    all_word_bits_list = []
    all_letter_bits = ''
    total_syllables = 0

    for idx, s in block:
        pattern, word_list = get_full_stress_pattern(s)
        if not pattern:
            continue
        total_syllables += len(pattern)
        toggle = get_toggle_bits_variable(pattern)
        wb = get_word_level_bits(s, pattern)

        all_syl_toggle += ''.join(str(b) for b in toggle)
        all_word_bits_list.extend(wb)
        all_letter_bits += get_letter_level_bits(wb)

    word_bit_str = ''.join(str(b) for w, b in all_word_bits_list)
    word_bit_inv = invert_bits(word_bit_str)
    syl_inv = invert_bits(all_syl_toggle)
    letter_inv = invert_bits(all_letter_bits)

    print(f"Total syllables: {total_syllables}")
    print(f"Total words: {len(all_word_bits_list)}")
    print(f"Total letters: {len(all_letter_bits)}")

    # === DECODE ALL METHODS ===
    print(f"\n{'=' * 80}")
    print("SYLLABLE-LEVEL TOGGLE")
    print("=" * 80)

    print(f"Bits: {len(all_syl_toggle)}")
    print(f"Ones: {all_syl_toggle.count('1')} ({all_syl_toggle.count('1')/len(all_syl_toggle):.1%})")

    s_ascii = bits_to_ascii(all_syl_toggle)
    s_ascii_inv = bits_to_ascii(syl_inv)

    print(f"\n8-bit ASCII normal ({len(s_ascii)} chars):")
    print(f"  {s_ascii[:400]}")
    print(f"\nPrintable ratio: {check_printable_ratio(s_ascii):.1%}")

    print(f"\n8-bit ASCII inverted ({len(s_ascii_inv)} chars):")
    print(f"  {s_ascii_inv[:400]}")
    print(f"\nPrintable ratio: {check_printable_ratio(s_ascii_inv):.1%}")

    # === WORD LEVEL ===
    print(f"\n{'=' * 80}")
    print("WORD-LEVEL TOGGLE")
    print("=" * 80)

    print(f"Bits: {len(word_bit_str)}")
    w_ascii = bits_to_ascii(word_bit_str)
    w_ascii_inv = bits_to_ascii(word_bit_inv)

    print(f"\n8-bit ASCII normal ({len(w_ascii)} chars):")
    print(f"  {w_ascii[:400]}")
    print(f"\nPrintable ratio: {check_printable_ratio(w_ascii):.1%}")

    print(f"\n8-bit ASCII inverted ({len(w_ascii_inv)} chars):")
    print(f"  {w_ascii_inv[:400]}")
    print(f"\nPrintable ratio: {check_printable_ratio(w_ascii_inv):.1%}")

    # === LETTER LEVEL ===
    print(f"\n{'=' * 80}")
    print("LETTER-LEVEL TOGGLE")
    print("=" * 80)

    print(f"Bits: {len(all_letter_bits)}")
    l_ascii = bits_to_ascii(all_letter_bits)
    l_ascii_inv = bits_to_ascii(letter_inv)

    print(f"\n8-bit ASCII normal ({len(l_ascii)} chars):")
    print(f"  {l_ascii[:400]}")
    print(f"\nPrintable ratio: {check_printable_ratio(l_ascii):.1%}")

    print(f"\n8-bit ASCII inverted ({len(l_ascii_inv)} chars):")
    print(f"  {l_ascii_inv[:400]}")
    print(f"\nPrintable ratio: {check_printable_ratio(l_ascii_inv):.1%}")

    # === 5-BIT BACON ===
    print(f"\n{'=' * 80}")
    print("5-BIT BACON CIPHER")
    print("=" * 80)

    for label, bits in [("Syllable toggle", all_syl_toggle),
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
        decoded = ''.join(chars)
        print(f"\n{label} ({len(decoded)} chars):")
        print(f"  {decoded[:400]}")

        # Look for 3+ letter words
        found = look_for_words(decoded)
        if found:
            unique_words = set(w for _, w in found)
            print(f"  Words found ({len(found)} total, {len(unique_words)} unique): ", end='')
            for word in sorted(unique_words):
                count = sum(1 for _, w in found if w == word)
                if count > 1:
                    print(f"'{word}'x{count} ", end='')
                else:
                    print(f"'{word}' ", end='')
            print()

    # === WORD SEARCH IN ALL ASCII DECODES ===
    print(f"\n{'=' * 80}")
    print("WORD SEARCH IN ASCII DECODES")
    print("=" * 80)

    for label, decoded in [("Syl normal", s_ascii), ("Syl inverted", s_ascii_inv),
                           ("Word normal", w_ascii), ("Word inverted", w_ascii_inv)]:
        found = look_for_words(decoded)
        unique = set(w for _, w in found)
        if found:
            print(f"\n  {label} ({len(found)} matches, {len(unique)} unique words):")
            for pos, word in found[:20]:
                ctx = decoded[max(0,pos-4):pos+len(word)+4]
                print(f"    '{word}' at {pos}: ...{ctx}...")

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

    print(f"\nEnglish text = ~85%+. Random noise = ~37%.")
    print(f"\nBlock stats: {len(block)} sentences, {total_syllables} syllables, {len(all_word_bits_list)} words")


if __name__ == '__main__':
    main()
