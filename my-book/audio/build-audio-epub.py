#!/usr/bin/env python3
"""
Build an audio-ready EPUB for "Across the Revelation Bridge" by Joseph.

Reads the markdown chapter and appendix files in order, strips all citations
and formatting artifacts, keeps section headings and bold/italic for EPUB,
and produces both a combined markdown and an EPUB via pandoc.
"""

import re
import os
import subprocess
import sys

BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
CHAPTERS_DIR = os.path.join(BASE_DIR, 'chapters')
APPENDICES_DIR = os.path.join(BASE_DIR, 'appendices')
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# Ordered list of source files (13-chapter structure)
CHAPTER_FILES = [
    ('chapters', 'introduction.md'),
    ('chapters', 'chapter-01-the-two-revelations.md'),
    ('chapters', 'chapter-02-terminology-bridge.md'),
    ('chapters', 'chapter-03-central-thesis-fusion-between-father-and-son.md'),
    ('chapters', 'chapter-04-sonship-supreme.md'),
    ('chapters', 'chapter-05-what-is-real.md'),
    ('chapters', 'chapter-06-what-survives.md'),
    ('chapters', 'chapter-07-miracles-and-time.md'),
    ('chapters', 'chapter-08-forgiveness-mercy-vs-love.md'),
    ('chapters', 'chapter-09-the-architecture-of-mind.md'),
    ('chapters', 'chapter-10-lucifer-rebellion-why-we-suffer.md'),
    ('chapters', 'chapter-11-the-atonement-and-the-crucifixion.md'),
    ('chapters', 'chapter-12-from-here-to-paradise.md'),
    ('chapters', 'chapter-13-the-jesus-both-books-reveal.md'),
    ('appendices', 'appendix-a-terminology-mapping-v2.md'),
    ('appendices', 'appendix-b-parallels-condensed.md'),
    ('appendices', 'appendix-c-miracle-principles.md'),
]


def remove_citations(text):
    """Remove all parenthetical citation references from the text."""

    # ACIM OE citations: (acim oe txt 5.III.18), (acim oe wrk 1.5), (acim oe mnl 21.1)
    text = re.sub(r'\s*\(acim\s+oe\s+\w+\s+[^)]+\)', '', text)

    # Bare (acim oe ...) without the txt/wrk/mnl subtype (just in case)
    text = re.sub(r'\s*\(acim\s+oe\s+[^)]+\)', '', text)

    # JCIM citations: (JCIM, Tx 4.9), (JCIM, T 6 B 10), (JCIM, Chapter 1)
    text = re.sub(r'\s*\(JCIM[^)]*\)', '', text)

    # UB citations: (UB 188:5.2), (UB Paper 44, 44:0.15), (UB 153:2.11), (UB 111:6)
    text = re.sub(r'\s*\(UB\s+[^)]+\)', '', text)

    # ACIM Urtext citations: (ACIM Urtext, T 1B 40ab)
    text = re.sub(r'\s*\(ACIM\s+Urtext[^)]*\)', '', text)

    # Tx: citations used in appendix C: (Tx:1.1), (Tx:1.2)
    text = re.sub(r'\s*\(Tx:[^)]+\)', '', text)

    # Chapter cross-references in appendix A: (Ch 6), (Ch 5, 13), (Ch 6, 9)
    text = re.sub(r'\s*\(Ch\s+[\d,\s]+\)', '', text)

    # JCIM Tx citations: (JCIM Tx:24.42)
    text = re.sub(r'\s*\(JCIM\s+Tx:[^)]+\)', '', text)

    return text


