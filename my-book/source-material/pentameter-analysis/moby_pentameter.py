#!/usr/bin/env python3
"""
Pentameter prevalence analysis on Moby Dick as a control text.
Same methodology as the ACIM analysis.
"""

import re

MOBY_FILE = "/tmp/moby_dick.txt"

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


def estimate_pentameter_ratio(text):
    clauses = re.split(r'[.!?;:,]', text)
    clauses = [c.strip() for c in clauses if c.strip()]
    if not clauses:
        return 0.0, 0, 0
    pent_count = 0
    total = 0
    for clause in clauses:
        words = clause.split()
        if len(words) < 3:
            continue
        total += 1
        syl_count = sum(count_syllables(w) for w in words)
        if 9 <= syl_count <= 11:
            pent_count += 1
    if total == 0:
        return 0.0, 0, 0
    return pent_count / total, total, pent_count


# Read Moby Dick
with open(MOBY_FILE, 'r', encoding='utf-8') as f:
    full_text = f.read()

# Find start of actual text (after Gutenberg header)
start_marker = "CHAPTER 1. Loomings."
end_marker = "*** END OF THE PROJECT GUTENBERG EBOOK"
start_idx = full_text.find(start_marker)
end_idx = full_text.find(end_marker)
if start_idx == -1:
    start_marker = "CHAPTER 1."
    start_idx = full_text.find(start_marker)
if end_idx == -1:
    end_idx = len(full_text)

book_text = full_text[start_idx:end_idx]

# Parse into chapters
chapters = {}
chapter_pattern = re.compile(r'CHAPTER\s+(\d+)\.')
parts = chapter_pattern.split(book_text)

# parts[0] is before first chapter, then alternating: chapter_num, chapter_text
current_ch = None
for i in range(1, len(parts), 2):
    ch_num = int(parts[i])
    ch_text = parts[i+1] if i+1 < len(parts) else ""
    chapters[ch_num] = ch_text

total_chapters = len(chapters)
print(f"Moby Dick: {total_chapters} chapters found")
print(f"Total words: {len(book_text.split()):,}")
print()

# Analyze each chapter
print("=" * 70)
print("MOBY DICK - Pentameter Prevalence by Chapter")
print("=" * 70)
print()
print(f"{'Ch':>3s} | {'Words':>6s} | {'Clauses':>8s} | {'Pent':>5s} | {'Ratio':>6s} | {'Bar'}")
print(f"{'---':>3s} | {'------':>6s} | {'--------':>8s} | {'-----':>5s} | {'------':>6s} | {'---'}")

results = []
for ch_num in sorted(chapters.keys()):
    text = chapters[ch_num]
    word_count = len(text.split())
    ratio, total_clauses, pent_clauses = estimate_pentameter_ratio(text)
    bar = "#" * int(ratio * 50)
    print(f"{ch_num:3d} | {word_count:6d} | {total_clauses:8d} | {pent_clauses:5d} | {ratio:5.1%} | {bar}")
    results.append((ch_num, word_count, total_clauses, pent_clauses, ratio))

# Summary
print()
total_words = sum(r[1] for r in results)
total_clauses = sum(r[2] for r in results)
total_pent = sum(r[3] for r in results)
overall = total_pent / total_clauses if total_clauses > 0 else 0
print(f"{'ALL':>3s} | {total_words:6d} | {total_clauses:8d} | {total_pent:5d} | {overall:5.1%} |")

# Trend by thirds
third = total_chapters // 3
first_third = [r for r in results if r[0] <= third]
second_third = [r for r in results if third < r[0] <= 2 * third]
last_third = [r for r in results if r[0] > 2 * third]

print(f"\nTREND (by thirds):")
for label, group in [
    (f"Ch 1-{third}", first_third),
    (f"Ch {third+1}-{2*third}", second_third),
    (f"Ch {2*third+1}-{total_chapters}", last_third)
]:
    g_pent = sum(r[3] for r in group)
    g_total = sum(r[2] for r in group)
    if g_total > 0:
        print(f"  {label:>12s}: {g_pent/g_total:.1%} pentameter ({g_pent}/{g_total} clauses)")

# Quarters
q = total_chapters // 4
quarters = [
    (f"Ch 1-{q}", [r for r in results if r[0] <= q]),
    (f"Ch {q+1}-{2*q}", [r for r in results if q < r[0] <= 2*q]),
    (f"Ch {2*q+1}-{3*q}", [r for r in results if 2*q < r[0] <= 3*q]),
    (f"Ch {3*q+1}-{total_chapters}", [r for r in results if r[0] > 3*q]),
]
print(f"\nTREND (by quarters):")
for label, group in quarters:
    g_pent = sum(r[3] for r in group)
    g_total = sum(r[2] for r in group)
    if g_total > 0:
        print(f"  {label:>12s}: {g_pent/g_total:.1%} pentameter ({g_pent}/{g_total} clauses)")

# First 10 vs Last 10
first_10 = [r for r in results if r[0] <= 10]
last_10 = [r for r in results if r[0] > total_chapters - 10]
print(f"\nFirst 10 chapters: {sum(r[3] for r in first_10)/sum(r[2] for r in first_10):.1%}")
print(f"Last 10 chapters:  {sum(r[3] for r in last_10)/sum(r[2] for r in last_10):.1%}")

# Chapter with highest and lowest
highest = max(results, key=lambda r: r[4])
lowest = min(results, key=lambda r: r[4] if r[2] > 20 else 1.0)
print(f"\nHighest: Ch {highest[0]} ({highest[4]:.1%})")
print(f"Lowest:  Ch {lowest[0]} ({lowest[4]:.1%})")

# Compare to ACIM
print()
print("=" * 70)
print("COMPARISON: ACIM vs Moby Dick")
print("=" * 70)
print()
print(f"{'Metric':>30s} | {'ACIM Text':>10s} | {'Moby Dick':>10s}")
print(f"{'------':>30s} | {'----------':>10s} | {'----------':>10s}")
print(f"{'Overall pentameter':>30s} | {'23.4%':>10s} | {f'{overall:.1%}':>10s}")

# ACIM values from previous run
acim_early = 21.9
acim_late = 27.1
md_early = sum(r[3] for r in first_third) / sum(r[2] for r in first_third) * 100
md_late = sum(r[3] for r in last_third) / sum(r[2] for r in last_third) * 100
print(f"{'Early third':>30s} | {f'{acim_early:.1f}%':>10s} | {f'{md_early:.1f}%':>10s}")
print(f"{'Late third':>30s} | {f'{acim_late:.1f}%':>10s} | {f'{md_late:.1f}%':>10s}")
print(f"{'Change (early to late)':>30s} | {f'+{acim_late-acim_early:.1f}%':>10s} | {f'+{md_late-md_early:.1f}%':>10s}")
print(f"{'Increase ratio':>30s} | {f'{acim_late/acim_early:.2f}x':>10s} | {f'{md_late/md_early:.2f}x':>10s}")
