"""
Convert markdown book chapters to audio-ready text for ElevenLabs TTS.
Applies all formatting rules from the q-audio-ready skill.
"""
import re
import os
import glob

INPUT_DIR = r"C:\Alpha\UB-CIM (non fiction Author)\my-book"
OUTPUT_DIR = r"C:\Alpha\UB-CIM (non fiction Author)\my-book\audio"

# Files to process
CHAPTER_PATTERN = os.path.join(INPUT_DIR, "chapters", "chapter-*.md")
APPENDIX_FILES = [
    os.path.join(INPUT_DIR, "appendices", "appendix-b-parallels-condensed.md"),
    os.path.join(INPUT_DIR, "appendices", "appendix-c-miracle-principles.md"),
]


def convert_table_to_prose(table_text):
    """Convert a markdown table to narrated prose."""
    lines = table_text.strip().split("\n")
    # Extract header row
    headers = []
    data_rows = []
    for i, line in enumerate(lines):
        line = line.strip()
        if not line or line.startswith("|--") or line.startswith("| --") or re.match(r'^\|[\s\-:|]+\|$', line):
            continue
        cells = [c.strip() for c in line.split("|") if c.strip()]
        if i == 0:
            headers = cells
        else:
            data_rows.append(cells)

    if not headers or not data_rows:
        return table_text

    prose_lines = []
    for row in data_rows:
        if len(row) >= 2:
            # Clean bold markers from cells
            clean_cells = [re.sub(r'\*\*(.*?)\*\*', r'\1', c) for c in row]
            term_cim = clean_cells[0]
            term_ub = clean_cells[1] if len(clean_cells) > 1 else ""
            notes = clean_cells[2] if len(clean_cells) > 2 else ""
            chapter = clean_cells[3] if len(clean_cells) > 3 else ""

            line = f"{term_cim}. "
            if term_ub:
                line += f"The Urantia Book calls this {term_ub}. "
            if notes:
                line += f"{notes} "
            if chapter:
                line += f"Discussed in {chapter}."
            prose_lines.append(line.strip())

    return "\n\n".join(prose_lines)


def process_parenthetical_refs(text):
    """Convert parenthetical chapter references to narrated form."""
    # (Ch 5, 6) -> as discussed in Chapters 5 and 6
    def replace_ch_ref(m):
        content = m.group(1)
        # Multiple chapters
        if "," in content:
            parts = [p.strip() for p in content.split(",")]
            if len(parts) == 2:
                return f", as discussed in Chapters {parts[0]} and {parts[1]}"
            else:
                return f", as discussed in Chapters {', '.join(parts[:-1])}, and {parts[-1]}"
        return f", as discussed in Chapter {content}"

    # (Ch 5, Section 2) -> as discussed in Chapter 5, Section 2
    text = re.sub(r'\(Ch\s+(\d+),\s*Section\s+(\d+(?:-\d+)?)\)', r', as discussed in Chapter \1, Section \2', text)
    # (Ch 5, 6) or (Ch 5)
    text = re.sub(r'\(Ch\s+([\d,\s]+)\)', replace_ch_ref, text)
    # Standalone section refs like (Section 2)
    text = re.sub(r'\(Section\s+(\d+(?:-\d+)?)\)', r', Section \1', text)
    return text


