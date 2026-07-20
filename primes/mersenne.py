"""Lucas-Lehmer primality test for Mersenne numbers M_p = 2^p - 1.

Why this is the minimal-work approach for Mersenne numbers:

* Lucas-Lehmer is a DETERMINISTIC test (not probabilistic) that needs
  exactly p-2 modular squarings -- the proven optimal test for this
  special form. General-purpose tests (Miller-Rabin, AKS, ECPP) would
  be orders of magnitude slower on numbers this size.
* Reduction modulo 2^p - 1 costs no division at all: because
  2^p = 1 (mod M_p), any 2p-bit value x folds as
  (x & M_p) + (x >> p) -- one AND, one shift, one add.
* A composite exponent p always gives a composite M_p, so p itself is
  screened first with a fast deterministic Miller-Rabin (exact for all
  64-bit integers).
* If gmpy2 (GMP) is installed it is picked up automatically: GMP squares
  million-bit integers with FFT-based multiplication, far faster than
  CPython's Karatsuba. Pure Python works out of the box as a fallback.

Usage:
    python mersenne.py 31            # is M_31 = 2^31 - 1 prime?
    python mersenne.py --scan 10000  # all Mersenne primes with p <= 10000
"""
import sys
import time

try:
    from gmpy2 import mpz
    BACKEND = "gmpy2 (GMP, FFT multiplication)"
except ImportError:
    mpz = int
    BACKEND = "pure Python integers (Karatsuba)"

_MR_BASES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)


def is_prime_small(n: int) -> bool:
    """Deterministic Miller-Rabin, exact for all n < 3.3e24 (covers 64-bit)."""
    if n < 2:
        return False
    for q in _MR_BASES:
        if n % q == 0:
            return n == q
    d = n - 1
    r = ((d & -d).bit_length()) - 1  # count trailing zeros
    d >>= r
    for a in _MR_BASES:
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def lucas_lehmer(p: int) -> bool:
    """True iff M_p = 2^p - 1 is prime."""
    if p == 2:
        return True  # M_2 = 3, the only even-exponent case
    if not is_prime_small(p):
        return False  # composite p => composite M_p, no work needed
    m = (mpz(1) << p) - 1  # M_p; doubles as the bit mask for folding
    s = mpz(4)
    for _ in range(p - 2):
        s = s * s
        # fold the 2p-bit square back below 2^p: x mod M_p via shift+mask
        s = (s & m) + (s >> p)
        if s >= m:
            s -= m
        s -= 2
        if s < 0:
            s += m
    return s == 0


def scan(limit: int) -> None:
    t0 = time.perf_counter()
    found = []
    for p in range(2, limit + 1):
        if is_prime_small(p) and lucas_lehmer(p):
            found.append(p)
            digits = len(str((1 << p) - 1))
            print(f"p = {p:>6}  M_p prime  ({digits} digits)")
    dt = time.perf_counter() - t0
    print(f"\n{len(found)} Mersenne primes with p <= {limit}  [{dt:.2f}s, {BACKEND}]")
    print("exponents:", *found)


def main() -> None:
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return
    if args[0] == "--scan":
        scan(int(args[1]) if len(args) > 1 else 1000)
        return
    p = int(args[0])
    t0 = time.perf_counter()
    result = lucas_lehmer(p)
    dt = time.perf_counter() - t0
    digits = int(p * 0.30103) + 1  # log10(2^p)
    verdict = "PRIME" if result else "composite"
    print(f"M_{p} = 2^{p} - 1 ({digits} digits): {verdict}  [{dt:.2f}s, {BACKEND}]")


if __name__ == "__main__":
    main()
