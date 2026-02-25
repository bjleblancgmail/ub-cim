"""
Full Urtext Binary Analysis - Methods M3 and M4
Processes the entire ACIM Urtext (~21,000 sentences) looking for
hidden binary data encoded in iambic stress deviation patterns.
"""

import re
import math
import struct
from collections import Counter
from iambic_scan import get_stress, STRESS_DICT

# ── Helpers ──────────────────────────────────────────────────────────────────

def extract_sentences(text):
    """Split text into sentences on .!? followed by whitespace."""
    text = text.replace('\t', ' ')
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]


def is_real_sentence(s):
    """Filter: 3+ words, 70%+ alphabetic characters."""
    words = re.findall(r"[a-zA-Z']+", s)
    if len(words) < 3:
        return False
    alpha_chars = sum(1 for c in s if c.isalpha())
    total_chars = len(s)
    if total_chars == 0:
        return False
    return (alpha_chars / total_chars) >= 0.70


def get_sentence_words(s):
    """Extract alphabetic words from a sentence."""
    return re.findall(r"[a-zA-Z']+", s)


def hamming_distance_bytes(a, b):
    """Count bit differences between two byte sequences."""
    total = 0
    for x, y in zip(a, b):
        diff = x ^ y
        total += bin(diff).count('1')
    return total


def shannon_entropy(data):
    """Compute Shannon entropy of a byte sequence (bits per byte)."""
    if not data:
        return 0.0
    freq = Counter(data)
    length = len(data)
    entropy = 0.0
    for count in freq.values():
        p = count / length
        if p > 0:
            entropy -= p * math.log2(p)
    return entropy


def bits_to_bytes(bits):
    """Convert a list of bits to bytes (MSB first). Pads last byte with 0s."""
    result = bytearray()
    for i in range(0, len(bits), 8):
        chunk = bits[i:i+8]
        # Pad with zeros if needed
        while len(chunk) < 8:
            chunk.append(0)
        byte_val = 0
        for bit in chunk:
            byte_val = (byte_val << 1) | bit
        result.append(byte_val)
    return bytes(result)


# ── M3: Toggle at syllable level ────────────────────────────────────────────

def method_m3(sentences):
    """
    Walk through each syllable in each sentence.
    Compare actual stress to expected iambic position (0,1,0,1,...).
    Maintain toggle state (starts at 0). Flip on deviation.
    Output one bit per syllable.
    """
    all_bits = []
    for sent in sentences:
        words = get_sentence_words(sent)
        if not words:
            continue
        # Build full stress pattern for the sentence
        syllable_stresses = []
        for w in words:
            stress = get_stress(w)
            syllable_stresses.extend(stress)

        toggle = 0
        for pos, actual in enumerate(syllable_stresses):
            expected = pos % 2  # iambic: 0,1,0,1,...
            if actual != expected:
                toggle = 1 - toggle
            all_bits.append(toggle)
    return all_bits


# ── M4: Toggle at word level ────────────────────────────────────────────────

def method_m4(sentences):
    """
    Same toggle logic as M3, but output one bit per WORD
    (the toggle state at the word's first syllable position).
    """
    all_bits = []
    for sent in sentences:
        words = get_sentence_words(sent)
        if not words:
            continue

        toggle = 0
        pos = 0  # syllable position in sentence
        for w in words:
            stress = get_stress(w)
            word_first_pos = pos
            for i, actual in enumerate(stress):
                expected = (pos + i) % 2
                if actual != expected:
                    toggle = 1 - toggle
            # Output bit for this word = toggle state at word's first syllable
            # Actually: output the toggle state AFTER processing the word
            # But spec says "toggle state at the word's first syllable position"
            # We need toggle state when we reach the word's first syllable.
            # Let me re-read: "output one bit per WORD (the toggle state at the word's first syllable position)"
            # This means: snapshot the toggle at the start of the word, then process.
            # Let me redo with snapshot before processing.
            pos += len(stress)

        # Redo properly: snapshot toggle before each word
        toggle = 0
        pos = 0
        for w in words:
            stress = get_stress(w)
            # Snapshot toggle state at word's first syllable
            word_bit = toggle
            for i, actual in enumerate(stress):
                expected = (pos + i) % 2
                if actual != expected:
                    toggle = 1 - toggle
            all_bits.append(word_bit)
            pos += len(stress)

    return all_bits


# ── Signature scanning ──────────────────────────────────────────────────────

