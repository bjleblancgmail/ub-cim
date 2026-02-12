"""Build EPUB for UB-CIM Study Guide."""

import os
import markdown
from ebooklib import epub

BOOK_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "my-book")

# Chapter files in order
CHAPTERS = [
    ("chapters/chapter-01-introduction.md", "Chapter 1: Introduction"),
    ("chapters/chapter-02-urantia-book-overview.md", "Chapter 2: The Urantia Book Overview"),
    ("chapters/chapter-03-course-in-miracles-true-history.md", "Chapter 3: Course in Miracles True History"),
    ("chapters/chapter-04-epochal-vs-personal-revelation.md", "Chapter 4: Epochal vs Personal Revelation"),
    ("chapters/chapter-05-terminology-bridge.md", "Chapter 5: The Terminology Bridge"),
    ("chapters/chapter-06-central-thesis.md", "Chapter 6: The Central Thesis"),
    ("chapters/chapter-07-sonship-supreme.md", "Chapter 7: Sonship and the Supreme"),
    ("chapters/chapter-08-what-is-real-DRAFT.md", "Chapter 8: What Is Real"),
    ("chapters/chapter-09-miracles-and-time.md", "Chapter 9: Miracles and Time"),
    ("chapters/chapter-10-adjuster-fusion-transfer-bridge.md", "Chapter 10: Adjuster Fusion Transfer Bridge"),
    ("chapters/chapter-11-identify-with-spirit-reality.md", "Chapter 11: Identify with Spirit Reality"),
    ("chapters/chapter-12-forgiveness-mercy-vs-love.md", "Chapter 12: Forgiveness, Mercy vs Love"),
    ("chapters/chapter-13-perception-vs-knowledge.md", "Chapter 13: Perception vs Knowledge"),
    ("chapters/chapter-14-fear-vs-love.md", "Chapter 14: Fear vs Love"),
    ("chapters/chapter-15-lucifer-rebellion-why-we-suffer.md", "Chapter 15: The Lucifer Rebellion, Why We Suffer"),
    ("chapters/chapter-16-what-happens-after-ascension-path.md", "Chapter 16: What Happens After, The Ascension Path"),
]

APPENDICES = [
    ("appendices/appendix-a-terminology-mapping-v2.md", "Appendix A: Terminology Mapping"),
    ("appendices/appendix-b-parallels-condensed.md", "Appendix B: Selected Parallels"),
    ("appendices/appendix-c-miracle-principles.md", "Appendix C: Miracle Principles"),
]

# CSS for clean reading
BOOK_CSS = """
body {
    font-family: Georgia, "Times New Roman", serif;
    line-height: 1.6;
    margin: 1em;
    color: #222;
}
h1 {
    font-size: 1.8em;
    margin-top: 1.5em;
    margin-bottom: 0.5em;
    page-break-before: always;
}
h2 {
    font-size: 1.4em;
    margin-top: 1.2em;
    margin-bottom: 0.4em;
}
h3 {
    font-size: 1.15em;
    margin-top: 1em;
    margin-bottom: 0.3em;
}
p {
    margin: 0.5em 0;
    text-align: justify;
}
blockquote {
    margin: 1em 1.5em;
    padding: 0.5em 1em;
    border-left: 3px solid #888;
    font-style: italic;
    color: #444;
}
em {
    font-style: italic;
}
strong {
    font-weight: bold;
}
hr {
    border: none;
    border-top: 1px solid #ccc;
    margin: 1.5em 0;
}
table {
    border-collapse: collapse;
    width: 100%;
    margin: 1em 0;
}
th, td {
    border: 1px solid #aaa;
    padding: 0.4em 0.6em;
    text-align: left;
}
th {
    background-color: #eee;
    font-weight: bold;
}
"""

def read_md(filepath):
    """Read a markdown file and return HTML."""
    full_path = os.path.join(BOOK_DIR, filepath)
    with open(full_path, "r", encoding="utf-8") as f:
        text = f.read()
    html = markdown.markdown(text, extensions=["tables", "smarty"])
    return html


def build_epub():
    book = epub.EpubBook()

    # Metadata
    book.set_identifier("ub-cim-study-guide-2026")
    book.set_title("UB-CIM Study Guide")
    book.set_language("en")
    book.add_author("Joseph")
    book.add_metadata("DC", "description",
        "A study guide synthesizing The Urantia Book and A Course in Miracles")

    # CSS
    css = epub.EpubItem(
        uid="style",
        file_name="style/book.css",
        media_type="text/css",
        content=BOOK_CSS.encode("utf-8"),
    )
    book.add_item(css)

    # Title page
    title_html = """
    <div style="text-align: center; margin-top: 30%;">
        <h1 style="font-size: 2.2em; page-break-before: avoid;">UB-CIM Study Guide</h1>
        <p style="font-size: 1.2em; margin-top: 1em; font-style: italic;">
            A Study Guide Synthesizing<br/>
            The Urantia Book and A Course in Miracles
        </p>
        <p style="font-size: 1.1em; margin-top: 2em;">by Joseph</p>
    </div>
    """
    title_page = epub.EpubHtml(
        title="Title Page",
        file_name="title.xhtml",
        content=title_html,
    )
    title_page.add_item(css)
    book.add_item(title_page)

    spine = ["nav", title_page]
    toc = []

    # Chapters
    chapter_items = []
    for i, (filepath, title) in enumerate(CHAPTERS, 1):
        html = read_md(filepath)
        ch = epub.EpubHtml(
            title=title,
            file_name=f"chapter_{i:02d}.xhtml",
            content=f"<html><body>{html}</body></html>",
        )
        ch.add_item(css)
        book.add_item(ch)
        chapter_items.append(ch)
        spine.append(ch)

    toc.append((epub.Section("Chapters"), chapter_items))

    # Appendices
    appendix_items = []
    for i, (filepath, title) in enumerate(APPENDICES, 1):
        html = read_md(filepath)
        label = chr(64 + i)  # A, B, C
        ap = epub.EpubHtml(
            title=title,
            file_name=f"appendix_{label.lower()}.xhtml",
            content=f"<html><body>{html}</body></html>",
        )
        ap.add_item(css)
        book.add_item(ap)
        appendix_items.append(ap)
        spine.append(ap)

    toc.append((epub.Section("Appendices"), appendix_items))

    # Build
    book.toc = toc
    book.spine = spine
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    output_path = os.path.join(BOOK_DIR, "UB-CIM-Study-Guide.epub")
    epub.write_epub(output_path, book)
    print(f"EPUB created: {output_path}")
    print(f"  Chapters: {len(CHAPTERS)}")
    print(f"  Appendices: {len(APPENDICES)}")


if __name__ == "__main__":
    build_epub()
