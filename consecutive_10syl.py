import re


def count_syllables(word):
    word = word.lower().strip()
    if not word or not re.search(r'[a-z]', word):
        return 0

    exceptions = {
        'the': 1, 'a': 1, 'an': 1, 'i': 1, 'my': 1, 'our': 1,
        'your': 1, 'their': 1, 'its': 1, 'his': 1, 'her': 1,
        'are': 1, 'were': 1, 'fire': 1, 'hire': 1, 'tire': 1,
        'every': 3, 'everything': 4, 'everyone': 4, 'everywhere': 4,
        'being': 2, 'seeing': 2, 'doing': 2, 'going': 2,
        'idea': 3, 'ideal': 3, 'real': 1, 'really': 3,
        'miracle': 3, 'miracles': 3, 'spiritual': 4, 'experience': 4,
        'prayer': 2, 'power': 2, 'flower': 2, 'tower': 2,
        'hour': 1, 'sure': 1, 'pure': 1,
        'love': 1, 'loved': 1, 'above': 2, 'move': 1,
        'have': 1, 'give': 1, 'live': 1, 'come': 1,
        'some': 1, 'done': 1, 'gone': 1, 'none': 1,
        'one': 1, 'once': 1, 'where': 1, 'there': 1,
        'here': 1, 'bore': 1, 'more': 1,
        'before': 2, 'therefore': 3, 'ignore': 2,
        'create': 2, 'created': 3, 'creating': 3,
        'separate': 3, 'separated': 4,
        'communicate': 4, 'communicated': 5,
        'true': 1, 'blue': 1, 'due': 1,
        'people': 2, 'little': 2, 'simple': 2,
        'knowledge': 2, 'believed': 2, 'received': 2,
        'divine': 2, 'define': 2, 'refine': 2,
        'nature': 2, 'creature': 2, 'feature': 2,
        'atonement': 3, 'forgiveness': 3,
        'consciousness': 4, 'unconscious': 3,
        'different': 3, 'difference': 3,
        'establish': 3, 'established': 3,
        'impossible': 4, 'possible': 3,
        'necessary': 4, 'temporary': 4,
        'heaven': 2, 'given': 2, 'even': 2,
        'never': 2, 'ever': 2,
        'over': 2, 'under': 2, 'other': 2,
        'father': 2, 'brother': 2, 'mother': 2,
        'spirit': 2, 'merit': 2, 'inherit': 3,
        'world': 1, 'word': 1, 'work': 1,
        'easily': 4, 'family': 3, 'usually': 4,
        'beautiful': 3, 'meaningful': 3, 'meaningless': 3,
        'innocent': 3, 'difficult': 3,
        'special': 2, 'especially': 4,
        'actual': 3, 'actually': 4,
        'natural': 3, 'naturally': 4,
        'general': 3, 'generally': 4,
        'original': 4, 'originally': 5,
        'particular': 4, 'particularly': 5,
        'individual': 5, 'individually': 6,
        'communication': 5,
        'relationship': 4,
        'understanding': 4,
        'recognition': 4,
        'resurrection': 4,
        'crucifixion': 4,
        'perception': 3, 'correction': 3,
        'salvation': 3, 'creation': 3,
        'illusion': 3, 'delusion': 3, 'confusion': 3,
        'decision': 3, 'division': 3, 'communion': 3,
        'atonement': 3, 'awareness': 3,
        'denial': 3, 'negation': 3,
        'certainty': 3, 'eternity': 4,
        'reality': 4, 'ability': 4,
        'responsibility': 6,
        'accordingly': 4, 'responsible': 4,
        'ultimately': 4, 'immediately': 5,
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


def is_real_sentence(s):
    """Filter out garbage/binary data."""
    clean = re.sub(r'[^a-zA-Z\s]', '', s).strip()
    words = clean.split()
    if len(words) < 3:
        return False
    # Check that most characters are letters/spaces/punctuation
    alpha_count = sum(1 for c in s if c.isalpha() or c.isspace())
    if alpha_count < len(s) * 0.6:
        return False
    return True


def main():
    filepath = "my-book/source-material/CourseUB/urtext_extracted.txt"

    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        text = f.read()

    sentences = extract_sentences(text)

    # Tag each sentence
    tagged = []
    for idx, s in enumerate(sentences):
        if not is_real_sentence(s):
            tagged.append((idx, s, 0, False))
            continue
        syl_count = count_sentence_syllables(s)
        tagged.append((idx, s, syl_count, syl_count == 10))

    # Find consecutive groups of 10-syllable sentences
    groups = []
    current_group = []

    for idx, s, syl, is_ten in tagged:
        if is_ten:
            current_group.append((idx, s))
        else:
            if len(current_group) >= 2:
                groups.append(current_group)
            current_group = []

    # Don't forget the last group
    if len(current_group) >= 2:
        groups.append(current_group)

    # Sort by group size descending
    groups.sort(key=lambda g: len(g), reverse=True)

    print(f"Total consecutive groups of 10-syllable sentences: {len(groups)}")
    print()

    # Count by size
    sizes = {}
    for g in groups:
        sz = len(g)
        sizes[sz] = sizes.get(sz, 0) + 1

    for sz in sorted(sizes.keys(), reverse=True):
        print(f"  Groups of {sz}: {sizes[sz]}")
    print()

    print("=" * 70)
    print("ALL CONSECUTIVE 10-SYLLABLE GROUPINGS")
    print("=" * 70)

    # Re-sort by position in text for display
    groups.sort(key=lambda g: g[0][0])

    for gi, group in enumerate(groups, 1):
        size = len(group)
        print(f"\n--- Group {gi} ({size} consecutive lines) ---\n")
        for idx, s in group:
            print(f"  {s}")
        print()


if __name__ == '__main__':
    main()
