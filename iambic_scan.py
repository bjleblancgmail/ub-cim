import re
import sys

# CMU-style stress patterns for common words
# 0 = unstressed, 1 = stressed, 2 = secondary stress
# For iambic pentameter we care about: unstressed(0) stressed(1) alternating
STRESS_DICT = {
    # Articles, prepositions, conjunctions (unstressed)
    'a': [0], 'an': [0], 'the': [0], 'of': [0], 'in': [0], 'to': [0],
    'for': [0], 'and': [0], 'but': [0], 'or': [0], 'nor': [0],
    'on': [0], 'at': [0], 'by': [0], 'with': [0], 'from': [0],
    'as': [0], 'if': [0], 'so': [0], 'yet': [0], 'than': [0],
    'that': [0], 'this': [0], 'these': [0], 'those': [0],
    'it': [0], 'its': [0], 'is': [0], 'was': [0], 'are': [0],
    'were': [0], 'be': [0], 'been': [0], 'am': [0],
    'has': [0], 'had': [0], 'have': [0], 'do': [0], 'does': [0], 'did': [0],
    'will': [0], 'would': [0], 'shall': [0], 'should': [0],
    'can': [0], 'could': [0], 'may': [0], 'might': [0], 'must': [0],
    'not': [1], 'no': [1], 'nor': [0],
    'he': [0], 'she': [0], 'we': [0], 'they': [0], 'i': [0],
    'me': [0], 'him': [0], 'her': [0], 'us': [0], 'them': [0],
    'you': [0], 'your': [0], 'my': [0], 'his': [0], 'our': [0], 'their': [0],
    'who': [0], 'whom': [0], 'what': [0], 'which': [0], 'where': [0],
    'when': [0], 'how': [0], 'why': [0],

    # Common stressed monosyllables
    'god': [1], 'son': [1], 'love': [1], 'mind': [1], 'soul': [1],
    'truth': [1], 'light': [1], 'life': [1], 'death': [1], 'fear': [1],
    'sin': [1], 'guilt': [1], 'peace': [1], 'joy': [1], 'grace': [1],
    'world': [1], 'earth': [1], 'time': [1], 'space': [1],
    'heart': [1], 'word': [1], 'work': [1], 'rest': [1],
    'self': [1], 'all': [1], 'one': [1], 'none': [1],
    'give': [1], 'take': [1], 'make': [1], 'come': [1], 'go': [1],
    'see': [1], 'know': [1], 'think': [1], 'find': [1], 'seek': [1],
    'hear': [1], 'call': [1], 'ask': [1], 'tell': [1], 'say': [1],
    'said': [1], 'done': [1], 'made': [1], 'found': [1], 'held': [1],
    'thought': [1], 'brought': [1], 'taught': [1], 'sought': [1],
    'true': [1], 'false': [1], 'real': [1], 'whole': [1],
    'own': [1], 'each': [1], 'both': [1], 'such': [1],
    'first': [1], 'last': [1], 'next': [1], 'same': [1],
    'here': [1], 'there': [1], 'now': [1], 'then': [1],
    'still': [1], 'just': [1], 'right': [1], 'wrong': [1],
    'new': [1], 'old': [1], 'good': [1], 'great': [1],
    'long': [1], 'high': [1], 'deep': [1], 'far': [1],
    'hell': [1], 'heaven': [1, 0], 'vain': [1], 'pain': [1],
    'free': [1], 'gift': [1], 'choice': [1], 'change': [1],
    'form': [1], 'dream': [1], 'sleep': [1], 'wake': [1],
    'teach': [1], 'learn': [1], 'choose': [1], 'fail': [1],
    'join': [1], 'share': [1], 'keep': [1], 'hold': [1],
    'sight': [1], 'role': [1], 'way': [1], 'path': [1],
    'name': [1], 'part': [1], 'place': [1], 'home': [1],
    'hath': [1], 'thy': [0], 'wills': [1],

    # Two-syllable words (stress patterns)
    'about': [0, 1], 'above': [0, 1], 'across': [0, 1],
    'again': [0, 1], 'against': [0, 1], 'alone': [0, 1],
    'along': [0, 1], 'among': [0, 1], 'apart': [0, 1],
    'around': [0, 1], 'away': [0, 1], 'become': [0, 1],
    'before': [0, 1], 'begin': [0, 1], 'behind': [0, 1],
    'believe': [0, 1], 'belong': [0, 1], 'below': [0, 1],
    'beneath': [0, 1], 'beside': [0, 1], 'between': [0, 1],
    'beyond': [0, 1], 'behold': [0, 1], 'because': [0, 1],
    'within': [0, 1], 'without': [0, 1],
    'accept': [0, 1], 'achieve': [0, 1], 'allow': [0, 1],
    'appear': [0, 1], 'arise': [0, 1], 'attack': [0, 1],
    'attempt': [0, 1], 'await': [0, 1],
    'create': [0, 1], 'decide': [0, 1], 'define': [0, 1],
    'deny': [0, 1], 'desire': [0, 1], 'destroy': [0, 1],
    'divine': [0, 1], 'elect': [0, 1], 'entire': [0, 1],
    'escape': [0, 1], 'except': [0, 1], 'exist': [0, 1],
    'extend': [0, 1], 'forgive': [0, 1], 'forget': [0, 1],
    'fulfill': [0, 1], 'indeed': [0, 1], 'instead': [0, 1],
    'itself': [0, 1], 'myself': [0, 1], 'himself': [0, 1],
    'herself': [0, 1], 'yourself': [0, 1], 'ourselves': [0, 1],
    'undo': [0, 1], 'upon': [0, 1], 'release': [0, 1],
    'ordained': [0, 1], 'content': [0, 1], 'concern': [0, 1],
    'perceive': [0, 1], 'receive': [0, 1], 'remove': [0, 1],
    'replace': [0, 1], 'restore': [0, 1], 'return': [0, 1],
    'reveal': [0, 1], 'secure': [0, 1], 'select': [0, 1],
    'suppose': [0, 1], 'sustain': [0, 1], 'towards': [0, 1],

    'holy': [1, 0], 'only': [1, 0], 'also': [1, 0],
    'always': [1, 0], 'never': [1, 0], 'ever': [1, 0],
    'every': [1, 0, 0], 'over': [1, 0], 'under': [1, 0],
    'other': [1, 0], 'father': [1, 0], 'brother': [1, 0],
    'mother': [1, 0], 'spirit': [1, 0], 'certain': [1, 0],
    'nothing': [1, 0], 'something': [1, 0], 'everything': [1, 0, 0, 0],
    'someone': [1, 0], 'no one': [1, 0],
    'truly': [1, 0], 'wholly': [1, 0], 'merely': [1, 0],
    'simply': [1, 0], 'fully': [1, 0],
    'power': [1, 0], 'flower': [1, 0], 'tower': [1, 0],
    'healing': [1, 0], 'feeling': [1, 0], 'seeing': [1, 0],
    'being': [1, 0], 'doing': [1, 0], 'going': [1, 0],
    'thinking': [1, 0], 'choosing': [1, 0], 'asking': [1, 0],
    'calling': [1, 0], 'willing': [1, 0], 'giving': [1, 0],
    'living': [1, 0], 'loving': [1, 0], 'making': [1, 0],
    'taking': [1, 0], 'knowing': [1, 0], 'showing': [1, 0],
    'teacher': [1, 0], 'student': [1, 0], 'lesson': [1, 0],
    'perfect': [1, 0], 'present': [1, 0], 'absence': [1, 0],
    'judgement': [1, 0], 'judgment': [1, 0],
    'unless': [0, 1], 'until': [0, 1],
    'cannot': [1, 1], 'maybe': [1, 0],
    'equal': [1, 0], 'risen': [1, 0],
    'child': [1], 'children': [1, 0],
    'worthy': [1, 0], 'stranger': [1, 0],

    # Three-syllable words
    'another': [0, 1, 0], 'together': [0, 1, 0],
    'forever': [0, 1, 0], 'wherever': [0, 1, 0],
    'whatever': [0, 1, 0], 'however': [0, 1, 0],
    'remember': [0, 1, 0], 'consider': [0, 1, 0],
    'continue': [0, 1, 0], 'discover': [0, 1, 0],
    'establish': [0, 1, 0], 'entirely': [0, 1, 0],
    'beginning': [0, 1, 0], 'already': [1, 1, 0],
    'otherwise': [1, 0, 0], 'beautiful': [1, 0, 0],
    'universe': [1, 0, 0], 'everyone': [1, 0, 0],
    'innocent': [1, 0, 0], 'difficult': [1, 0, 0],
    'possible': [1, 0, 0], 'miracle': [1, 0, 0],
    'miracles': [1, 0, 0],
    'atonement': [0, 1, 0], 'forgiveness': [0, 1, 0],
    'awareness': [0, 1, 0], 'perception': [0, 1, 0],
    'salvation': [0, 1, 0], 'creation': [0, 1, 0],
    'correction': [0, 1, 0], 'protection': [0, 1, 0],
    'condition': [0, 1, 0], 'confusion': [0, 1, 0],
    'illusion': [0, 1, 0], 'delusion': [0, 1, 0],
    'decision': [0, 1, 0], 'division': [0, 1, 0],
    'communion': [0, 1, 0],
    'denial': [0, 1, 0], 'negation': [0, 1, 0],
    'eternal': [0, 1, 0], 'internal': [0, 1, 0],
    'accepting': [0, 1, 0],
    'undoing': [0, 1, 0],

    # Four-syllable
    'accordingly': [0, 1, 0, 0],
    'understanding': [0, 0, 1, 0],
    'certainty': [1, 0, 0],
    'responsible': [0, 1, 0, 0],
    'ultimately': [1, 0, 0, 0],
    'naturally': [1, 0, 0, 0],
    'unwelcome': [0, 1, 0],
}


