#!/usr/bin/env python3
"""
Deep Pattern Analysis of ACIM Urtext Stress Pattern Binary Files
Analyzes m3_full.bin (syllable-level) and m4_full.bin (word-level)
plus their bitwise-inverted versions.
"""

import os
import math
import struct
import collections
import numpy as np
from pathlib import Path

BASE_DIR = Path(r"C:\Alpha\UB-CIM (non fiction Author)")

# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def entropy(data):
    """Shannon entropy of a byte sequence."""
    if not data:
        return 0.0
    counts = collections.Counter(data)
    total = len(data)
    ent = 0.0
    for c in counts.values():
        p = c / total
        if p > 0:
            ent -= p * math.log2(p)
    return ent


def invert_bytes(data):
    """Bitwise invert every byte."""
    return bytes(b ^ 0xFF for b in data)


def hex_dump(data, max_bytes=64):
    """Return a hex dump string."""
    hex_str = ' '.join(f'{b:02X}' for b in data[:max_bytes])
    ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in data[:max_bytes])
    return f"{hex_str}  |{ascii_str}|"


def print_separator(char='=', length=80):
    print(char * length)


# ============================================================
# 1. BINWALK-STYLE DEEP SIGNATURE SCAN
# ============================================================

BINARY_SIGNATURES = {
    "PDF":          bytes([0x25, 0x50, 0x44, 0x46]),
    "ZIP":          bytes([0x50, 0x4B, 0x03, 0x04]),
    "ZIP end":      bytes([0x50, 0x4B, 0x05, 0x06]),
    "PNG":          bytes([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A]),
    "JPEG SOI E0":  bytes([0xFF, 0xD8, 0xFF, 0xE0]),
    "JPEG SOI E1":  bytes([0xFF, 0xD8, 0xFF, 0xE1]),
    "JPEG SOI DB":  bytes([0xFF, 0xD8, 0xFF, 0xDB]),
    "GIF87a":       bytes([0x47, 0x49, 0x46, 0x38, 0x37, 0x61]),
    "GIF89a":       bytes([0x47, 0x49, 0x46, 0x38, 0x39, 0x61]),
    "BMP":          bytes([0x42, 0x4D]),
    "RIFF":         bytes([0x52, 0x49, 0x46, 0x46]),
    "MP3 ID3":      bytes([0x49, 0x44, 0x33]),
    "MIDI":         bytes([0x4D, 0x54, 0x68, 0x64]),
    "OGG":          bytes([0x4F, 0x67, 0x67, 0x53]),
    "FLAC":         bytes([0x66, 0x4C, 0x61, 0x43]),
    "GZIP":         bytes([0x1F, 0x8B, 0x08]),
    "BZIP2":        bytes([0x42, 0x5A, 0x68]),
    "XZ":           bytes([0xFD, 0x37, 0x7A, 0x58, 0x5A, 0x00]),
    "LZMA":         bytes([0x5D, 0x00, 0x00]),
    "7z":           bytes([0x37, 0x7A, 0xBC, 0xAF, 0x27, 0x1C]),
    "RAR":          bytes([0x52, 0x61, 0x72, 0x21, 0x1A, 0x07]),
    "TAR ustar":    bytes([0x75, 0x73, 0x74, 0x61, 0x72]),
    "EXE MZ":       bytes([0x4D, 0x5A]),
    "ELF":          bytes([0x7F, 0x45, 0x4C, 0x46]),
    "Mach-O LE32":  bytes([0xFE, 0xED, 0xFA, 0xCE]),
    "Mach-O LE64":  bytes([0xFE, 0xED, 0xFA, 0xCF]),
    "Mach-O BE64":  bytes([0xCF, 0xFA, 0xED, 0xFE]),
    "Mach-O BE32":  bytes([0xCE, 0xFA, 0xED, 0xFE]),
    "Java Class":   bytes([0xCA, 0xFE, 0xBA, 0xBE]),
    "SQLite":       bytes([0x53, 0x51, 0x4C, 0x69, 0x74, 0x65]),
    "RTF":          bytes([0x7B, 0x5C, 0x72, 0x74, 0x66]),
    "DOC OLE":      bytes([0xD0, 0xCF, 0x11, 0xE0, 0xA1, 0xB1, 0x1A, 0xE1]),
    "XML":          bytes([0x3C, 0x3F, 0x78, 0x6D, 0x6C]),
    "HTML lower":   bytes([0x3C, 0x68, 0x74, 0x6D, 0x6C]),
    "HTML upper":   bytes([0x3C, 0x48, 0x54, 0x4D, 0x4C]),
    "WASM":         bytes([0x00, 0x61, 0x73, 0x6D]),
    "EBML/WEBM":    bytes([0x1A, 0x45, 0xDF, 0xA3]),
    "TIFF LE":      bytes([0x49, 0x49, 0x2A, 0x00]),
    "TIFF BE":      bytes([0x4D, 0x4D, 0x00, 0x2A]),
    "PSD":          bytes([0x38, 0x42, 0x50, 0x53]),
    "ICO":          bytes([0x00, 0x00, 0x01, 0x00]),
    "ftyp":         b'ftyp',
    "WOFF":         bytes([0x77, 0x4F, 0x46, 0x46]),
    "WOFF2":        bytes([0x77, 0x4F, 0x46, 0x32]),
    "PostScript":   bytes([0x25, 0x21, 0x50, 0x53]),
}

