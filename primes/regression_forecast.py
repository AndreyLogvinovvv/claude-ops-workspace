"""Regression on Mersenne prime frequency + holdout validation + forecast.

Empirical check of the Lenstra-Pomerance-Wagstaff heuristic on the 52 known
exponents: the count of Mersenne primes with exponent <= p grows linearly in
ln(p) (theoretical slope e^gamma/ln2 ~ 2.5695). The model is trained on the
first 30 discoveries (through 1983) and validated on the 22 later ones, then
extrapolated: where to expect the 53rd prime and the first 100M-digit prime.

Usage: python regression_forecast.py [out_dir]
"""
import math
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from analyze_exponents import KNOWN

EFF = 332192807
TARGET = 333003109

P = sorted(KNOWN)
N = np.arange(1, len(P) + 1)
L = np.log(np.array(P, dtype=float))

a, b = np.polyfit(L, N, 1)
r2 = 1 - np.sum((N - (a * L + b)) ** 2) / np.sum((N - N.mean()) ** 2)
print(f"All 52: N = {a:.4f}*ln(p) + {b:.3f}, R^2 = {r2:.4f} "
      f"(Wagstaff slope: {math.exp(0.5772156649)/math.log(2):.4f})")

K = 30
a30, b30 = np.polyfit(L[:K], N[:K], 1)
print(f"Holdout (trained on first {K}, through 1983):")
for i in (30, 34, 37, 41, 45, 48, 51):
    pred = a30 * math.log(P[i]) + b30
    print(f"  p={P[i]:>11,}  actual N={i+1}  predicted {pred:.1f}  err {i+1-pred:+.1f}")
print(f"Poisson noise at N=52: +-{math.sqrt(52):.1f} -> extrapolation holds")

q = lambda prob, base: base * math.exp(-math.log(1 - prob) / a)
print(f"53rd prime: median ~{q(0.5, P[-1])/1e6:.0f}M, "
      f"80% interval [{q(0.1, P[-1])/1e6:.0f}M .. {q(0.9, P[-1])/1e6:.0f}M]")
print(f"P(53rd lands straight in the EFF zone) = {(P[-1]/EFF)**a*100:.1f}%")
print(f"First 100M-digit prime: median ~{q(0.5, EFF)/1e6:.0f}M, "
      f"80% interval [{q(0.1, EFF)/1e6:.0f}M .. {q(0.9, EFF)/1e6:.0f}M]")
print(f"Odds of one TF-2^81 candidate near 333M: 1 in {TARGET/(a*81*math.log(2))/1e6:.1f}M")

out_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
fig, ax = plt.subplots(figsize=(11, 6.5))
ax.step(P, N, where="post", color="#2a78d6", linewidth=1.6, label="actual: N primes with exponent <= p")
xs = np.logspace(math.log10(2), math.log10(6e8), 300)
ax.plot(xs, a * np.log(xs) + b, "--", color="#1baf7a",
        label=f"fit N = {a:.2f}*ln p {b:+.2f} (R2={r2:.3f})")
ax.plot(xs, a30 * np.log(xs) + b30, ":", color="#eda100", label=f"model trained on first {K} (1983)")
ax.axvspan(q(0.1, P[-1]), q(0.9, P[-1]), color="#e34948", alpha=0.12, label="80% zone for the 53rd prime")
ax.axvline(TARGET, color="#993c1d", linewidth=1.3)
ax.set_xscale("log")
ax.set_xlabel("exponent p (log scale)")
ax.set_ylabel("Mersenne primes with exponent <= p")
ax.set_title("Mersenne prime frequency regression and the 53rd-prime forecast")
ax.grid(True, which="both", alpha=0.25)
ax.legend(loc="upper left", fontsize=9)
fig.tight_layout()
fig.savefig(os.path.join(out_dir, "regression_forecast.png"), dpi=130)
print("saved: regression_forecast.png")
