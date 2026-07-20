# primes

Prime number tools.

## mersenne.py — Lucas-Lehmer test for Mersenne numbers

Deterministic primality test for M_p = 2^p - 1, built to minimize
computational work on very large numbers:

- **Lucas-Lehmer**: exactly p-2 modular squarings, the proven optimal
  deterministic test for the Mersenne form (used by GIMPS).
- **Division-free reduction**: x mod (2^p - 1) is computed as
  `(x & M) + (x >> p)` — one AND, one shift, one add.
- **Exponent pre-screen**: composite p means composite M_p, so p is
  checked first with a deterministic Miller-Rabin (exact for 64-bit).
- **Optional GMP backend**: if `gmpy2` is installed it is used
  automatically (FFT multiplication — the way to go for million-bit
  numbers). Pure Python fallback needs no dependencies.

```
python mersenne.py 31            # is M_31 prime?
python mersenne.py 44497         # 13395-digit number, ~16 s pure Python
python mersenne.py --scan 10000  # all Mersenne primes with p <= 10000
```

## primes.py — Sieve of Eratosthenes

Find all primes up to N.

```
python primes.py [N]    # defaults to 100
```

Prints the count of primes up to N followed by the primes themselves.
Fast enough for N up to ~10,000,000 (fractions of a second).
