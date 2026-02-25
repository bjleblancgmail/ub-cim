"""
Entropy analysis of the toggle binary string from the dense block.
"""

import math
from collections import Counter


def shannon_entropy(bits, block_size=1):
    """Calculate Shannon entropy in bits per symbol."""
    # Split into blocks
    blocks = [bits[i:i+block_size] for i in range(0, len(bits) - block_size + 1, block_size)]
    total = len(blocks)
    counts = Counter(blocks)

    entropy = 0
    for count in counts.values():
        p = count / total
        if p > 0:
            entropy -= p * math.log2(p)
    return entropy


def max_entropy(block_size):
    """Maximum possible entropy for given block size."""
    return block_size  # log2(2^block_size) = block_size


def run_length_stats(bits):
    """Analyze run lengths (consecutive same bits)."""
    runs = []
    current = bits[0]
    length = 1
    for b in bits[1:]:
        if b == current:
            length += 1
        else:
            runs.append((current, length))
            current = b
            length = 1
    runs.append((current, length))
    return runs


def main():
    toggle_bits = "011110000001100001111011100000000000011110000001111000000001101110100100111101000000000000001000000000001011001111110000000000100000000000000011111110000000010111000111100001111010000001100000001111001011001001110000001000001010001101110100001011111011111000011111010000000011100011001100010111011100000001010001111000001010111111101000100001110010110000000001001111111100001010111111010001000111111110000000111000100010111100001000001101000100111101010101011001110010101001101100001111110101010101010000001011011000011101010100001010101010100101010111010110100010100101010101010100001010101010000010100001010001110000001111110000001001111101000001010001111100000101010100011111111011110000001000001110001111100001111111011010100010100110100110111100001111111010001010011110001111000001010001111000000001111111101110000101011101000100010101010011100100010000010000000001000"

    print(f"Total bits: {len(toggle_bits)}")
    print(f"Zeros: {toggle_bits.count('0')} ({toggle_bits.count('0')/len(toggle_bits):.3f})")
    print(f"Ones:  {toggle_bits.count('1')} ({toggle_bits.count('1')/len(toggle_bits):.3f})")

    # Single-bit entropy
    print(f"\n{'=' * 60}")
    print("SHANNON ENTROPY AT VARIOUS BLOCK SIZES")
    print("=" * 60)

    for bs in [1, 2, 3, 4, 5, 8]:
        ent = shannon_entropy(toggle_bits, bs)
        max_ent = max_entropy(bs)
        efficiency = ent / max_ent * 100
        print(f"\n  Block size {bs}:")
        print(f"    Entropy:    {ent:.4f} bits per {bs}-bit block")
        print(f"    Maximum:    {max_ent:.4f} bits")
        print(f"    Efficiency: {efficiency:.1f}% of maximum")
        print(f"    (100% = perfectly random, 0% = completely predictable)")

    # Compare to benchmarks
    print(f"\n{'=' * 60}")
    print("COMPARISON BENCHMARKS")
    print("=" * 60)

    # Generate random bits for comparison
    import random
    random.seed(42)
    random_bits = ''.join(str(random.randint(0, 1)) for _ in range(len(toggle_bits)))

    # Generate English text bits (approximate)
    english_text = "to be or not to be that is the question whether tis nobler in the mind to suffer the slings and arrows of outrageous fortune"
    english_bits = ''.join(format(ord(c), '08b') for c in english_text)[:len(toggle_bits)]

    # Generate all zeros
    zero_bits = '0' * len(toggle_bits)

    # Generate iambic pattern
    iambic_bits = ('0101010101' * (len(toggle_bits) // 10 + 1))[:len(toggle_bits)]

    benchmarks = [
        ("ACIM toggle bits", toggle_bits),
        ("Pure random", random_bits),
        ("English text (binary)", english_bits),
        ("All zeros", zero_bits),
        ("Repeating 0101010101", iambic_bits),
    ]

    for bs in [1, 2, 4, 8]:
        print(f"\n  Block size {bs}:")
        for name, bits in benchmarks:
            ent = shannon_entropy(bits, bs)
            max_ent = max_entropy(bs)
            eff = ent / max_ent * 100
            print(f"    {name:<30} {ent:.4f} bits  ({eff:.1f}%)")

    # Run length analysis
    print(f"\n{'=' * 60}")
    print("RUN LENGTH ANALYSIS")
    print("=" * 60)

    runs = run_length_stats(toggle_bits)
    run_lengths = [length for _, length in runs]

    print(f"\n  Total runs: {len(runs)}")
    print(f"  Average run length: {sum(run_lengths)/len(run_lengths):.2f}")
    print(f"  Median run length: {sorted(run_lengths)[len(run_lengths)//2]}")
    print(f"  Max run length: {max(run_lengths)}")
    print(f"  Min run length: {min(run_lengths)}")

    # Run length distribution
    rl_counts = Counter(run_lengths)
    print(f"\n  Run length distribution:")
    for length in sorted(rl_counts.keys()):
        count = rl_counts[length]
        bar = '#' * count
        print(f"    Length {length:>2}: {count:>4} runs  {bar}")

    # For comparison: random bit run lengths
    random_runs = run_length_stats(random_bits)
    random_rl = [length for _, length in random_runs]
    print(f"\n  Comparison (random bits):")
    print(f"    Total runs: {len(random_runs)}")
    print(f"    Average run length: {sum(random_rl)/len(random_rl):.2f}")
    print(f"    Max run length: {max(random_rl)}")

    random_rl_counts = Counter(random_rl)
    print(f"    Run length distribution:")
    for length in sorted(random_rl_counts.keys()):
        count = random_rl_counts[length]
        bar = '#' * count
        print(f"      Length {length:>2}: {count:>4} runs  {bar}")

    # Autocorrelation
    print(f"\n{'=' * 60}")
    print("AUTOCORRELATION (does the pattern repeat at fixed intervals?)")
    print("=" * 60)

    bits_int = [int(b) for b in toggle_bits]
    mean = sum(bits_int) / len(bits_int)
    variance = sum((b - mean) ** 2 for b in bits_int) / len(bits_int)

    print(f"\n  Checking lags 1-50:")
    significant = []
    for lag in range(1, 51):
        corr = 0
        n = len(bits_int) - lag
        for i in range(n):
            corr += (bits_int[i] - mean) * (bits_int[i + lag] - mean)
        corr /= (n * variance) if variance > 0 else 1

        marker = ""
        if abs(corr) > 0.1:
            marker = " <<<"
            significant.append((lag, corr))
        if lag <= 20 or marker:
            print(f"    Lag {lag:>3}: {corr:>+.4f}{marker}")

    if significant:
        print(f"\n  Significant correlations (|r| > 0.1):")
        for lag, corr in significant:
            print(f"    Lag {lag}: {corr:+.4f}")
    else:
        print(f"\n  No significant autocorrelation found at any lag.")

    # Summary
    print(f"\n{'=' * 60}")
    print("INTERPRETATION")
    print("=" * 60)

    ent1 = shannon_entropy(toggle_bits, 1)
    ent_rand = shannon_entropy(random_bits, 1)

    print(f"""
  Single-bit entropy: {ent1:.4f} (random would be {ent_rand:.4f})

  The toggle bits are {'MORE' if ent1 > 0.95 else 'LESS'} random than pure noise.

  Key finding: The run lengths tell the real story.
  Average run length of {sum(run_lengths)/len(run_lengths):.1f} vs random's {sum(random_rl)/len(random_rl):.1f}
  means the bits are {'clumpier' if sum(run_lengths)/len(run_lengths) > sum(random_rl)/len(random_rl) else 'more scattered'} than random.

  This is consistent with {'structured data (possible encoding)' if ent1 > 0.9 and sum(run_lengths)/len(run_lengths) < 2.5 else 'natural language rhythm patterns (not encoded data)'}.
""")


if __name__ == '__main__':
    main()
