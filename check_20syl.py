import re


def count_syllables(word):
    word = word.lower().strip()
    if not word or not re.search(r'[a-z]', word):
        return 0
    exceptions = {
        'the': 1, 'a': 1, 'an': 1, 'i': 1, 'my': 1, 'our': 1,
        'your': 1, 'their': 1, 'its': 1, 'his': 1, 'her': 1,
        'are': 1, 'were': 1, 'every': 3, 'being': 2, 'real': 1,
        'miracle': 3, 'miracles': 3, 'prayer': 2, 'power': 2,
        'hour': 1, 'love': 1, 'have': 1, 'give': 1, 'live': 1,
        'come': 1, 'some': 1, 'done': 1, 'gone': 1, 'none': 1,
        'one': 1, 'once': 1, 'where': 1, 'there': 1, 'here': 1,
        'more': 1, 'before': 2, 'therefore': 3,
        'true': 1, 'heaven': 2, 'given': 2, 'even': 2,
        'never': 2, 'ever': 2, 'over': 2, 'under': 2, 'other': 2,
        'father': 2, 'brother': 2, 'spirit': 2,
        'world': 1, 'word': 1, 'certainty': 3,
        'ordained': 2, 'content': 2,
        'spiritual': 4, 'experience': 4,
        'consciousness': 4, 'unconscious': 3,
        'different': 3, 'difference': 3,
        'impossible': 4, 'possible': 3,
        'necessary': 4, 'temporary': 4,
        'perception': 3, 'correction': 3,
        'salvation': 3, 'creation': 3,
        'illusion': 3, 'communion': 3,
        'atonement': 3, 'forgiveness': 3,
        'awareness': 3, 'beautiful': 3,
        'innocent': 3, 'difficult': 3,
        'meaningless': 3, 'meaningful': 3,
        'communication': 5, 'relationship': 4,
        'understanding': 4, 'recognition': 4,
        'accordingly': 4, 'responsible': 4,
        'ultimately': 4, 'naturally': 4,
        'eternity': 4, 'reality': 4,
    }
    clean = re.sub(r'[^a-z]', '', word)
    if clean in exceptions:
        return exceptions[clean]
    w = clean
    if w.endswith('e') and len(w) > 2 and w[-2] not in 'aeiou':
        if w.endswith('le') and len(w) > 3 and w[-3] not in 'aeiou':
            pass
        else:
            w = w[:-1]
    count = len(re.findall(r'[aeiouy]+', w))
    if w.endswith('ed') and len(w) > 3 and w[-3] not in 'td':
        count -= 1
    if w.endswith('es') and len(w) > 3 and w[-3] not in 'sxz' and not w.endswith('ies'):
        count -= 1
    if re.search(r'ia|io|iu|eo|ua|ue|ui', w):
        count += 1
    return max(1, count)


def count_sentence_syllables(sentence):
    words = re.findall(r"[a-zA-Z']+", sentence)
    return sum(count_syllables(w) for w in words)


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


def find_split_point(sentence):
    """Try to split a sentence at a natural midpoint (comma, semicolon, 'and', 'but', 'or', 'for', 'yet', 'nor')
    and check if each half is 10 syllables."""
    words = re.findall(r"[a-zA-Z']+|[,;:]", sentence)

    # Build a list of (word, syllable_count, cumulative_syllables)
    items = []
    cumul = 0
    for w in words:
        if w in (',', ';', ':'):
            items.append((w, 0, cumul, True))  # punctuation marker
        else:
            sc = count_syllables(w)
            cumul += sc
            items.append((w, sc, cumul, False))

    total = cumul
    if total != 20:
        return None, None, None

    # Look for split points where cumulative = 10
    best_splits = []
    for idx, (w, sc, cum, is_punct) in enumerate(items):
        if cum == 10:
            # Check if this is a natural break point
            # Is this word followed by punctuation or a conjunction?
            natural = False
            reason = ""

            # Check if next item is punctuation
            if idx + 1 < len(items) and items[idx + 1][3]:  # next is punctuation
                natural = True
                reason = f"after '{w}' + punct '{items[idx+1][0]}'"
            # Check if next word is a conjunction
            elif idx + 1 < len(items) and items[idx + 1][0].lower() in ('and', 'but', 'or', 'for', 'yet', 'nor', 'so', 'if', 'when', 'where', 'while', 'though', 'that', 'which', 'who'):
                natural = True
                reason = f"after '{w}' + conj '{items[idx+1][0]}'"
            # Check if current word ends the clause naturally
            else:
                reason = f"after '{w}' (mid-phrase)"

            best_splits.append((idx, natural, reason))

        # Also check at punctuation points
        if is_punct and idx > 0:
            prev_cum = items[idx - 1][2] if not items[idx - 1][3] else (items[idx - 2][2] if idx >= 2 else 0)
            # Already handled above

    if not best_splits:
        return None, None, None

    # Prefer natural splits
    natural_splits = [s for s in best_splits if s[1]]
    if natural_splits:
        split_idx, _, reason = natural_splits[0]
    else:
        split_idx, _, reason = best_splits[0]

    # Reconstruct the two halves from the original sentence
    # Find the character position of the split
    word_positions = []
    for m in re.finditer(r"[a-zA-Z']+|[,;:]", sentence):
        word_positions.append((m.start(), m.end(), m.group()))

    if split_idx < len(word_positions):
        split_char = word_positions[split_idx][1]
        # If next char is punctuation, include it
        if split_char < len(sentence) and sentence[split_char] in ',;:':
            split_char += 1
        first_half = sentence[:split_char].strip()
        second_half = sentence[split_char:].strip()
        # Clean up leading punctuation/space from second half
        second_half = re.sub(r'^[,;:\s]+', '', second_half).strip()
        return first_half, second_half, reason

    return None, None, None


