#!/usr/bin/env python3
"""
Look for binary patterns in the high-density pentameter passages.
1. Encode each clause as 1 (pentameter) or 0 (not) - look for patterns
2. Catalog the binary oppositions in the content
3. Look for structural symmetries
"""

import re
from collections import Counter

ACIM_FILE = "/Users/brianleblanc/code/ub-cim/my-book/Course In Miracles/ACourseInMiraclesUrtextEdition.md"

def count_syllables(word):
    word = word.lower().strip()
    if not word:
        return 0
    word = re.sub(r'[^a-z]', '', word)
    if not word:
        return 0
    if len(word) <= 2:
        return 1
    vowels = 'aeiouy'
    count = 0
    prev_vowel = False
    for ch in word:
        if ch in vowels:
            if not prev_vowel:
                count += 1
            prev_vowel = True
        else:
            prev_vowel = False
    if word.endswith('e') and count > 1 and not word.endswith('le'):
        count -= 1
    if word.endswith('ed') and count > 1:
        if len(word) >= 4 and word[-3] not in 'dt':
            count -= 1
    return max(count, 1)


def clause_pentameter_binary(text):
    """Return binary string: 1 for pentameter clause, 0 for not."""
    clauses = re.split(r'[.!?;:,]', text)
    clauses = [c.strip() for c in clauses if c.strip() and len(c.split()) >= 3]
    binary = []
    details = []
    for clause in clauses:
        words = clause.split()
        syl = sum(count_syllables(w) for w in words)
        is_pent = 9 <= syl <= 11
        binary.append('1' if is_pent else '0')
        details.append((clause, syl, is_pent))
    return ''.join(binary), details


