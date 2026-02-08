"""
Generate a single EPUB from audio-ready text files for ElevenLabs audiobook import.
"""
import os
from ebooklib import epub

AUDIO_DIR = r"C:\Alpha\UB-CIM (non fiction Author)\my-book\audio"
OUTPUT_PATH = os.path.join(AUDIO_DIR, "UB-CIM-Study-Guide-Audiobook.epub")

# Files in order: chapters first, appendices at end
FILES = [
    ("chapter-01-introduction.txt", "Chapter 1: Introduction"),
    ("chapter-02-urantia-book-overview.txt", "Chapter 2: The Urantia Book Overview"),
    ("chapter-03-course-in-miracles-true-history.txt", "Chapter 3: A Course in Miracles True History"),
    ("chapter-04-epochal-vs-personal-revelation.txt", "Chapter 4: Epochal vs Personal Revelation"),
    ("chapter-05-terminology-bridge.txt", "Chapter 5: The Terminology Bridge"),
    ("chapter-06-central-thesis.txt", "Chapter 6: The Central Thesis"),
    ("chapter-07-sonship-supreme.txt", "Chapter 7: Sonship and the Supreme"),
    ("chapter-08-what-is-real-DRAFT.txt", "Chapter 8: What Is Real"),
    ("chapter-09-miracles-and-time.txt", "Chapter 9: Miracles and Time"),
    ("chapter-10-adjuster-fusion-transfer-bridge.txt", "Chapter 10: Adjuster Fusion, Transfer, and the Bridge"),
    ("chapter-11-identify-with-spirit-reality.txt", "Chapter 11: Identify with Spirit Reality"),
    ("chapter-12-forgiveness-mercy-vs-love.txt", "Chapter 12: Forgiveness, Mercy vs Love"),
    ("chapter-13-perception-vs-knowledge.txt", "Chapter 13: Perception vs Knowledge"),
    ("chapter-14-fear-vs-love.txt", "Chapter 14: Fear vs Love"),
    ("chapter-15-lucifer-rebellion-why-we-suffer.txt", "Chapter 15: The Lucifer Rebellion, Why We Suffer"),
    ("chapter-16-what-happens-after-ascension-path.txt", "Chapter 16: What Happens After, The Ascension Path"),
    ("appendix-b-parallels-condensed.txt", "Appendix B: Selected Parallels"),
    ("appendix-c-miracle-principles.txt", "Appendix C: The 53 Miracle Principles"),
]


def txt_to_html(text):
    """Convert plain text to simple HTML paragraphs."""
    lines = text.strip().split("\n")
    html_parts = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Escape HTML entities
        line = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        html_parts.append(f"<p>{line}</p>")
    return "\n".join(html_parts)


def main():
    book = epub.EpubBook()

    # Metadata
    book.set_identifier("ub-cim-study-guide-audiobook-2026")
    book.set_title("UB-CIM Study Guide")
    book.set_language("en")
    book.add_author("Joseph")

    chapters = []
    spine = ["nav"]
    toc = []

    for i, (filename, title) in enumerate(FILES):
        filepath = os.path.join(AUDIO_DIR, filename)
        if not os.path.exists(filepath):
            print(f"SKIP: {filename} not found")
            continue

        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()

        html_content = txt_to_html(text)

        # Create chapter
        ch = epub.EpubHtml(
            title=title,
            file_name=f"ch{i+1:02d}.xhtml",
            lang="en",
        )
        ch.content = f"<h1>{title}</h1>\n{html_content}"
        book.add_item(ch)
        chapters.append(ch)
        spine.append(ch)
        toc.append(epub.Link(f"ch{i+1:02d}.xhtml", title, f"ch{i+1:02d}"))

    # Table of contents
    book.toc = toc

    # Navigation
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # Spine
    book.spine = spine

    # Write
    epub.write_epub(OUTPUT_PATH, book, {})

    size = os.path.getsize(OUTPUT_PATH)
    print(f"Created: {OUTPUT_PATH}")
    print(f"Size: {size:,} bytes ({size // 1024} KB)")
    print(f"Chapters: {len(chapters)}")


if __name__ == "__main__":
    main()
