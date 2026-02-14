#!/usr/bin/env python3
"""Generate audio-ready EPUB from book chapters and appendices."""

import re
import os
from ebooklib import epub

CHAPTERS_DIR = "/Users/brianleblanc/code/ub-cim/my-book/chapters"
APPENDICES_DIR = "/Users/brianleblanc/code/ub-cim/my-book/appendices"
OUTPUT_PATH = "/Users/brianleblanc/code/ub-cim/my-book/audio/UB-CIM-Study-Guide-Audiobook.epub"

# Ordered list of source files
CHAPTER_FILES = [
    "chapter-01-introduction.md",
    "chapter-02-urantia-book-overview.md",
    "chapter-03-course-in-miracles-true-history.md",
    "chapter-04-epochal-vs-personal-revelation.md",
    "chapter-05-terminology-bridge.md",
    "chapter-06-central-thesis.md",
    "chapter-07-sonship-supreme.md",
    "chapter-08-what-is-real-DRAFT.md",
    "chapter-09-miracles-and-time.md",
    "chapter-10-adjuster-fusion-transfer-bridge.md",
    "chapter-11-identify-with-spirit-reality.md",
    "chapter-12-forgiveness-mercy-vs-love.md",
    "chapter-13-perception-vs-knowledge.md",
    "chapter-14-fear-vs-love.md",
    "chapter-15-lucifer-rebellion-why-we-suffer.md",
    "chapter-16-what-happens-after-ascension-path.md",
    "chapter-17-the-honest-question.md",
]

APPENDIX_FILES = [
    "appendix-a-terminology-mapping-v2.md",
    "appendix-b-parallels-condensed.md",
    "appendix-c-miracle-principles.md",
]


def apply_audio_rules(text):
    """Apply all ElevenLabs audio formatting rules to markdown text."""

    # Remove STATUS lines
    text = re.sub(r'\*\*STATUS:.*?\*\*\s*\n?', '', text)

    # Remove horizontal rules
    text = re.sub(r'^---+\s*$', '', text, flags=re.MULTILINE)

    # Convert ## Section headings to blank lines (pause markers)
    # But keep # Chapter headings as spoken text
    text = re.sub(r'^## .+$', '\n', text, flags=re.MULTILINE)
    # Remove ### sub-headings too
    text = re.sub(r'^### .+$', '\n', text, flags=re.MULTILINE)

    # Keep # Chapter headings - remove the # marker
    text = re.sub(r'^# (.+)$', r'\1', text, flags=re.MULTILINE)

    # Remove bold markers
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)

    # Remove italic markers
    text = re.sub(r'\*(.+?)\*', r'\1', text)

    # Remove blockquote markers
    text = re.sub(r'^>\s?', '', text, flags=re.MULTILINE)

    # Convert markdown tables to narrated prose
    text = convert_tables(text)

    # Replace em dashes
    # Pattern: space em-dash space (parenthetical)
    text = text.replace(' — ', ', ')
    text = text.replace(' —', ',')
    text = text.replace('— ', ', ')
    text = text.replace('—', ', ')

    # Replace en dashes
    text = text.replace(' – ', ', ')
    text = text.replace('–', ', ')

    # Replace three dots with unicode ellipsis
    text = text.replace('...', '\u2026')

    # Remove markdown link syntax [text](url) -> just text
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)

    # Spell out cross-references
    text = re.sub(r'\(Ch\.?\s*(\d+)\)', lambda m: f'(as discussed in Chapter {m.group(1)})', text)
    text = re.sub(r'\(Ch\s+(\d+),\s*(\d+)\)', lambda m: f'(as discussed in Chapters {m.group(1)} and {m.group(2)})', text)
    # Handle references like (Ch 5, 13) in appendix
    text = re.sub(r'\(Ch\s+(\d+(?:,\s*\d+)*)\)', lambda m: '(as discussed in Chapters ' + m.group(1) + ')', text)

    # Remove citations from quotes
    # Patterns: (JCIM, ...), (UB Paper ...), (CIM-OE ...), (UB, ...)
    text = re.sub(r'\s*\(JCIM[^)]*\)', '', text)
    text = re.sub(r'\s*\(UB Paper[^)]*\)', '', text)
    text = re.sub(r'\s*\(UB,\s*[^)]*\)', '', text)
    text = re.sub(r'\s*\(CIM-OE[^)]*\)', '', text)

    # Remove bare URLs
    text = re.sub(r'https?://\S+', '', text)

    # Remove markdown checkbox items
    text = re.sub(r'^- \[[ x]\] ', '- ', text, flags=re.MULTILINE)

    # Clean up multiple blank lines
    text = re.sub(r'\n{4,}', '\n\n\n', text)

    # Strip leading/trailing whitespace
    text = text.strip()

    return text