def clean_for_audio(text):
    """
    Apply all transformations for audio-ready EPUB output.
    Keeps bold/italic markers and blockquote > markers (pandoc handles them).
    Keeps # and ## headings for EPUB chapter/section structure.
    """

    # 1. Remove STATUS lines
    text = re.sub(r'\*\*STATUS:\s*\w+\*\*\n*', '', text)

    # 2. Remove all citations
    text = remove_citations(text)

    # 3. Remove horizontal rules (--- on its own line)
    text = re.sub(r'\n---\n', '\n\n', text)
    text = re.sub(r'\n---$', '\n', text, flags=re.MULTILINE)
    text = re.sub(r'^---\n', '\n', text, flags=re.MULTILINE)

    # 4. Replace em dashes with commas (no em dashes for TTS)
    text = re.sub(r'\s*\u2014\s*', ', ', text)
    # En dashes too
    text = re.sub(r'\s*\u2013\s*', ', ', text)

    # 5. Three dots to unicode ellipsis
    text = re.sub(r'\.\.\.', '\u2026', text)

    # 6. Remove markdown links, keep just the text
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)

    # 7. Clean up multiple blank lines (3+ to 2)
    text = re.sub(r'\n{3,}', '\n\n', text)

    # 8. Fix double spaces
    text = re.sub(r'  +', ' ', text)

    # 9. Fix comma at start of line (artifact from em-dash replacement)
    text = re.sub(r'^\s*,\s*', '', text, flags=re.MULTILINE)

    # 10. Fix ", ," artifacts
    text = re.sub(r',\s*,', ',', text)

    # 11. Remove "**ACIM OE:**" labels (keep them as readable labels)
    # Replace "**ACIM OE:**" with "A Course in Miracles:" for readability
    text = re.sub(r'\*\*ACIM OE[^:]*:\*\*', '**A Course in Miracles:**', text)

    # 12. Clean up any "(with ... substituted ...)" notes after ACIM label
    # These are already captured by the label replacement above

    return text.strip()


def process_file(folder, filename):
    """Read a file and apply audio transformations."""
    if folder == 'chapters':
        filepath = os.path.join(CHAPTERS_DIR, filename)
    else:
        filepath = os.path.join(APPENDICES_DIR, filename)

    if not os.path.exists(filepath):
        print(f"  WARNING: {filepath} not found!")
        return None, filepath

    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()

    cleaned = clean_for_audio(text)
    return cleaned, filepath


def count_words(text):
    """Count words in text."""
    return len(text.split())


def main():
    all_content = []
    total_words = 0
    missing = []

    print("Building audio-ready EPUB: Across the Revelation Bridge")
    print("=" * 60)

    for folder, filename in CHAPTER_FILES:
        content, filepath = process_file(folder, filename)
        if content is None:
            missing.append(filepath)
            continue

        words = count_words(content)
        total_words += words
        all_content.append(content)
        print(f"  {filename}: {words:,} words")

    if missing:
        print(f"\nWARNING: {len(missing)} file(s) not found:")
        for m in missing:
            print(f"  {m}")

    # Combine into single markdown (page break between chapters for EPUB)
    combined = '\n\n\n'.join(all_content)

    # Write combined markdown for review
    md_path = os.path.join(OUTPUT_DIR, 'across-the-revelation-bridge-audio.md')
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(combined)
    md_size = os.path.getsize(md_path)
    print(f"\nCombined markdown: {md_path}")
    print(f"Total words: {total_words:,}")
    print(f"Markdown file size: {md_size / 1024:.1f} KB")

    # Generate EPUB with pandoc
    epub_path = os.path.join(OUTPUT_DIR, 'across-the-revelation-bridge-audio.epub')
    cmd = [
        'pandoc',
        md_path,
        '-o', epub_path,
        '--metadata', 'title=Across the Revelation Bridge',
        '--metadata', 'author=Joseph',
        '--toc',
        '--toc-depth=2',
        '--epub-chapter-level=1',
    ]

    print(f"\nGenerating EPUB with pandoc...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        epub_size = os.path.getsize(epub_path)
        print(f"EPUB generated: {epub_path}")
        print(f"EPUB file size: {epub_size / 1024:.1f} KB")
    else:
        print(f"ERROR generating EPUB:")
        print(result.stderr)
        sys.exit(1)

    # Verify no em dashes remain
    em_dash_count = combined.count('\u2014')
    en_dash_count = combined.count('\u2013')
    if em_dash_count > 0 or en_dash_count > 0:
        print(f"\nWARNING: {em_dash_count} em dashes and {en_dash_count} en dashes still present!")
    else:
        print("\nVerified: No em dashes or en dashes in output.")

    # Verify no citations remain
    acim_remaining = len(re.findall(r'\(acim\s+oe', combined, re.IGNORECASE))
    ub_remaining = len(re.findall(r'\(UB\s+\d', combined))
    if acim_remaining > 0 or ub_remaining > 0:
        print(f"WARNING: {acim_remaining} ACIM citations and {ub_remaining} UB citations still present!")
    else:
        print("Verified: No ACIM OE or UB citations in output.")

    print(f"\nDone! Output files:")
    print(f"  {md_path} ({md_size / 1024:.1f} KB)")
    print(f"  {epub_path} ({os.path.getsize(epub_path) / 1024:.1f} KB)")


if __name__ == '__main__':
    main()