SIGNATURES = {
    'PDF':       bytes([0x25, 0x50, 0x44, 0x46]),
    'ZIP':       bytes([0x50, 0x4B, 0x03, 0x04]),
    'PNG':       bytes([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A]),
    'JPEG':      bytes([0xFF, 0xD8, 0xFF]),
    'GIF':       bytes([0x47, 0x49, 0x46, 0x38]),
    'BMP':       bytes([0x42, 0x4D]),
    'WAV/RIFF':  bytes([0x52, 0x49, 0x46, 0x46]),
    'MP3 ID3':   bytes([0x49, 0x44, 0x33]),
    'MP3 frame (FB)': bytes([0xFF, 0xFB]),
    'MP3 frame (F3)': bytes([0xFF, 0xF3]),
    'MIDI':      bytes([0x4D, 0x54, 0x68, 0x64]),
    'OGG':       bytes([0x4F, 0x67, 0x67, 0x53]),
    'GZIP':      bytes([0x1F, 0x8B]),
    'DOC OLE':   bytes([0xD0, 0xCF, 0x11, 0xE0]),
    'RTF':       bytes([0x7B, 0x5C, 0x72, 0x74]),
    'EXE MZ':    bytes([0x4D, 0x5A]),
    'SQLite':    bytes([0x53, 0x51, 0x4C, 0x69]),
}


def scan_signatures(data, label):
    """Scan byte data for file format signatures with fuzzy matching."""
    print(f"\n  [{label}] Signature scan ({len(data)} bytes):")
    found_any = False
    for name, sig in SIGNATURES.items():
        sig_len = len(sig)
        # For 2-byte sigs, only exact match. For 3+ byte sigs, up to 4 bit flips.
        max_flips = 0 if sig_len <= 2 else 4
        matches = []
        for offset in range(len(data) - sig_len + 1):
            window = data[offset:offset + sig_len]
            dist = hamming_distance_bytes(sig, window)
            if dist <= max_flips:
                matches.append((offset, dist))
        if matches:
            found_any = True
            if len(matches) <= 20:
                for offset, dist in matches:
                    hex_at = ' '.join(f'{b:02X}' for b in data[offset:offset+sig_len])
                    print(f"    {name} at offset {offset} ({dist} bit flips) [{hex_at}]")
            else:
                print(f"    {name}: {len(matches)} matches (showing first 10, last 5)")
                for offset, dist in matches[:10]:
                    hex_at = ' '.join(f'{b:02X}' for b in data[offset:offset+sig_len])
                    print(f"      offset {offset} ({dist} bit flips) [{hex_at}]")
                print(f"      ...")
                for offset, dist in matches[-5:]:
                    hex_at = ' '.join(f'{b:02X}' for b in data[offset:offset+sig_len])
                    print(f"      offset {offset} ({dist} bit flips) [{hex_at}]")
    if not found_any:
        print("    No signatures found.")


# ── Entropy mapping ─────────────────────────────────────────────────────────

def entropy_mapping(data, label, window_size=256):
    """Divide into windows, compute entropy per window."""
    print(f"\n  [{label}] Entropy mapping (window={window_size} bytes):")
    if len(data) < window_size:
        e = shannon_entropy(data)
        print(f"    Data too short for windowing. Overall entropy: {e:.4f}")
        return

    entropies = []
    for i in range(0, len(data) - window_size + 1, window_size):
        window = data[i:i+window_size]
        e = shannon_entropy(window)
        entropies.append((i, e))

    vals = [e for _, e in entropies]
    min_e = min(vals)
    max_e = max(vals)
    mean_e = sum(vals) / len(vals)

    print(f"    Windows: {len(entropies)}")
    print(f"    Min entropy: {min_e:.4f} bits/byte")
    print(f"    Max entropy: {max_e:.4f} bits/byte")
    print(f"    Mean entropy: {mean_e:.4f} bits/byte")

    low_windows = [(off, e) for off, e in entropies if e < 6.5]
    if low_windows:
        print(f"    LOW ENTROPY WINDOWS (< 6.5): {len(low_windows)}")
        for off, e in low_windows[:30]:
            print(f"      Offset {off}: {e:.4f} bits/byte")
        if len(low_windows) > 30:
            print(f"      ... and {len(low_windows) - 30} more")
    else:
        print("    No windows below 6.5 bits/byte threshold.")


# ── Byte distribution ───────────────────────────────────────────────────────

