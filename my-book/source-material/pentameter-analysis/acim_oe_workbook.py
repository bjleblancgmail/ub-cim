#!/usr/bin/env python3
"""
Pentameter scan of ACIM Original Edition WORKBOOK.
Splits each file into individual lessons by 'LESSON N' markers,
then groups into ranges for trend analysis.
"""

import zipfile
import re

EPUB = '/Users/brianleblanc/code/ub-cim/my-book/Course In Miracles/Original Edition/acim-oe-complete-2026.epub'

def strip_html(html):
    text = re.sub(r'<[^>]+>', ' ', html)
    text = re.sub(r'&[a-z]+;', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

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

def split_into_lessons(text):
    """Split text by 'LESSON N' markers, return dict of lesson_num -> text."""
    parts = re.split(r'(LESSON\s+\d+)', text, flags=re.IGNORECASE)
    lessons = {}
    i = 0
    while i < len(parts):
        m = re.match(r'LESSON\s+(\d+)', parts[i], re.IGNORECASE)
        if m:
            num = int(m.group(1))
            content = parts[i+1] if i+1 < len(parts) else ""
            lessons[num] = content
            i += 2
        else:
            i += 1
    return lessons

# ============ MAIN ============

all_lessons = {}

with zipfile.ZipFile(EPUB) as z:
    # All workbook files
    wb_files = [
        'OEBPS/Text/p1-chap1.xhtml',      # L1-50
        'OEBPS/Text/review_1.xhtml',       # L51-80
        'OEBPS/Text/review_2.xhtml',       # L81-110
        'OEBPS/Text/review_3.xhtml',       # L111-140
        'OEBPS/Text/review_4.xhtml',       # L141-170
        'OEBPS/Text/review_5.xhtml',       # L171-200
        'OEBPS/Text/review_6.xhtml',       # L201-220
    ]
    # Part 2 lessons
    for i in range(1, 16):
        wb_files.append(f'OEBPS/Text/p2-chap{i}.xhtml')

    for fname in wb_files:
        if fname in z.namelist():
            data = z.read(fname).decode('utf-8')
            text = strip_html(data)
            lessons = split_into_lessons(text)
            all_lessons.update(lessons)

print(f"Total lessons found: {len(all_lessons)}")
print(f"Range: {min(all_lessons.keys())}-{max(all_lessons.keys())}")
print()

# Analyze each lesson
lesson_results = {}
for num in sorted(all_lessons.keys()):
    text = all_lessons[num]
    words = text.split()
    ratio, clauses = estimate_pentameter_ratio(text)
    lesson_results[num] = (ratio, clauses, len(words))

# ---- Output by ranges of 10 ----
print("=" * 70)
print("WORKBOOK: PENTAMETER BY LESSON GROUPS OF 10")
print("=" * 70)

for start in range(1, 366, 10):
    end = min(start + 9, 365)
    group = [(num, *lesson_results[num]) for num in range(start, end + 1) if num in lesson_results]
    if group:
        total_pent = sum(r * c for _, r, c, _ in group)
        total_cl = sum(c for _, _, c, _ in group)
        total_w = sum(w for _, _, _, w in group)
        if total_cl > 0:
            pct = total_pent / total_cl * 100
            bar = "█" * int(pct) + "·" * (35 - int(pct))
            print(f"  L {start:3d}-{end:3d}: {pct:5.1f}%  ({total_cl:4d} cl, {total_w:5d} w)  {bar}")

# ---- Output by ranges of 50 ----
print()
print("=" * 70)
print("WORKBOOK: PENTAMETER BY LESSON GROUPS OF 50")
print("=" * 70)

for start in range(1, 366, 50):
    end = min(start + 49, 365)
    group = [(num, *lesson_results[num]) for num in range(start, end + 1) if num in lesson_results]
    if group:
        total_pent = sum(r * c for _, r, c, _ in group)
        total_cl = sum(c for _, _, c, _ in group)
        total_w = sum(w for _, _, _, w in group)
        if total_cl > 0:
            pct = total_pent / total_cl * 100
            bar = "█" * int(pct) + "·" * (35 - int(pct))
            print(f"  L {start:3d}-{end:3d}: {pct:5.1f}%  ({total_cl:4d} cl, {total_w:5d} w)  {bar}")

# ---- Overall trend ----
print()
print("=" * 70)
print("WORKBOOK: OVERALL TREND")
print("=" * 70)

early = [(n, *lesson_results[n]) for n in range(1, 101) if n in lesson_results]
mid = [(n, *lesson_results[n]) for n in range(101, 251) if n in lesson_results]
late = [(n, *lesson_results[n]) for n in range(251, 366) if n in lesson_results]

for label, group in [("L 1-100 (early)", early), ("L 101-250 (mid)", mid), ("L 251-365 (late)", late)]:
    if group:
        total_pent = sum(r * c for _, r, c, _ in group)
        total_cl = sum(c for _, _, c, _ in group)
        total_w = sum(w for _, _, _, w in group)
        if total_cl > 0:
            print(f"  {label:25s}: {total_pent/total_cl*100:5.1f}%  ({total_w} words)")

all_pent = sum(r * c for r, c, w in lesson_results.values())
all_cl = sum(c for r, c, w in lesson_results.values())
all_w = sum(w for r, c, w in lesson_results.values())
print(f"\n  {'OVERALL':25s}: {all_pent/all_cl*100:5.1f}%  ({all_w} words, {len(lesson_results)} lessons)")

# ---- Top 10 and Bottom 10 individual lessons ----
print()
print("=" * 70)
print("TOP 10 HIGHEST PENTAMETER LESSONS (min 5 clauses)")
print("=" * 70)

valid = [(n, r, c, w) for n, (r, c, w) in lesson_results.items() if c >= 5]
valid.sort(key=lambda x: x[1], reverse=True)
for n, r, c, w in valid[:10]:
    print(f"  Lesson {n:3d}: {r*100:5.1f}%  ({c} clauses, {w} words)")

print()
print("=" * 70)
print("BOTTOM 10 LOWEST PENTAMETER LESSONS (min 5 clauses)")
print("=" * 70)
for n, r, c, w in valid[-10:]:
    print(f"  Lesson {n:3d}: {r*100:5.1f}%  ({c} clauses, {w} words)")
