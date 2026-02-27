#!/usr/bin/env python3
"""
Transform book chapters and appendices into audio-ready format
for ElevenLabs TTS conversion, then generate an EPUB.
"""

import re
import os
import subprocess
import sys

CHAPTERS_DIR = os.path.join(os.path.dirname(__file__), '..', 'chapters')
APPENDICES_DIR = os.path.join(os.path.dirname(__file__), '..', 'appendices')
OUTPUT_DIR = os.path.dirname(__file__)

# Order of files for the EPUB
CHAPTER_ORDER = [
    'introduction.md',
    'chapter-01-two-revelations-one-path.md',
    'chapter-02-urantia-book-overview.md',
    'chapter-03-course-in-miracles-true-history.md',
    'chapter-04-epochal-vs-personal-revelation.md',
    'chapter-05-terminology-bridge.md',
    'chapter-06-central-thesis.md',
    'chapter-07-sonship-supreme.md',
    'chapter-08-what-is-real.md',
    'chapter-09-miracles-and-time.md',
    'chapter-10-forgiveness-mercy-vs-love.md',
    'chapter-11-perception-vs-knowledge.md',
    'chapter-12-the-architecture-of-mind.md',
    'chapter-13-fear-vs-love.md',
    'chapter-14-lucifer-rebellion-why-we-suffer.md',
    'chapter-15-the-atonement-and-the-crucifixion.md',
    'chapter-16-from-here-to-paradise.md',
    'chapter-17-my-lesson-was-like-yours.md',
]

APPENDIX_ORDER = [
    'appendix-a-terminology-mapping-v2.md',
    'appendix-b-parallels-condensed.md',
    'appendix-c-miracle-principles.md',
]


def remove_citations(text):
    """Remove all citation references from the text."""
    # ACIM OE citations: (acim oe txt 5.III.18), (acim oe wrk 1.5), (acim oe mnl 21.1)
    text = re.sub(r'\s*\(acim\s+oe\s+\w+\s+[^)]+\)', '', text)

    # JCIM citations: (JCIM, Tx 4.9), (JCIM, T 6 B 10), (JCIM, Chapter 1), (JCIM, Notes), (JCIM, U 2 A 6)
    text = re.sub(r'\s*\(JCIM[^)]*\)', '', text)

    # UB citations: (UB 188:5.2), (UB Paper 44, 44:0.15), (UB 153:2.11)
    text = re.sub(r'\s*\(UB\s+[^)]+\)', '', text)

    # ACIM Urtext citations: (ACIM Urtext, T 1B 40ab)
    text = re.sub(r'\s*\(ACIM\s+Urtext[^)]*\)', '', text)

    # Tx: citations used in appendix C: (Tx:1.1), (Tx:1.2)
    text = re.sub(r'\s*\(Tx:[^)]+\)', '', text)

    # Chapter cross-references: (Ch 6), (Ch 5, 13), (Ch 6, 9)
    text = re.sub(r'\s*\(Ch\s+[\d,\s]+\)', '', text)

    # Inline citation labels like "**ACIM OE (acim oe txt 2.III.56):**"
    text = re.sub(r'\*\*ACIM\s+OE\s*\([^)]+\):\*\*', 'A Course in Miracles:', text)

    # Inline citation labels like "**Urantia Book (118:9.4):**"
    text = re.sub(r'\*\*Urantia Book\s*\([^)]+\):\*\*', 'The Urantia Book:', text)

    # JCIM Tx citations in appendix C: (JCIM Tx:24.42)
    text = re.sub(r'\s*\(JCIM\s+Tx:[^)]+\)', '', text)

    return text


