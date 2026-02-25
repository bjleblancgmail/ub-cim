"""
Toggle Binary: Syllable-Letter Level

Each letter in each SYLLABLE carries that syllable's toggle state.
So if syllable "sal" is in toggle state 0 and "va" is state 1 and "tion" is state 0:
  sal  va  tion
  000  11  0000

This is different from:
- Syllable-level (one bit per syllable: 0, 1, 0)
- Word-level (one bit per word spread across all letters: 000000000)
- Letter-level (word's bit per letter: 000000000)

Runs on the dense block (20710-20771) and the full chapter (20509-20771).
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
    state = 0
    toggle_bits = []
    for i, actual in enumerate(pattern):
        expected = i % 2
        if actual != expected:
            state = 1 - state
        toggle_bits.append(state)
    return toggle_bits


def syllabify_word(word):
    """Split a word into approximate syllable groups of letters.
    Returns list of letter groups, one per syllable."""
    clean = re.sub(r'[^a-zA-Z]', '', word)
    if not clean:
        return []

    stress = get_stress(word)
    num_syls = len(stress)

    if num_syls <= 1:
        return [clean]

    # Simple syllabification: distribute letters roughly evenly across syllables
    # But try to split at consonant-vowel boundaries
    vowels = set('aeiouyAEIOUY')
    letters = list(clean)
    n = len(letters)

    if n <= num_syls:
        # Edge case: fewer letters than syllables (rare)
        return [c for c in letters] + [''] * (num_syls - n)

    # Find potential split points (before a consonant that precedes a vowel)
    split_candidates = []
    for i in range(1, n - 1):
        if letters[i] not in vowels and i + 1 < n and letters[i + 1] in vowels:
            split_candidates.append(i)
        elif letters[i] in vowels and letters[i - 1] in vowels and i > 1:
            split_candidates.append(i)

    # We need (num_syls - 1) split points
    needed = num_syls - 1

    if len(split_candidates) >= needed:
        # Space them as evenly as possible
        ideal_spacing = n / num_syls
        chosen = []
        for s in range(needed):
            target = ideal_spacing * (s + 1)
            best = min(split_candidates, key=lambda x: abs(x - target))
            if best not in chosen:
                chosen.append(best)
                split_candidates.remove(best)

        if len(chosen) == needed:
            chosen.sort()
            groups = []
            prev = 0
            for sp in chosen:
                groups.append(clean[prev:sp])
                prev = sp
            groups.append(clean[prev:])
            return groups

    # Fallback: split evenly by character count
    groups = []
    chars_per_syl = n / num_syls
    for s in range(num_syls):
        start = int(s * chars_per_syl)
        end = int((s + 1) * chars_per_syl)
        groups.append(clean[start:end])

    return groups


def get_syllable_letter_bits(sentence, pattern):
    """Each letter in each syllable carries that syllable's toggle state."""
    words = re.findall(r"[a-zA-Z']+", sentence)
    stresses = [get_stress(w) for w in words]
    toggle_bits = get_toggle_bits_variable(pattern)

    bits = ''
    syl_pos = 0
    details = []

    for w, stress in zip(words, stresses):
        syl_groups = syllabify_word(w)
        num_syls = len(stress)

        # Pad or trim syl_groups to match num_syls
        while len(syl_groups) < num_syls:
            syl_groups.append('')
        syl_groups = syl_groups[:num_syls]

        for i, group in enumerate(syl_groups):
            if syl_pos < len(toggle_bits):
                bit = toggle_bits[syl_pos]
                group_bits = str(bit) * len(group)
                bits += group_bits
                if group:
                    details.append((group, bit))
            syl_pos += 1

    return bits, details


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
        'done', 'self', 'free', 'true', 'real', 'word', 'life', 'body', 'eyes',
        'see', 'way', 'new', 'old', 'sin', 'joy', 'ask', 'say', 'let', 'put',
        'own', 'set', 'run', 'use', 'try', 'end', 'far', 'yet', 'why', 'who',
        'save', 'seek', 'teach', 'learn', 'hear', 'child', 'name', 'open',
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

    # Dense block
    block = [(i, s) for i, s in real if 20710 <= i <= 20771]
    # Full chapter
    chapter = [(i, s) for i, s in real if 20509 <= i <= 20771]

    for label, data in [("DENSE BLOCK (20710-20771)", block),
                        ("FULL CHAPTER (20509-20771)", chapter)]:
        print(f"\n{'=' * 80}")
        print(f"{label}: {len(data)} sentences")
        print("=" * 80)

        all_bits = ''
        for idx, s in data:
            pattern, _ = get_sentence_stress(s) if count_sentence_syllables(s) <= 60 else ([], [])
            if not pattern:
                # For very long sentences, build pattern manually
                words = re.findall(r"[a-zA-Z']+", s)
                pattern = []
                for w in words:
                    pattern.extend(get_stress(w))
            if not pattern:
                continue

            bits, details = get_syllable_letter_bits(s, pattern)
            all_bits += bits

        inv_bits = invert_bits(all_bits)

        print(f"\nTotal bits: {len(all_bits)}")
        print(f"Ones: {all_bits.count('1')} ({all_bits.count('1')/len(all_bits):.1%})")

        # Show first 20 sentences with details
        if label.startswith("DENSE"):
            print(f"\n--- First 15 sentences with syllable-letter details ---\n")
            count = 0
            for idx, s in data:
                if count >= 15:
                    break
                pattern, _ = get_sentence_stress(s) if count_sentence_syllables(s) <= 60 else ([], [])
                if not pattern:
                    words = re.findall(r"[a-zA-Z']+", s)
                    pattern = []
                    for w in words:
                        pattern.extend(get_stress(w))
                if not pattern:
                    continue

                bits, details = get_syllable_letter_bits(s, pattern)
                syl_count = len(pattern)
                is_ten = " *** 10-SYL ***" if syl_count == 10 else ""

                print(f"[{idx}] ({syl_count} syl){is_ten}")
                print(f"  {s[:120]}")
                detail_str = ' '.join([f"{grp}({b})" for grp, b in details])
                print(f"  Syllables: {detail_str}")
                print(f"  Bits: {bits}")
                print()
                count += 1

        # Show continuous string
        print(f"\n--- Continuous bit string (first 1000 bits) ---\n")
        print(all_bits[:1000])

        # Decode
        ascii_n = bits_to_ascii(all_bits)
        ascii_i = bits_to_ascii(inv_bits)

        print(f"\n--- 8-bit ASCII normal ({len(ascii_n)} chars) ---")
        print(f"  {ascii_n[:400]}")
        print(f"  Printable ratio: {check_printable_ratio(ascii_n):.1%}")

        print(f"\n--- 8-bit ASCII inverted ({len(ascii_i)} chars) ---")
        print(f"  {ascii_i[:400]}")
        print(f"  Printable ratio: {check_printable_ratio(ascii_i):.1%}")

        # 5-bit Bacon
        for blabel, bits in [("Normal", all_bits), ("Inverted", inv_bits)]:
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
            print(f"\n--- 5-bit Bacon {blabel} ---")
            print(f"  {decoded[:400]}")
            found = look_for_words(decoded)
            if found:
                unique = set(w for _, w in found)
                print(f"  Words found: {', '.join(sorted(unique))}")

        # Word search
        print(f"\n--- Word search in ASCII ---")
        for wlabel, decoded in [("Normal", ascii_n), ("Inverted", ascii_i)]:
            found = look_for_words(decoded)
            if found:
                unique = set(w for _, w in found)
                print(f"  {wlabel}: {', '.join(sorted(unique))}")
            else:
                print(f"  {wlabel}: no words found")

    # Summary
    print(f"\n{'=' * 80}")
    print("SUMMARY: ALL FOUR METHODS COMPARED (dense block)")
    print("=" * 80)

    # Recompute dense block for all methods for comparison
    block_data = [(i, s) for i, s in real if 20710 <= i <= 20771]
    syl_bits = ''
    word_bits = ''
    letter_bits = ''
    sylletter_bits = ''

    for idx, s in block_data:
        words = re.findall(r"[a-zA-Z']+", s)
        pattern = []
        for w in words:
            pattern.extend(get_stress(w))
        if not pattern:
            continue

        toggle = get_toggle_bits_variable(pattern)
        syl_bits += ''.join(str(b) for b in toggle)

        # Word level
        stresses = [get_stress(w) for w in words]
        pos = 0
        for w, stress in zip(words, stresses):
            if pos < len(toggle):
                word_bits += str(toggle[pos])
            pos += len(stress)

        # Letter level (word's bit per letter)
        pos = 0
        for w, stress in zip(words, stresses):
            if pos < len(toggle):
                clean = re.sub(r'[^a-zA-Z]', '', w)
                letter_bits += str(toggle[pos]) * len(clean)
            pos += len(stress)

        # Syllable-letter level
        sl_bits, _ = get_syllable_letter_bits(s, pattern)
        sylletter_bits += sl_bits

    methods = [
        ("1. Syllable-level", syl_bits),
        ("2. Word-level", word_bits),
        ("3. Letter-level (word bit)", letter_bits),
        ("4. Syllable-letter-level", sylletter_bits),
    ]

    print(f"\n{'Method':<35} {'Bits':>6} {'8-bit Print%':>13} {'Inv Print%':>11}")
    print("-" * 70)
    for name, bits in methods:
        a = bits_to_ascii(bits)
        ai = bits_to_ascii(invert_bits(bits))
        pr = check_printable_ratio(a)
        pri = check_printable_ratio(ai)
        print(f"  {name:<33} {len(bits):>6} {pr:>12.1%} {pri:>10.1%}")


if __name__ == '__main__':
    main()
