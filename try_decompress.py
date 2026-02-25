"""
Attempt to decompress binary files from ACIM Urtext stress pattern analysis.
Tries multiple decompression methods, offsets, bit rotations, and inversions.
"""

import zlib
import gzip
import bz2
import lzma
import math
import os
import io
from collections import Counter

def shannon_entropy(data: bytes) -> float:
    """Calculate Shannon entropy per byte."""
    if not data:
        return 0.0
    counts = Counter(data)
    length = len(data)
    entropy = 0.0
    for count in counts.values():
        p = count / length
        if p > 0:
            entropy -= p * math.log2(p)
    return entropy

def printable_pct(data: bytes) -> float:
    """Percentage of bytes that are printable ASCII (32-126)."""
    if not data:
        return 0.0
    printable = sum(1 for b in data if 32 <= b <= 126)
    return 100.0 * printable / len(data)

def to_ascii_preview(data: bytes, max_len=200) -> str:
    """First max_len bytes as ASCII, non-printable replaced with dots."""
    preview = data[:max_len]
    return ''.join(chr(b) if 32 <= b <= 126 else '.' for b in preview)

def classify_output(data: bytes) -> str:
    """Classify output as text, structured data, or noise."""
    pct = printable_pct(data)
    ent = shannon_entropy(data)
    if pct > 90 and ent < 5.0:
        return "LIKELY TEXT"
    elif pct > 70:
        return "POSSIBLY TEXT/STRUCTURED"
    elif ent < 4.0:
        return "LOW ENTROPY - STRUCTURED?"
    elif ent > 7.5:
        return "HIGH ENTROPY - NOISE/ENCRYPTED"
    else:
        return "BINARY DATA"

def report_success(method: str, data: bytes):
    """Report a successful decompression."""
    print(f"\n  *** SUCCESS: {method} ***")
    print(f"  Output size: {len(data)} bytes")
    print(f"  Entropy: {shannon_entropy(data):.4f} bits/byte")
    print(f"  Printable ASCII: {printable_pct(data):.1f}%")
    print(f"  Classification: {classify_output(data)}")
    print(f"  Preview: {to_ascii_preview(data)}")
    print()

def invert_bits(data: bytes) -> bytes:
    """Flip all bits."""
    return bytes(b ^ 0xFF for b in data)

def reverse_bytes(data: bytes) -> bytes:
    """Reverse byte order."""
    return data[::-1]

def rotate_bits(data: bytes, shift: int) -> bytes:
    """Rotate all bits in the byte stream by shift positions (1-7)."""
    # Convert to a single big integer
    n = int.from_bytes(data, 'big')
    total_bits = len(data) * 8
    # Rotate left by shift
    shifted = ((n << shift) | (n >> (total_bits - shift))) & ((1 << total_bits) - 1)
    return shifted.to_bytes(len(data), 'big')

def try_decompress_all(data: bytes, label: str):
    """Try all decompression methods on data."""
    successes = 0

    # 1. zlib (raw DEFLATE)
    try:
        result = zlib.decompress(data, -15)
        report_success(f"{label} | zlib raw deflate (wbits=-15)", result)
        successes += 1
    except Exception:
        pass

    # zlib-wrapped
    try:
        result = zlib.decompress(data)
        report_success(f"{label} | zlib-wrapped", result)
        successes += 1
    except Exception:
        pass

    # Also try wbits=15 and wbits=31 (gzip via zlib)
    for wbits in [15, 31, -9, -10, -11, -12, -13, -14]:
        try:
            result = zlib.decompress(data, wbits)
            report_success(f"{label} | zlib wbits={wbits}", result)
            successes += 1
        except Exception:
            pass

    # 2. gzip
    try:
        result = gzip.decompress(data)
        report_success(f"{label} | gzip", result)
        successes += 1
    except Exception:
        pass

    # 3. bzip2
    try:
        result = bz2.decompress(data)
        report_success(f"{label} | bzip2", result)
        successes += 1
    except Exception:
        pass

    # 4. LZMA
    try:
        result = lzma.decompress(data)
        report_success(f"{label} | lzma (auto)", result)
        successes += 1
    except Exception:
        pass

    # Try LZMA with various formats
    for fmt in [lzma.FORMAT_XZ, lzma.FORMAT_ALONE, lzma.FORMAT_RAW]:
        if fmt == lzma.FORMAT_RAW:
            # Try a few common filter chains for raw LZMA
            filter_chains = [
                [{"id": lzma.FILTER_LZMA1}],
                [{"id": lzma.FILTER_LZMA2}],
                [{"id": lzma.FILTER_DELTA, "dist": 1}, {"id": lzma.FILTER_LZMA2}],
            ]
            for filters in filter_chains:
                try:
                    result = lzma.decompress(data, format=fmt, filters=filters)
                    report_success(f"{label} | lzma raw filters={filters}", result)
                    successes += 1
                except Exception:
                    pass
        else:
            try:
                fmt_name = "XZ" if fmt == lzma.FORMAT_XZ else "ALONE"
                result = lzma.decompress(data, format=fmt)
                report_success(f"{label} | lzma {fmt_name}", result)
                successes += 1
            except Exception:
                pass

    return successes

