"""Find the last chapter boundary in the urtext."""
import re
from iambic_scan import count_sentence_syllables


def extract_sentences(text):
    text = text.replace('\t', ' ')
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]


def is_real(s):
    clean = re.sub(r'[^a-zA-Z\s]', '', s).strip()
    words = clean.split()
    if len(words) < 3:
        return False
    alpha = sum(1 for c in s if c.isalpha() or c.isspace())
    return alpha >= len(s) * 0.7


def main():
    filepath = "my-book/source-material/CourseUB/urtext_extracted.txt"
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        text = f.read()

    sentences = extract_sentences(text)
    real = [(i, s) for i, s in enumerate(sentences) if is_real(s)]

    # Look for date markers, chapter headers, or section breaks in last 30% of text
    print("Looking for chapter/section markers in last portion of text...\n")

    cutoff = int(len(real) * 0.70)
    for idx, s in real[cutoff:]:
        sl = s.lower()
        # Look for date stamps (Helen's dating), chapter markers, section headers
        if (re.search(r'(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d', sl)
            or re.search(r'chapter\s+\d', sl)
            or 'section' in sl[:20]
            or re.search(r'^\d+\.\s', s)  # numbered sections
            or 'tc ' in sl  # table of contents markers
            ):
            print(f"[{idx}] {s[:150]}")

    # Also show sentences around index 20500-20550 to find chapter start
    print("\n\nSentences around 20500-20600:")
    for idx, s in real:
        if 20500 <= idx <= 20600:
            syl = count_sentence_syllables(s)
            print(f"[{idx}] ({syl:>2} syl) {s[:140]}")


if __name__ == '__main__':
    main()