# The key high-density passages (deduplicated, cleaned)
passages = [
    {
        "name": "Text: 'Think not that He has forgotten' (77%)",
        "text": "Think not that He has forgotten anyone, in the purpose He has given you. And think not that He has forgotten YOU, to whom He GAVE this gift. He uses everyone who calls on Him, as means for the salvation of everyone. And He will waken everyone through you, who offered your relationship to Him. If you but recognized His gratitude! For we are joined as one in purpose, being of one mind with Him. Let not the dream take hold to close your eyes. It is not strange that dreams can make a world that is unreal."
    },
    {
        "name": "Text: 'Dreams of pardon' (75%)",
        "text": "And what they are FOR cannot BE seen. In any thought of loss there IS no meaning. No-one has agreed with you on what it means. It is a part of a distorted script, which cannot be interpreted with meaning. It must be forever unintelligible. This is NOT communication. Your dark dreams are but the senseless, isolated scripts you write in sleep. Look not to separate dreams for meaning. ONLY dreams of pardon can be shared. They mean the same for BOTH of you."
    },
    {
        "name": "Text: 'Darkened mind / light' (71%)",
        "text": "For a darkened mind cannot live in the light, and it must seek a place of darkness, where it can believe it is where it is NOT. God did not ALLOW this to happen. But you DEMANDED that it happen, and therefore believed that it was so. To SINGLE OUT is to MAKE ALONE, and thus MAKE LONELY. God did not do this to you. Could He SET YOU APART, KNOWING that your peace lies in His Oneness? He denied you only your request for pain, for suffering is not of His creation. Having GIVEN you creation."
    },
    {
        "name": "Text: 'Sleeping or awake' (70%)",
        "text": "You cannot dream some dreams and wake from some. For you are either sleeping OR awake. And dreaming goes with only ONE of these. The dreams you THINK you like would hold you back, as much as those in which the fear is seen. For EVERY dream is but a dream of fear, no matter what the form it seems to take. The fear is seen within, without, or both. Or it can be disguised in pleasant form. But never is it ABSENT from the dream. For fear is the material of dreams, from which they ALL are made. Their form can change, but they cannot be MADE of something else."
    },
    {
        "name": "Text: 'Completion / God's Son' (67%)",
        "text": "Completion is the FUNCTION of God's Son. He has no need to SEEK for it at all. Beyond ALL idols stands his holy will to be but what he IS. For MORE than whole is meaningless. If there were change in him; if he could be reduced to ANY form and limited to what is NOT in him, he would not BE as God created him. What idol CAN he need to be himself? For CAN he give a part of him away? What is not whole cannot MAKE whole. But what is REALLY asked for CANNOT be denied. Your will IS granted."
    },
    {
        "name": "Text: 'Truth vs illusion' (71%)",
        "text": "There IS no conflict between them and the TRUTH. Nor ARE they different from each other. And so it matters not what form they take. What made them is insane, and they remain part of what made them. Madness holds out no menace to reality, and has no influence upon it. Illusions CANNOT triumph over truth, nor can they threaten it in any way. And the reality which they deny is NOT a part of them. What YOU remember IS a part of you. For you MUST be as God created you. Truth does not fight against illusion, nor do illusions fight against the truth. Illusions battle ONLY with themselves. Being fragmented, they fragment."
    },
    {
        "name": "Text: 'Death is nothing' (67%)",
        "text": "He merely shines them away. His light is ALWAYS the call to awake, WHATEVER you may have been dreaming. Nothing lasting lies in dreams, and the Holy Spirit, shining with the light from God Himself, speaks only for what lasts forever. When your body and your ego and your dreams are gone, you will know that YOU will last forever. Many think that this is accomplished through death, but NOTHING is accomplished through death because death is nothing. EVERYTHING is accomplished through life, and life is of the mind and in the Mind. The body neither lives nor dies, because it cannot contain you who ARE life."
    },
    {
        "name": "Workbook: 'We take a stand' (76%)",
        "text": "We take a stand on but one side today. We side with the truth and let illusions go. We will not vacillate between the two, but take a firm position with the One. We dedicate ourselves to truth today, and to salvation as God planned it be. We will not argue it is something else, we will not seek for it where it is not. In gladness we accept it as it is, and take the part assigned to us by God. How happy to be certain! All our doubts we lay aside today, and take our stand with certainty of purpose, and with thanks that doubt is gone and surety has come. We have a mighty purpose to fulfill, and have been given everything we need with which to reach the goal. Not one mistake stands in our way."
    },
    {
        "name": "Workbook: 'God created limitless' (76%)",
        "text": "Whom God created limitless is free. I can invent imprisonment for him, but only in illusions, not in truth. No Thought of God has left Its Father's Mind. No Thought of God is limited at all. No Thought of God but is forever pure. Can I lay limits on the Son of God, whose Father willed that he be limitless, and like Himself in freedom and in love? Today let me give honor to Your Son, for thus alone I find the way to You. Father, I lay no limits on the Son You love, and You created limitless. The honor that I give to him is Yours, and what is Yours belongs to me as well."
    },
    {
        "name": "Workbook: 'Pain / forgiveness' (71%)",
        "text": "As an effect it cannot make effects. As an illusion it is what you will. Your idle wishes represent its pains. Your strange desires bring it evil dreams. Your thoughts of death envelop it in fear, while in your kind forgiveness does it live. Pain is the thought of evil taking form, and working havoc in your holy mind. Pain is the ransom you have gladly paid not to be free. In pain is God denied the Son He loves. In pain does fear appear to triumph over love, and time replace eternity and Heaven. And the world becomes a cruel and a bitter place, where sorrow rules and little joys give way before the onslaught of the savage pain that waits to end all joy in misery."
    },
    {
        "name": "Workbook: 'Condemn / forgive' (67%)",
        "text": "And yet illusion makes illusion. If you can condemn you can be injured. For you have believed that you can injure, and the right you have established for yourself can be now used against you, til you lay it down as valueless, unwanted and unreal. Then does illusion cease to have effects, and all it seemed to have will be undone. Then are you free, for freedom is your gift, and you can now receive the gift you gave. Condemn and you are made a prisoner. Forgive and you are freed. Such is the law that rules perception. It is not a law that knowledge understands, for freedom is a part of knowledge. To condemn is thus impossible in truth. What seems to be its influence and its effects have not occurred at all."
    },
    {
        "name": "Manual: 'Universe / peace' (62%)",
        "text": "He does not seek to keep it for Himself. Why would you seek to keep your tiny, frail imaginings apart from Him? The Will of God is One and all there is. This is your heritage. The universe beyond the sun and stars, and all the thoughts of which you can conceive, belong to you. God's peace is the condition for His Will. Attain His peace, and you remember Him."
    },
    {
        "name": "Manual: 'Sacrifice is total' (62%)",
        "text": "Do not forget that sacrifice is total. There are no half sacrifices. You cannot give up Heaven partially. You cannot be a little bit in hell. The Word of God has no exceptions. It is this that makes It holy and beyond the world. It is Its holiness that points to God. It is Its holiness that makes you safe. It is denied if you attack any brother for anything."
    },
    {
        "name": "Manual: 'Curriculum ends' (56%)",
        "text": "Christ's face is seen in every living thing, and nothing is held in darkness apart from the light of forgiveness. There is no sorrow still upon the earth. The joy of Heaven has come upon it. Here the curriculum ends. From here on no directions are needed. Vision is wholly corrected and all mistakes undone. Attack is meaningless and peace has come. The goal of the curriculum has been achieved. Thoughts turn to Heaven and away from hell. All longings are satisfied, for what remains unanswered or incomplete? The last illusion spreads over the world, forgiving all things and replacing all attack. The whole reversal is accomplished. Nothing is left to contradict the Word of God."
    },
]