def try_offset_deflate(data: bytes, label: str, max_offset=1000):
    """Try raw deflate at every byte offset from 0 to max_offset."""
    successes = 0
    actual_max = min(max_offset, len(data) - 2)
    for offset in range(actual_max + 1):
        try:
            result = zlib.decompress(data[offset:], -15)
            if len(result) > 100:
                report_success(f"{label} | raw deflate at offset {offset}", result)
                successes += 1
        except Exception:
            pass
        # Also try zlib-wrapped at each offset
        try:
            result = zlib.decompress(data[offset:])
            if len(result) > 100:
                report_success(f"{label} | zlib-wrapped at offset {offset}", result)
                successes += 1
        except Exception:
            pass
    return successes


def main():
    files = {
        "m3_full.bin": "Toggle syllable-level",
        "m4_full.bin": "Toggle word-level",
    }

    for filename, description in files.items():
        filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        if not os.path.exists(filepath):
            print(f"FILE NOT FOUND: {filepath}")
            continue

        with open(filepath, 'rb') as f:
            raw = f.read()

        print("=" * 80)
        print(f"FILE: {filename} ({description})")
        print(f"Size: {len(raw)} bytes")
        print(f"Raw entropy: {shannon_entropy(raw):.4f} bits/byte")
        print("=" * 80)

        total_successes = 0

        # --- Original data ---
        print(f"\n--- Original data ---")
        total_successes += try_decompress_all(raw, f"{filename} original")

        # --- Inverted data ---
        inv = invert_bits(raw)
        print(f"\n--- Inverted (all bits flipped) ---")
        total_successes += try_decompress_all(inv, f"{filename} inverted")

        # --- Reversed byte order ---
        rev = reverse_bytes(raw)
        print(f"\n--- Reversed byte order ---")
        total_successes += try_decompress_all(rev, f"{filename} reversed")

        # --- Reversed + inverted ---
        rev_inv = invert_bits(rev)
        print(f"\n--- Reversed + inverted ---")
        total_successes += try_decompress_all(rev_inv, f"{filename} reversed+inverted")

        # --- Offset deflate on original ---
        print(f"\n--- Trying raw deflate/zlib at every offset 0-1000 (original) ---")
        total_successes += try_offset_deflate(raw, f"{filename} original")

        # --- Offset deflate on inverted ---
        print(f"\n--- Trying raw deflate/zlib at every offset 0-1000 (inverted) ---")
        total_successes += try_offset_deflate(inv, f"{filename} inverted")

        # --- Bit rotations (1-7) ---
        for shift in range(1, 8):
            print(f"\n--- Bit rotation by {shift} ---")
            rotated = rotate_bits(raw, shift)
            total_successes += try_decompress_all(rotated, f"{filename} rotated-{shift}")

        # --- Bit rotations on inverted ---
        for shift in range(1, 8):
            print(f"\n--- Bit rotation by {shift} (inverted) ---")
            rotated = rotate_bits(inv, shift)
            total_successes += try_decompress_all(rotated, f"{filename} inv-rotated-{shift}")

        print(f"\n{'=' * 80}")
        print(f"TOTAL SUCCESSES for {filename}: {total_successes}")
        print(f"{'=' * 80}\n")

    print("\nDone. If all attempts failed, the binary data is likely not compressed data")
    print("in any standard format, or uses a custom/unknown compression scheme.")


if __name__ == "__main__":
    main()