TEXT_PATTERNS = {
    "PK (ZIP)":     b'PK',
    "JFIF":         b'JFIF',
    "Exif":         b'Exif',
    "IHDR (PNG)":   b'IHDR',
    "IDAT (PNG)":   b'IDAT',
    "IEND (PNG)":   b'IEND',
    "ftyp (MP4)":   b'ftyp',
    "moov (MP4)":   b'moov',
    "mdat (MP4)":   b'mdat',
    "<!DOCTYPE":    b'<!DOCTYPE',
    "<?xml":        b'<?xml',
}


def scan_signatures(data, label):
    print(f"\n{'='*80}")
    print(f"  1. BINWALK-STYLE SIGNATURE SCAN: {label}")
    print(f"{'='*80}")

    found_any = False

    print("\n  --- Binary Signatures ---")
    for name, sig in BINARY_SIGNATURES.items():
        sig_len = len(sig)
        offset = 0
        while offset <= len(data) - sig_len:
            idx = data.find(sig, offset)
            if idx == -1:
                break
            print(f"  [MATCH] {name} at offset {idx} (0x{idx:06X})")
            found_any = True
            offset = idx + 1

    # Special check: TAR ustar at offset 257 from any position
    print("\n  --- TAR ustar check (signature at +257 from block start) ---")
    for block_start in range(0, len(data) - 262, 512):
        check_offset = block_start + 257
        if check_offset + 5 <= len(data):
            if data[check_offset:check_offset+5] == b'ustar':
                print(f"  [MATCH] TAR ustar at block offset {block_start}, sig at {check_offset}")
                found_any = True

    print("\n  --- Text Pattern Signatures ---")
    for name, pat in TEXT_PATTERNS.items():
        pat_len = len(pat)
        offset = 0
        while offset <= len(data) - pat_len:
            idx = data.find(pat, offset)
            if idx == -1:
                break
            context_start = max(0, idx - 4)
            context_end = min(len(data), idx + pat_len + 4)
            context = hex_dump(data[context_start:context_end], 32)
            print(f"  [MATCH] {name} at offset {idx} (0x{idx:06X})  context: {context}")
            found_any = True
            offset = idx + 1

    if not found_any:
        print("  No signatures found.")


# ============================================================
# 2. N-GRAM FREQUENCY ANALYSIS
# ============================================================

