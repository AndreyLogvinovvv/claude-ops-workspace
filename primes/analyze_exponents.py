"""Analyze the 52 known Mersenne prime exponents and pick promising
candidates for a 100-million-digit Mersenne prime.

What is actually known about the pattern:

* Wagstaff's conjecture: the number of Mersenne primes with exponent
  below x grows like (e^gamma / ln 2) * ln x, i.e. successive exponents
  grow geometrically with average ratio 2^(1/e^gamma) ~ 1.4757.
  Beyond that, the exponents look Poisson-random on the log scale --
  no proven local pattern exists.
* Hard filters that DO provably remove candidates:
  - the exponent p must itself be prime;
  - if p = 3 (mod 4) and 2p+1 is prime, then 2p+1 divides M_p
    (Sophie Germain / Euler), so M_p is composite;
  - any factor of M_p has the form q = 2kp+1 with q = +-1 (mod 8),
    so cheap trial factoring kills many candidates: checking
    pow(2, p, q) == 1 costs ~30 squarings of small ints.

Usage:
    python analyze_exponents.py            # stats + candidate hunt
    python analyze_exponents.py --tf 50    # deeper trial factoring (2^50)
"""
import sys
from decimal import Decimal, getcontext

from mersenne import is_prime_small

KNOWN = [
    2, 3, 5, 7, 13, 17, 19, 31, 61, 89, 107, 127, 521, 607, 1279,
    2203, 2281, 3217, 4253, 4423, 9689, 9941, 11213, 19937, 21701,
    23209, 44497, 86243, 110503, 132049, 216091, 756839, 859433,
    1257787, 1398269, 2976221, 3021377, 6972593, 13466917, 20996011,
    24036583, 25964951, 30402457, 32582657, 37156667, 42643801,
    43112609, 57885161, 74207281, 77232917, 82589933, 136279841,
]

WAGSTAFF_RATIO = 1.47576  # 2^(1/e^gamma)

getcontext().prec = 40
LOG10_2 = Decimal(2).ln() / Decimal(10).ln()


def digit_count(p: int) -> int:
    return int(p * LOG10_2) + 1


def stats() -> None:
    print(f"Known Mersenne prime exponents: {len(KNOWN)}")
    ratios = [b / a for a, b in zip(KNOWN, KNOWN[1:])]
    geo = 1.0
    for r in ratios:
        geo *= r
    geo **= 1.0 / len(ratios)
    print(f"Geometric mean of successive exponent ratios: {geo:.4f}")
    print(f"Wagstaff-conjecture prediction:               {WAGSTAFF_RATIO}")
    twins = [(a, b) for a, b in zip(KNOWN, KNOWN[1:]) if b - a == 2]
    print(f"Adjacent (twin) exponent pairs: {twins} -- none since p=19")
    nxt = KNOWN[-1] * WAGSTAFF_RATIO
    print(f"Statistically expected next exponent: ~{nxt/1e6:.0f}M "
          f"({digit_count(int(nxt))/1e6:.1f}M digits)")
    p100 = 2
    while digit_count(p100) < 10**8:
        p100 += 1
    print(f"Smallest exponent giving 100M digits: {p100}")
    print(f"EFF award zone starts at p >= {p100} "
          f"(expected Mersenne primes per octave: ~1.78)")


def survives(p: int, tf_bits: int) -> str:
    """Return '' if p survives all cheap filters, else the reason it dies."""
    if not is_prime_small(p):
        return "p composite"
    if p % 4 == 3 and is_prime_small(2 * p + 1):
        return f"2p+1={2*p+1} divides M_p (Sophie Germain)"
    limit = 1 << tf_bits
    q = 2 * p + 1
    while q < limit:
        if q & 7 in (1, 7) and pow(2, p, q) == 1:
            return f"factor {q}"
        q += 2 * p
    return ""


def hunt(tf_bits: int) -> None:
    start = 2
    while digit_count(start) < 10**8:
        start += 1
    print(f"\nHunting candidates from p={start} (trial factoring to 2^{tf_bits})")
    survivors = []
    p = start if start % 2 else start + 1
    while len(survivors) < 8:
        reason = survives(p, tf_bits)
        if not reason:
            survivors.append(p)
            print(f"  CANDIDATE p={p}  (M_p has {digit_count(p)} digits)")
        p += 2
    print(f"Scanned {p - start} numbers, {len(survivors)} survivors")

    print("\nTwin hunt: adjacent prime exponents p, p+2 both surviving")
    p = start if start % 2 else start + 1
    while True:
        if not survives(p, tf_bits) and not survives(p + 2, tf_bits):
            print(f"  TWIN PAIR: p={p} and p={p+2}")
            break
        p += 2


if __name__ == "__main__":
    tf_bits = 46
    if len(sys.argv) > 2 and sys.argv[1] == "--tf":
        tf_bits = int(sys.argv[2])
    stats()
    hunt(tf_bits)