def main():
    filepath = "my-book/source-material/CourseUB/urtext_extracted.txt"

    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        text = f.read()

    sentences = extract_sentences(text)
    real = [s for s in sentences if is_real(s)]

    twenty_syl = []
    for s in real:
        if count_sentence_syllables(s) == 20:
            twenty_syl.append(s)

    print(f"Total 20-syllable sentences: {len(twenty_syl)}")
    print()

    # Try to split each one at 10+10
    natural_10_10 = []
    forced_10_10 = []
    no_split = []

    for s in twenty_syl:
        first, second, reason = find_split_point(s)
        if first is not None:
            # Verify both halves are 10
            fc = count_sentence_syllables(first)
            sc = count_sentence_syllables(second)
            if fc == 10 and sc == 10:
                if 'punct' in reason or 'conj' in reason:
                    natural_10_10.append((s, first, second, reason))
                else:
                    forced_10_10.append((s, first, second, reason))
            else:
                no_split.append(s)
        else:
            no_split.append(s)

    total_splits = len(natural_10_10) + len(forced_10_10)
    print(f"Split naturally into 10+10 (at punctuation or conjunction): {len(natural_10_10)}")
    print(f"Split at 10+10 (mid-phrase): {len(forced_10_10)}")
    print(f"Total that split into 10+10: {total_splits} ({total_splits/len(twenty_syl)*100:.1f}%)")
    print(f"Cannot split into 10+10: {len(no_split)} ({len(no_split)/len(twenty_syl)*100:.1f}%)")

    print(f"\n{'='*70}")
    print(f"NATURAL 10+10 SPLITS (at punctuation or conjunction)")
    print(f"{'='*70}\n")

    for i, (orig, first, second, reason) in enumerate(natural_10_10, 1):
        print(f"{i}.")
        print(f"   {first}")
        print(f"   {second}")
        print()

    print(f"\n{'='*70}")
    print(f"MID-PHRASE 10+10 SPLITS")
    print(f"{'='*70}\n")

    for i, (orig, first, second, reason) in enumerate(forced_10_10[:50], 1):
        print(f"{i}.")
        print(f"   {first}")
        print(f"   {second}")
        print()

    # Compare: what percentage of 18, 19, 21, 22 syllable sentences split into equal halves?
    print(f"\n{'='*70}")
    print(f"COMPARISON: Do other even-syllable counts split into equal halves?")
    print(f"{'='*70}\n")

    for target in [16, 18, 20, 22, 24]:
        half = target // 2
        target_sents = [s for s in real if count_sentence_syllables(s) == target]
        split_count = 0
        for s in target_sents:
            words = re.findall(r"[a-zA-Z']+", s)
            cumul = 0
            found = False
            for w in words:
                cumul += count_syllables(w)
                if cumul == half:
                    found = True
                    break
            if found:
                split_count += 1
        pct = split_count / len(target_sents) * 100 if target_sents else 0
        marker = " <<<" if target == 20 else ""
        print(f"  {target} syllables: {split_count}/{len(target_sents)} split into {half}+{half} ({pct:.1f}%){marker}")


if __name__ == '__main__':
    main()
