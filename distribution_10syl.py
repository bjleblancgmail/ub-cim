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


def main():
    filepath = "my-book/source-material/CourseUB/urtext_extracted.txt"

    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        text = f.read()

    sentences = extract_sentences(text)

    # Filter to real sentences only
    real = [(i, s) for i, s in enumerate(sentences) if is_real(s)]

    total_real = len(real)
    print(f"Total real sentences: {total_real}")

    # Divide into 10 equal segments (deciles)
    num_segments = 10
    segment_size = total_real // num_segments

    print(f"\n{'='*70}")
    print(f"DISTRIBUTION OF 10-SYLLABLE SENTENCES ACROSS THE TEXT")
    print(f"(Text divided into 10 equal segments of ~{segment_size} sentences each)")
    print(f"{'='*70}\n")

    print(f"{'Segment':<12} {'Sentences':<12} {'10-syl':<10} {'Rate':<10} {'Bar'}")
    print(f"{'-'*12} {'-'*12} {'-'*10} {'-'*10} {'-'*40}")

    segment_data = []
    for seg in range(num_segments):
        start = seg * segment_size
        end = start + segment_size if seg < num_segments - 1 else total_real
        segment_sents = real[start:end]

        ten_count = 0
        for _, s in segment_sents:
            if count_sentence_syllables(s) == 10:
                ten_count += 1

        rate = ten_count / len(segment_sents) * 100
        segment_data.append((seg, len(segment_sents), ten_count, rate))

        pct_label = f"{seg*10}-{(seg+1)*10}%"
        bar = '#' * int(rate * 5)
        print(f"{pct_label:<12} {len(segment_sents):<12} {ten_count:<10} {rate:>5.1f}%    {bar}")

    # Now do 20 segments for finer granularity
    num_segments = 20
    segment_size = total_real // num_segments

    print(f"\n{'='*70}")
    print(f"FINER DISTRIBUTION (20 segments of ~{segment_size} sentences)")
    print(f"{'='*70}\n")

    print(f"{'Segment':<12} {'10-syl':<10} {'Rate':<10} {'Bar'}")
    print(f"{'-'*12} {'-'*10} {'-'*10} {'-'*40}")

    for seg in range(num_segments):
        start = seg * segment_size
        end = start + segment_size if seg < num_segments - 1 else total_real
        segment_sents = real[start:end]

        ten_count = 0
        for _, s in segment_sents:
            if count_sentence_syllables(s) == 10:
                ten_count += 1

        rate = ten_count / len(segment_sents) * 100
        pct_label = f"{seg*5}-{(seg+1)*5}%"
        bar = '#' * int(rate * 5)
        print(f"{pct_label:<12} {ten_count:<10} {rate:>5.1f}%    {bar}")

    # Also show distribution of ALL syllable counts to see if 10 is special
    print(f"\n{'='*70}")
    print(f"SYLLABLE COUNT DISTRIBUTION (all real sentences)")
    print(f"{'='*70}\n")

    syl_counts = {}
    for _, s in real:
        syl = count_sentence_syllables(s)
        if 3 <= syl <= 40:  # reasonable sentence range
            syl_counts[syl] = syl_counts.get(syl, 0) + 1

    total_in_range = sum(syl_counts.values())
    print(f"{'Syllables':<12} {'Count':<10} {'Rate':<10} {'Bar'}")
    print(f"{'-'*12} {'-'*10} {'-'*10} {'-'*40}")

    for syl in sorted(syl_counts.keys()):
        count = syl_counts[syl]
        rate = count / total_in_range * 100
        bar = '#' * int(rate * 3)
        marker = ' <<<' if syl == 10 else ''
        print(f"{syl:<12} {count:<10} {rate:>5.1f}%    {bar}{marker}")

    # Compare first half vs second half
    print(f"\n{'='*70}")
    print(f"FIRST HALF vs SECOND HALF")
    print(f"{'='*70}\n")

    mid = total_real // 2
    first_half = real[:mid]
    second_half = real[mid:]

    first_ten = sum(1 for _, s in first_half if count_sentence_syllables(s) == 10)
    second_ten = sum(1 for _, s in second_half if count_sentence_syllables(s) == 10)

    print(f"First half:  {first_ten} ten-syllable sentences out of {len(first_half)} ({first_ten/len(first_half)*100:.1f}%)")
    print(f"Second half: {second_ten} ten-syllable sentences out of {len(second_half)} ({second_ten/len(second_half)*100:.1f}%)")
    print(f"Ratio: second half has {second_ten/first_ten:.1f}x as many")

    # Last 10% vs rest
    last_10 = real[int(total_real * 0.9):]
    rest = real[:int(total_real * 0.9)]

    last_ten = sum(1 for _, s in last_10 if count_sentence_syllables(s) == 10)
    rest_ten = sum(1 for _, s in rest if count_sentence_syllables(s) == 10)

    print(f"\nFirst 90%:   {rest_ten} ten-syllable sentences out of {len(rest)} ({rest_ten/len(rest)*100:.1f}%)")
    print(f"Last 10%:    {last_ten} ten-syllable sentences out of {len(last_10)} ({last_ten/len(last_10)*100:.1f}%)")
    if rest_ten > 0:
        rest_rate = rest_ten / len(rest)
        last_rate = last_ten / len(last_10)
        print(f"The last 10% has {last_rate/rest_rate:.1f}x the rate of the first 90%")


if __name__ == '__main__':
    main()