print("=" * 70)
print("ANALYSIS 1: Clause-by-clause pentameter binary sequences")
print("=" * 70)
print()
print("Each clause encoded: 1 = pentameter (9-11 syllables), 0 = not")
print()

all_binaries = []

for p in passages:
    binary, details = clause_pentameter_binary(p["text"])
    all_binaries.append(binary)
    ones = binary.count('1')
    zeros = binary.count('0')
    print(f"--- {p['name']} ---")
    print(f"Binary: {binary}")
    print(f"Length: {len(binary)} clauses, {ones} pentameter, {zeros} non-pent")

    # Show clause details
    for i, (clause, syl, is_pent) in enumerate(details):
        marker = ">>>" if is_pent else "   "
        words = clause.split()
        short = ' '.join(words[:8]) + ("..." if len(words) > 8 else "")
        print(f"  {marker} [{binary[i]}] {syl:2d} syl: {short}")
    print()

# ============================================================
print("=" * 70)
print("ANALYSIS 2: Binary opposition pairs in pentameter passages")
print("=" * 70)
print()

# Define binary pairs to search for
binary_pairs = [
    ("truth", "illusion"), ("light", "darkness"), ("love", "fear"),
    ("god", "ego"), ("life", "death"), ("awake", "sleep"),
    ("heaven", "hell"), ("peace", "war"), ("peace", "conflict"),
    ("forgive", "condemn"), ("free", "prisoner"), ("whole", "fragment"),
    ("reality", "dream"), ("one", "separate"), ("create", "destroy"),
    ("give", "take"), ("joy", "pain"), ("eternal", "temporal"),
    ("holy", "sinful"), ("spirit", "body"), ("knowledge", "perception"),
    ("gain", "loss"), ("remember", "forget"), ("limitless", "limited"),
    ("everything", "nothing"), ("infinite", "finite"),
]

all_text = ' '.join(p["text"].lower() for p in passages)

print("Binary oppositions found across all high-pentameter passages:")
print()
found_pairs = []
for word_a, word_b in binary_pairs:
    count_a = len(re.findall(r'\b' + word_a + r'\w*\b', all_text))
    count_b = len(re.findall(r'\b' + word_b + r'\w*\b', all_text))
    if count_a > 0 or count_b > 0:
        found_pairs.append((word_a, word_b, count_a, count_b))
        print(f"  {word_a:>15s} ({count_a:2d}) vs {word_b:<15s} ({count_b:2d})")

# ============================================================
print()
print("=" * 70)
print("ANALYSIS 3: Sentence-level binary structure")
print("=" * 70)
print()
print("Looking for paired/mirrored sentences in pentameter passages...")
print()

# Check for sentences that mirror each other structurally
mirror_examples = [
    ("Condemn and you are made a prisoner", "Forgive and you are freed"),
    ("As an effect it cannot make effects", "As an illusion it is what you will"),
    ("Your idle wishes represent its pains", "Your strange desires bring it evil dreams"),
    ("In pain is God denied the Son He loves", "In pain does fear appear to triumph over love"),
    ("No Thought of God has left Its Father's Mind", "No Thought of God is limited at all"),
    ("No Thought of God is limited at all", "No Thought of God but is forever pure"),
    ("You cannot give up Heaven partially", "You cannot be a little bit in hell"),
    ("It is Its holiness that points to God", "It is Its holiness that makes you safe"),
    ("We side with the truth and let illusions go", "We will not vacillate between the two"),
    ("Thoughts turn to Heaven and away from hell", "Attack is meaningless and peace has come"),
    ("Truth does not fight against illusion", "nor do illusions fight against the truth"),
    ("NOTHING is accomplished through death", "EVERYTHING is accomplished through life"),
    ("You cannot dream some dreams and wake from some", "For you are either sleeping OR awake"),
]

