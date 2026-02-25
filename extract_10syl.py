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
        'awareness': 3,
        'denial': 3, 'negation': 3,
        'certainty': 3, 'eternity': 4,
        'reality': 4, 'ability': 4,
        'responsibility': 6,
        'accordingly': 4, 'responsible': 4,
        'ultimately': 4, 'immediately': 5,
        'ordained': 2, 'content': 2,
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

    results = []
    for idx, s in enumerate(sentences):
        if not is_real(s):
            continue
        if count_sentence_syllables(s) == 10:
            # Clean up: strip leading/trailing whitespace, normalize spaces
            clean = ' '.join(s.split())
            results.append((idx, clean))

    outpath = "my-book/source-material/research/acim-urtext-10-syllable-sentences.md"
    with open(outpath, 'w', encoding='utf-8') as f:
        f.write("# All 10-Syllable Sentences in the ACIM Urtext\n\n")
        f.write(f"**Total:** {len(results)} sentences\n")
        f.write(f"**Source:** urtext_extracted.txt\n")
        f.write(f"**Date:** 2026-02-24\n\n")
        f.write("Listed in order of appearance in the text.\n\n")
        f.write("---\n\n")

        for i, (idx, s) in enumerate(results, 1):
            f.write(f"{i}. {s}\n")

    print(f"Extracted {len(results)} ten-syllable sentences to {outpath}")


if __name__ == '__main__':
    main()
