"""Render two charts about known Mersenne primes to a PNG.

Left:  digit count vs exponent (log-log) - a perfect straight line,
       because digits = floor(p * log10(2)) + 1.
Right: record exponent vs year of discovery (log y) - every computing
       era produces a visible jump.

Usage: python plot_mersenne.py [output.png]
"""
import csv
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET_P, TARGET_D, TARGET_YEAR = 333003109, 100243925, 2026

rows = []
with open(os.path.join(HERE, "known_mersenne_primes.csv"), encoding="utf-8") as f:
    for r in csv.DictReader(f):
        rows.append(r)

P = [int(r["exponent"]) for r in rows]
D = [int(r["digits"]) for r in rows]
Y = [int(r["year"]) if r["year"] else None for r in rows]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle("Mersenne primes: 52 known and our target", fontsize=14)

ax1.loglog([2, 6e8], [2 * 0.30103, 6e8 * 0.30103], "--", color="gray",
           linewidth=1, label="digits = 0.30103*p")
ax1.loglog(P, D, "o", color="#2a78d6", markersize=5, label="known primes")
ax1.loglog([TARGET_P], [TARGET_D], "D", color="#e34948", markersize=10,
           label="target M333003109")
ax1.set_xlabel("exponent p")
ax1.set_ylabel("digits in M_p")
ax1.set_title("Digits vs exponent (log-log)")
ax1.grid(True, which="both", alpha=0.25)
ax1.legend()

eras = [
    ("by hand (before 1952)", "#eda100", "^", lambda y: y is not None and y < 1952),
    ("mainframes and Cray (1952-1996)", "#2a78d6", "o", lambda y: y is not None and 1952 <= y < 1996),
    ("GIMPS (since 1996)", "#1baf7a", "d", lambda y: y is not None and y >= 1996),
]
for label, color, marker, cond in eras:
    xs = [y for y, p in zip(Y, P) if cond(y)]
    ys = [p for y, p in zip(Y, P) if cond(y)]
    ax2.semilogy(xs, ys, marker, color=color, markersize=6, linestyle="none",
                 label=label)
ax2.semilogy([TARGET_YEAR], [TARGET_P], "s", color="#e34948", markersize=10,
             label="target M333003109")
ax2.set_xlabel("year of discovery")
ax2.set_ylabel("exponent p")
ax2.set_title("Record growth by year: computing eras")
ax2.grid(True, which="both", alpha=0.25)
ax2.legend(loc="upper left")

out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "mersenne_charts.png")
fig.tight_layout()
fig.savefig(out, dpi=130)
print("saved:", out)
