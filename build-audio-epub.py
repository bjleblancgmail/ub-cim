"""
Build audio-ready EPUB for ElevenLabs TTS.
Applies all formatting transformations per q-audio-ready rules.
"""

import re
import os
from ebooklib import epub

# --- Configuration ---
BOOK_DIR = os.path.join(os.path.dirname(__file__), "my-book")
CHAPTERS_DIR = os.path.join(BOOK_DIR, "chapters")
APPENDICES_DIR = os.path.join(BOOK_DIR, "appendices")
OUTPUT_PATH = os.path.join(BOOK_DIR, "audio", "UB-CIM-Study-Guide-Audiobook.epub")

# Ordered list of (filename, directory)
SOURCES = [
    ("chapter-01-introduction.md", CHAPTERS_DIR),
    ("chapter-02-urantia-book-overview.md", CHAPTERS_DIR),
    ("chapter-03-course-in-miracles-true-history.md", CHAPTERS_DIR),
    ("chapter-04-epochal-vs-personal-revelation.md", CHAPTERS_DIR),
    ("chapter-05-terminology-bridge.md", CHAPTERS_DIR),
    ("chapter-06-central-thesis.md", CHAPTERS_DIR),
    ("chapter-07-sonship-supreme.md", CHAPTERS_DIR),
    ("chapter-08-what-is-real-DRAFT.md", CHAPTERS_DIR),
    ("chapter-09-miracles-and-time.md", CHAPTERS_DIR),
    ("chapter-10-adjuster-fusion-transfer-bridge.md", CHAPTERS_DIR),
    ("chapter-11-identify-with-spirit-reality.md", CHAPTERS_DIR),
    ("chapter-12-forgiveness-mercy-vs-love.md", CHAPTERS_DIR),
    ("chapter-13-perception-vs-knowledge.md", CHAPTERS_DIR),
    ("chapter-14-fear-vs-love.md", CHAPTERS_DIR),
    ("chapter-15-lucifer-rebellion-why-we-suffer.md", CHAPTERS_DIR),
    ("chapter-16-what-happens-after-ascension-path.md", CHAPTERS_DIR),
    ("chapter-17-the-honest-question.md", CHAPTERS_DIR),
    ("appendix-a-terminology-mapping-v2.md", APPENDICES_DIR),
    ("appendix-b-parallels-condensed.md", APPENDICES_DIR),
    ("appendix-c-miracle-principles.md", APPENDICES_DIR),
]


def transform_for_audio(text):
    """Apply all ElevenLabs formatting rules to markdown text."""

    # Remove STATUS lines
    text = re.sub(r'\*\*STATUS:.*?\*\*\n*', '', text)

    # Remove horizontal rules
    text = re.sub(r'\n---\n', '\n\n', text)
    text = re.sub(r'^---$', '', text, flags=re.MULTILINE)

    # Convert blockquotes: remove > markers
    text = re.sub(r'^>\s?', '', text, flags=re.MULTILINE)

    # Remove bold markers
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)

    # Remove italic markers
    text = re.sub(r'\*(.+?)\*', r'\1', text)

    # Remove markdown link syntax [text](url) -> text
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)

    # Em dashes: replace with comma-space for parenthetical, period-space for clause breaks
    # Simple heuristic: if preceded by a space and followed by a space, use comma
    text = text.replace('\u2014', ', ')  # em dash
    text = text.replace('\u2013', ', ')  # en dash

    # Convert ## Section headings to blank lines (audio pauses)
    # Keep # Chapter headings as spoken text
    text = re.sub(r'^## .+$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^### .+$', '', text, flags=re.MULTILINE)

    # Convert # Chapter headings to plain spoken text
    text = re.sub(r'^# (.+)$', r'\1', text, flags=re.MULTILINE)

    # Convert parenthetical references like (Ch 6) to spoken form
    text = re.sub(r'\(Ch\.?\s*(\d+)\)', r'as discussed in Chapter \1', text)
    text = re.sub(r'\(Ch\.?\s*(\d+),\s*(\d+)\)', r'as discussed in Chapters \1 and \2', text)

    # Replace three dots with ellipsis character
    text = text.replace('...', '\u2026')

    # Convert markdown tables to narrated prose
    text = convert_tables_to_prose(text)

    # Clean up excessive blank lines
    text = re.sub(r'\n{4,}', '\n\n\n', text)

    # Strip leading/trailing whitespace
    text = text.strip()

    return text


