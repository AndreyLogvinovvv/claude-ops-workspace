"""Statistical tests for hidden patterns in Mersenne exponent gaps.

Four detectors applied to log-gaps between consecutive known exponents:
1. Kolmogorov-Smirnov vs the exponential distribution (Poisson rain).
2. Lag-1 autocorrelation with a permutation test (memory between gaps).
3. Proximity to powers of two (a popular folklore claim).
4. Clustering index CV^2 (1.0 = pure randomness).

Result on the 52 known exponents: indistinguishable from randomness on all
four - the only exploitable structure is the global rate (see regression).

Usage: python gap_tests.py
"""
import math

import numpy as np

from analyze_exponents import KNOWN

g = np.diff(np.log(np.array(sorted(KNOWN), dtype=float)))
n = len(g)
rng = np.random.default_rng(42)
print(f"log-gaps: {n}, mean {g.mean():.4f}, median {np.median(g):.4f}")
print(f"min ratio {math.exp(g.min()):.4f}, max ratio {math.exp(g.max()):.3f}")

lam = 1.0 / g.mean()
gs = np.sort(g)
cdf = 1 - np.exp(-lam * gs)
D = max(np.max(np.abs(np.arange(1, n + 1) / n - cdf)),
        np.max(np.abs(cdf - np.arange(0, n) / n)))
ks = (math.sqrt(n) + 0.12 + 0.11 / math.sqrt(n)) * D
p_ks = 2 * sum((-1) ** (k - 1) * math.exp(-2 * k * k * ks * ks) for k in range(1, 101))
print(f"1) KS vs exponential: D={D:.4f}, p={p_ks:.3f} (p>0.05 -> random)")

r = np.corrcoef(g[:-1], g[1:])[0, 1]
cnt = sum(abs(np.corrcoef(s[:-1], s[1:])[0, 1]) >= abs(r)
          for s in (rng.permutation(g) for _ in range(20000)))
print(f"2) lag-1 autocorrelation: r={r:+.3f}, permutation p={cnt/20000:.3f}")

l2 = np.log2(np.array(sorted(KNOWN)[3:], dtype=float))
frac = np.abs(l2 - np.round(l2))
cnt2 = sum(rng.uniform(0, 0.5, size=len(frac)).mean() <= frac.mean()
           for _ in range(20000))
print(f"3) power-of-2 proximity: mean dist {frac.mean():.3f} (random ~0.25), p={cnt2/20000:.3f}")

print(f"4) clustering index CV^2 = {g.var(ddof=1)/g.mean()**2:.3f} (random = 1.0)")