def ngram_analysis(data, label):
    print(f"\n{'='*80}")
    print(f"  2. N-GRAM FREQUENCY ANALYSIS: {label}")
    print(f"{'='*80}")
    total = len(data)

    # Bigrams
    print(f"\n  --- Bigram (2-byte) Analysis ---")
    bigrams = collections.Counter()
    for i in range(total - 1):
        bigrams[data[i:i+2]] += 1
    total_bigrams = sum(bigrams.values())
    expected_per_bigram = total_bigrams / (256 * 256)
    print(f"  Total bigrams: {total_bigrams}")
    print(f"  Unique bigrams: {len(bigrams)} out of {256*256} possible")
    print(f"  Expected per bigram (uniform): {expected_per_bigram:.4f}")

    top20 = bigrams.most_common(20)
    print(f"\n  Top 20 most frequent bigrams:")
    for bg, count in top20:
        print(f"    {bg.hex().upper():>4s}  count={count:>5d}  ({count/total_bigrams*100:.3f}%)")

    bottom20 = bigrams.most_common()[-20:]
    print(f"\n  Bottom 20 least frequent bigrams:")
    for bg, count in bottom20:
        print(f"    {bg.hex().upper():>4s}  count={count:>5d}")

    # Chi-squared for bigrams
    chi2 = 0.0
    # Include zero-count bigrams
    observed_set = set(bigrams.keys())
    for bg, count in bigrams.items():
        chi2 += (count - expected_per_bigram) ** 2 / expected_per_bigram
    # Add contributions from bigrams that never appeared
    zero_count_bigrams = 256 * 256 - len(bigrams)
    chi2 += zero_count_bigrams * (expected_per_bigram ** 2 / expected_per_bigram)
    # simplify: zero_count * expected_per_bigram
    # Wait, (0 - E)^2 / E = E
    chi2_corrected = 0.0
    for bg, count in bigrams.items():
        chi2_corrected += (count - expected_per_bigram) ** 2 / expected_per_bigram
    chi2_corrected += zero_count_bigrams * expected_per_bigram
    dof = 256 * 256 - 1
    print(f"\n  Chi-squared statistic: {chi2_corrected:.2f}")
    print(f"  Degrees of freedom: {dof}")
    print(f"  Chi-squared / DOF: {chi2_corrected / dof:.4f}")
    print(f"  (For uniform random data, chi2/dof should be ~1.0)")

    # Trigrams
    print(f"\n  --- Trigram (3-byte) Analysis ---")
    trigrams = collections.Counter()
    for i in range(total - 2):
        trigrams[data[i:i+3]] += 1
    total_trigrams = sum(trigrams.values())
    expected_tri = total_trigrams / (256 ** 3)
    print(f"  Total trigrams: {total_trigrams}")
    print(f"  Unique trigrams: {len(trigrams)} out of {256**3} possible")
    print(f"  Expected per trigram (uniform): {expected_tri:.6f}")

    top20_tri = trigrams.most_common(20)
    print(f"\n  Top 20 most frequent trigrams:")
    for tg, count in top20_tri:
        print(f"    {tg.hex().upper():>6s}  count={count:>4d}  ({count/total_trigrams*100:.4f}%)")

    # 4-grams
    print(f"\n  --- 4-gram (4-byte) Analysis ---")
    fourgrams = collections.Counter()
    for i in range(total - 3):
        fourgrams[data[i:i+4]] += 1
    total_4g = sum(fourgrams.values())
    expected_4g = total_4g / (256 ** 4)
    print(f"  Total 4-grams: {total_4g}")
    print(f"  Unique 4-grams: {len(fourgrams)} out of {256**4} possible")
    print(f"  Expected per 4-gram (uniform): {expected_4g:.8f}")

    top20_4g = fourgrams.most_common(20)
    print(f"\n  Top 20 most frequent 4-grams:")
    for fg, count in top20_4g:
        print(f"    {fg.hex().upper():>8s}  count={count:>4d}  ({count/total_4g*100:.4f}%)")


# ============================================================
# 3. PERIODIC STRUCTURE DETECTION
# ============================================================

def periodic_structure(data, label):
    print(f"\n{'='*80}")
    print(f"  3. PERIODIC STRUCTURE DETECTION: {label}")
    print(f"{'='*80}")
    total = len(data)

    print(f"\n  --- Periodic Entropy (periods 2-1000) ---")
    print(f"  Checking entropy of every Pth byte (flagging if < 6.0)...")
    low_entropy_periods = []
    for p in range(2, 1001):
        subset = data[::p]
        if len(subset) < 10:
            continue
        ent = entropy(subset)
        if ent < 6.0:
            low_entropy_periods.append((p, ent, len(subset)))

    if low_entropy_periods:
        print(f"\n  Periods with entropy < 6.0:")
        for p, ent, n in sorted(low_entropy_periods, key=lambda x: x[1]):
            print(f"    Period {p:>5d}: entropy = {ent:.4f}  (sample size = {n})")
    else:
        print("  No periods found with entropy < 6.0")

    # Autocorrelation
    print(f"\n  --- Autocorrelation (lags 1-500) ---")
    arr = np.frombuffer(data, dtype=np.uint8).astype(np.float64)
    mean = arr.mean()
    arr_centered = arr - mean
    var = np.sum(arr_centered ** 2)
    if var == 0:
        print("  Variance is zero, cannot compute autocorrelation.")
        return

    significant_lags = []
    max_lag = min(500, total - 1)
    for lag in range(1, max_lag + 1):
        corr = np.sum(arr_centered[:total-lag] * arr_centered[lag:]) / var
        if abs(corr) > 0.1:
            significant_lags.append((lag, corr))

    if significant_lags:
        print(f"  Lags with |correlation| > 0.1:")
        for lag, corr in significant_lags[:50]:  # limit output
            print(f"    Lag {lag:>4d}: correlation = {corr:.6f}")
        if len(significant_lags) > 50:
            print(f"    ... and {len(significant_lags)-50} more")
    else:
        print("  No lags with |correlation| > 0.1 found.")

    # Also report top 10 autocorrelation peaks
    print(f"\n  --- Top 10 Autocorrelation Peaks (lags 1-500) ---")
    all_corrs = []
    for lag in range(1, max_lag + 1):
        corr = np.sum(arr_centered[:total-lag] * arr_centered[lag:]) / var
        all_corrs.append((lag, corr))
    all_corrs.sort(key=lambda x: abs(x[1]), reverse=True)
    for lag, corr in all_corrs[:10]:
        print(f"    Lag {lag:>4d}: correlation = {corr:.6f}")