print("Paired/mirrored sentences found:")
for a, b in mirror_examples:
    syl_a = sum(count_syllables(w) for w in a.split())
    syl_b = sum(count_syllables(w) for w in b.split())
    match = "SAME" if syl_a == syl_b else f"diff({syl_a} vs {syl_b})"
    pent_a = "PENT" if 9 <= syl_a <= 11 else f"{syl_a}syl"
    pent_b = "PENT" if 9 <= syl_b <= 11 else f"{syl_b}syl"
    print(f"  [{pent_a:>5s}] \"{a}\"")
    print(f"  [{pent_b:>5s}] \"{b}\"")
    print(f"          Syllable match: {match}")
    print()

# ============================================================
print("=" * 70)
print("ANALYSIS 4: The binary within the binary")
print("=" * 70)
print()
print("Iambic pentameter is itself binary: da-DUM da-DUM da-DUM da-DUM da-DUM")
print("The pentameter/non-pentameter clause pattern is another binary layer.")
print("The thematic content presents binary choices.")
print()
print("THREE LAYERS OF BINARY:")
print("  1. MICRO:  Each syllable is unstressed(0) or stressed(1) - da/DUM")
print("  2. MESO:   Each clause is pentameter(1) or not(0)")
print("  3. MACRO:  Each teaching presents a binary choice:")
print("             truth/illusion, love/fear, God/ego, awake/asleep")
print()

# Count how many of the high-density passages contain explicit binary choices
binary_keywords = [
    r'\bor\b', r'\beither\b', r'\bchoose\b', r'\bchoice\b',
    r'\bbetween\b', r'\bnor\b', r'\boppos\w+\b', r'\binstead\b',
    r'\brather\b', r'\bnot\b.*\bbut\b',
]

passages_with_binary_choice = 0
for p in passages:
    text_lower = p["text"].lower()
    has_binary = False
    for pattern in binary_keywords:
        if re.search(pattern, text_lower):
            has_binary = True
            break
    # Also check for explicit opposite pairs
    for word_a, word_b in binary_pairs:
        if re.search(r'\b' + word_a, text_lower) and re.search(r'\b' + word_b, text_lower):
            has_binary = True
            break
    if has_binary:
        passages_with_binary_choice += 1

print(f"Passages containing explicit binary choices: {passages_with_binary_choice}/{len(passages)} ({passages_with_binary_choice/len(passages):.0%})")
print()

# ============================================================
print("=" * 70)
print("ANALYSIS 5: Aggregate binary sequence patterns")
print("=" * 70)
print()

# Look at all binary strings for common subsequences
all_combined = ''.join(all_binaries)
print(f"Combined binary string (all passages): {all_combined}")
print(f"Total clauses: {len(all_combined)}")
print(f"Pentameter (1): {all_combined.count('1')} ({all_combined.count('1')/len(all_combined):.0%})")
print(f"Non-pent (0):   {all_combined.count('0')} ({all_combined.count('0')/len(all_combined):.0%})")
print()

# Count bigrams
bigrams = Counter()
for b in all_binaries:
    for i in range(len(b) - 1):
        bigrams[b[i:i+2]] += 1

print("Bigram frequencies (consecutive clause pairs):")
for bg in ['11', '10', '01', '00']:
    count = bigrams[bg]
    total = sum(bigrams.values())
    print(f"  {bg}: {count} ({count/total:.0%})")

print()

# Check for runs
print("Run analysis (consecutive pentameter clauses):")
for b_str in all_binaries[:5]:
    runs = re.findall(r'1+', b_str)
    if runs:
        run_lengths = [len(r) for r in runs]
        print(f"  {b_str} -> runs of 1s: {run_lengths}")

print()
print("Longest pentameter runs across all passages:")
all_runs = []
for i, b_str in enumerate(all_binaries):
    runs = re.findall(r'1+', b_str)
    for r in runs:
        if len(r) >= 3:
            all_runs.append((len(r), passages[i]["name"]))
all_runs.sort(reverse=True)
for length, name in all_runs[:10]:
    print(f"  {length} consecutive pentameter clauses: {name}")
