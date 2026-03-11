#!/usr/bin/env python3
"""
Build audio-ready EPUB of Fusion: Two Revelations, One Path
Applies ElevenLabs formatting rules:
- Strips citations from blockquotes
- Removes markdown formatting (bold, italic, horizontal rules)
- Converts tables to prose
- Replaces em dashes
- Removes STATUS lines
- Keeps chapter and section headings
- Removes blockquote markers
"""

import re
import os
import subprocess
from datetime import date

# Chapter files in order
CHAPTERS = [
    "chapters/introduction.md",
    "chapters/chapter-01-the-two-revelations.md",
    "chapters/chapter-02-terminology-bridge.md",
    "chapters/chapter-03-central-thesis-fusion-between-father-and-son.md",
    "chapters/chapter-04-sonship-supreme.md",
    "chapters/chapter-05-miracles-and-time.md",
    "chapters/chapter-06-forgiveness-mercy-vs-love.md",
    "chapters/chapter-07-what-is-real.md",
    "chapters/chapter-08-what-survives.md",
    "chapters/chapter-09-the-architecture-of-mind.md",
    "chapters/chapter-10-lucifer-rebellion-why-we-suffer.md",
    "chapters/chapter-11-the-atonement-and-the-crucifixion.md",
    "chapters/chapter-12-from-here-to-paradise.md",
    "chapters/chapter-13-the-jesus-both-books-reveal.md",
]

APPENDICES = [
    "appendices/appendix-a-terminology-mapping-v2.md",
    "appendices/appendix-b-parallels-condensed.md",
    "appendices/appendix-c-miracle-principles.md",
]

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def process_text(text):
    """Apply all audio formatting rules to text."""

    # Remove STATUS lines
    text = re.sub(r'\*\*STATUS:.*?\*\*\n*', '', text)

    # Remove horizontal rules
    text = re.sub(r'\n---\n', '\n\n', text)
    text = re.sub(r'^---$', '', text, flags=re.MULTILINE)

    # Strip citations from blockquotes and inline text
    # Patterns: (acim oe txt 1.I.52), (UB 107:1.2), (acim oe wrk 160.8), (acim oe mnl 21.1)
    # Also handles multiple citations: (UB 194:2.2, 194:2.5)
    text = re.sub(r'\s*\(acim oe [a-z]+ [\w.:,\s/-]+\)', '', text)
    text = re.sub(r'\s*\(UB [\d:.,\s]+\)', '', text)
    # Catch any remaining parenthetical citations
    text = re.sub(r'\s*\(acim oe [^)]+\)', '', text)
    text = re.sub(r'\s*\(UB [^)]+\)', '', text)

    # Remove blockquote markers but keep the text
    text = re.sub(r'^>\s?', '', text, flags=re.MULTILINE)

    # Remove bold markers
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)

    # Remove italic markers (but be careful with emphasis in quotes)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)

    # Replace em dashes with commas or periods
    # Em dash between words in a sentence (parenthetical) -> comma
    text = text.replace('\u2014', ', ')
    # En dash
    text = text.replace('\u2013', ', ')

    # Replace three dots with unicode ellipsis
    text = re.sub(r'\.\.\.', '\u2026', text)

    # Remove markdown link syntax [text](url) -> text
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)

    # Convert section headings to clean text (keep them as requested)
    # ## Section 1: Opening -> Section 1: Opening
    text = re.sub(r'^## (.*)', r'\1', text, flags=re.MULTILINE)

    # Convert chapter headings: # Chapter 1: Title -> Chapter 1: Title
    text = re.sub(r'^# (.*)', r'\1', text, flags=re.MULTILINE)

    # Clean up multiple blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Strip leading/trailing whitespace
    text = text.strip()

    return text


