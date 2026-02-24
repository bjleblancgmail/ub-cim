#!/usr/bin/env python3
"""
Full pentameter prevalence scan across entire ACIM:
  1. Text (Chapters 1-31)
  2. Workbook (Lessons 1-365 + reviews/intros)
  3. Manual for Teachers (Sections 1-30)

Outputs results for each volume separately.
"""

import re
import sys

ACIM_FILE = "/Users/brianleblanc/code/ub-cim/my-book/Course In Miracles/ACourseInMiraclesUrtextEdition.md"

# ============================================================
# SYLLABLE COUNTING
# ============================================================
def count_syllables(word):
    """Estimate syllable count using vowel-group heuristic."""
    word = word.lower().strip()
    if not word:
        return 0
    # Remove non-alpha
    word = re.sub(r'[^a-z]', '', word)
    if not word:
        return 0
    if len(word) <= 2:
        return 1
    # Count vowel groups
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
    # Subtract silent e
    if word.endswith('e') and count > 1 and not word.endswith('le'):
        count -= 1
    # Handle special endings
    if word.endswith('ed') and count > 1:
        if len(word) >= 4 and word[-3] not in 'dt':
            count -= 1
    return max(count, 1)


def estimate_pentameter_ratio(text):
    """
    Estimate what fraction of the text falls into pentameter-like clauses.
    Split on punctuation to get clauses, count syllables per clause,
    check if 9-11 syllables (iambic pentameter range).
    Returns (ratio, total_clauses, pentameter_clauses).
    """
    # Split on sentence-ending and clause-ending punctuation
    clauses = re.split(r'[.!?;:,]', text)
    clauses = [c.strip() for c in clauses if c.strip()]

    if not clauses:
        return 0.0, 0, 0

    pent_count = 0
    total = 0

    for clause in clauses:
        words = clause.split()
        if len(words) < 3:  # skip very short fragments
            continue
        total += 1
        syl_count = sum(count_syllables(w) for w in words)
        if 9 <= syl_count <= 11:
            pent_count += 1

    if total == 0:
        return 0.0, 0, 0

    return pent_count / total, total, pent_count


def clean_text(text):
    """Remove footnotes, page numbers, editorial markers, and reference codes."""
    # Remove footnote numbers (standalone digits)
    text = re.sub(r'\b\d{1,4}\b', '', text)
    # Remove page references like T(544) or W(12)
    text = re.sub(r'[TWM]\(\d+\)', '', text)
    # Remove "PROOF COPY" and similar
    text = re.sub(r'PROOF\s+COPY', '', text)
    # Remove "Notes" references like (Notes 1936 12:71)
    text = re.sub(r'\(Notes?\s+[\d\s:]+\)', '', text)
    # Remove "Volume I Text" headers
    text = re.sub(r'Volume [IVX]+ Text', '', text)
    # Remove footnote text (starts with number and contains manuscript/Notes references)
    # These are harder to remove perfectly, but let's strip obvious patterns
    text = re.sub(r'Urtext manuscript[^.]*\.', '', text)
    text = re.sub(r'The Notes has[^.]*\.', '', text)
    text = re.sub(r'Handwritten mark-up[^.]*\.', '', text)
    # Remove paragraph markers like "T 1 A 1." or "T 21 B 5."
    # Keep the actual text content
    text = re.sub(r'\bT\s+\d+\s+[A-Z]\s+\d+[a-z]?\.\s*', '', text)
    text = re.sub(r'\bT\s+\d+\s+[A-Z]\.\s*', '', text)
    # Remove section headers like "Chapter 1 - Introduction to Miracles"
    text = re.sub(r'Chapter \d+\s*-\s*[A-Za-z\s]+(?=[A-Z])', '', text)
    # Remove workbook lesson markers
    text = re.sub(r'\bW\s+\d+\s+L\s+\d+\.?\s*', '', text)
    text = re.sub(r'\bw\s+\d+\s+L\s+\d+\.?\s*', '', text)
    text = re.sub(r'\bw\s+\d+\s+ini\s+\d+\.?\s*', '', text)
    # Remove manual markers
    text = re.sub(r'\bM\s+\d+\s+[A-Z]\s+\d+\.?\s*', '', text)
    text = re.sub(r'\bm\s+\d+\s+[A-Z]\s+\d+\.?\s*', '', text)
    # Remove page number references like "1-2 12" or "II-3"
    text = re.sub(r'\b[IVX]+-\d+\b', '', text)
    text = re.sub(r'\b\d+-\d+\b', '', text)
    # Clean up extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text


