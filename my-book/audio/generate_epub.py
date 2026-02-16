#!/usr/bin/env python3
"""Generate audio-ready EPUB from book chapters and appendices for ElevenLabs TTS."""

import re
import glob
import os
from ebooklib import epub

BASE_DIR = os.path.join(os.path.dirname(__file__), '..')
CHAPTERS_DIR = os.path.join(BASE_DIR, 'chapters')
APPENDICES_DIR = os.path.join(BASE_DIR, 'appendices')
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), 'Audiobook.epub')


def convert_table_to_prose(lines, start_idx):
    """Convert a markdown table starting at start_idx to narrated prose.
    Returns (prose_lines, end_idx)."""
    # Collect all table lines
    table_lines = []
    idx = start_idx
    while idx < len(lines) and (lines[idx].strip().startswith('|') or lines[idx].strip() == ''):
        stripped = lines[idx].strip()
        if stripped.startswith('|'):
            table_lines.append(stripped)
        elif stripped == '' and table_lines:
            break
        idx += 1

    if not table_lines:
        return [], start_idx

    # Parse header
    header_cells = [c.strip() for c in table_lines[0].split('|') if c.strip()]

    # Skip separator row (|---|---|)
    data_start = 1
    if len(table_lines) > 1 and re.match(r'^[\|\s\-:]+$', table_lines[1]):
        data_start = 2

    prose = []
    for row_line in table_lines[data_start:]:
        cells = [c.strip() for c in row_line.split('|') if c.strip()]
        if len(cells) >= 2:
            if len(header_cells) >= 2:
                prose.append(f'{header_cells[0]}: {cells[0]}. {header_cells[1]}: {cells[1]}.')
            else:
                prose.append('. '.join(cells) + '.')

    return prose, idx


