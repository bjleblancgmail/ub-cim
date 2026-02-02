from fpdf import FPDF
from fpdf.enums import XPos, YPos

class OutlinePDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_page()
        self.set_auto_page_break(auto=True, margin=15)

    def main_title(self, title):
        self.set_font('Helvetica', 'B', 20)
        self.cell(0, 15, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        self.ln(5)

    def subtitle(self, text):
        self.set_font('Helvetica', 'I', 12)
        self.multi_cell(0, 6, text, align='C')
        self.ln(3)

    def part_title(self, title):
        self.ln(8)
        self.set_font('Helvetica', 'B', 14)
        self.set_fill_color(240, 240, 240)
        self.cell(0, 10, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True)
        self.ln(5)

    def chapter_title(self, title):
        self.set_font('Helvetica', 'B', 11)
        self.ln(3)
        self.cell(0, 7, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def bullet_item(self, text):
        self.set_font('Helvetica', '', 10)
        self.set_x(15)
        # Clean special chars
        text = text.replace('—', '-').replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'").replace('↔', '<->')
        self.multi_cell(0, 5, text)

    def section_text(self, text):
        self.set_font('Helvetica', '', 10)
        text = text.replace('—', '-').replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")
        self.multi_cell(0, 5, text)
        self.ln(2)

    def separator(self):
        self.ln(5)

def create_outline_pdf():
    pdf = OutlinePDF()

    # Title
    pdf.main_title("UB-CIM Study Guide")
    pdf.subtitle("Book Outline")
    pdf.ln(5)

    # Core info
    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(0, 7, "Core Thesis:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.section_text("The Course in Miracles is a course in Adjuster fusion, presented from the eternal spirit perspective by Jesus. The UB provides the cosmological framework; the CIM provides the practical path.")

    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(0, 7, "Purpose:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.section_text("A study guide synthesizing The Urantia Book and A Course in Miracles for readers of either or both texts.")

    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(0, 7, "Audiences:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.bullet_item("1. UB readers wanting to understand CIM")
    pdf.bullet_item("2. CIM readers wanting to understand UB")
    pdf.bullet_item("3. Readers of both seeking deeper synthesis")
    pdf.bullet_item("4. Newcomers to both books")

    # Part 1
    pdf.part_title("Part 1: Why These Two Books")

    pdf.chapter_title("Chapter 1: Introduction [DRAFT COMPLETE]")
    pdf.bullet_item("- Two revelations in 50 years (UB 1955, CIM 1965-72)")
    pdf.bullet_item("- What this study guide offers")
    pdf.bullet_item("- Why two revelations?")
    pdf.bullet_item("- Four audiences")

    pdf.chapter_title("Chapter 2: The Urantia Book - An Overview")
    pdf.bullet_item("- The four parts (Cosmology, Local Universe, History, Life of Jesus)")
    pdf.bullet_item("- How it was transmitted (celestial authors, contact commission)")
    pdf.bullet_item("- Jesus approved but did not write it - epochal revelation")
    pdf.bullet_item("- Key themes relevant to CIM study")

    pdf.chapter_title("Chapter 3: A Course in Miracles - The True History")
    pdf.bullet_item("- Helen Schucman and Bill Thetford's original work")
    pdf.bullet_item("- Helen's shorthand -> handwritten -> Bill's typed edit")
    pdf.bullet_item("- Ken Wapnick's further editing")
    pdf.bullet_item("- The 2001 lawsuit and discovery of notes in Library of Congress")
    pdf.bullet_item("- JCIM vs ACIM: Why this distinction matters")
    pdf.bullet_item("- The critical error: 'ego created all material reality' (NOT in urtext)")

    pdf.chapter_title("Chapter 4: Epochal vs Personal Revelation")
    pdf.bullet_item("- UB as epochal revelation (no conscious mind filter)")
    pdf.bullet_item("- CIM as personal revelation (filtered through Helen)")
    pdf.bullet_item("- Why Jesus works through scribes, never writes directly")
    pdf.bullet_item("- Helen did not know the UB - Jesus stayed within her vocabulary")

    pdf.chapter_title("Chapter 5: The Terminology Bridge")
    pdf.bullet_item("- Sonship <-> God the Supreme")
    pdf.bullet_item("- Soul <-> Thought Adjuster")
    pdf.bullet_item("- Knowledge <-> Eternal Perspective")
    pdf.bullet_item("- Perception <-> Temporal/Animal Mind")
    pdf.bullet_item("- Holy Spirit <-> Spirit of Truth / Superconscious")
    pdf.bullet_item("- Atonement <-> Plan of Ascension")

    # Part 2
    pdf.part_title("Part 2: Thematic Deep Dives")

    pdf.chapter_title("Chapter 6: The Central Thesis - A Course in Adjuster Fusion")
    pdf.bullet_item("- CIM as the practical path to fusion")
    pdf.bullet_item("- UB provides the map, CIM provides the method")
    pdf.bullet_item("- 'The miracle itself is just this fusion or union of will'")

    pdf.chapter_title("Chapter 7: The Sonship / God the Supreme")
    pdf.bullet_item("- CIM: 'The Sonship is the sum of all souls God created'")
    pdf.bullet_item("- UB: 'The Supreme is the sum total of all finite growth'")
    pdf.bullet_item("- We will all simultaneously discover God the Supreme together")

    pdf.chapter_title("Chapter 8: What is Real? The Eternal Perspective")
    pdf.bullet_item("- To spirit, material seems unreal; to material, spirit seems unreal")
    pdf.bullet_item("- We become real as we identify with eternal realities")
    pdf.bullet_item("- 'Conceptual frames are serviceable scaffolding'")

    pdf.chapter_title("Chapter 9: Miracles and Time")
    pdf.bullet_item("- 'Miracles shorten time' (both books use this language)")
    pdf.bullet_item("- Jesus remained 'constantly time conscious' to prevent time miracles")
    pdf.bullet_item("- The 50 miracle principles with UB parallels")

    pdf.chapter_title("Chapter 10: Adjuster Fusion - Transfer and the Bridge")
    pdf.bullet_item("- 'Transfer of the seat of identity' from body to soul")
    pdf.bullet_item("- 'The Holy Spirit is the bridge of perception to knowledge'")
    pdf.bullet_item("- Jesus: 'I am the living BRIDGE from one world to another'")

    pdf.chapter_title("Chapter 11: Identify with Spirit Reality")
    pdf.bullet_item("- CIM as mind training: lessen focus on material")
    pdf.bullet_item("- Do we identify with Ego or indwelling Adjuster?")
    pdf.bullet_item("- 'Only as a creature becomes God-identified does he become truly real'")

    pdf.chapter_title("Chapter 12: Forgiveness - Mercy vs Love")
    pdf.bullet_item("- Forgiveness of mercy: 'retain the proof he is not innocent'")
    pdf.bullet_item("- Forgiveness of love: 'holds not the proof of sin'")
    pdf.bullet_item("- 'Divine love absorbs and actually destroys' wrongdoing")

    pdf.chapter_title("Chapter 13: Perception vs Knowledge")
    pdf.bullet_item("- Two incompatible thought systems")
    pdf.bullet_item("- Perception = animal mind / ego")
    pdf.bullet_item("- Knowledge = eternal perspective / superconscious")
    pdf.bullet_item("- 'When the Holy Spirit has led you to Christ... perception fuses into knowledge'")

    pdf.chapter_title("Chapter 14: Fear vs Love")
    pdf.bullet_item("- 'The opposite of love is fear'")
    pdf.bullet_item("- 'Unreasoned fear is a master intellectual fraud'")
    pdf.bullet_item("- The Lucifer rebellion as source of fear")

    pdf.chapter_title("Chapter 15: The Lucifer Rebellion and Why We Suffer")
    pdf.bullet_item("- CIM's oblique references ('darkness and death')")
    pdf.bullet_item("- UB's detailed account")
    pdf.bullet_item("- How rebellion created our confused planet")

    pdf.chapter_title("Chapter 16: What Happens After - The Ascension Path")
    pdf.bullet_item("- Where CIM leaves off, UB picks up")
    pdf.bullet_item("- Mansion world training, morontia transition")
    pdf.bullet_item("- The long journey to Paradise")
    pdf.bullet_item("- Fusion as milestone, not destination")

    # Part 3
    pdf.part_title("Part 3: Quick Reference")

    pdf.chapter_title("Appendix A: Terminology Mapping Table")
    pdf.bullet_item("- Comprehensive side-by-side terms")

    pdf.chapter_title("Appendix B: CIM Miracle Principles with UB Parallels")
    pdf.bullet_item("- All 50 principles with corresponding UB quotes")

    pdf.chapter_title("Appendix C: Key UB Papers for CIM Students")
    pdf.bullet_item("- Papers 108, 110, 111, 112, 117, 136, 196")

    pdf.chapter_title("Appendix D: Key CIM Sections for UB Students")
    pdf.bullet_item("- Introduction, Chapter 1, urtext guidance")

    pdf.chapter_title("Appendix E: Study Questions for Groups")
    pdf.bullet_item("- Discussion questions by chapter")

    pdf.chapter_title("Appendix F: Where to Find the Urtext")
    pdf.bullet_item("- Online sources, published versions")

    # Save
    output_path = r'C:\Alpha\UB-CIM (non fiction Author)\my-book\outline\book-outline.pdf'
    pdf.output(output_path)
    print(f"PDF created: {output_path}")

if __name__ == '__main__':
    create_outline_pdf()
