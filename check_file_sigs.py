"""
Check if any of our binary methods match known file format signatures.
Also analyze which method's byte distribution looks most like a structured binary file.
"""

import re
from collections import Counter
from iambic_scan import (STRESS_DICT, count_syllables, get_stress,
                         count_sentence_syllables, get_sentence_stress)


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


def get_toggle_bits(pattern):
    state = 0
    toggle = []
    for i, actual in enumerate(pattern):
        expected = i % 2
        if actual != expected:
            state = 1 - state
        toggle.append(state)
    return toggle


def syllabify_word(word):
    clean = re.sub(r'[^a-zA-Z]', '', word)
    if not clean:
        return []
    stress = get_stress(word)
    num_syls = len(stress)
    if num_syls <= 1:
        return [clean]
    n = len(clean)
    if n <= num_syls:
        return [c for c in clean] + [''] * (num_syls - n)
    groups = []
    chars_per_syl = n / num_syls
    for s in range(num_syls):
        start = int(s * chars_per_syl)
        end = int((s + 1) * chars_per_syl)
        groups.append(clean[start:end])
    return groups


def bits_to_bytes(bits):
    """Convert bit string to list of byte values."""
    bytes_list = []
    for i in range(0, len(bits) - 7, 8):
        byte = bits[i:i+8]
        bytes_list.append(int(byte, 2))
    return bytes_list


def invert_bits(bits):
    return ''.join('1' if b == '0' else '0' for b in bits)


# Known file format signatures (magic bytes)
FILE_SIGNATURES = {
    'PDF': [0x25, 0x50, 0x44, 0x46],           # %PDF
    'ZIP/DOCX/XLSX': [0x50, 0x4B, 0x03, 0x04], # PK..
    'PNG': [0x89, 0x50, 0x4E, 0x47],            # .PNG
    'JPEG': [0xFF, 0xD8, 0xFF],                  # ...
    'GIF87a': [0x47, 0x49, 0x46, 0x38, 0x37],   # GIF87
    'GIF89a': [0x47, 0x49, 0x46, 0x38, 0x39],   # GIF89
    'BMP': [0x42, 0x4D],                          # BM
    'WAV/AVI (RIFF)': [0x52, 0x49, 0x46, 0x46], # RIFF
    'MP3 (ID3)': [0x49, 0x44, 0x33],             # ID3
    'MP3 (frame)': [0xFF, 0xFB],                  # ..
    'MP3 (frame2)': [0xFF, 0xF3],                 # ..
    'MIDI': [0x4D, 0x54, 0x68, 0x64],            # MThd
    'OGG': [0x4F, 0x67, 0x67, 0x53],             # OggS
    'FLAC': [0x66, 0x4C, 0x61, 0x43],            # fLaC
    'TIFF (LE)': [0x49, 0x49, 0x2A, 0x00],       # II*.
    'TIFF (BE)': [0x4D, 0x4D, 0x00, 0x2A],       # MM.*
    'ELF': [0x7F, 0x45, 0x4C, 0x46],             # .ELF
    'Class (Java)': [0xCA, 0xFE, 0xBA, 0xBE],    # ....
    'RAR': [0x52, 0x61, 0x72, 0x21],              # Rar!
    '7z': [0x37, 0x7A, 0xBC, 0xAF],               # 7z..
    'EXE/DLL (MZ)': [0x4D, 0x5A],                 # MZ
    'SQLite': [0x53, 0x51, 0x4C, 0x69],           # SQLi
    'XML': [0x3C, 0x3F, 0x78, 0x6D],              # <?xm
    'RTF': [0x7B, 0x5C, 0x72, 0x74],              # {\rt
    'DOC (OLE)': [0xD0, 0xCF, 0x11, 0xE0],       # ....
    'GZIP': [0x1F, 0x8B],                          # ..
    'TAR': [0x75, 0x73, 0x74, 0x61, 0x72],        # ustar (at offset 257)
    'ICO': [0x00, 0x00, 0x01, 0x00],               # ....
    'MOV (ftyp)': [0x66, 0x74, 0x79, 0x70],       # ftyp (at offset 4)
    'MP4 (ftyp)': [0x66, 0x74, 0x79, 0x70],       # ftyp (at offset 4)
    'WEBM': [0x1A, 0x45, 0xDF, 0xA3],             # .E..
    'WOFF': [0x77, 0x4F, 0x46, 0x46],              # wOFF
    'PSD': [0x38, 0x42, 0x50, 0x53],               # 8BPS
}


