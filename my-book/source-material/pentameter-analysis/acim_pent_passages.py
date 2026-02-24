#!/usr/bin/env python3
"""
Find high-density pentameter passages in ACIM.
Uses a sliding window over sentences to find sustained runs
where pentameter prevalence is highest.
Outputs the passages and their stressed-word distillations.
"""

import re
import sys

ACIM_FILE = "/Users/brianleblanc/code/ub-cim/my-book/Course In Miracles/ACourseInMiraclesUrtextEdition.md"
OUTPUT_FILE = "/tmp/acim_high_pentameter_passages.md"

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


def is_pentameter_clause(clause):
    """Check if a clause has 9-11 syllables (pentameter range)."""
    words = clause.split()
    if len(words) < 3:
        return False, 0
    syl_count = sum(count_syllables(w) for w in words)
    return (9 <= syl_count <= 11), syl_count


def get_stressed_words(clause):
    """
    Simple heuristic: in iambic pentameter, content words (nouns, verbs,
    adjectives, adverbs) tend to fall on stressed beats.
    Return content words (skip common function words).
    """
    function_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to',
        'for', 'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were',
        'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
        'will', 'would', 'could', 'should', 'may', 'might', 'shall',
        'can', 'it', 'its', 'he', 'she', 'they', 'them', 'their',
        'his', 'her', 'my', 'your', 'our', 'who', 'which', 'that',
        'this', 'these', 'those', 'what', 'when', 'where', 'how',
        'not', 'no', 'nor', 'if', 'as', 'so', 'than', 'too',
        'very', 'just', 'also', 'there', 'here', 'then', 'now',
        'up', 'out', 'about', 'into', 'over', 'after', 'before',
        'between', 'through', 'during', 'without', 'within',
        'you', 'we', 'i', 'me', 'us', 'him', 'whom',
    }
    words = clause.split()
    stressed = []
    for w in words:
        clean = re.sub(r'[^a-zA-Z]', '', w).lower()
        if clean and clean not in function_words:
            stressed.append(clean)
    return stressed