def convert_tables_to_prose(text):
    """Convert markdown tables to narrated prose for audio."""
    lines = text.split('\n')
    result = []
    i = 0
    while i < len(lines):
        line = lines[i]
        # Detect table start (line with | characters)
        if '|' in line and i + 1 < len(lines) and '---' in lines[i + 1]:
            # Parse header
            headers = [h.strip() for h in line.split('|') if h.strip()]
            i += 2  # skip header and separator

            # Parse rows
            while i < len(lines) and '|' in lines[i] and lines[i].strip():
                cells = [c.strip() for c in lines[i].split('|') if c.strip()]
                if len(cells) >= 2 and len(headers) >= 2:
                    # Build narrated sentence
                    if headers[0].lower() in ('cim', 'course in miracles', 'course'):
                        result.append(f"The Course speaks of {cells[0]}. The Urantia Book calls this {cells[1]}.")
                    elif headers[0].lower() in ('decision', 'term'):
                        result.append(f"{cells[0]}. {cells[1]}.")
                    else:
                        result.append(f"{cells[0]}: {cells[1]}.")
                    if len(cells) > 2 and cells[2]:
                        result.append(f"{cells[2]}")
                i += 1
            result.append('')  # blank line after table
        else:
            result.append(line)
            i += 1

    return '\n'.join(result)


def md_to_html(text):
    """Minimal markdown to HTML conversion for EPUB content."""
    lines = text.split('\n')
    html_parts = []
    in_paragraph = False

    for line in lines:
        stripped = line.strip()

        if not stripped:
            if in_paragraph:
                html_parts.append('</p>')
                in_paragraph = False
            continue

        # Escape HTML entities
        stripped = stripped.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

        if not in_paragraph:
            html_parts.append('<p>')
            in_paragraph = True
        else:
            html_parts.append('<br/>')

        html_parts.append(stripped)

    if in_paragraph:
        html_parts.append('</p>')

    return '\n'.join(html_parts)


def extract_title(text):
    """Extract the chapter/appendix title from the first # heading."""
    match = re.match(r'^#\s+(.+)$', text, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return "Untitled"


def build_epub():
    """Build the audio-ready EPUB."""
    book = epub.EpubBook()

    # Metadata
    book.set_identifier('ub-cim-study-guide-audiobook')
    book.set_title('The Urantia Book and A Course in Miracles: A Study Guide')
    book.set_language('en')
    book.add_author('Joseph')

    # Style
    style = '''
    body { font-family: Georgia, serif; line-height: 1.6; margin: 2em; }
    p { margin-bottom: 1em; }
    h1 { font-size: 1.5em; margin-top: 2em; }
    '''
    nav_css = epub.EpubItem(
        uid="style_nav",
        file_name="style/nav.css",
        media_type="text/css",
        content=style
    )
    book.add_item(nav_css)

    chapters = []
    spine = ['nav']
    toc = []
    total_words = 0

    for idx, (filename, directory) in enumerate(SOURCES):
        filepath = os.path.join(directory, filename)
        if not os.path.exists(filepath):
            print(f"WARNING: {filepath} not found, skipping")
            continue

        with open(filepath, 'r', encoding='utf-8') as f:
            raw_text = f.read()

        title = extract_title(raw_text)
        audio_text = transform_for_audio(raw_text)
        html_content = md_to_html(audio_text)
        word_count = len(audio_text.split())
        total_words += word_count

        # Create EPUB chapter
        chapter_id = f'chapter_{idx:02d}'
        epub_chapter = epub.EpubHtml(
            title=title,
            file_name=f'{chapter_id}.xhtml',
            lang='en'
        )
        epub_chapter.content = f'<html><head><link rel="stylesheet" href="style/nav.css"/></head><body><h1>{title}</h1>{html_content}</body></html>'
        epub_chapter.add_item(nav_css)

        book.add_item(epub_chapter)
        chapters.append(epub_chapter)
        spine.append(epub_chapter)
        toc.append(epub.Link(f'{chapter_id}.xhtml', title, chapter_id))

        print(f"  {title}: {word_count:,} words")

    # Table of contents
    book.toc = toc

    # Navigation
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # Spine
    book.spine = spine

    # Ensure output directory exists
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    # Write EPUB
    epub.write_epub(OUTPUT_PATH, book, {})

    print(f"\nTotal: {total_words:,} words")
    print(f"EPUB written to: {OUTPUT_PATH}")
    return total_words


if __name__ == '__main__':
    build_epub()
