from fpdf import FPDF
from fpdf.enums import XPos, YPos
import re

class ChapterPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_page()
        self.set_auto_page_break(auto=True, margin=15)

    def chapter_title(self, title):
        self.set_font('Helvetica', 'B', 18)
        self.cell(0, 15, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        self.ln(10)

    def part_title(self, title):
        self.set_font('Helvetica', 'B', 14)
        self.ln(8)
        self.cell(0, 10, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
        self.ln(3)

    def section_title(self, title):
        self.set_font('Helvetica', 'B', 12)
        self.ln(5)
        self.cell(0, 8, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(3)

    def outline_chapter(self, title):
        self.set_font('Helvetica', 'B', 11)
        self.cell(0, 7, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def outline_item(self, text):
        self.set_font('Helvetica', '', 10)
        self.set_x(15)
        # Clean special chars
        text = text.replace('—', '-').replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'").replace('↔', '<->')
        self.multi_cell(0, 5, text)

    def body_text(self, text):
        self.set_font('Helvetica', '', 11)
        self.multi_cell(0, 6, text)
        self.ln(3)

    def quote_text(self, text):
        self.set_font('Helvetica', 'I', 10)
        self.set_x(20)
        self.multi_cell(0, 6, text)
        self.set_x(10)
        self.ln(3)

    def separator(self):
        self.ln(5)
        self.set_font('Helvetica', '', 11)
        self.cell(0, 5, '* * *', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        self.ln(5)

    def page_break_with_title(self, title):
        self.add_page()
        self.set_font('Helvetica', 'B', 16)
        self.cell(0, 15, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        self.ln(10)

def convert_chapter_to_pdf(pdf, md_path):
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Main title
        if line.startswith('# ') and not line.startswith('## '):
            pdf.chapter_title(line[2:])

        # Section title
        elif line.startswith('## '):
            pdf.section_title(line[3:])

        # Horizontal rule / separator
        elif line == '---':
            pdf.separator()

        # Quote
        elif line.startswith('> '):
            quote = line[2:]
            while i + 1 < len(lines) and lines[i + 1].strip().startswith('> '):
                i += 1
                quote += ' ' + lines[i].strip()[2:]
            quote = quote.replace('—', '-').replace('"', '"').replace('"', '"')
            quote = quote.replace(''', "'").replace(''', "'")
            pdf.quote_text(quote)

        # Bold paragraph header
        elif line.startswith('**') and line.endswith('**'):
            text = line[2:-2]
            pdf.set_font('Helvetica', 'B', 11)
            pdf.multi_cell(0, 6, text)
            pdf.ln(2)

        # Regular paragraph
        elif line and not line.startswith('#'):
            text = line
            text = re.sub(r'\*([^*]+)\*', r'\1', text)
            text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
            text = text.replace('—', '-').replace('"', '"').replace('"', '"')
            text = text.replace(''', "'").replace(''', "'")

            if text.strip():
                pdf.body_text(text)

        i += 1

def add_outline(pdf):
    pdf.page_break_with_title("Book Outline")

    # Part 1
    pdf.part_title("Part 1: Why These Two Books")

    pdf.outline_chapter("Chapter 1: Introduction")
    pdf.outline_item("- Two revelations in 50 years")
    pdf.outline_item("- What this study guide offers")
    pdf.outline_item("- [DRAFT COMPLETE]")

    pdf.outline_chapter("Chapter 2: The Urantia Book - An Overview")
    pdf.outline_item("- The four parts of the UB")
    pdf.outline_item("- How it was transmitted")
    pdf.outline_item("- Key themes relevant to CIM study")

    pdf.outline_chapter("Chapter 3: A Course in Miracles - The True History")
    pdf.outline_item("- Helen Schucman and Bill Thetford")
    pdf.outline_item("- The urtext vs edited versions")
    pdf.outline_item("- JCIM vs ACIM: Why this distinction matters")

    pdf.outline_chapter("Chapter 4: Epochal vs Personal Revelation")
    pdf.outline_item("- UB as epochal revelation")
    pdf.outline_item("- CIM as personal revelation")
    pdf.outline_item("- Mapping concepts across different language")

    pdf.outline_chapter("Chapter 5: The Terminology Bridge")
    pdf.outline_item("- Core mapping table (Sonship <-> Supreme, Soul <-> Adjuster, etc.)")
    pdf.outline_item("- Why these mappings matter")

    pdf.ln(5)

    # Part 2
    pdf.part_title("Part 2: Thematic Deep Dives")

    pdf.outline_chapter("Chapter 6: The Central Thesis - A Course in Adjuster Fusion")
    pdf.outline_item("- CIM as the practical path to fusion")
    pdf.outline_item("- UB provides the map, CIM provides the method")

    pdf.outline_chapter("Chapter 7: The Sonship / God the Supreme")
    pdf.outline_item("- 'The Sonship is the sum of all souls God created'")
    pdf.outline_item("- 'The Supreme is the sum total of all finite growth'")

    pdf.outline_chapter("Chapter 8: What is Real? The Eternal Perspective")
    pdf.outline_item("- To spirit, material seems unreal; to material, spirit seems unreal")
    pdf.outline_item("- We become real as we identify with eternal realities")

    pdf.outline_chapter("Chapter 9: Miracles and Time")
    pdf.outline_item("- 'Miracles shorten time' (both books)")
    pdf.outline_item("- The 50 miracle principles with UB parallels")

    pdf.outline_chapter("Chapter 10: Adjuster Fusion - Transfer and the Bridge")
    pdf.outline_item("- Transfer of identity from material to morontia soul")
    pdf.outline_item("- The Holy Spirit as bridge")

    pdf.outline_chapter("Chapter 11: Identify with Spirit Reality")
    pdf.outline_item("- CIM as mind training")
    pdf.outline_item("- Ego vs indwelling Adjuster")

    pdf.outline_chapter("Chapter 12: Forgiveness - Mercy vs Love")
    pdf.outline_item("- The forgiveness of mercy vs the forgiveness of love")
    pdf.outline_item("- 'Divine love absorbs and destroys' wrongdoing")

    pdf.outline_chapter("Chapter 13: Perception vs Knowledge")
    pdf.outline_item("- Two incompatible thought systems")
    pdf.outline_item("- The Holy Spirit bridges them")

    pdf.outline_chapter("Chapter 14: Fear vs Love")
    pdf.outline_item("- 'The opposite of love is fear'")
    pdf.outline_item("- The Lucifer rebellion as source of fear")

    pdf.outline_chapter("Chapter 15: The Lucifer Rebellion and Why We Suffer")
    pdf.outline_item("- CIM's oblique references")
    pdf.outline_item("- UB's detailed account")

    pdf.outline_chapter("Chapter 16: What Happens After - The Ascension Path")
    pdf.outline_item("- Where CIM leaves off, UB picks up")
    pdf.outline_item("- The long journey to Paradise")

    pdf.ln(5)

    # Part 3
    pdf.part_title("Part 3: Quick Reference")

    pdf.outline_chapter("Appendix A: Terminology Mapping Table")
    pdf.outline_chapter("Appendix B: CIM Miracle Principles with UB Parallels")
    pdf.outline_chapter("Appendix C: Key UB Papers for CIM Students")
    pdf.outline_chapter("Appendix D: Key CIM Sections for UB Students")
    pdf.outline_chapter("Appendix E: Study Questions for Groups")
    pdf.outline_chapter("Appendix F: Where to Find the Urtext")

def main():
    pdf = ChapterPDF()

    # Add Chapter 1
    convert_chapter_to_pdf(
        pdf,
        r'C:\Alpha\UB-CIM (non fiction Author)\my-book\chapters\chapter-01-introduction.md'
    )

    # Add Outline
    add_outline(pdf)

    # Save
    output_path = r'C:\Alpha\UB-CIM (non fiction Author)\my-book\chapters\chapter-01-with-outline.pdf'
    pdf.output(output_path)
    print(f"PDF created: {output_path}")

if __name__ == '__main__':
    main()