def transform_for_audio(text):
    """Apply all ElevenLabs formatting transformations."""

    # 1. Remove STATUS lines
    text = re.sub(r'\*\*STATUS:\s*\w+\*\*\n*', '', text)

    # 2. Remove citations (before removing bold/italic markers)
    text = remove_citations(text)

    # 3. Convert tables to narrated prose
    text = convert_tables(text)

    # 4. Handle section headings - KEEP them (user requested)
    # Convert ## Section X: Title to just the title as spoken text
    # Keep ## headings but remove the markdown ## marker
    # Actually, for EPUB we keep # and ## as they become H1/H2 in EPUB
    # The H1/H2 tags in EPUB are what ElevenLabs uses for chapter detection
    # So we keep them as markdown headings

    # 5. Remove horizontal rules
    text = re.sub(r'\n---\n', '\n\n', text)
    text = re.sub(r'\n---$', '\n', text, flags=re.MULTILINE)
    text = re.sub(r'^---\n', '\n', text, flags=re.MULTILINE)

    # 6. Remove bold markers
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)

    # 7. Remove italic markers
    text = re.sub(r'\*([^*]+)\*', r'\1', text)

    # 8. Handle blockquotes - remove > marker
    text = re.sub(r'^>\s?', '', text, flags=re.MULTILINE)

    # 9. Em dashes - replace with comma or period
    # Em dash between clauses with space on both sides
    text = re.sub(r'\s*—\s*', ', ', text)
    # En dash
    text = re.sub(r'\s*–\s*', ', ', text)

    # 10. Three dots to unicode ellipsis
    text = re.sub(r'\.\.\.', '…', text)

    # 11. Remove markdown links - keep just the text
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)

    # 12. Clean up multiple blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)

    # 13. Clean up any remaining ### headings (sub-section headings in appendices)
    # Keep them as spoken headings

    # 14. Fix double spaces that may have been introduced
    text = re.sub(r'  +', ' ', text)

    # 15. Fix comma-space at start of sentences (from em-dash replacement)
    text = re.sub(r'^\s*,\s*', '', text, flags=re.MULTILINE)

    # 16. Fix ", ," artifacts
    text = re.sub(r',\s*,', ',', text)

    # 17. Remove "Part Two: Themes" line at end of ch5
    text = re.sub(r'^## Part Two: Themes\n.*$', '', text, flags=re.MULTILINE)

    return text.strip()


def convert_tables(text):
    """Convert markdown tables to narrated prose."""
    lines = text.split('\n')
    result = []
    i = 0
    while i < len(lines):
        line = lines[i]
        # Detect table start (line with |)
        if '|' in line and i + 1 < len(lines) and '---' in lines[i + 1]:
            # Parse header
            headers = [h.strip() for h in line.split('|') if h.strip()]
            i += 2  # Skip header and separator
            # Parse rows
            while i < len(lines) and '|' in lines[i]:
                cells = [c.strip() for c in lines[i].split('|') if c.strip()]
                if len(cells) >= 2 and len(headers) >= 2:
                    # Build narrated version
                    narrated = f"{cells[0]}. "
                    if len(headers) >= 2 and len(cells) >= 2:
                        narrated += f"The corresponding Urantia Book term is {cells[1]}."
                    result.append(narrated)
                    result.append('')
                i += 1
        else:
            result.append(line)
            i += 1
    return '\n'.join(result)


def process_file(filepath):
    """Read a file and apply audio transformations."""
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    return transform_for_audio(text)


def count_words(text):
    """Count words in text."""
    return len(text.split())


def main():
    # Process all chapters
    all_content = []
    total_words = 0

    print("Processing chapters...")
    for filename in CHAPTER_ORDER:
        filepath = os.path.join(CHAPTERS_DIR, filename)
        if os.path.exists(filepath):
            content = process_file(filepath)
            words = count_words(content)
            total_words += words
            all_content.append(content)
            print(f"  {filename}: {words:,} words")
        else:
            print(f"  WARNING: {filename} not found!")

    print("\nProcessing appendices...")
    for filename in APPENDIX_ORDER:
        filepath = os.path.join(APPENDICES_DIR, filename)
        if os.path.exists(filepath):
            content = process_file(filepath)
            words = count_words(content)
            total_words += words
            all_content.append(content)
            print(f"  {filename}: {words:,} words")
        else:
            print(f"  WARNING: {filename} not found!")

    # Combine into single markdown
    combined = '\n\n---\n\n'.join(all_content)

    # Write combined markdown
    md_path = os.path.join(OUTPUT_DIR, 'UB-CIM-Study-Guide-audio.md')
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(combined)
    print(f"\nCombined markdown: {md_path}")
    print(f"Total words: {total_words:,}")

    # Generate EPUB with pandoc
    epub_path = os.path.join(OUTPUT_DIR, 'UB-CIM-Study-Guide-audio.epub')
    cmd = [
        'pandoc',
        md_path,
        '-o', epub_path,
        '--metadata', 'title=The Urantia Book and A Course in Miracles: A Study Guide',
        '--metadata', 'author=Joseph',
        '--toc',
        '--toc-depth=2',
        '--epub-chapter-level=1',
    ]

    print(f"\nGenerating EPUB...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"EPUB generated: {epub_path}")
        # Get file size
        size = os.path.getsize(epub_path)
        print(f"File size: {size / 1024:.0f} KB")
    else:
        print(f"ERROR generating EPUB:")
        print(result.stderr)
        sys.exit(1)

    # Clean up intermediate markdown
    # Keep it for reference
    print(f"\nDone! Files in {OUTPUT_DIR}:")
    for f in sorted(os.listdir(OUTPUT_DIR)):
        if f.startswith('UB-CIM'):
            fpath = os.path.join(OUTPUT_DIR, f)
            fsize = os.path.getsize(fpath)
            print(f"  {f} ({fsize / 1024:.0f} KB)")


if __name__ == '__main__':
    main()
