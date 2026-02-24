#!/usr/bin/env python3
"""
Pentameter scan of The Urantia Book.
196 Papers organized into 4 Parts.
"""

import re

UB_FILE = '/Users/brianleblanc/code/ub-cim/my-book/Urantia Book/UF-ENG-001-1955-1.22.md'

def count_syllables(word):
    word = word.lower().strip()
    if not word:
        return 0
    vowels = 'aeiouy'
    count = 0
    prev_vowel = False
    for ch in word:
        is_vowel = ch in vowels
        if is_vowel and not prev_vowel:
            count += 1
        prev_vowel = is_vowel
    if word.endswith('e') and count > 1:
        count -= 1
    return max(count, 1)

def estimate_pentameter_ratio(text):
    clauses = re.split(r'[.!?;:,\-\—\–\(\)]', text)
    total = 0
    pent = 0
    for clause in clauses:
        words = [w for w in clause.split() if any(c.isalpha() for c in w)]
        if len(words) < 3:
            continue
        syllables = sum(count_syllables(w) for w in words)
        total += 1
        if 9 <= syllables <= 11:
            pent += 1
    if total == 0:
        return 0, 0
    return pent / total, total

def strip_markdown(text):
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\[([^\]]*)\]\([^\)]*\)', r'\1', text)
    text = re.sub(r'[#*_`>]', ' ', text)
    text = re.sub(r'&[a-z]+;', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# Read file
with open(UB_FILE) as f:
    lines = f.readlines()

# Find all papers
paper_starts = []
for i, line in enumerate(lines):
    m = re.match(r'^## Paper (\d+)', line)
    if m:
        paper_starts.append((int(m.group(1)), i))

# Extract text for each paper
papers = {}
for idx, (num, start) in enumerate(paper_starts):
    if idx + 1 < len(paper_starts):
        end = paper_starts[idx + 1][1]
    else:
        end = len(lines)
    text = ''.join(lines[start:end])
    text = strip_markdown(text)
    papers[num] = text

print(f"Papers found: {len(papers)} (Paper {min(papers.keys())}-{max(papers.keys())})")
print()

# UB Parts:
# Part I: Papers 1-31 (Central and Superuniverses)
# Part II: Papers 32-56 (Local Universe)
# Part III: Papers 57-119 (History of Urantia)
# Part IV: Papers 120-196 (Life and Teachings of Jesus)

# Analyze each paper
results = {}
for num in sorted(papers.keys()):
    text = papers[num]
    words = text.split()
    ratio, clauses = estimate_pentameter_ratio(text)
    results[num] = (ratio, clauses, len(words))

# ---- Output by Part ----
parts = [
    ("PART I: Central and Superuniverses", 1, 31),
    ("PART II: The Local Universe", 32, 56),
    ("PART III: The History of Urantia", 57, 119),
    ("PART IV: The Life and Teachings of Jesus", 120, 196),
]

def avg_ratio(nums):
    total_pent = sum(results[n][0] * results[n][1] for n in nums if n in results)
    total_cl = sum(results[n][1] for n in nums if n in results)
    return total_pent / total_cl * 100 if total_cl else 0

def total_words(nums):
    return sum(results[n][2] for n in nums if n in results)

def total_clauses(nums):
    return sum(results[n][1] for n in nums if n in results)

print("=" * 70)
print("THE URANTIA BOOK: PENTAMETER BY PAPER")
print("=" * 70)

for part_name, start, end in parts:
    print(f"\n--- {part_name} (Papers {start}-{end}) ---")
    for num in range(start, end + 1):
        if num in results:
            r, c, w = results[num]
            print(f"  Paper {num:3d}: {r*100:5.1f}%  ({c:4d} clauses, {w:5d} words)")

    part_nums = list(range(start, end + 1))
    pct = avg_ratio(part_nums)
    tw = total_words(part_nums)
    tc = total_clauses(part_nums)
    print(f"\n  PART TOTAL: {pct:.1f}%  ({tc} clauses, {tw} words)")

# ---- By groups of 10 ----
print("\n" + "=" * 70)
print("PENTAMETER BY GROUPS OF 10 PAPERS")
print("=" * 70)

for start in range(1, 197, 10):
    end = min(start + 9, 196)
    group = [n for n in range(start, end + 1) if n in results]
    if group:
        pct = avg_ratio(group)
        tw = total_words(group)
        tc = total_clauses(group)
        bar = "█" * int(pct) + "·" * (35 - int(pct))
        print(f"  P {start:3d}-{end:3d}: {pct:5.1f}%  ({tc:5d} cl, {tw:6d} w)  {bar}")

# ---- Overall trend ----
print("\n" + "=" * 70)
print("OVERALL TREND")
print("=" * 70)

for part_name, start, end in parts:
    part_nums = list(range(start, end + 1))
    pct = avg_ratio(part_nums)
    tw = total_words(part_nums)
    print(f"  {part_name:45s}: {pct:5.1f}%  ({tw:,} words)")

# Early vs late within each part
print("\n--- Early vs Late Within Each Part ---")
for part_name, start, end in parts:
    mid = (start + end) // 2
    early = list(range(start, mid + 1))
    late = list(range(mid + 1, end + 1))
    e_pct = avg_ratio(early)
    l_pct = avg_ratio(late)
    print(f"  {part_name[:30]:30s}: Early {e_pct:5.1f}% -> Late {l_pct:5.1f}%  (change: {l_pct - e_pct:+.1f}%)")

# Grand total
all_nums = list(results.keys())
grand_pct = avg_ratio(all_nums)
grand_w = total_words(all_nums)
grand_c = total_clauses(all_nums)

print(f"\n  GRAND TOTAL: {grand_pct:.1f}%  ({grand_c:,} clauses, {grand_w:,} words)")

# First 50 vs last 50
first50 = list(range(1, 51))
last50 = list(range(147, 197))
print(f"\n  Papers 1-50 (first quarter):    {avg_ratio(first50):.1f}%")
print(f"  Papers 147-196 (last quarter):  {avg_ratio(last50):.1f}%")

# ---- Top 10 / Bottom 10 ----
print("\n" + "=" * 70)
print("TOP 10 HIGHEST PENTAMETER PAPERS")
print("=" * 70)

sorted_papers = sorted(results.items(), key=lambda x: x[1][0], reverse=True)
for num, (r, c, w) in sorted_papers[:10]:
    print(f"  Paper {num:3d}: {r*100:5.1f}%  ({c} clauses, {w} words)")

print("\n" + "=" * 70)
print("BOTTOM 10 LOWEST PENTAMETER PAPERS")
print("=" * 70)

for num, (r, c, w) in sorted_papers[-10:]:
    print(f"  Paper {num:3d}: {r*100:5.1f}%  ({c} clauses, {w} words)")

# ---- Comparison summary ----
print("\n" + "=" * 70)
print("COMPARISON: UB vs ACIM vs MOBY DICK")
print("=" * 70)
print(f"  Urantia Book:    {grand_pct:.1f}%  ({grand_w:,} words)")
print(f"  ACIM (OE):       22.2%  (468,779 words)")
print(f"  Moby Dick:       18.8%  (213,000 words)")
print()
print(f"  UB early (P1-50):     {avg_ratio(first50):.1f}%")
print(f"  UB late (P147-196):   {avg_ratio(last50):.1f}%")
print(f"  ACIM Text early:      20.6%")
print(f"  ACIM Text late:       23.5%")
print(f"  Moby Dick early:      19.1%")
print(f"  Moby Dick late:       18.6%")