# ============================================================
# READ THE FILE
# ============================================================
print("Reading ACIM file...")
with open(ACIM_FILE, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total lines in file: {len(lines)}")
print()

# ============================================================
# PART 1: TEXT (Chapters 1-31)
# ============================================================
print("=" * 70)
print("PART 1: TEXT - Pentameter Prevalence by Chapter (1-31)")
print("=" * 70)
print()

# Text chapters are on lines 77, 81, 85, ..., 2033 (0-indexed: 76, 80, 84, ..., 2032)
# Each line contains "Chapter N - Title" followed by the entire chapter content
# Some chapters span across the next line too (line and line+2)

text_chapters = {}
chapter_lines = list(range(76, 2034, 4))  # 0-indexed: 76, 80, 84, ...

current_chapter = None
for line_idx in chapter_lines:
    if line_idx >= len(lines):
        break
    line = lines[line_idx].strip()
    if not line:
        continue

    # Try to extract chapter number
    ch_match = re.match(r'Chapter\s+(\d+)', line)
    if ch_match:
        ch_num = int(ch_match.group(1))
        if ch_num not in text_chapters:
            text_chapters[ch_num] = ""
        text_chapters[ch_num] += " " + line
        current_chapter = ch_num
    elif current_chapter:
        # Continuation line for same chapter (some content spills over)
        text_chapters[current_chapter] += " " + line

# Also pick up content from the alternate lines (some chapters have content on adjacent lines)
for line_idx in range(76, 2034):
    if line_idx >= len(lines):
        break
    line = lines[line_idx].strip()
    if not line or len(line) < 100:  # Skip short lines (headers, page numbers)
        continue
    # Check if this line starts with "Volume I Text" (continuation content)
    if line.startswith("Volume I Text"):
        # Find which chapter this belongs to by looking at paragraph markers
        ch_match = re.search(r'\bT\s+(\d+)\s+[A-Z]', line)
        if ch_match:
            ch_num = int(ch_match.group(1))
            if ch_num in text_chapters:
                text_chapters[ch_num] += " " + line

print(f"{'Ch':>3s} | {'Words':>6s} | {'Clauses':>8s} | {'Pent':>5s} | {'Ratio':>6s} | {'Bar'}")
print(f"{'---':>3s} | {'------':>6s} | {'--------':>8s} | {'-----':>5s} | {'------':>6s} | {'---'}")

chapter_results = []
for ch_num in sorted(text_chapters.keys()):
    raw_text = text_chapters[ch_num]
    cleaned = clean_text(raw_text)
    word_count = len(cleaned.split())
    ratio, total_clauses, pent_clauses = estimate_pentameter_ratio(cleaned)
    bar = "#" * int(ratio * 50)
    print(f"{ch_num:3d} | {word_count:6d} | {total_clauses:8d} | {pent_clauses:5d} | {ratio:5.1%} | {bar}")
    chapter_results.append((ch_num, word_count, total_clauses, pent_clauses, ratio))

# Summary
if chapter_results:
    total_words = sum(r[1] for r in chapter_results)
    total_clauses = sum(r[2] for r in chapter_results)
    total_pent = sum(r[3] for r in chapter_results)
    overall = total_pent / total_clauses if total_clauses > 0 else 0
    print(f"\n{'ALL':>3s} | {total_words:6d} | {total_clauses:8d} | {total_pent:5d} | {overall:5.1%} |")

    # Trend: first half vs second half
    first_half = [r for r in chapter_results if r[0] <= 15]
    second_half = [r for r in chapter_results if r[0] > 15]
    fh_pent = sum(r[3] for r in first_half)
    fh_total = sum(r[2] for r in first_half)
    sh_pent = sum(r[3] for r in second_half)
    sh_total = sum(r[2] for r in second_half)
    print(f"\nTREND:")
    print(f"  Chapters  1-15: {fh_pent/fh_total:.1%} pentameter ({fh_pent}/{fh_total} clauses)")
    print(f"  Chapters 16-31: {sh_pent/sh_total:.1%} pentameter ({sh_pent}/{sh_total} clauses)")

    # Thirds
    third1 = [r for r in chapter_results if r[0] <= 10]
    third2 = [r for r in chapter_results if 11 <= r[0] <= 20]
    third3 = [r for r in chapter_results if r[0] > 20]
    for label, group in [("Ch 1-10", third1), ("Ch 11-20", third2), ("Ch 21-31", third3)]:
        g_pent = sum(r[3] for r in group)
        g_total = sum(r[2] for r in group)
        if g_total > 0:
            print(f"  {label:>8s}: {g_pent/g_total:.1%} pentameter ({g_pent}/{g_total} clauses)")

print()
print("TEXT RESULTS COMPLETE.")
print()
sys.stdout.flush()

# ============================================================
# PART 2: WORKBOOK
# ============================================================
print("=" * 70)
print("PART 2: WORKBOOK - Pentameter Prevalence")
print("=" * 70)
print()

# Workbook content lines: 2064-3363 (0-indexed)
# Lines alternate between content and headers/page numbers
# Content lines tend to be very long (actual lesson text)

workbook_text_by_section = {}
current_section = "Introduction"

for line_idx in range(2064, 3365):
    if line_idx >= len(lines):
        break
    line = lines[line_idx].strip()
    if not line or len(line) < 50:
        continue

    # Detect lesson numbers
    lesson_match = re.search(r'Lesson\s+(\d+)', line)
    review_match = re.search(r'Review\s+(\d+)', line)
    part_match = re.search(r'Part\s+(\d+)', line)

    if lesson_match:
        lesson_num = int(lesson_match.group(1))
        # Group lessons into ranges for cleaner output
        if lesson_num <= 50:
            current_section = "Lessons 1-50"
        elif lesson_num <= 100:
            current_section = "Lessons 51-100"
        elif lesson_num <= 150:
            current_section = "Lessons 101-150"
        elif lesson_num <= 200:
            current_section = "Lessons 151-200"
        elif lesson_num <= 250:
            current_section = "Lessons 201-250"
        elif lesson_num <= 300:
            current_section = "Lessons 251-300"
        elif lesson_num <= 365:
            current_section = "Lessons 301-365"

    if current_section not in workbook_text_by_section:
        workbook_text_by_section[current_section] = ""
    workbook_text_by_section[current_section] += " " + line

# Order sections logically
wb_order = [
    "Introduction",
    "Lessons 1-50", "Lessons 51-100", "Lessons 101-150",
    "Lessons 151-200", "Lessons 201-250", "Lessons 251-300",
    "Lessons 301-365"
]

print(f"{'Section':>20s} | {'Words':>6s} | {'Clauses':>8s} | {'Pent':>5s} | {'Ratio':>6s} | {'Bar'}")
print(f"{'-------':>20s} | {'------':>6s} | {'--------':>8s} | {'-----':>5s} | {'------':>6s} | {'---'}")

wb_results = []
for section in wb_order:
    if section not in workbook_text_by_section:
        continue
    raw_text = workbook_text_by_section[section]
    cleaned = clean_text(raw_text)
    word_count = len(cleaned.split())
    ratio, total_clauses, pent_clauses = estimate_pentameter_ratio(cleaned)
    bar = "#" * int(ratio * 50)
    print(f"{section:>20s} | {word_count:6d} | {total_clauses:8d} | {pent_clauses:5d} | {ratio:5.1%} | {bar}")
    wb_results.append((section, word_count, total_clauses, pent_clauses, ratio))

if wb_results:
    total_words = sum(r[1] for r in wb_results)
    total_clauses = sum(r[2] for r in wb_results)
    total_pent = sum(r[3] for r in wb_results)
    overall = total_pent / total_clauses if total_clauses > 0 else 0
    print(f"\n{'WORKBOOK TOTAL':>20s} | {total_words:6d} | {total_clauses:8d} | {total_pent:5d} | {overall:5.1%} |")

    # Early vs Late comparison
    early_sections = ["Introduction", "Lessons 1-50", "Lessons 51-100"]
    late_sections = ["Lessons 251-300", "Lessons 301-365"]
    early = [r for r in wb_results if r[0] in early_sections]
    late = [r for r in wb_results if r[0] in late_sections]
    if early and late:
        e_pent = sum(r[3] for r in early)
        e_total = sum(r[2] for r in early)
        l_pent = sum(r[3] for r in late)
        l_total = sum(r[2] for r in late)
        print(f"\n  TREND:")
        print(f"  Early (Intro-L100): {e_pent/e_total:.1%} pentameter")
        print(f"  Late  (L251-365):   {l_pent/l_total:.1%} pentameter")

print()
print("WORKBOOK RESULTS COMPLETE.")
print()
sys.stdout.flush()

# ============================================================
# PART 3: MANUAL FOR TEACHERS
# ============================================================
print("=" * 70)
print("PART 3: MANUAL FOR TEACHERS - Pentameter Prevalence")
print("=" * 70)
print()

# Manual content: lines 3364-3523 (0-indexed)
# Sections are numbered M 1 through M 30

manual_text_by_section = {}
current_section = None

for line_idx in range(3364, 3525):
    if line_idx >= len(lines):
        break
    line = lines[line_idx].strip()
    if not line or len(line) < 50:
        continue

    # Detect section numbers from M references
    m_match = re.search(r'\bM\s+(\d+)\s+A\s+\d+', line)
    if m_match:
        section_num = int(m_match.group(1))
        current_section = f"M {section_num}"

    if current_section is None:
        current_section = "M 1"

    if current_section not in manual_text_by_section:
        manual_text_by_section[current_section] = ""
    manual_text_by_section[current_section] += " " + line

# Group manual sections for cleaner output
manual_groups = {}
for section_key, text in manual_text_by_section.items():
    m_num = int(section_key.split()[1])
    if m_num <= 10:
        group = "Sections 1-10"
    elif m_num <= 20:
        group = "Sections 11-20"
    else:
        group = "Sections 21-30"
    if group not in manual_groups:
        manual_groups[group] = ""
    manual_groups[group] += " " + text

# Also compute per-section for individual detail
print("Individual Sections:")
print(f"{'Section':>10s} | {'Words':>6s} | {'Clauses':>8s} | {'Pent':>5s} | {'Ratio':>6s}")
print(f"{'-------':>10s} | {'------':>6s} | {'--------':>8s} | {'-----':>5s} | {'------':>6s}")

manual_results = []
for section_key in sorted(manual_text_by_section.keys(), key=lambda x: int(x.split()[1])):
    raw_text = manual_text_by_section[section_key]
    cleaned = clean_text(raw_text)
    word_count = len(cleaned.split())
    ratio, total_clauses, pent_clauses = estimate_pentameter_ratio(cleaned)
    print(f"{section_key:>10s} | {word_count:6d} | {total_clauses:8d} | {pent_clauses:5d} | {ratio:5.1%}")
    manual_results.append((section_key, word_count, total_clauses, pent_clauses, ratio))

if manual_results:
    total_words = sum(r[1] for r in manual_results)
    total_clauses = sum(r[2] for r in manual_results)
    total_pent = sum(r[3] for r in manual_results)
    overall = total_pent / total_clauses if total_clauses > 0 else 0
    print(f"\n{'MANUAL TOTAL':>10s} | {total_words:6d} | {total_clauses:8d} | {total_pent:5d} | {overall:5.1%}")

    # Grouped trend
    print(f"\nGrouped Trend:")
    for group_name in ["Sections 1-10", "Sections 11-20", "Sections 21-30"]:
        if group_name in manual_groups:
            cleaned = clean_text(manual_groups[group_name])
            word_count = len(cleaned.split())
            ratio, tc, pc = estimate_pentameter_ratio(cleaned)
            print(f"  {group_name}: {ratio:.1%} pentameter ({pc}/{tc} clauses, {word_count} words)")

print()
print("MANUAL RESULTS COMPLETE.")
print()

# ============================================================
# GRAND SUMMARY
# ============================================================
print("=" * 70)
print("GRAND SUMMARY: All Three Volumes")
print("=" * 70)
print()

text_total_clauses = sum(r[2] for r in chapter_results) if chapter_results else 0
text_total_pent = sum(r[3] for r in chapter_results) if chapter_results else 0
text_ratio = text_total_pent / text_total_clauses if text_total_clauses > 0 else 0

wb_total_clauses = sum(r[2] for r in wb_results) if wb_results else 0
wb_total_pent = sum(r[3] for r in wb_results) if wb_results else 0
wb_ratio = wb_total_pent / wb_total_clauses if wb_total_clauses > 0 else 0

man_total_clauses = sum(r[2] for r in manual_results) if manual_results else 0
man_total_pent = sum(r[3] for r in manual_results) if manual_results else 0
man_ratio = man_total_pent / man_total_clauses if man_total_clauses > 0 else 0

print(f"{'Volume':>20s} | {'Clauses':>8s} | {'Pentameter':>10s} | {'Ratio':>6s}")
print(f"{'------':>20s} | {'--------':>8s} | {'----------':>10s} | {'------':>6s}")
print(f"{'Text (Ch 1-31)':>20s} | {text_total_clauses:8d} | {text_total_pent:10d} | {text_ratio:5.1%}")
print(f"{'Workbook (L 1-365)':>20s} | {wb_total_clauses:8d} | {wb_total_pent:10d} | {wb_ratio:5.1%}")
print(f"{'Manual (S 1-30)':>20s} | {man_total_clauses:8d} | {man_total_pent:10d} | {man_ratio:5.1%}")

grand_clauses = text_total_clauses + wb_total_clauses + man_total_clauses
grand_pent = text_total_pent + wb_total_pent + man_total_pent
grand_ratio = grand_pent / grand_clauses if grand_clauses > 0 else 0
print(f"{'TOTAL':>20s} | {grand_clauses:8d} | {grand_pent:10d} | {grand_ratio:5.1%}")

print()
print("ANALYSIS COMPLETE.")