# ============================================================
# 4. BLOCK-LEVEL ENTROPY HEATMAP
# ============================================================

def block_entropy(data, label, block_size=64):
    print(f"\n{'='*80}")
    print(f"  4. BLOCK-LEVEL ENTROPY (block_size={block_size}): {label}")
    print(f"{'='*80}")
    total = len(data)
    num_blocks = total // block_size

    entropies = []
    for i in range(num_blocks):
        block = data[i*block_size:(i+1)*block_size]
        ent = entropy(block)
        entropies.append((i, ent))

    # Overall stats
    ent_values = [e for _, e in entropies]
    print(f"\n  Total blocks: {num_blocks}")
    print(f"  Entropy range: {min(ent_values):.4f} to {max(ent_values):.4f}")
    print(f"  Mean entropy: {np.mean(ent_values):.4f}")
    print(f"  Std entropy: {np.std(ent_values):.4f}")

    # Lowest 20 entropy blocks
    sorted_ent = sorted(entropies, key=lambda x: x[1])
    print(f"\n  20 Lowest Entropy Blocks:")
    for idx, ent_val in sorted_ent[:20]:
        offset = idx * block_size
        block = data[offset:offset+block_size]
        print(f"    Block {idx:>5d} (offset {offset:>6d} / 0x{offset:06X}): entropy = {ent_val:.4f}")
        print(f"      {hex_dump(block, 64)}")

    # Runs of 3+ consecutive blocks below 7.0
    print(f"\n  Runs of 3+ consecutive blocks with entropy < 7.0:")
    in_run = False
    run_start = 0
    run_count = 0
    runs = []
    for idx, ent_val in entropies:
        if ent_val < 7.0:
            if not in_run:
                run_start = idx
                run_count = 1
                in_run = True
            else:
                run_count += 1
        else:
            if in_run and run_count >= 3:
                runs.append((run_start, run_count))
            in_run = False
            run_count = 0
    if in_run and run_count >= 3:
        runs.append((run_start, run_count))

    if runs:
        for rs, rc in runs:
            offset_s = rs * block_size
            offset_e = (rs + rc) * block_size
            block_ents = [entropies[rs+i][1] for i in range(rc)]
            avg_ent = np.mean(block_ents)
            print(f"    Blocks {rs}-{rs+rc-1} (offsets {offset_s}-{offset_e}): "
                  f"{rc} blocks, avg entropy = {avg_ent:.4f}")
    else:
        print("    None found.")


# ============================================================
# 5. BYTE TRANSITION MATRIX
# ============================================================