def process_text(text):
    """Apply all audio formatting rules to chapter/appendix text."""
    lines = text.split('\n')
    processed_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Remove STATUS lines
        if re.match(r'\s*\*?\*?STATUS:?\*?\*?', line, re.IGNORECASE):
            i += 1
            continue

        # Remove horizontal rules
        if re.match(r'^---+\s*$', line.strip()):
            i += 1
            continue

        # Detect and convert tables
        if line.strip().startswith('|') and i + 1 < len(lines) and lines[i + 1].strip().startswith('|'):
            prose, end_idx = convert_table_to_prose(lines, i)
            processed_lines.append('')
            processed_lines.extend(prose)
            processed_lines.append('')
            i = end_idx
            continue

        # Remove ### sub-section headings (replace with blank line for pause)
        if re.match(r'^###\s+', line):
            # Extract the heading text for narration
            heading_text = re.sub(r'^###\s+', '', line).strip()
            # Remove numbering like "1. " or "25. "
            heading_text = re.sub(r'^\d+\.\s+', '', heading_text)
            # Remove bold/italic
            heading_text = re.sub(r'\*\*([^*]+)\*\*', r'\1', heading_text)
            heading_text = re.sub(r'\*([^*]+)\*', r'\1', heading_text)
            processed_lines.append('')
            processed_lines.append(heading_text)
            processed_lines.append('')
            i += 1
            continue

        # Remove ## section headings (replace with blank line for pause)
        if re.match(r'^##\s+', line):
            processed_lines.append('')
            i += 1
            continue

        # Keep # Chapter/Appendix headings as spoken text (remove the #)
        chapter_match = re.match(r'^#\s+(.+)$', line)
        if chapter_match:
            heading = chapter_match.group(1)
            heading = heading.replace('\u2014', ', ').replace('\u2013', ', ')
            heading = re.sub(r'\s*—\s*', ', ', heading)
            heading = re.sub(r'\s*–\s*', ', ', heading)
            processed_lines.append(heading)
            i += 1
            continue

        # Process blockquotes: remove > marker
        if line.startswith('> '):
            line = line[2:]
        elif line == '>':
            line = ''

        # Remove citations at end of quotes (comprehensive patterns)
        # UB patterns: (UB Paper X, X:X.X), (UB X:X.X), (UB Paper X)
        line = re.sub(r'\s*\(UB Paper \d+,?\s*\d+:\d+\.\d+\)\s*$', '', line)
        line = re.sub(r'\s*\(UB Paper \d+\)\s*$', '', line)
        line = re.sub(r'\s*\(UB \d+:\d+\.\d+\)\s*$', '', line)
        # JCIM/CIM patterns
        line = re.sub(r'\s*\(JCIM[^)]*\)\s*$', '', line)
        line = re.sub(r'\s*\(CIM-OE[^)]*\)\s*$', '', line)
        line = re.sub(r'\s*\(CIM[^)]*\)\s*$', '', line)
        line = re.sub(r'\s*\(Course[^)]*\)\s*$', '', line)
        line = re.sub(r'\s*\(Workbook[^)]*\)\s*$', '', line)
        line = re.sub(r'\s*\(Text[^)]*\)\s*$', '', line)
        line = re.sub(r'\s*\(Manual[^)]*\)\s*$', '', line)
        # Short citation patterns: (Tx:1.1), (W1 45.8), etc.
        line = re.sub(r'\s*\(Tx[^)]*\)\s*$', '', line)
        line = re.sub(r'\s*\(W\d[^)]*\)\s*$', '', line)

        # Inline citation references like (Ch 5, 13) or (Ch 6, 8)
        line = re.sub(r'\s*\(Ch \d+(?:,\s*\d+)*\)\s*$', '', line)

        # Remove bold markers
        line = re.sub(r'\*\*([^*]+)\*\*', r'\1', line)

        # Remove italic markers
        line = re.sub(r'\*([^*]+)\*', r'\1', line)

        # Replace em dashes (unicode and ASCII variants)
        line = re.sub(r'\s*\u2014\s*', ', ', line)  # unicode em dash
        line = re.sub(r'\s*—\s*', ', ', line)  # HTML em dash
        line = re.sub(r'\s*\u2013\s*', ', ', line)  # unicode en dash
        line = re.sub(r'\s*–\s*', ', ', line)  # HTML en dash

        # Replace ... with ellipsis character
        line = re.sub(r'\.\.\.', '\u2026', line)

        # Parenthetical chapter references
        line = re.sub(r'\(Ch (\d+)\)', r'as discussed in Chapter \1', line)
        line = re.sub(r'\(Chapter (\d+)\)', r'as discussed in Chapter \1', line)

        # Remove markdown link syntax [text](url) -> text
        line = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', line)

        # Remove bare URLs
        line = re.sub(r'https?://\S+', '', line)

        # Clean up any double spaces
        line = re.sub(r'  +', ' ', line)

        # Clean up trailing/leading whitespace
        line = line.strip()

        processed_lines.append(line)
        i += 1

    # Join and clean up excessive blank lines
    text = '\n'.join(processed_lines)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = text.strip()

    return text


def text_to_html(text):
    """Convert processed plain text to simple HTML for EPUB."""
    paragraphs = text.split('\n\n')
    html_parts = []

    for para in paragraphs:
        if not para.strip():
            continue

        # Check if this is a chapter title (first line, no markup)
        lines = para.strip().split('\n')

        # Join multi-line paragraphs
        content = ' '.join(line.strip() for line in lines if line.strip())

        if (content.startswith('Chapter ') or content.startswith('Appendix ')) and ':' in content and len(content) < 120:
            html_parts.append(f'<h1>{content}</h1>')
        elif content.startswith('Part ') and ':' in content and len(content) < 80:
            html_parts.append(f'<h2>{content}</h2>')
        elif content.startswith('Principle ') and len(content) < 20:
            html_parts.append(f'<h2>{content}</h2>')
        else:
            # Break very long paragraphs (>500 words)
            words = content.split()
            if len(words) > 500:
                chunks = []
                current = []
                for word in words:
                    current.append(word)
                    if len(current) >= 400 and word.endswith('.'):
                        chunks.append(' '.join(current))
                        current = []
                if current:
                    chunks.append(' '.join(current))
                for chunk in chunks:
                    html_parts.append(f'<p>{chunk}</p>')
            else:
                html_parts.append(f'<p>{content}</p>')

    return '\n'.join(html_parts)


def get_chapter_files():
    """Get sorted list of chapter files."""
    pattern = os.path.join(CHAPTERS_DIR, 'chapter-*.md')
    files = glob.glob(pattern)

    def sort_key(f):
        match = re.search(r'chapter-(\d+)', os.path.basename(f))
        return int(match.group(1)) if match else 0

    return sorted(files, key=sort_key)


