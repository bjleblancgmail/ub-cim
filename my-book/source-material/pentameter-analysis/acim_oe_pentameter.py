#!/usr/bin/env python3
"""
Pentameter scan of ACIM Original Edition (EPUB).
Scans Text, Workbook, and Manual for Teachers separately.
Reports chapter-by-chapter and overall trends.
"""

import zipfile
import re

EPUB = '/Users/brianleblanc/code/ub-cim/my-book/Course In Miracles/Original Edition/acim-oe-complete-2026.epub'

def strip_html(html):
    """Remove HTML tags and clean text."""
    text = re.sub(r'<[^>]+>', ' ', html)
    text = re.sub(r'&[a-z]+;', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def count_syllables(word):
    """Estimate syllable count."""
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
    """Split text into clauses on punctuation, count syllables per clause,
    check if 9-11 syllables (pentameter range)."""
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

def read_epub_file(z, path):
    """Read and strip HTML from an EPUB file."""
    data = z.read(path).decode('utf-8')
    return strip_html(data)

# ============ MAIN ============

with zipfile.ZipFile(EPUB) as z:
    files = z.namelist()

    # ---- TEXT (chap1-31) ----
    print("=" * 70)
    print("TEXT (Chapters 1-31)")
    print("=" * 70)

    text_results = []
    for ch in range(1, 32):
        fname = f'OEBPS/Text/chap{ch}.xhtml'
        if fname in files:
            text = read_epub_file(z, fname)
            words = text.split()
            ratio, clauses = estimate_pentameter_ratio(text)
            text_results.append((ch, ratio, clauses, len(words)))
            print(f"  Ch {ch:2d}: {ratio*100:5.1f}% pentameter  ({clauses} clauses, {len(words)} words)")
        else:
            print(f"  Ch {ch:2d}: FILE NOT FOUND")

    # Text summary
    early = [r for r in text_results if r[0] <= 10]
    mid = [r for r in text_results if 11 <= r[0] <= 20]
    late = [r for r in text_results if r[0] >= 21]

    def avg_ratio(results):
        total_pent = sum(r[1] * r[2] for r in results)
        total_clauses = sum(r[2] for r in results)
        return total_pent / total_clauses * 100 if total_clauses else 0

    all_text_pent = sum(r[1] * r[2] for r in text_results)
    all_text_clauses = sum(r[2] for r in text_results)

    print(f"\n  OVERALL: {all_text_pent/all_text_clauses*100:.1f}%")
    print(f"  Ch 1-10:  {avg_ratio(early):.1f}%")
    print(f"  Ch 11-20: {avg_ratio(mid):.1f}%")
    print(f"  Ch 21-31: {avg_ratio(late):.1f}%")
    print(f"  Total words: {sum(r[3] for r in text_results)}")

    # ---- WORKBOOK ----
    print("\n" + "=" * 70)
    print("WORKBOOK FOR STUDENTS")
    print("=" * 70)

    # Collect all workbook files
    wb_files = []
    # Part 1 intro
    if 'OEBPS/Text/part1.xhtml' in files:
        wb_files.append(('Part1-Intro', 'OEBPS/Text/part1.xhtml'))
    # Lessons (p1-chap = individual lessons or groups)
    for f in sorted(files):
        if f.startswith('OEBPS/Text/p1-chap'):
            num = re.search(r'p1-chap(\d+)', f)
            if num:
                wb_files.append((f'Lesson-{num.group(1)}', f))
    # Reviews
    for i in range(1, 7):
        fname = f'OEBPS/Text/review_{i}.xhtml'
        if fname in files:
            wb_files.append((f'Review-{i}', fname))
    # Part 2
    if 'OEBPS/Text/part2.xhtml' in files:
        wb_files.append(('Part2-Intro', 'OEBPS/Text/part2.xhtml'))

    wb_results = []
    for label, fname in wb_files:
        text = read_epub_file(z, fname)
        words = text.split()
        ratio, clauses = estimate_pentameter_ratio(text)
        wb_results.append((label, ratio, clauses, len(words)))

    # Group workbook results for trend display
    # Figure out lesson numbers
    lesson_data = []
    for label, ratio, clauses, words in wb_results:
        m = re.search(r'Lesson-(\d+)', label)
        if m:
            lesson_data.append((int(m.group(1)), ratio, clauses, words))

    # Sort by lesson number
    lesson_data.sort(key=lambda x: x[0])

    # Show in ranges
    ranges = [(1, 50), (51, 100), (101, 150), (151, 200), (201, 250), (251, 300), (301, 365)]
    for lo, hi in ranges:
        group = [r for r in lesson_data if lo <= r[0] <= hi]
        if group:
            total_pent = sum(r[1] * r[2] for r in group)
            total_cl = sum(r[2] for r in group)
            total_w = sum(r[3] for r in group)
            if total_cl > 0:
                print(f"  Lessons {lo:3d}-{hi:3d}: {total_pent/total_cl*100:5.1f}% pentameter  ({total_cl} clauses, {total_w} words)")

    # Reviews
    review_data = [(l, r, c, w) for l, r, c, w in wb_results if 'Review' in l]
    if review_data:
        total_pent = sum(r[1] * r[2] for r in review_data)
        total_cl = sum(r[2] for r in review_data)
        total_w = sum(r[3] for r in review_data)
        if total_cl > 0:
            print(f"  Reviews:       {total_pent/total_cl*100:5.1f}% pentameter  ({total_cl} clauses, {total_w} words)")

    # Overall workbook
    all_wb_pent = sum(r[1] * r[2] for r in wb_results)
    all_wb_clauses = sum(r[2] for r in wb_results)
    all_wb_words = sum(r[3] for r in wb_results)

    early_wb = [r for r in lesson_data if r[0] <= 100]
    late_wb = [r for r in lesson_data if r[0] > 250]

    print(f"\n  OVERALL: {all_wb_pent/all_wb_clauses*100:.1f}%")
    if early_wb:
        e_pent = sum(r[1]*r[2] for r in early_wb)
        e_cl = sum(r[2] for r in early_wb)
        print(f"  Early (L1-100):   {e_pent/e_cl*100:.1f}%")
    if late_wb:
        l_pent = sum(r[1]*r[2] for r in late_wb)
        l_cl = sum(r[2] for r in late_wb)
        print(f"  Late (L251-365):  {l_pent/l_cl*100:.1f}%")
    print(f"  Total words: {all_wb_words}")

    # ---- MANUAL FOR TEACHERS ----
    print("\n" + "=" * 70)
    print("MANUAL FOR TEACHERS")
    print("=" * 70)

    manual_results = []
    # b3-intro
    if 'OEBPS/Text/b3-intro.xhtml' in files:
        text = read_epub_file(z, 'OEBPS/Text/b3-intro.xhtml')
        words = text.split()
        ratio, clauses = estimate_pentameter_ratio(text)
        manual_results.append((0, ratio, clauses, len(words)))
        print(f"  Intro:  {ratio*100:5.1f}% pentameter  ({clauses} clauses, {len(words)} words)")

    for ch in range(1, 30):
        fname = f'OEBPS/Text/b3-chap{ch}.xhtml'
        if fname in files:
            text = read_epub_file(z, fname)
            words = text.split()
            ratio, clauses = estimate_pentameter_ratio(text)
            manual_results.append((ch, ratio, clauses, len(words)))
            print(f"  M {ch:2d}:   {ratio*100:5.1f}% pentameter  ({clauses} clauses, {len(words)} words)")

    # Manual summary
    all_m_pent = sum(r[1] * r[2] for r in manual_results)
    all_m_clauses = sum(r[2] for r in manual_results)
    all_m_words = sum(r[3] for r in manual_results)

    early_m = [r for r in manual_results if r[0] <= 14]
    late_m = [r for r in manual_results if r[0] > 14]

    print(f"\n  OVERALL: {all_m_pent/all_m_clauses*100:.1f}%")
    if early_m:
        e_pent = sum(r[1]*r[2] for r in early_m)
        e_cl = sum(r[2] for r in early_m)
        print(f"  Early (Intro-M14): {e_pent/e_cl*100:.1f}%")
    if late_m:
        l_pent = sum(r[1]*r[2] for r in late_m)
        l_cl = sum(r[2] for r in late_m)
        print(f"  Late (M15-M29):    {l_pent/l_cl*100:.1f}%")
    print(f"  Total words: {all_m_words}")

    # ---- CLARIFICATION OF TERMS ----
    print("\n" + "=" * 70)
    print("CLARIFICATION OF TERMS")
    print("=" * 70)

    cot_results = []
    for ch in range(1, 16):
        fname = f'OEBPS/Text/p2-chap{ch}.xhtml'
        if fname in files:
            text = read_epub_file(z, fname)
            words = text.split()
            ratio, clauses = estimate_pentameter_ratio(text)
            cot_results.append((ch, ratio, clauses, len(words)))
            print(f"  Term {ch:2d}: {ratio*100:5.1f}% pentameter  ({clauses} clauses, {len(words)} words)")

    # Epilogue
    if 'OEBPS/Text/p2-epi.xhtml' in files:
        text = read_epub_file(z, 'OEBPS/Text/p2-epi.xhtml')
        words = text.split()
        ratio, clauses = estimate_pentameter_ratio(text)
        cot_results.append((99, ratio, clauses, len(words)))
        print(f"  Epilog: {ratio*100:5.1f}% pentameter  ({clauses} clauses, {len(words)} words)")

    if cot_results:
        all_c_pent = sum(r[1] * r[2] for r in cot_results)
        all_c_clauses = sum(r[2] for r in cot_results)
        all_c_words = sum(r[3] for r in cot_results)
        print(f"\n  OVERALL: {all_c_pent/all_c_clauses*100:.1f}%")
        print(f"  Total words: {all_c_words}")

    # ---- GRAND SUMMARY ----
    print("\n" + "=" * 70)
    print("GRAND SUMMARY")
    print("=" * 70)

    grand_clauses = all_text_clauses + all_wb_clauses + all_m_clauses
    grand_pent = all_text_pent + all_wb_pent + all_m_pent
    grand_words = sum(r[3] for r in text_results) + all_wb_words + all_m_words
    if cot_results:
        grand_clauses += all_c_clauses
        grand_pent += all_c_pent
        grand_words += all_c_words

    print(f"  Total words analyzed: {grand_words}")
    print(f"  Total clauses: {grand_clauses}")
    print(f"  Overall pentameter: {grand_pent/grand_clauses*100:.1f}%")
    print()
    print(f"  Text:      {all_text_pent/all_text_clauses*100:.1f}%  ({sum(r[3] for r in text_results)} words)")
    print(f"  Workbook:  {all_wb_pent/all_wb_clauses*100:.1f}%  ({all_wb_words} words)")
    print(f"  Manual:    {all_m_pent/all_m_clauses*100:.1f}%  ({all_m_words} words)")
    if cot_results:
        print(f"  Terms:     {all_c_pent/all_c_clauses*100:.1f}%  ({all_c_words} words)")
