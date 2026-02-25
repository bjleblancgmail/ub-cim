import re
import sys

def count_syllables(word):
    """Heuristic syllable counter for English words."""
    word = word.lower().strip()
    if not word or not re.search(r'[a-z]', word):
        return 0

    # Common exceptions
    exceptions = {
        'the': 1, 'a': 1, 'an': 1, 'i': 1, 'my': 1, 'our': 1,
        'your': 1, 'their': 1, 'its': 1, 'his': 1, 'her': 1,
        'are': 1, 'were': 1, 'fire': 1, 'hire': 1, 'tire': 1,
        'every': 3, 'everything': 4, 'everyone': 4, 'everywhere': 4,
        'being': 2, 'seeing': 2, 'doing': 2, 'going': 2,
        'idea': 3, 'ideal': 3, 'real': 1, 'really': 3,
        'miracle': 3, 'miracles': 3, 'spiritual': 4, 'experience': 4,
        'prayer': 2, 'power': 2, 'flower': 2, 'tower': 2,
        'hour': 1, 'our': 1, 'sure': 1, 'pure': 1,
        'love': 1, 'loved': 1, 'above': 2, 'move': 1,
        'have': 1, 'give': 1, 'live': 1, 'come': 1,
        'some': 1, 'done': 1, 'gone': 1, 'none': 1,
        'one': 1, 'once': 1, 'where': 1, 'there': 1,
        'here': 1, 'were': 1, 'bore': 1, 'more': 1,
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
        'never': 2, 'ever': 2, 'every': 3,
        'over': 2, 'under': 2, 'other': 2,
        'father': 2, 'brother': 2, 'mother': 2,
        'spirit': 2, 'merit': 2, 'inherit': 3,
        'world': 1, 'word': 1, 'work': 1,
    }

    clean = re.sub(r'[^a-z]', '', word)
    if clean in exceptions:
        return exceptions[clean]

    # Remove trailing silent e
    if clean.endswith('e') and len(clean) > 2 and clean[-2] not in 'aeiou':
        # But not if it's 'le' preceded by consonant (e.g., 'table')
        if clean.endswith('le') and len(clean) > 3 and clean[-3] not in 'aeiou':
            pass  # keep the e, 'le' is a syllable
        else:
            clean = clean[:-1]

    # Count vowel groups
    count = len(re.findall(r'[aeiouy]+', clean))

    # Adjust for common patterns
    if clean.endswith('ed') and len(clean) > 3 and clean[-3] not in 'td':
        count -= 1  # 'ed' is usually silent after non t/d
    if clean.endswith('es') and len(clean) > 3 and clean[-3] not in 'sxz' and not clean.endswith('ies'):
        count -= 1
    if clean.endswith('ion'):
        count += 0  # already counted
    if re.search(r'ia|io|iu|eo|ua|ue|ui', clean):
        count += 1  # these are usually separate syllables

    return max(1, count)


def count_sentence_syllables(sentence):
    """Count syllables in a sentence."""
    words = re.findall(r"[a-zA-Z']+", sentence)
    total = sum(count_syllables(w) for w in words)
    return total


def extract_sentences(text):
    """Split text into sentences."""
    # Replace tabs with spaces
    text = text.replace('\t', ' ')
    # Split on sentence-ending punctuation
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]


def main():
    filepath = sys.argv[1] if len(sys.argv) > 1 else "my-book/source-material/CourseUB/urtext_extracted.txt"

    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        text = f.read()

    sentences = extract_sentences(text)

    ten_syllable = []
    for s in sentences:
        # Skip very short or non-text
        clean = re.sub(r'[^a-zA-Z\s]', '', s).strip()
        words = clean.split()
        if len(words) < 3:  # skip fragments
            continue

        syl_count = count_sentence_syllables(s)
        if syl_count == 10:
            ten_syllable.append(s)

    print(f"Total sentences analyzed: {len(sentences)}")
    print(f"Sentences with exactly 10 syllables: {len(ten_syllable)}")
    print(f"\n{'='*60}")
    print("ALL 10-SYLLABLE SENTENCES:")
    print(f"{'='*60}\n")

    for i, s in enumerate(ten_syllable, 1):
        # Show syllable breakdown
        words = re.findall(r"[a-zA-Z']+", s)
        breakdown = [(w, count_syllables(w)) for w in words]
        bd_str = " + ".join(f"{w}({c})" for w, c in breakdown)
        print(f"{i}. {s}")
        print(f"   [{bd_str}]")
        print()


if __name__ == '__main__':
    main()