def byte_distribution(data, label):
    """Overall byte stats."""
    print(f"\n  [{label}] Byte distribution:")
    e = shannon_entropy(data)
    unique = len(set(data))
    mean_val = sum(data) / len(data) if data else 0
    print(f"    Overall entropy: {e:.4f} bits/byte")
    print(f"    Unique byte values: {unique}/256")
    print(f"    Mean byte value: {mean_val:.2f}")

    # Show top 10 most common bytes
    freq = Counter(data)
    print(f"    Top 10 most common bytes:")
    for val, count in freq.most_common(10):
        pct = 100 * count / len(data)
        print(f"      0x{val:02X} ({val:3d}): {count} ({pct:.2f}%)")


# ── Text detection ──────────────────────────────────────────────────────────

def text_detection(data, label, window_size=64):
    """Slide window looking for printable ASCII regions."""
    print(f"\n  [{label}] Text detection (window={window_size}):")
    found = []
    for offset in range(len(data) - window_size + 1):
        window = data[offset:offset + window_size]
        printable = sum(1 for b in window if 32 <= b <= 126)
        pct = printable / window_size
        if pct >= 0.70:
            # Decode as ASCII, replacing non-printable with '.'
            text = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in window)
            found.append((offset, pct, text))

    if found:
        # Collapse overlapping windows, just show distinct regions
        print(f"    Found {len(found)} windows with 70%+ printable ASCII")
        # Show first 20 unique starting offsets
        shown = 0
        last_shown = -100
        for offset, pct, text in found:
            if offset - last_shown < window_size // 2:
                continue
            print(f"      Offset {offset} ({pct:.0%}): {text[:80]}")
            last_shown = offset
            shown += 1
            if shown >= 20:
                remaining = sum(1 for o, _, _ in found if o > offset and o - last_shown >= window_size // 2)
                if remaining > 0:
                    print(f"      ... and more regions")
                break
    else:
        print("    No windows with 70%+ printable ASCII found.")


# ── Repeating structure detection ───────────────────────────────────────────

def repeating_structure(data, label):
    """Find common 2-byte and 4-byte sequences and check for periodicity."""
    print(f"\n  [{label}] Repeating structure detection:")

    # 2-byte sequences
    seq2 = Counter()
    for i in range(len(data) - 1):
        seq2[data[i:i+2]] += 1

    print(f"    Top 10 most common 2-byte sequences:")
    for seq, count in seq2.most_common(10):
        hex_str = ' '.join(f'{b:02X}' for b in seq)
        pct = 100 * count / (len(data) - 1) if len(data) > 1 else 0
        print(f"      [{hex_str}]: {count} ({pct:.3f}%)")

    # 4-byte sequences
    if len(data) >= 4:
        seq4 = Counter()
        for i in range(len(data) - 3):
            seq4[data[i:i+4]] += 1

        print(f"    Top 10 most common 4-byte sequences:")
        for seq, count in seq4.most_common(10):
            hex_str = ' '.join(f'{b:02X}' for b in seq)
            pct = 100 * count / (len(data) - 3)
            print(f"      [{hex_str}]: {count} ({pct:.3f}%)")

    # Check for periodicity in top 2-byte sequence
    top_seq, top_count = seq2.most_common(1)[0]
    if top_count >= 10:
        positions = []
        for i in range(len(data) - 1):
            if data[i:i+2] == top_seq:
                positions.append(i)

        if len(positions) >= 2:
            gaps = [positions[i+1] - positions[i] for i in range(len(positions)-1)]
            gap_counter = Counter(gaps)
            most_common_gap, gap_count = gap_counter.most_common(1)[0]
            hex_str = ' '.join(f'{b:02X}' for b in top_seq)
            print(f"    Periodicity check for [{hex_str}] ({top_count} occurrences):")
            print(f"      Most common gap: {most_common_gap} bytes ({gap_count} times)")
            print(f"      Top 5 gaps: {gap_counter.most_common(5)}")
            regularity = gap_count / len(gaps) if gaps else 0
            if regularity > 0.3:
                print(f"      ** POTENTIAL PERIODIC STRUCTURE: {regularity:.1%} of gaps = {most_common_gap} **")


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    import time

    filepath = "my-book/source-material/CourseUB/urtext_extracted.txt"
    print(f"Reading {filepath}...")
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        text = f.read()
    print(f"  File size: {len(text):,} characters")

    print("Extracting sentences...")
    raw_sentences = extract_sentences(text)
    print(f"  Raw sentences: {len(raw_sentences):,}")

    sentences = [s for s in raw_sentences if is_real_sentence(s)]
    print(f"  Filtered (real) sentences: {len(sentences):,}")

    # ── Process M3 ──
    print("\nProcessing M3 (toggle, syllable level)...")
    t0 = time.time()
    m3_bits = method_m3(sentences)
    t1 = time.time()
    m3_bytes = bits_to_bytes(m3_bits)
    print(f"  Done in {t1-t0:.1f}s")
    print(f"  Total bits: {len(m3_bits):,}")
    print(f"  Total bytes: {len(m3_bytes):,}")

    # ── Process M4 ──
    print("\nProcessing M4 (toggle, word level)...")
    t0 = time.time()
    m4_bits = method_m4(sentences)
    t1 = time.time()
    m4_bytes = bits_to_bytes(m4_bits)
    print(f"  Done in {t1-t0:.1f}s")
    print(f"  Total bits: {len(m4_bits):,}")
    print(f"  Total bytes: {len(m4_bytes):,}")

    # ── Save binary files ──
    with open('m3_full.bin', 'wb') as f:
        f.write(m3_bytes)
    print(f"\nSaved m3_full.bin ({len(m3_bytes):,} bytes)")

    with open('m4_full.bin', 'wb') as f:
        f.write(m4_bytes)
    print(f"Saved m4_full.bin ({len(m4_bytes):,} bytes)")

    # ── Inverted versions ──
    m3_inv_bits = [1 - b for b in m3_bits]
    m4_inv_bits = [1 - b for b in m4_bits]
    m3_inv_bytes = bits_to_bytes(m3_inv_bits)
    m4_inv_bytes = bits_to_bytes(m4_inv_bits)

    # ══════════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 70)
    print("SECTION B: SIGNATURE SCANNING (fuzzy matching)")
    print("=" * 70)

    for data, label in [
        (m3_bytes, "M3"),
        (m4_bytes, "M4"),
        (m3_inv_bytes, "M3-inverted"),
        (m4_inv_bytes, "M4-inverted"),
    ]:
        scan_signatures(data, label)

    # ══════════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 70)
    print("SECTION C: ENTROPY MAPPING")
    print("=" * 70)

    for data, label in [
        (m3_bytes, "M3"),
        (m4_bytes, "M4"),
    ]:
        entropy_mapping(data, label)

    # ══════════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 70)
    print("SECTION D: BYTE DISTRIBUTION")
    print("=" * 70)

    for data, label in [
        (m3_bytes, "M3"),
        (m4_bytes, "M4"),
    ]:
        byte_distribution(data, label)

    # ══════════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 70)
    print("SECTION E: TEXT DETECTION")
    print("=" * 70)

    for data, label in [
        (m3_bytes, "M3"),
        (m4_bytes, "M4"),
        (m3_inv_bytes, "M3-inverted"),
        (m4_inv_bytes, "M4-inverted"),
    ]:
        text_detection(data, label)

    # ══════════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 70)
    print("SECTION F: REPEATING STRUCTURE DETECTION")
    print("=" * 70)

    for data, label in [
        (m3_bytes, "M3"),
        (m4_bytes, "M4"),
    ]:
        repeating_structure(data, label)

    # ══════════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)

    # Quick summary
    print(f"\nSummary:")
    print(f"  Sentences processed: {len(sentences):,}")
    print(f"  M3: {len(m3_bits):,} bits -> {len(m3_bytes):,} bytes (m3_full.bin)")
    print(f"  M4: {len(m4_bits):,} bits -> {len(m4_bytes):,} bytes (m4_full.bin)")
    print(f"  M3 entropy: {shannon_entropy(m3_bytes):.4f} bits/byte")
    print(f"  M4 entropy: {shannon_entropy(m4_bytes):.4f} bits/byte")

    # Bit balance
    m3_ones = sum(m3_bits)
    m4_ones = sum(m4_bits)
    print(f"  M3 bit balance: {m3_ones} ones / {len(m3_bits)-m3_ones} zeros ({100*m3_ones/len(m3_bits):.1f}% ones)")
    print(f"  M4 bit balance: {m4_ones} ones / {len(m4_bits)-m4_ones} zeros ({100*m4_ones/len(m4_bits):.1f}% ones)")


if __name__ == '__main__':
    main()