def transition_matrix(data, label):
    print(f"\n{'='*80}")
    print(f"  5. BYTE TRANSITION MATRIX: {label}")
    print(f"{'='*80}")
    total = len(data)

    matrix = np.zeros((256, 256), dtype=np.int64)
    for i in range(total - 1):
        matrix[data[i]][data[i+1]] += 1

    total_transitions = total - 1
    expected = total_transitions / (256 * 256)

    # Top 20 transitions
    flat = []
    for i in range(256):
        for j in range(256):
            if matrix[i][j] > 0:
                flat.append((i, j, matrix[i][j]))
    flat.sort(key=lambda x: x[2], reverse=True)

    print(f"\n  Total transitions: {total_transitions}")
    print(f"  Expected per transition (uniform): {expected:.4f}")
    print(f"  Non-zero transitions: {len(flat)} out of {256*256}")

    print(f"\n  Top 20 Most Common Transitions:")
    for a, b, count in flat[:20]:
        ratio = count / expected
        print(f"    0x{a:02X} -> 0x{b:02X}  count={count:>5d}  ({ratio:.1f}x expected)")

    # Most suspiciously frequent (highest ratio)
    print(f"\n  Top 20 Most Over-Represented Transitions (vs random):")
    flat_ratio = [(a, b, c, c/expected) for a, b, c in flat if c > 5]
    flat_ratio.sort(key=lambda x: x[3], reverse=True)
    for a, b, count, ratio in flat_ratio[:20]:
        print(f"    0x{a:02X} -> 0x{b:02X}  count={count:>5d}  ({ratio:.1f}x expected)")

    # Check for always/never follows patterns
    print(f"\n  Checking for deterministic transitions (byte A ALWAYS followed by byte B):")
    # For each byte value that appears, check if it always leads to the same next byte
    byte_counts = collections.Counter(data[:-1])  # exclude last byte
    deterministic = []
    for a in range(256):
        if byte_counts[a] < 5:  # need at least 5 occurrences
            continue
        successors = matrix[a]
        nonzero = np.count_nonzero(successors)
        if nonzero == 1:
            b = np.argmax(successors)
            deterministic.append((a, b, byte_counts[a]))

    if deterministic:
        for a, b, cnt in deterministic[:20]:
            print(f"    0x{a:02X} ALWAYS -> 0x{b:02X}  ({cnt} occurrences)")
    else:
        print("    None found (no byte always followed by exactly one other byte).")

    # Check for bytes that are NEVER followed by certain common bytes
    print(f"\n  Checking for absent transitions among common bytes:")
    common_bytes = [b for b, c in collections.Counter(data).most_common(16)]
    absent = []
    for a in common_bytes:
        for b in common_bytes:
            if matrix[a][b] == 0 and byte_counts.get(a, 0) > 50:
                absent.append((a, b))
    if absent:
        for a, b in absent[:20]:
            print(f"    0x{a:02X} -> 0x{b:02X}  NEVER occurs (0x{a:02X} appears {byte_counts[a]} times)")
    else:
        print("    None found among top 16 byte values.")


# ============================================================
# 6. RUN LENGTH ANALYSIS
# ============================================================

def run_length_analysis(data, label):
    print(f"\n{'='*80}")
    print(f"  6. RUN LENGTH ANALYSIS: {label}")
    print(f"{'='*80}")
    total = len(data)

    runs = []  # (value, length, offset)
    if total == 0:
        print("  Empty data.")
        return

    current_val = data[0]
    current_len = 1
    current_off = 0

    for i in range(1, total):
        if data[i] == current_val:
            current_len += 1
        else:
            runs.append((current_val, current_len, current_off))
            current_val = data[i]
            current_len = 1
            current_off = i
    runs.append((current_val, current_len, current_off))

    # Longest run
    longest = max(runs, key=lambda x: x[1])
    print(f"\n  Longest run: value=0x{longest[0]:02X}, length={longest[1]}, offset={longest[2]}")

    # Runs of 4+ identical bytes
    long_runs = [(v, l, o) for v, l, o in runs if l >= 4]
    print(f"\n  Runs of 4+ identical bytes: {len(long_runs)} found")
    if long_runs:
        long_runs.sort(key=lambda x: x[1], reverse=True)
        for v, l, o in long_runs[:30]:
            print(f"    Offset {o:>6d} (0x{o:06X}): 0x{v:02X} x {l}")
        if len(long_runs) > 30:
            print(f"    ... and {len(long_runs)-30} more")

    # Run length distribution
    print(f"\n  Run Length Distribution:")
    len_counts = collections.Counter(l for _, l, _ in runs)
    for length in sorted(len_counts.keys()):
        if length <= 10 or len_counts[length] > 1:
            print(f"    Length {length:>4d}: {len_counts[length]:>6d} runs")


# ============================================================
# 7. ASCII STRING EXTRACTION
# ============================================================

