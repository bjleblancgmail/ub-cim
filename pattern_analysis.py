import re
from collections import Counter


def load_sentences(filepath):
    sentences = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            m = re.match(r'^\d+\.\s+(.+)$', line)
            if m:
                sentences.append(m.group(1))
    return sentences


def main():
    filepath = "my-book/source-material/research/acim-urtext-10-syllable-sentences.md"
    sentences = load_sentences(filepath)
    print(f"Total sentences: {len(sentences)}\n")

    # 1. FIRST WORD ANALYSIS
    print("=" * 70)
    print("1. FIRST WORD FREQUENCY")
    print("=" * 70)
    first_words = []
    for s in sentences:
        words = re.findall(r"[a-zA-Z']+", s)
        if words:
            first_words.append(words[0].lower())

    fw_counts = Counter(first_words)
    print(f"\nTop 30 first words:")
    for word, count in fw_counts.most_common(30):
        bar = '#' * count
        print(f"  {word:<15} {count:>4}  {bar}")

    # 2. LAST WORD ANALYSIS
    print(f"\n{'=' * 70}")
    print("2. LAST WORD FREQUENCY")
    print("=" * 70)
    last_words = []
    for s in sentences:
        words = re.findall(r"[a-zA-Z']+", s)
        if words:
            last_words.append(words[-1].lower())

    lw_counts = Counter(last_words)
    print(f"\nTop 30 last words:")
    for word, count in lw_counts.most_common(30):
        bar = '#' * count
        print(f"  {word:<15} {count:>4}  {bar}")

    # 3. ACROSTIC CHECK - first letters
    print(f"\n{'=' * 70}")
    print("3. ACROSTIC CHECK (first letters of each sentence)")
    print("=" * 70)
    first_letters = []
    for s in sentences:
        words = re.findall(r"[a-zA-Z]", s)
        if words:
            first_letters.append(words[0].upper())

    acrostic = ''.join(first_letters)
    print(f"\nFirst 100 letters: {acrostic[:100]}")
    print(f"Last 100 letters:  {acrostic[-100:]}")

    # Check for repeated sequences
    print(f"\nLetter frequency in acrostic:")
    letter_counts = Counter(acrostic)
    for letter, count in sorted(letter_counts.items()):
        pct = count / len(acrostic) * 100
        bar = '#' * int(pct * 2)
        print(f"  {letter}: {count:>4} ({pct:>4.1f}%)  {bar}")

    # 4. KEY WORD FREQUENCY across all sentences
    print(f"\n{'=' * 70}")
    print("4. MOST FREQUENT CONTENT WORDS")
    print("=" * 70)
    stop_words = {'the', 'a', 'an', 'is', 'it', 'in', 'to', 'of', 'and', 'but',
                  'or', 'for', 'not', 'no', 'on', 'at', 'by', 'with', 'from',
                  'as', 'if', 'so', 'yet', 'that', 'this', 'these', 'those',
                  'he', 'she', 'we', 'they', 'i', 'me', 'him', 'her', 'us',
                  'them', 'you', 'your', 'my', 'his', 'our', 'their', 'its',
                  'who', 'whom', 'what', 'which', 'where', 'when', 'how', 'why',
                  'be', 'been', 'am', 'are', 'was', 'were', 'has', 'had', 'have',
                  'do', 'does', 'did', 'will', 'would', 'shall', 'should',
                  'can', 'could', 'may', 'might', 'must', 'than',
                  'all', 'each', 'both', 'such', 'only', 'own',
                  'nor', 'too', 'very', 'just', 's', 't', 'hs', 'tc'}

    all_words = []
    for s in sentences:
        words = re.findall(r"[a-zA-Z']+", s)
        for w in words:
            wl = w.lower().strip("'")
            if wl not in stop_words and len(wl) > 1:
                all_words.append(wl)

    word_counts = Counter(all_words)
    print(f"\nTop 40 content words:")
    for word, count in word_counts.most_common(40):
        bar = '#' * (count // 2)
        print(f"  {word:<15} {count:>4}  {bar}")

    # 5. THEMATIC GROUPINGS
    print(f"\n{'=' * 70}")
    print("5. THEMATIC PATTERNS")
    print("=" * 70)

    themes = {
        'God/Father': ['god', 'father', 'creator'],
        'Son/Christ': ['son', 'christ', 'brother', 'brothers'],
        'Holy Spirit': ['holy', 'spirit'],
        'Love': ['love', 'loved', 'loving', 'loves'],
        'Fear': ['fear', 'afraid', 'fearful', 'fears'],
        'Sin/Guilt': ['sin', 'guilt', 'sins', 'guilty', 'sinned'],
        'Death': ['death', 'die', 'dying', 'dead', 'died'],
        'Life': ['life', 'live', 'living', 'lives', 'alive'],
        'Dream': ['dream', 'dreams', 'dreaming', 'dreamer'],
        'Truth': ['truth', 'true', 'truly'],
        'Peace': ['peace', 'peaceful'],
        'World': ['world'],
        'Mind': ['mind', 'minds', 'thinking', 'thought', 'thoughts', 'think'],
        'Will': ['will', 'wills', 'willed', 'willing'],
        'Forgiveness': ['forgive', 'forgiveness', 'forgiven'],
        'Healing': ['heal', 'healed', 'healing', 'heals'],
        'Miracle': ['miracle', 'miracles'],
        'Light/Dark': ['light', 'dark', 'darkness'],
        'Heaven/Hell': ['heaven', 'hell'],
        'Salvation': ['salvation', 'saved', 'save'],
        'Illusion': ['illusion', 'illusions'],
        'Ego': ['ego'],
        'Atonement': ['atonement'],
        'Body': ['body', 'bodies'],
        'Attack': ['attack', 'attacks', 'attacking', 'attacked'],
    }

    print()
    for theme, keywords in themes.items():
        count = 0
        for s in sentences:
            sl = s.lower()
            if any(re.search(r'\b' + kw + r'\b', sl) for kw in keywords):
                count += 1
        bar = '#' * (count // 2)
        print(f"  {theme:<20} {count:>4} sentences  {bar}")

    # 6. SENTENCES THAT START WITH "AND"
    print(f"\n{'=' * 70}")
    print("6. SENTENCES STARTING WITH 'AND' (biblical/poetic connector)")
    print("=" * 70)
    and_sentences = [s for s in sentences if s.lower().startswith('and ')]
    print(f"\nTotal: {len(and_sentences)} ({len(and_sentences)/len(sentences)*100:.1f}%)\n")
    # Show last 20 (likely most poetic)
    print("Last 20:")
    for s in and_sentences[-20:]:
        print(f"  {s}")

    # 7. QUESTION vs STATEMENT
    print(f"\n{'=' * 70}")
    print("7. QUESTIONS vs STATEMENTS")
    print("=" * 70)
    questions = [s for s in sentences if s.rstrip().endswith('?')]
    statements = [s for s in sentences if not s.rstrip().endswith('?')]
    print(f"\nQuestions:   {len(questions)} ({len(questions)/len(sentences)*100:.1f}%)")
    print(f"Statements:  {len(statements)} ({len(statements)/len(sentences)*100:.1f}%)")
    print(f"\nSample questions:")
    for s in questions[-15:]:
        print(f"  {s}")

    # 8. PARALLEL STRUCTURES (sentences sharing first 3+ words)
    print(f"\n{'=' * 70}")
    print("8. PARALLEL STRUCTURES (shared openings)")
    print("=" * 70)
    openings = {}
    for s in sentences:
        words = s.split()[:3]
        key = ' '.join(words).lower()
        if key not in openings:
            openings[key] = []
        openings[key].append(s)

    parallels = {k: v for k, v in openings.items() if len(v) >= 2}
    print(f"\nOpening phrases appearing 2+ times: {len(parallels)}\n")
    for key, sents in sorted(parallels.items(), key=lambda x: -len(x[1])):
        if len(sents) >= 3:
            print(f'  "{key}..." ({len(sents)} times):')
            for s in sents:
                print(f"    {s}")
            print()


if __name__ == '__main__':
    main()