def apply_audio_rules(text, filename=""):
    """Apply all ElevenLabs formatting rules."""

    # Remove STATUS lines (all variants: **STATUS: text**, STATUS: text, etc.)
    text = re.sub(r'^\*\*STATUS[^\n]*\*\*\s*\n?', '', text, flags=re.MULTILINE | re.IGNORECASE)
    text = re.sub(r'^STATUS:[^\n]*\n?', '', text, flags=re.MULTILINE | re.IGNORECASE)

    # Convert tables to prose
    table_pattern = re.compile(r'(\|[^\n]+\|\n(?:\|[^\n]+\|\n)+)', re.MULTILINE)
    tables = table_pattern.findall(text)
    for table in tables:
        prose = convert_table_to_prose(table)
        text = text.replace(table, prose + "\n\n")

    # Convert # Chapter headings to spoken text
    text = re.sub(r'^# (Chapter \d+):\s*(.+)$', r'\1. \2.', text, flags=re.MULTILINE)
    text = re.sub(r'^# (Appendix [A-Z]):\s*(.+)$', r'\1. \2.', text, flags=re.MULTILINE)
    text = re.sub(r'^# (.+)$', r'\1.', text, flags=re.MULTILINE)

    # Remove ## and ### section headings but keep text for context
    text = re.sub(r'^###\s+(.+)$', r'\1.', text, flags=re.MULTILINE)
    text = re.sub(r'^##\s+(.+)$', r'\1.', text, flags=re.MULTILINE)

    # Remove horizontal rules
    text = re.sub(r'^---+\s*$', '', text, flags=re.MULTILINE)

    # Remove blockquote markers
    text = re.sub(r'^>\s?', '', text, flags=re.MULTILINE)

    # Remove bold markers
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)

    # Remove italic markers
    text = re.sub(r'\*(.+?)\*', r'\1', text)

    # Remove markdown links, keep text
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)

    # Remove bare URLs
    text = re.sub(r'https?://\S+', '', text)

    # Em dashes to commas (most common case for parenthetical)
    text = text.replace(' \u2014 ', ', ')
    text = text.replace('\u2014', ', ')

    # En dashes to commas
    text = text.replace(' \u2013 ', ', ')
    text = text.replace('\u2013', ', ')

    # Three dots to ellipsis character
    text = text.replace('...', '\u2026')

    # Process parenthetical references
    text = process_parenthetical_refs(text)

    # Clean up JCIM/UB citation format for audio
    # (JCIM, Chapter 5, Tx 5.32) -> from the Course, Chapter 5
    text = re.sub(r'\(JCIM,\s*Chapter\s*(\d+),\s*Tx\s*[\d.]+\)', r'from the Course, Chapter \1', text)
    text = re.sub(r'\(JCIM,\s*Tx:?[\d.]+\)', 'from the Course', text)
    text = re.sub(r'\(JCIM,\s*Chapter\s*(\d+)\)', r'from the Course, Chapter \1', text)
    text = re.sub(r'\(JCIM\s*\(Tx:[\d.]+\)\)', 'from the Course', text)

    # UB citations
    text = re.sub(r'\(UB Paper\s*(\d+),\s*[\d:.]+\)', r'from the Urantia Book, Paper \1', text)
    text = re.sub(r'\(UB\s+[\d:.]+\)', 'from the Urantia Book', text)

    # Clean up header citation formats from appendix B
    # JCIM (Tx:5.46): -> From the Course.
    text = re.sub(r'JCIM\s*\(Tx:[\d.]+(?:,\s*[\d.]+)*\):', 'From the Course:', text)
    text = re.sub(r'JCIM\s*\(W1:[\d.]+\):', 'From the Course, Workbook:', text)
    text = re.sub(r'JCIM\s*\(M:[\d.]+\):', 'From the Course, Manual:', text)
    text = re.sub(r'JCIM:', 'From the Course:', text)

    # Urantia Book (184:4.6): -> From the Urantia Book. (header lines only)
    text = re.sub(r'^Urantia Book\s*\([\d:.]+\):', 'From the Urantia Book:', text, flags=re.MULTILINE)
    # Standalone "Urantia Book:" at start of line only
    text = re.sub(r'^(?<!From the )Urantia Book:', 'From the Urantia Book:', text, flags=re.MULTILINE)

    # Clean up double spaces
    text = re.sub(r'  +', ' ', text)

    # Clean up excessive blank lines (max 2)
    text = re.sub(r'\n{4,}', '\n\n\n', text)

    # Clean up leading/trailing whitespace on lines
    lines = text.split('\n')
    lines = [line.rstrip() for line in lines]
    text = '\n'.join(lines)

    return text.strip()


def process_file(input_path, output_dir):
    """Process a single file."""
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    filename = os.path.basename(input_path)
    audio_text = apply_audio_rules(content, filename)

    # Output as .txt
    output_name = os.path.splitext(filename)[0] + ".txt"
    output_path = os.path.join(output_dir, output_name)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(audio_text)

    word_count = len(audio_text.split())
    return output_name, word_count


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Gather all input files
    chapter_files = sorted(glob.glob(CHAPTER_PATTERN))
    all_files = chapter_files + APPENDIX_FILES

    results = []
    total_words = 0

    for filepath in all_files:
        if not os.path.exists(filepath):
            print(f"SKIP (not found): {filepath}")
            continue
        name, words = process_file(filepath, OUTPUT_DIR)
        results.append((name, words))
        total_words += words
        print(f"  {name}: {words:,} words")

    print(f"\n{'='*50}")
    print(f"Files generated: {len(results)}")
    print(f"Total words: {total_words:,}")
    print(f"Output directory: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
