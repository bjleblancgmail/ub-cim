import re
import sys


STRESS_DICT = {
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
    'not': [1], 'no': [1],
    'he': [0], 'she': [0], 'we': [0], 'they': [0], 'i': [0],
    'me': [0], 'him': [0], 'her': [0], 'us': [0], 'them': [0],
    'you': [0], 'your': [0], 'my': [0], 'his': [0], 'our': [0], 'their': [0],
    'who': [0], 'whom': [0], 'what': [0], 'which': [0], 'where': [0],
    'when': [0], 'how': [0], 'why': [0],
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
    'someone': [1, 0],
    'truly': [1, 0], 'wholly': [1, 0], 'merely': [1, 0],
    'simply': [1, 0], 'fully': [1, 0],
    'power': [1, 0], 'healing': [1, 0], 'feeling': [1, 0],
    'seeing': [1, 0], 'being': [1, 0], 'doing': [1, 0], 'going': [1, 0],
    'thinking': [1, 0], 'choosing': [1, 0], 'asking': [1, 0],
    'calling': [1, 0], 'willing': [1, 0], 'giving': [1, 0],
    'living': [1, 0], 'loving': [1, 0], 'making': [1, 0],
    'taking': [1, 0], 'knowing': [1, 0], 'showing': [1, 0],
    'teacher': [1, 0], 'student': [1, 0], 'lesson': [1, 0],
    'perfect': [1, 0], 'present': [1, 0], 'absence': [1, 0],
    'unless': [0, 1], 'until': [0, 1],
    'cannot': [1, 1], 'maybe': [1, 0],
    'equal': [1, 0], 'risen': [1, 0],
    'child': [1], 'children': [1, 0],
    'worthy': [1, 0], 'stranger': [1, 0],
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
    'accordingly': [0, 1, 0, 0],
    'understanding': [0, 0, 1, 0],
    'certainty': [1, 0, 0],
    'responsible': [0, 1, 0, 0],
    'ultimately': [1, 0, 0, 0],
    'naturally': [1, 0, 0, 0],
    'unwelcome': [0, 1, 0],
}


def count_syllables(word):
    word = word.lower().strip()
    if not word or not re.search(r'[a-z]', word):
        return 0
    clean = re.sub(r'[^a-z]', '', word)
    if clean in STRESS_DICT:
        return len(STRESS_DICT[clean])
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
    clean = re.sub(r'[^a-z]', '', word.lower())
    if clean in STRESS_DICT:
        return STRESS_DICT[clean]
    syls = count_syllables(word)
    if syls == 1:
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
        if clean.endswith(('ing', 'ly', 'er', 'ness', 'ment', 'ful', 'less', 'ous', 'ive', 'dom')):
            return [1, 0]
        return [0, 1]
    elif syls == 3:
        if clean.endswith(('tion', 'sion', 'ness', 'ment')):
            return [0, 1, 0]
        return [1, 0, 0]
    elif syls == 4:
        return [0, 1, 0, 0]
    else:
        return [0 if i % 2 == 0 else 1 for i in range(syls)]


def count_sentence_syllables(sentence):
    words = re.findall(r"[a-zA-Z']+", sentence)
    return sum(count_syllables(w) for w in words)