def extract_strings(data, label, min_len=4):
    print(f"\n{'='*80}")
    print(f"  7. ASCII STRING EXTRACTION (min length {min_len}): {label}")
    print(f"{'='*80}")

    strings = []
    current = []
    start_offset = 0

    for i, b in enumerate(data):
        if 0x20 <= b <= 0x7E:
            if not current:
                start_offset = i
            current.append(chr(b))
        else:
            if len(current) >= min_len:
                strings.append((start_offset, ''.join(current)))
            current = []

    # Don't forget last run
    if len(current) >= min_len:
        strings.append((start_offset, ''.join(current)))

    print(f"\n  Found {len(strings)} strings of {min_len}+ printable ASCII chars:")
    for off, s in strings:
        # Truncate very long strings for display
        display = s if len(s) <= 80 else s[:77] + "..."
        print(f"    Offset {off:>6d} (0x{off:06X}) [{len(s):>3d} chars]: {display}")

    if not strings:
        print("    None found.")


# ============================================================
# 8. REPEATING BLOCK DETECTION
# ============================================================

def repeating_blocks(data, label):
    print(f"\n{'='*80}")
    print(f"  8. REPEATING BLOCK DETECTION: {label}")
    print(f"{'='*80}")
    total = len(data)

    for block_size in [8, 16, 32]:
        print(f"\n  --- {block_size}-byte Block Repeats ---")
        block_map = collections.defaultdict(list)
        for i in range(total - block_size + 1):
            block = data[i:i+block_size]
            block_map[block].append(i)

        repeats = {k: v for k, v in block_map.items() if len(v) > 1}
        print(f"  Unique {block_size}-byte blocks: {len(block_map)}")
        print(f"  Blocks appearing 2+ times: {len(repeats)}")

        if repeats:
            # Sort by frequency
            sorted_repeats = sorted(repeats.items(), key=lambda x: len(x[1]), reverse=True)
            shown = 0
            for block, offsets in sorted_repeats:
                if shown >= 15:
                    remaining = len(sorted_repeats) - shown
                    print(f"    ... and {remaining} more repeating {block_size}-byte blocks")
                    break
                off_str = ', '.join(str(o) for o in offsets[:10])
                if len(offsets) > 10:
                    off_str += f" ... ({len(offsets)} total)"
                print(f"    {block.hex().upper()}  x{len(offsets):>4d}  offsets: [{off_str}]")
                shown += 1
        else:
            print(f"    No {block_size}-byte blocks repeat.")


# ============================================================
# MAIN
# ============================================================

def analyze_file(filepath, label):
    print(f"\n{'#'*80}")
    print(f"##  ANALYZING: {label}")
    print(f"##  File: {filepath}")
    data = open(filepath, 'rb').read()
    print(f"##  Size: {len(data)} bytes")
    print(f"##  Overall entropy: {entropy(data):.6f} bits/byte")
    print(f"{'#'*80}")

    scan_signatures(data, label)
    ngram_analysis(data, label)
    periodic_structure(data, label)
    block_entropy(data, label)
    transition_matrix(data, label)
    run_length_analysis(data, label)
    extract_strings(data, label)
    repeating_blocks(data, label)

    return data


def analyze_inverted(data, label):
    inv = invert_bytes(data)
    inv_label = f"{label} (INVERTED)"
    print(f"\n{'#'*80}")
    print(f"##  ANALYZING: {inv_label}")
    print(f"##  Size: {len(inv)} bytes")
    print(f"##  Overall entropy: {entropy(inv):.6f} bits/byte")
    print(f"{'#'*80}")

    scan_signatures(inv, inv_label)
    ngram_analysis(inv, inv_label)
    # Skip periodic structure for inverted (same entropy profile, just shifted values)
    print(f"\n  [Periodic structure and autocorrelation identical to non-inverted; skipped]")
    block_entropy(inv, inv_label)
    transition_matrix(inv, inv_label)
    run_length_analysis(inv, inv_label)
    extract_strings(inv, inv_label)
    repeating_blocks(inv, inv_label)


if __name__ == '__main__':
    print("=" * 80)
    print("  DEEP PATTERN ANALYSIS OF ACIM URTEXT STRESS PATTERN BINARY FILES")
    print("=" * 80)

    m3_path = BASE_DIR / "m3_full.bin"
    m4_path = BASE_DIR / "m4_full.bin"

    # M3 analysis
    m3_data = analyze_file(m3_path, "m3_full.bin (syllable-level toggle, 56882 bytes)")
    analyze_inverted(m3_data, "m3_full.bin")

    # M4 analysis
    m4_data = analyze_file(m4_path, "m4_full.bin (word-level toggle, 40388 bytes)")
    analyze_inverted(m4_data, "m4_full.bin")

    print(f"\n{'='*80}")
    print("  ANALYSIS COMPLETE")
    print(f"{'='*80}")