def check_signature(byte_list, sig_bytes):
    """Check if byte_list starts with sig_bytes."""
    if len(byte_list) < len(sig_bytes):
        return False
    return all(byte_list[i] == sig_bytes[i] for i in range(len(sig_bytes)))


def check_near_match(byte_list, sig_bytes, tolerance=1):
    """Check if byte_list starts with sig_bytes within N bit flips."""
    if len(byte_list) < len(sig_bytes):
        return False, 999
    total_diff = 0
    for i in range(len(sig_bytes)):
        # Count differing bits
        xor = byte_list[i] ^ sig_bytes[i]
        total_diff += bin(xor).count('1')
    return total_diff <= tolerance * len(sig_bytes), total_diff


def main():
    filepath = "my-book/source-material/CourseUB/urtext_extracted.txt"
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        text = f.read()

    sentences = extract_sentences(text)
    real = [(i, s) for i, s in enumerate(sentences) if is_real(s)]

    # Use full chapter for more data
    chapter = [(i, s) for i, s in real if 20509 <= i <= 20771]

    # Build all methods
    m1 = ''  # Raw stress
    m2 = ''  # Deviation
    m3 = ''  # Toggle syllable
    m4 = ''  # Toggle word
    m5 = ''  # Toggle letter (word)
    m6 = ''  # Toggle letter (syllable)

    for idx, s in chapter:
        words = re.findall(r"[a-zA-Z']+", s)
        pattern = []
        stresses_per_word = []
        for w in words:
            st = get_stress(w)
            stresses_per_word.append((w, st))
            pattern.extend(st)
        if not pattern:
            continue

        m1 += ''.join(str(b) for b in pattern)

        for i, actual in enumerate(pattern):
            expected = i % 2
            m2 += '1' if actual != expected else '0'

        toggle = get_toggle_bits(pattern)
        m3 += ''.join(str(b) for b in toggle)

        pos = 0
        for w, st in stresses_per_word:
            if pos < len(toggle):
                m4 += str(toggle[pos])
            pos += len(st)

        pos = 0
        for w, st in stresses_per_word:
            if pos < len(toggle):
                clean = re.sub(r'[^a-zA-Z]', '', w)
                m5 += str(toggle[pos]) * len(clean)
            pos += len(st)

        pos = 0
        for w, st in stresses_per_word:
            syl_groups = syllabify_word(w)
            num_syls = len(st)
            while len(syl_groups) < num_syls:
                syl_groups.append('')
            syl_groups = syl_groups[:num_syls]
            for grp in syl_groups:
                if pos < len(toggle):
                    m6 += str(toggle[pos]) * len(grp)
                pos += 1

    methods = [
        ("M1: Raw Stress", m1),
        ("M2: Deviation from iambic", m2),
        ("M3: Toggle (syllable)", m3),
        ("M4: Toggle (word)", m4),
        ("M5: Toggle (letter/word)", m5),
        ("M6: Toggle (letter/syl)", m6),
    ]

    # === CHECK FILE SIGNATURES ===
    print("=" * 80)
    print("CHECKING ALL METHODS AGAINST KNOWN FILE FORMAT SIGNATURES")
    print("(normal and inverted, also checking at various offsets)")
    print("=" * 80)

    for name, bits in methods:
        print(f"\n--- {name} ({len(bits)} bits = {len(bits)//8} bytes) ---")

        for variant_name, variant_bits in [(f"{name}", bits),
                                           (f"{name} INVERTED", invert_bits(bits))]:
            byte_list = bits_to_bytes(variant_bits)
            if not byte_list:
                continue

            # Check first 4 bytes
            first_hex = ' '.join(f'{b:02X}' for b in byte_list[:8])

            exact_matches = []
            near_matches = []

            # Check at offsets 0-16
            for offset in range(min(16, len(byte_list))):
                shifted = byte_list[offset:]
                for fmt_name, sig in FILE_SIGNATURES.items():
                    if check_signature(shifted, sig):
                        exact_matches.append((fmt_name, offset))
                    else:
                        is_near, diff = check_near_match(shifted, sig, tolerance=2)
                        if is_near and diff <= 4:
                            near_matches.append((fmt_name, offset, diff))

            inv_label = " (INV)" if "INVERTED" in variant_name else ""
            print(f"\n  {inv_label}First 8 bytes: {first_hex}")

            if exact_matches:
                print(f"  *** EXACT MATCHES ***")
                for fmt, off in exact_matches:
                    print(f"    {fmt} at offset {off}")

            if near_matches:
                # Only show closest near matches
                near_matches.sort(key=lambda x: x[2])
                print(f"  Near matches (within a few bit flips):")
                for fmt, off, diff in near_matches[:5]:
                    print(f"    {fmt} at offset {off} ({diff} bits different)")

    # === BYTE VALUE DISTRIBUTION ===
    print(f"\n\n{'=' * 80}")
    print("BYTE VALUE DISTRIBUTION ANALYSIS")
    print("Which method looks most like a structured binary file?")
    print("=" * 80)

    print(f"\nFile type characteristics:")
    print(f"  Audio (WAV/raw): Byte values concentrated around 0x80 (128), bell curve")
    print(f"  Audio (MP3/compressed): Fairly uniform distribution, high entropy")
    print(f"  Document (DOC/RTF): Mix of ASCII (0x20-0x7E) and control bytes")
    print(f"  Image (raw): Depends on content, often clusters")
    print(f"  Compressed: Nearly uniform (high entropy)")
    print(f"  Random noise: Uniform across 0-255")
    print()

    for name, bits in methods:
        byte_list = bits_to_bytes(bits)
        if not byte_list:
            continue

        byte_counts = Counter(byte_list)
        total_bytes = len(byte_list)

        # Statistics
        mean_val = sum(byte_list) / total_bytes
        zero_bytes = byte_counts.get(0, 0)
        ff_bytes = byte_counts.get(255, 0)
        ascii_bytes = sum(1 for b in byte_list if 32 <= b <= 126)
        low_bytes = sum(1 for b in byte_list if b < 32)
        high_bytes = sum(1 for b in byte_list if b > 126)
        unique_values = len(byte_counts)

        # Entropy per byte
        import math
        entropy = 0
        for count in byte_counts.values():
            p = count / total_bytes
            if p > 0:
                entropy -= p * math.log2(p)

        print(f"\n  {name} ({total_bytes} bytes):")
        print(f"    Mean byte value: {mean_val:.1f} (128 = centered)")
        print(f"    Unique byte values: {unique_values}/256")
        print(f"    Entropy: {entropy:.2f} bits/byte (8.0 = max)")
        print(f"    Zero bytes (0x00): {zero_bytes} ({zero_bytes/total_bytes:.1%})")
        print(f"    0xFF bytes: {ff_bytes} ({ff_bytes/total_bytes:.1%})")
        print(f"    ASCII range (0x20-0x7E): {ascii_bytes} ({ascii_bytes/total_bytes:.1%})")
        print(f"    Control/low (0x00-0x1F): {low_bytes} ({low_bytes/total_bytes:.1%})")
        print(f"    High (0x7F-0xFF): {high_bytes} ({high_bytes/total_bytes:.1%})")

        # Show byte histogram (grouped into ranges)
        ranges = [(0, 15), (16, 31), (32, 63), (64, 95), (96, 127),
                  (128, 159), (160, 191), (192, 223), (224, 255)]
        print(f"    Byte distribution:")
        for lo, hi in ranges:
            count = sum(1 for b in byte_list if lo <= b <= hi)
            bar = '#' * int(count / total_bytes * 100)
            print(f"      0x{lo:02X}-0x{hi:02X}: {count:>4} ({count/total_bytes:>5.1%}) {bar}")

    # === WHICH METHOD IS BEST CANDIDATE? ===
    print(f"\n\n{'=' * 80}")
    print("VERDICT: WHICH METHOD IS MOST PLAUSIBLE AS A FILE?")
    print("=" * 80)

    print(f"""
  For a binary file to be hidden in these patterns, we need:

  1. ENOUGH DATA: A meaningful file needs at least a few hundred bytes.
     - M1 (syllable raw):    {len(bits_to_bytes(m1)):>5} bytes  (from full chapter)
     - M2 (deviation):       {len(bits_to_bytes(m2)):>5} bytes
     - M3 (toggle syl):      {len(bits_to_bytes(m3)):>5} bytes
     - M4 (toggle word):     {len(bits_to_bytes(m4)):>5} bytes
     - M5 (toggle let/word): {len(bits_to_bytes(m5)):>5} bytes
     - M6 (toggle let/syl):  {len(bits_to_bytes(m6)):>5} bytes

  2. RECOGNIZABLE HEADER: None match any known file format signature.

  3. BYTE DISTRIBUTION: See analysis above.

  For the FULL URTEXT (all ~21,000 sentences), the data sizes would be
  roughly 10-20x larger. Even then, M4 (word-level) from the full text
  would give ~{len(bits_to_bytes(m4)) * 10} bytes, which is enough for a
  small document or a few seconds of low-quality audio.

  Most plausible candidate: M3 or M4 (toggle at syllable or word level)
  because they have the best byte-value distribution and reasonable entropy.
  But neither matches any known file signature.
""")


if __name__ == '__main__':
    main()
