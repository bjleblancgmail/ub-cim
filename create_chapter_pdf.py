from fpdf import FPDF
from fpdf.enums import XPos, YPos
import re
import sys

class ChapterPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_page()
        self.set_auto_page_break(auto=True, margin=15)

    def chapter_title(self, title):
        self.set_font('Helvetica', 'B', 18)
        self.multi_cell(0, 10, title, align='C')
        self.ln(10)

    def section_title(self, title):
        self.set_font('Helvetica', 'B', 12)
        self.ln(5)
        self.cell(0, 8, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(3)

    def body_text(self, text):
        self.set_font('Helvetica', '', 11)
        self.multi_cell(0, 6, text)
        self.ln(3)

    def quote_text(self, text):
        self.set_font('Helvetica', 'I', 10)
        self.set_x(15)
        self.multi_cell(180, 6, text)
        self.set_x(10)
        self.ln(3)

    def separator(self):
        self.ln(5)
        self.set_font('Helvetica', '', 11)
        self.cell(0, 5, '* * *', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        self.ln(5)

def clean_text(text):
    """Clean special characters for PDF"""
    text = text.replace('—', '-').replace('"', '"').replace('"', '"')
    text = text.replace(''', "'").replace(''', "'").replace('↔', '<->')
    # Remove markdown italic/bold markers
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    return text

def convert_md_to_pdf(md_path, pdf_path):
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    pdf = ChapterPDF()

    lines = content.split('\n')
    i = 0
    in_quote = False
    quote_buffer = []

    while i < len(lines):
        line = lines[i].strip()

        # Main title
        if line.startswith('# ') and not line.startswith('## '):
            title = clean_text(line[2:])
            pdf.chapter_title(title)

        # Section title
        elif line.startswith('## '):
            title = clean_text(line[3:])
            pdf.section_title(title)

        # Horizontal rule / separator
        elif line == '---':
            pdf.separator()

        # Quote start or continuation
        elif line.startswith('> '):
            quote_text = line[2:]
            # Collect multi-line quote
            while i + 1 < len(lines) and (lines[i + 1].strip().startswith('> ') or lines[i + 1].strip() == '>'):
                i += 1
                next_line = lines[i].strip()
                if next_line == '>':
                    quote_text += '\n\n'
                else:
                    quote_text += ' ' + next_line[2:]
            pdf.quote_text(clean_text(quote_text))

        # Regular paragraph
        elif line and not line.startswith('#'):
            pdf.body_text(clean_text(line))

        i += 1

    pdf.output(pdf_path)
    print(f"PDF created: {pdf_path}")

if __name__ == '__main__':
    if len(sys.argv) >= 3:
        convert_md_to_pdf(sys.argv[1], sys.argv[2])
    else:
        # Default: Chapter 6
        convert_md_to_pdf(
            r'C:\Alpha\UB-CIM (non fiction Author)\my-book\chapters\chapter-06-central-thesis.md',
            r'C:\Alpha\UB-CIM (non fiction Author)\my-book\chapters\chapter-06-central-thesis.pdf'
        )