def process_table(text):
    """Convert markdown tables to narrated prose."""
    lines = text.split('\n')
    result = []
    in_table = False
    table_rows = []
    header = []

    for line in lines:
        stripped = line.strip()
        if '|' in stripped and not in_table:
            # Start of table
            in_table = True
            # Parse header
            header = [c.strip() for c in stripped.split('|') if c.strip()]
            table_rows = []
            continue
        elif in_table and re.match(r'^[\s|:-]+$', stripped):
            # Separator row, skip
            continue
        elif in_table and '|' in stripped:
            # Data row
            cells = [c.strip() for c in stripped.split('|') if c.strip()]
            table_rows.append(cells)
            continue
        elif in_table:
            # End of table, convert to prose
            in_table = False
            for row in table_rows:
                if len(row) >= 2:
                    result.append(f"{row[0]}. {row[1]}")
                elif len(row) == 1:
                    result.append(row[0])
            result.append('')
            result.append(line)
            continue

        result.append(line)

    # Handle table at end of file
    if in_table and table_rows:
        for row in table_rows:
            if len(row) >= 2:
                result.append(f"{row[0]}. {row[1]}")
            elif len(row) == 1:
                result.append(row[0])

    return '\n'.join(result)


def process_cross_references(text):
    """Convert parenthetical chapter references to narrated form."""
    # (Ch 6) -> as discussed in Chapter 6
    text = re.sub(r'\(Ch (\d+)\)', r'as discussed in Chapter \1', text)
    # (Ch 5, 13) -> as discussed in Chapters 5 and 13
    text = re.sub(r'\(Ch (\d+), (\d+)\)', r'as discussed in Chapters \1 and \2', text)
    # (Ch 5, 6, 9) -> as discussed in Chapters 5, 6, and 9
    text = re.sub(r'\(Ch (\d+), (\d+), (\d+)\)', r'as discussed in Chapters \1, \2, and \3', text)
    return text


def build_audio_markdown():
    """Build complete audio-ready markdown."""
    sections = []

    # Title page
    sections.append("# Fusion: Two Revelations, One Path\n")
    sections.append("A Bridge Between the Urantia Book and A Course in Miracles\n")
    sections.append("By Joseph\n\n")

    # Process chapters
    for filepath in CHAPTERS:
        full_path = os.path.join(BASE, filepath)
        if not os.path.exists(full_path):
            print(f"WARNING: {full_path} not found, skipping")
            continue

        with open(full_path, 'r') as f:
            content = f.read()

        # Process tables first (before stripping markdown)
        content = process_table(content)
        # Then process text
        content = process_text(content)
        # Then cross-references
        content = process_cross_references(content)

        # Re-add markdown heading for EPUB chapter detection
        # Find the first line (should be the chapter title)
        lines = content.split('\n')
        if lines and not lines[0].startswith('#'):
            lines[0] = '# ' + lines[0]
        content = '\n'.join(lines)

        sections.append(content)
        sections.append('\n\n')

    # Process appendices
    for filepath in APPENDICES:
        full_path = os.path.join(BASE, filepath)
        if not os.path.exists(full_path):
            print(f"WARNING: {full_path} not found, skipping")
            continue

        with open(full_path, 'r') as f:
            content = f.read()

        content = process_table(content)
        content = process_text(content)
        content = process_cross_references(content)

        lines = content.split('\n')
        if lines and not lines[0].startswith('#'):
            lines[0] = '# ' + lines[0]
        content = '\n'.join(lines)

        sections.append(content)
        sections.append('\n\n')

    return '\n'.join(sections)


def main():
    audio_dir = os.path.join(BASE, 'audio')
    os.makedirs(audio_dir, exist_ok=True)

    # Build markdown
    md_content = build_audio_markdown()

    # Write markdown
    today = date.today().isoformat()
    md_path = os.path.join(audio_dir, f'fusion-audio-{today}.md')
    with open(md_path, 'w') as f:
        f.write(md_content)

    # Word count
    words = len(md_content.split())
    print(f"Audio markdown: {md_path}")
    print(f"Word count: {words:,}")

    # Build EPUB
    epub_path = os.path.join(audio_dir, f'fusion-audio-{today}.epub')
    cmd = [
        'pandoc',
        md_path,
        '-o', epub_path,
        '--metadata', 'title=Fusion: Two Revelations, One Path',
        '--metadata', 'author=Joseph',
        '--toc',
        '--toc-depth=1',
        '--split-level=1',
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            size = os.path.getsize(epub_path)
            print(f"Audio EPUB: {epub_path} ({size:,} bytes)")
        else:
            print(f"Pandoc error: {result.stderr}")
    except FileNotFoundError:
        print("pandoc not found. Markdown file created; run pandoc manually to create EPUB.")

    print("Done!")


if __name__ == '__main__':
    main()