def count_syllables(word):
    """Heuristic syllable counter."""
    word = word.lower().strip()
    if not word or not re.search(r'[a-z]', word):
        return 0

    clean = re.sub(r'[^a-z]', '', word)

    if clean in STRESS_DICT:
        return len(STRESS_DICT[clean])

    # Fallback heuristic
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


def get_stress(word):
    """Get stress pattern for a word. Returns list of 0s and 1s."""
    clean = re.sub(r'[^a-z]', '', word.lower())
    if clean in STRESS_DICT:
        return STRESS_DICT[clean]

    # Heuristic: for unknown words, guess based on syllable count
    syls = count_syllables(word)
    if syls == 1:
        # Single syllable content words are stressed by default
        if clean in ('a', 'an', 'the', 'of', 'in', 'to', 'for', 'and', 'but',
                     'or', 'on', 'at', 'by', 'with', 'from', 'as', 'if', 'so',
                     'it', 'is', 'was', 'be', 'he', 'she', 'we', 'they', 'me',
                     'him', 'her', 'us', 'them', 'you', 'my', 'his', 'our', 'their',
                     'do', 'does', 'did', 'has', 'had', 'have', 'will', 'would',
                     'shall', 'should', 'can', 'could', 'may', 'might', 'must',
                     'am', 'are', 'were', 'been', 'its', 'that', 'this', 'what',
                     'who', 'whom', 'which', 'where', 'when', 'how', 'why', 'than'):
            return [0]
        return [1]
    elif syls == 2:
        # Default: iambic (unstressed-stressed) for unknown 2-syllable words
        # But words ending in -ing, -ly, -er, -ness, -ment tend to be trochaic
        if clean.endswith(('ing', 'ly', 'er', 'ness', 'ment', 'ful', 'less', 'ous', 'ive', 'dom')):
            return [1, 0]
        return [0, 1]
    elif syls == 3:
        # Default: dactylic or anapestic
        if clean.endswith(('tion', 'sion', 'ness', 'ment')):
            return [0, 1, 0]
        return [1, 0, 0]
    elif syls == 4:
        return [0, 1, 0, 0]
    else:
        # Alternate
        return [0 if i % 2 == 0 else 1 for i in range(syls)]