def convert_tables(text):
    """Convert markdown tables to narrated prose."""
    lines = text.split('\n')
    result = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        # Detect table start (line with | characters)
        if '|' in line and i + 1 < len(lines) and re.match(r'\s*\|[-| ]+\|', lines[i + 1].strip()):
            # This is a table header row, next is separator
            headers = [h.strip() for h in line.split('|') if h.strip()]
            i += 2  # Skip header and separator

            # Process data rows
            while i < len(lines) and '|' in lines[i]:
                row_line = lines[i].strip()
                if row_line.startswith('|') and row_line.endswith('|'):
                    cells = [c.strip() for c in row_line.split('|') if c.strip()]
                else:
                    cells = [c.strip() for c in row_line.split('|') if c.strip()]

                if cells and any(c for c in cells):
                    # Create narrated version
                    if len(headers) == 2 and len(cells) >= 2:
                        if cells[0] and cells[1]:
                            result.append(f"{cells[0]}. {cells[1]}.")
                    elif len(headers) >= 2 and len(cells) >= 2:
                        parts = []
                        for j, cell in enumerate(cells):
                            if cell and j < len(headers):
                                parts.append(f"{headers[j]}: {cell}")
                        if parts:
                            result.append(". ".join(parts) + ".")
                i += 1
            result.append('')  # blank line after table
        else:
            result.append(lines[i])
            i += 1

    return '\n'.join(result)


def markdown_to_html(text):
    """Convert simple cleaned markdown to basic HTML for EPUB."""
    paragraphs = text.split('\n\n')
    html_parts = []

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        # Check if it's a list
        if para.startswith('- '):
            items = para.split('\n')
            html_parts.append('<ul>')
            for item in items:
                item_text = re.sub(r'^-\s+', '', item.strip())
                if item_text:
                    html_parts.append(f'<li>{item_text}</li>')
            html_parts.append('</ul>')
        else:
            # Regular paragraph - handle line breaks within
            para = para.replace('\n', ' ')
            # Clean up extra spaces
            para = re.sub(r'  +', ' ', para)
            html_parts.append(f'<p>{para}</p>')

    return '\n'.join(html_parts)


def create_epub():
    """Create the audiobook EPUB."""
    book = epub.EpubBook()

    # Set metadata
    book.set_identifier('ub-cim-audiobook-2026')
    book.set_title('The Urantia Book and A Course in Miracles: A Study Guide')
    book.set_language('en')
    book.add_author('Joseph')

    # Add default CSS
    style = '''
    body { font-family: Georgia, serif; line-height: 1.6; margin: 1em; }
    h1 { font-size: 1.5em; margin-top: 2em; }
    p { margin: 0.5em 0; text-indent: 0; }
    ul { margin: 0.5em 0; }
    '''
    css = epub.EpubItem(
        uid="style",
        file_name="style/default.css",
        media_type="text/css",
        content=style
    )
    book.add_item(css)

    chapters = []
    spine = ['nav']
    toc = []

    # Process chapters
    for idx, filename in enumerate(CHAPTER_FILES, 1):
        filepath = os.path.join(CHAPTERS_DIR, filename)
        if not os.path.exists(filepath):
            print(f"WARNING: {filepath} not found, skipping")
            continue

        with open(filepath, 'r') as f:
            content = f.read()

        # Apply audio rules
        audio_text = apply_audio_rules(content)

        # Convert to HTML
        html_content = markdown_to_html(audio_text)

        # Extract title from first line
        first_line = audio_text.split('\n')[0].strip()
        title = first_line if first_line else f'Chapter {idx}'

        # Create EPUB chapter
        epub_chapter = epub.EpubHtml(
            title=title,
            file_name=f'chapter_{idx:02d}.xhtml',
            lang='en'
        )
        epub_chapter.content = f'<html><head><link rel="stylesheet" href="style/default.css"/></head><body><h1>{title}</h1>{html_content}</body></html>'
        epub_chapter.add_item(css)

        book.add_item(epub_chapter)
        chapters.append(epub_chapter)
        spine.append(epub_chapter)
        toc.append(epub_chapter)

        print(f"Processed: {title} ({len(audio_text.split())} words)")

    # Process appendices
    for idx, filename in enumerate(APPENDIX_FILES, 1):
        filepath = os.path.join(APPENDICES_DIR, filename)
        if not os.path.exists(filepath):
            print(f"WARNING: {filepath} not found, skipping")
            continue

        with open(filepath, 'r') as f:
            content = f.read()

        # Apply audio rules
        audio_text = apply_audio_rules(content)

        # Convert to HTML
        html_content = markdown_to_html(audio_text)

        # Extract title
        first_line = audio_text.split('\n')[0].strip()
        title = first_line if first_line else f'Appendix {idx}'

        # Create EPUB chapter
        epub_appendix = epub.EpubHtml(
            title=title,
            file_name=f'appendix_{idx:02d}.xhtml',
            lang='en'
        )
        epub_appendix.content = f'<html><head><link rel="stylesheet" href="style/default.css"/></head><body><h1>{title}</h1>{html_content}</body></html>'
        epub_appendix.add_item(css)

        book.add_item(epub_appendix)
        chapters.append(epub_appendix)
        spine.append(epub_appendix)
        toc.append(epub_appendix)

        print(f"Processed: {title} ({len(audio_text.split())} words)")

    # Set table of contents
    book.toc = toc

    # Add navigation files
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # Set spine
    book.spine = spine

    # Write EPUB
    epub.write_epub(OUTPUT_PATH, book, {})
    print(f"\nEPUB created: {OUTPUT_PATH}")

    # Total word count
    total_words = 0
    for filename in CHAPTER_FILES:
        filepath = os.path.join(CHAPTERS_DIR, filename)
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                total_words += len(apply_audio_rules(f.read()).split())
    for filename in APPENDIX_FILES:
        filepath = os.path.join(APPENDICES_DIR, filename)
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                total_words += len(apply_audio_rules(f.read()).split())
    print(f"Total words: {total_words:,}")


if __name__ == '__main__':
    create_epub()