def clean_editorial(text):
    """Remove footnotes, page refs, editorial markers."""
    text = re.sub(r'\b\d{1,4}\b', '', text)
    text = re.sub(r'[TWM]\(\d+\)', '', text)
    text = re.sub(r'PROOF\s+COPY', '', text)
    text = re.sub(r'\(Notes?\s+[\d\s:]+\)', '', text)
    text = re.sub(r'Volume [IVX]+ Text', '', text)
    text = re.sub(r'Volume [IVX]+ Workbook', '', text)
    text = re.sub(r'Volume [IVX]+ Manual', '', text)
    text = re.sub(r'Urtext manuscript[^.]*\.', '', text)
    text = re.sub(r'The Notes has[^.]*\.', '', text)
    text = re.sub(r'Handwritten mark-up[^.]*\.', '', text)
    text = re.sub(r'[IVX]+-\d+', '', text)
    text = re.sub(r'\b\d+-\d+\b', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def extract_paragraphs_with_refs(text, volume_prefix):
    """
    Split text into paragraphs using paragraph markers.
    Returns list of (reference, paragraph_text).
    """
    if volume_prefix == 'T':
        # Match T N X N. patterns
        pattern = r'(T\s+\d+\s+[A-Z]\s+\d+[a-z]?)\.\s*'
    elif volume_prefix == 'W':
        # Match W/w N L N or w N ini N patterns
        pattern = r'([Ww]\s+\d+\s+(?:L|ini|R\d|In\d|W\d|FL|EP)\s*\d*)\.\s*'
    elif volume_prefix == 'M':
        pattern = r'([Mm]\s+\d+\s+[A-Z]\s+\d+)\.\s*'
    else:
        pattern = None

    if pattern is None:
        return [("unknown", text)]

    parts = re.split(pattern, text)
    paragraphs = []
    for i in range(1, len(parts) - 1, 2):
        ref = parts[i].strip()
        para_text = parts[i + 1].strip() if i + 1 < len(parts) else ""
        if para_text:
            paragraphs.append((ref, para_text))

    if not paragraphs:
        return [("unknown", text)]

    return paragraphs


# ============================================================
# READ THE FILE
# ============================================================
print("Reading ACIM file...")
with open(ACIM_FILE, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# ============================================================
# COLLECT ALL TEXT BY VOLUME
# ============================================================

# Text: lines 77-2033 (1-indexed)
text_content = ""
for line_idx in range(76, 2034):
    line = lines[line_idx].strip()
    if line and len(line) > 100:
        text_content += " " + line

# Workbook: lines 2065-3364
wb_content = ""
for line_idx in range(2064, 3365):
    line = lines[line_idx].strip()
    if line and len(line) > 100:
        wb_content += " " + line

# Manual: lines 3365-3524
manual_content = ""
for line_idx in range(3364, 3525):
    line = lines[line_idx].strip()
    if line and len(line) > 100:
        manual_content += " " + line

# ============================================================
# ANALYZE USING SLIDING WINDOW OVER SENTENCES
# ============================================================

def find_high_pentameter_passages(text, volume_prefix, volume_name):
    """
    Split into sentences. Use sliding window of 8 sentences.
    Find windows where pentameter ratio >= 50%.
    Merge overlapping windows. Return top passages.
    """
    # Split into sentences
    sentence_endings = re.split(r'(?<=[.!?])\s+', text)
    sentences = [s.strip() for s in sentence_endings if s.strip() and len(s.strip()) > 20]

    if not sentences:
        return []

    # For each sentence, split into clauses and check pentameter
    sentence_scores = []
    for sent in sentences:
        clauses = re.split(r'[,;:]', sent)
        clauses = [c.strip() for c in clauses if c.strip() and len(c.split()) >= 3]
        if not clauses:
            sentence_scores.append((sent, 0, 0, 0))
            continue
        pent = sum(1 for c in clauses if is_pentameter_clause(c)[0])
        total = len(clauses)
        ratio = pent / total if total > 0 else 0
        sentence_scores.append((sent, ratio, pent, total))

    # Sliding window of 8 sentences
    WINDOW = 8
    MIN_RATIO = 0.40  # 40% pentameter threshold for "high density"

    windows = []
    for i in range(len(sentence_scores) - WINDOW + 1):
        window = sentence_scores[i:i + WINDOW]
        total_clauses = sum(s[3] for s in window)
        pent_clauses = sum(s[2] for s in window)
        if total_clauses < 5:
            continue
        ratio = pent_clauses / total_clauses
        if ratio >= MIN_RATIO:
            windows.append((i, i + WINDOW, ratio, pent_clauses, total_clauses))

    if not windows:
        # Lower threshold
        MIN_RATIO = 0.35
        for i in range(len(sentence_scores) - WINDOW + 1):
            window = sentence_scores[i:i + WINDOW]
            total_clauses = sum(s[3] for s in window)
            pent_clauses = sum(s[2] for s in window)
            if total_clauses < 5:
                continue
            ratio = pent_clauses / total_clauses
            if ratio >= MIN_RATIO:
                windows.append((i, i + WINDOW, ratio, pent_clauses, total_clauses))

    # Merge overlapping windows, keeping best ratio for each region
    if not windows:
        return []

    # Sort by ratio descending
    windows.sort(key=lambda x: x[2], reverse=True)

    # Merge overlapping
    merged = []
    used = set()
    for start, end, ratio, pc, tc in windows:
        if any(start <= u < end or start < u_end <= end
               for u, u_end in used):
            continue
        # Expand to find full extent of high-pentameter region
        while start > 0 and sentence_scores[start - 1][1] >= 0.3:
            start -= 1
        while end < len(sentence_scores) and sentence_scores[end - 1][1] >= 0.3:
            end += 1
        end = min(end, len(sentence_scores))

        region = sentence_scores[start:end]
        total_c = sum(s[3] for s in region)
        pent_c = sum(s[2] for s in region)
        if total_c == 0:
            continue
        region_ratio = pent_c / total_c

        passage_text = " ".join(s[0] for s in region)
        passage_text = clean_editorial(passage_text)

        # Get stressed words from pentameter clauses
        all_stressed = []
        for sent_text, s_ratio, s_pent, s_total in region:
            clauses = re.split(r'[,;:]', sent_text)
            for clause in clauses:
                clause = clause.strip()
                if len(clause.split()) >= 3:
                    is_pent, syl = is_pentameter_clause(clause)
                    if is_pent:
                        all_stressed.extend(get_stressed_words(clause))

        merged.append({
            'start_idx': start,
            'end_idx': end,
            'sentences': end - start,
            'ratio': region_ratio,
            'pent_clauses': pent_c,
            'total_clauses': total_c,
            'text': passage_text,
            'stressed_words': all_stressed,
            'volume': volume_name,
        })
        used.add((start, end))

        if len(merged) >= 25:  # Top 25 per volume
            break

    # Sort by ratio
    merged.sort(key=lambda x: x['ratio'], reverse=True)
    return merged[:25]


print("Analyzing Text...")
text_passages = find_high_pentameter_passages(text_content, 'T', 'Text')
print(f"  Found {len(text_passages)} high-density passages")

print("Analyzing Workbook...")
wb_passages = find_high_pentameter_passages(wb_content, 'W', 'Workbook')
print(f"  Found {len(wb_passages)} high-density passages")

print("Analyzing Manual...")
manual_passages = find_high_pentameter_passages(manual_content, 'M', 'Manual')
print(f"  Found {len(manual_passages)} high-density passages")

# ============================================================
# TRY TO IDENTIFY CHAPTER/SECTION FOR EACH PASSAGE
# ============================================================

def find_reference(passage_text):
    """Try to find ACIM paragraph references in the passage."""
    refs = re.findall(r'T\s+(\d+)\s+([A-Z])\s+(\d+)', passage_text)
    if refs:
        first = refs[0]
        last = refs[-1]
        if first == last:
            return f"T {first[0]} {first[1]} {first[2]}"
        else:
            return f"T {first[0]} {first[1]} {first[2]} - T {last[0]} {last[1]} {last[2]}"

    refs = re.findall(r'[Ww]\s+(\d+)\s+L\s+(\d+)', passage_text)
    if refs:
        first = refs[0]
        last = refs[-1]
        return f"W {first[0]} L {first[1]} - W {last[0]} L {last[1]}" if first != last else f"W {first[0]} L {first[1]}"

    refs = re.findall(r'[Mm]\s+(\d+)\s+[A-Z]\s+(\d+)', passage_text)
    if refs:
        first = refs[0]
        last = refs[-1]
        return f"M {first[0]}.{first[1]} - M {last[0]}.{last[1]}" if first != last else f"M {first[0]}.{first[1]}"

    return "Reference not found"


# ============================================================
# WRITE OUTPUT FILE
# ============================================================

output_lines = []
output_lines.append("# ACIM High-Density Pentameter Passages")
output_lines.append("")
output_lines.append("Passages where pentameter-length clauses (9-11 syllables) reach")
output_lines.append("40%+ of all clauses in a sliding window of 8+ sentences.")
output_lines.append("")
output_lines.append("Method: Split text on punctuation into clauses, count syllables,")
output_lines.append("check for 9-11 syllable range. Sliding window finds sustained runs.")
output_lines.append("")
output_lines.append(f"Control comparison: Moby Dick overall = 18.8% (flat across book)")
output_lines.append(f"ACIM overall = 23.9% (increasing toward conclusion of each volume)")
output_lines.append("")

all_passages = []
for p in text_passages:
    p['ref'] = find_reference(p['text'])
    all_passages.append(p)
for p in wb_passages:
    p['ref'] = find_reference(p['text'])
    all_passages.append(p)
for p in manual_passages:
    p['ref'] = find_reference(p['text'])
    all_passages.append(p)

# Sort all by ratio
all_passages.sort(key=lambda x: x['ratio'], reverse=True)

output_lines.append("---")
output_lines.append("")
output_lines.append("## Summary: Top 50 Passages Across All Volumes")
output_lines.append("")
output_lines.append(f"| # | Volume | Ratio | Pent/Total | Reference |")
output_lines.append(f"|---|--------|-------|------------|-----------|")

for i, p in enumerate(all_passages[:50], 1):
    output_lines.append(
        f"| {i} | {p['volume']} | {p['ratio']:.0%} | "
        f"{p['pent_clauses']}/{p['total_clauses']} | {p['ref']} |"
    )

output_lines.append("")
output_lines.append("---")
output_lines.append("")

# Write detailed passages by volume
for vol_name, passages in [("Text", text_passages), ("Workbook", wb_passages), ("Manual", manual_passages)]:
    output_lines.append(f"## {vol_name}: High-Density Pentameter Passages")
    output_lines.append("")

    if not passages:
        output_lines.append("No passages found above threshold.")
        output_lines.append("")
        continue

    for i, p in enumerate(passages[:15], 1):
        ref = find_reference(p['text'])
        output_lines.append(f"### {vol_name} Passage {i} ({p['ratio']:.0%} pentameter)")
        output_lines.append(f"**Reference:** {ref}")
        output_lines.append(f"**Pentameter clauses:** {p['pent_clauses']}/{p['total_clauses']}")
        output_lines.append(f"**Sentences:** {p['sentences']}")
        output_lines.append("")

        # Clean and truncate passage text for readability
        clean = p['text']
        # Remove paragraph markers for readability
        clean = re.sub(r'T\s+\d+\s+[A-Z]\s+\d+[a-z]?\.\s*', '', clean)
        clean = re.sub(r'[Ww]\s+\d+\s+(?:L|ini|R\d|In\d|W\d|FL|EP)\s*\d*\.\s*', '', clean)
        clean = re.sub(r'[Mm]\s+\d+\s+[A-Z]\s+\d+\.\s*', '', clean)
        clean = re.sub(r'Chapter \d+\s*-\s*[A-Za-z\s]+(?=[A-Z])', '', clean)
        # Trim to reasonable length
        words = clean.split()
        if len(words) > 300:
            clean = ' '.join(words[:300]) + " [...]"

        output_lines.append("**Passage:**")
        output_lines.append(f"> {clean}")
        output_lines.append("")

        # Stressed words distillation
        if p['stressed_words']:
            unique_stressed = []
            seen = set()
            for w in p['stressed_words']:
                if w not in seen:
                    unique_stressed.append(w)
                    seen.add(w)
            output_lines.append(f"**Stressed-word distillation** (content words from pentameter clauses):")
            output_lines.append(f"> {', '.join(unique_stressed[:40])}")
            output_lines.append("")

        output_lines.append("---")
        output_lines.append("")

# Write the file
output_text = '\n'.join(output_lines)
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.write(output_text)

print(f"\nResults written to {OUTPUT_FILE}")
print(f"Total passages found: {len(all_passages)}")
print(f"Top passage: {all_passages[0]['volume']} at {all_passages[0]['ratio']:.0%} ({all_passages[0]['ref']})")
print(f"File size: {len(output_text):,} characters")