def count_sentence_syllables(sentence):
    words = re.findall(r"[a-zA-Z']+", sentence)
    return sum(count_syllables(w) for w in words)


def get_sentence_stress(sentence):
    """Get full stress pattern for a sentence."""
    words = re.findall(r"[a-zA-Z']+", sentence)
    pattern = []
    word_boundaries = []
    for w in words:
        stress = get_stress(w)
        word_boundaries.append((w, stress))
        pattern.extend(stress)
    return pattern, word_boundaries


def iambic_score(pattern):
    """Score how well a 10-syllable pattern matches iambic pentameter.
    Perfect iambic = [0,1,0,1,0,1,0,1,0,1]
    Returns score from 0.0 to 1.0 (1.0 = perfect match)."""
    if len(pattern) != 10:
        return 0.0

    ideal = [0, 1, 0, 1, 0, 1, 0, 1, 0, 1]
    matches = sum(1 for a, b in zip(pattern, ideal) if a == b)
    return matches / 10.0


def extract_sentences(text):
    text = text.replace('\t', ' ')
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]


def main():
    filepath = "my-book/source-material/CourseUB/urtext_extracted.txt"

    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        text = f.read()

    sentences = extract_sentences(text)

    results = []
    for s in sentences:
        clean = re.sub(r'[^a-zA-Z\s]', '', s).strip()
        words = clean.split()
        if len(words) < 3:
            continue

        syl_count = count_sentence_syllables(s)
        if syl_count == 10:
            pattern, word_boundaries = get_sentence_stress(s)
            if len(pattern) == 10:
                score = iambic_score(pattern)
                results.append((s, pattern, word_boundaries, score))

    # Sort by iambic score descending
    results.sort(key=lambda x: x[3], reverse=True)

    # Stats
    perfect = [r for r in results if r[3] >= 1.0]
    strong = [r for r in results if 0.8 <= r[3] < 1.0]
    moderate = [r for r in results if 0.6 <= r[3] < 0.8]
    weak = [r for r in results if r[3] < 0.6]

    print(f"Total 10-syllable sentences: {len(results)}")
    print(f"Perfect iambic pentameter (10/10): {len(perfect)}")
    print(f"Strong iambic (8-9/10): {len(strong)}")
    print(f"Moderate iambic (6-7/10): {len(moderate)}")
    print(f"Weak/non-iambic (<6/10): {len(weak)}")

    print(f"\n{'='*70}")
    print("PERFECT IAMBIC PENTAMETER (10/10 match)")
    print(f"{'='*70}\n")
    for i, (s, pat, wb, score) in enumerate(perfect, 1):
        pat_str = ''.join(['/' if x == 1 else 'u' for x in pat])
        print(f"{i}. {s}")
        print(f"   Pattern: {pat_str}  (u=unstressed, /=stressed)")
        wb_str = ' '.join([f"{w}({''.join(['/' if x==1 else 'u' for x in st])})" for w, st in wb])
        print(f"   Words: {wb_str}")
        print()

    print(f"\n{'='*70}")
    print("STRONG IAMBIC (8-9/10 match)")
    print(f"{'='*70}\n")
    for i, (s, pat, wb, score) in enumerate(strong, 1):
        pat_str = ''.join(['/' if x == 1 else 'u' for x in pat])
        print(f"{i}. {s} [{score:.0%}]")
        print(f"   Pattern: {pat_str}")
        print()

    print(f"\n{'='*70}")
    print("SAMPLE MODERATE IAMBIC (6-7/10 match) - first 30")
    print(f"{'='*70}\n")
    for i, (s, pat, wb, score) in enumerate(moderate[:30], 1):
        pat_str = ''.join(['/' if x == 1 else 'u' for x in pat])
        print(f"{i}. {s} [{score:.0%}]")
        print(f"   Pattern: {pat_str}")
        print()


if __name__ == '__main__':
    main()