def get_appendix_files():
    """Get sorted list of appendix files."""
    pattern = os.path.join(APPENDICES_DIR, 'appendix-*.md')
    files = glob.glob(pattern)

    def sort_key(f):
        basename = os.path.basename(f).lower()
        # Extract letter: appendix-a, appendix-b, appendix-c
        match = re.search(r'appendix-([a-z])', basename)
        return match.group(1) if match else 'z'

    return sorted(files, key=sort_key)


def main():
    # Create EPUB book
    book = epub.EpubBook()
    book.set_identifier('ub-cim-study-guide-audio')
    book.set_title('The Urantia Book and A Course in Miracles: A Study Guide')
    book.set_language('en')
    book.add_author('Joseph')

    # Minimal CSS
    style = '''
    body { font-family: serif; line-height: 1.6; margin: 1em; }
    h1 { page-break-before: always; margin-top: 2em; }
    h2 { margin-top: 1.5em; }
    p { margin-bottom: 0.8em; text-indent: 0; }
    '''
    css = epub.EpubItem(
        uid='style',
        file_name='style/default.css',
        media_type='text/css',
        content=style.encode('utf-8')
    )
    book.add_item(css)

    spine = ['nav']
    toc = []
    total_words = 0

    # Process chapters
    chapter_files = get_chapter_files()
    print(f"Found {len(chapter_files)} chapters")

    for filepath in chapter_files:
        basename = os.path.basename(filepath)
        with open(filepath, 'r', encoding='utf-8') as f:
            raw_text = f.read()

        processed = process_text(raw_text)
        html_content = text_to_html(processed)

        title_match = re.search(r'(?:Chapter|Appendix) \d+[^<]*', html_content)
        title = title_match.group(0) if title_match else basename
        title = title.replace('\u2014', ', ').replace('\u2013', ', ')

        word_count = len(processed.split())
        total_words += word_count

        chapter_id = re.sub(r'[^a-z0-9]', '-', basename.lower().replace('.md', ''))
        epub_chapter = epub.EpubHtml(
            title=title,
            file_name=f'{chapter_id}.xhtml',
            lang='en'
        )
        epub_chapter.content = f'<html><body>{html_content}</body></html>'
        epub_chapter.add_item(css)

        book.add_item(epub_chapter)
        spine.append(epub_chapter)
        toc.append(epub.Link(f'{chapter_id}.xhtml', title, chapter_id))

        print(f"  {basename}: {word_count:,} words")

    # Process appendices
    appendix_files = get_appendix_files()
    print(f"\nFound {len(appendix_files)} appendices")

    for filepath in appendix_files:
        basename = os.path.basename(filepath)
        with open(filepath, 'r', encoding='utf-8') as f:
            raw_text = f.read()

        processed = process_text(raw_text)
        html_content = text_to_html(processed)

        title_match = re.search(r'Appendix [A-Z][^<]*', html_content)
        title = title_match.group(0) if title_match else basename
        title = title.replace('\u2014', ', ').replace('\u2013', ', ')

        word_count = len(processed.split())
        total_words += word_count

        appendix_id = re.sub(r'[^a-z0-9]', '-', basename.lower().replace('.md', ''))
        epub_appendix = epub.EpubHtml(
            title=title,
            file_name=f'{appendix_id}.xhtml',
            lang='en'
        )
        epub_appendix.content = f'<html><body>{html_content}</body></html>'
        epub_appendix.add_item(css)

        book.add_item(epub_appendix)
        spine.append(epub_appendix)
        toc.append(epub.Link(f'{appendix_id}.xhtml', title, appendix_id))

        print(f"  {basename}: {word_count:,} words")

    # Set TOC and spine
    book.toc = toc
    book.spine = spine

    # Add navigation files
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # Write EPUB
    epub.write_epub(OUTPUT_PATH, book, {})

    print(f"\n{'='*50}")
    print(f"Total words: {total_words:,}")
    print(f"Chapters: {len(chapter_files)}")
    print(f"Appendices: {len(appendix_files)}")
    print(f"EPUB written to: {OUTPUT_PATH}")


if __name__ == '__main__':
    main()