def iambic_score(pattern):
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

    # Tag each sentence with its index, syllable count, and iambic score
    tagged = []
    for idx, s in enumerate(sentences):
        clean = re.sub(r'[^a-zA-Z\s]', '', s).strip()
        words_list = clean.split()
        if len(words_list) < 3:
            tagged.append((idx, s, 0, 0.0, False))
            continue

        syl_count = count_sentence_syllables(s)
        if syl_count == 10:
            words = re.findall(r"[a-zA-Z']+", s)
            pattern = []
            for w in words:
                pattern.extend(get_stress(w))
            if len(pattern) == 10:
                score = iambic_score(pattern)
                is_iambic = score >= 0.8  # strong or perfect
                tagged.append((idx, s, syl_count, score, is_iambic))
            else:
                tagged.append((idx, s, syl_count, 0.0, False))
        else:
            tagged.append((idx, s, syl_count, 0.0, False))

    # Find clusters: consecutive or near-consecutive iambic lines
    # "Near-consecutive" = iambic lines separated by at most 1 non-iambic sentence
    # A cluster = 3+ iambic lines within a window where gaps are <= 2 sentences

    iambic_indices = [(idx, s, score) for idx, s, syl, score, is_iambic in tagged if is_iambic]

    print(f"Total sentences: {len(sentences)}")
    print(f"Strong/perfect iambic pentameter sentences (>=80%): {len(iambic_indices)}")
    print()

    # Find clusters: groups where iambic lines are close together
    # Use a sliding window: if the gap between consecutive iambic lines is <= 3, they're in the same cluster
    MAX_GAP = 3  # max non-iambic sentences between cluster members

    clusters = []
    if iambic_indices:
        current_cluster = [iambic_indices[0]]
        for i in range(1, len(iambic_indices)):
            prev_idx = iambic_indices[i-1][0]
            curr_idx = iambic_indices[i][0]
            gap = curr_idx - prev_idx - 1
            if gap <= MAX_GAP:
                current_cluster.append(iambic_indices[i])
            else:
                if len(current_cluster) >= 2:
                    clusters.append(current_cluster)
                current_cluster = [iambic_indices[i]]
        if len(current_cluster) >= 2:
            clusters.append(current_cluster)

    # Sort clusters by size
    clusters.sort(key=lambda c: len(c), reverse=True)

    print(f"Clusters found (2+ iambic lines within {MAX_GAP} sentences of each other): {len(clusters)}")
    print()

    # Show all clusters with their surrounding context
    print("=" * 70)
    print("IAMBIC PENTAMETER CLUSTERS")
    print("(showing iambic lines with intervening sentences for context)")
    print("=" * 70)

    for ci, cluster in enumerate(clusters, 1):
        first_idx = cluster[0][0]
        last_idx = cluster[-1][0]
        iambic_count = len(cluster)

        print(f"\n--- Cluster {ci}: {iambic_count} iambic lines (sentences #{first_idx}-{last_idx}) ---\n")

        # Show all sentences from first to last in the cluster
        for idx in range(max(0, first_idx - 1), min(len(tagged), last_idx + 2)):
            sent_idx, sent, syl, score, is_iambic = tagged[idx]
            if is_iambic:
                pat = []
                words = re.findall(r"[a-zA-Z']+", sent)
                for w in words:
                    pat.extend(get_stress(w))
                pat_str = ''.join(['/' if x == 1 else 'u' for x in pat[:10]])
                print(f"  >>> {sent}")
                print(f"      [{pat_str}] ({score:.0%})")
            else:
                # Show non-iambic sentences in between for context
                if first_idx <= idx <= last_idx:
                    print(f"      {sent} ({syl} syl)")
        print()

    # Also show the final passage of the text
    print("\n" + "=" * 70)
    print("FINAL 30 SENTENCES OF THE URTEXT (with iambic marking)")
    print("=" * 70 + "\n")

    start = max(0, len(tagged) - 30)
    for idx in range(start, len(tagged)):
        sent_idx, sent, syl, score, is_iambic = tagged[idx]
        if is_iambic:
            pat = []
            words = re.findall(r"[a-zA-Z']+", sent)
            for w in words:
                pat.extend(get_stress(w))
            pat_str = ''.join(['/' if x == 1 else 'u' for x in pat[:10]])
            print(f"  >>> {sent}")
            print(f"      [{pat_str}] ({score:.0%}) [10 syl]")
        else:
            marker = f" [10 syl]" if syl == 10 else ""
            print(f"      {sent} ({syl} syl){marker}")


if __name__ == '__main__':
    main()
