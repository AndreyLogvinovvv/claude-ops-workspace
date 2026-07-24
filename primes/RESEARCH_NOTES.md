# Research notes: hunting for structure in Mersenne prime exponents

Week of 2026-07-21 .. 2026-07-24. Data: the 52 known Mersenne prime
exponents (`known_mersenne_primes.csv`). Tools: scripts in this folder
(`analyze_exponents.py`, `regression_forecast.py`, `gap_tests.py`, ad-hoc
scripts summarized here). Motivation: pick the next 100M-digit candidate
rationally and test every "maybe there is a pattern" idea properly.

## Scoreboard

| # | Hypothesis | Method | Result | Verdict |
|---|-----------|--------|--------|---------|
| 1 | Gap sizes follow a non-random law | KS test of log-gaps vs exponential | D=0.083, p=0.86 | random (Poisson rain) |
| 2 | Gaps have memory (big follows small) | lag-1 autocorr + permutation | r=-0.11, p=0.43 | no memory |
| 3 | Exponents cling to powers of two | mean log2-distance vs uniform | 0.259 vs 0.25, p=0.66 | myth |
| 4 | Gaps cluster more than random | CV^2 index | 0.785 (random=1), n.s. | within noise |
| 5 | Exponents sit in prime-dense spots | prime counts in +-25 ln p windows vs random-prime control | 46.4 vs 46.1, p=0.81 | ordinary background |
| 6 | ...or in prime-SPARSE spots (central dip) | central-bin count vs 30 control sets | 67 vs control range 52-85 (p=0.23) | control shows same dip; procedural, not Mersenne-specific |
| 7 | Special forms 2^k+-1, 4^k+-3 dominate | enumeration | 9 of 52, ALL <= 127; 0 of last 43 | small-number illusion |
| 8 | Binary of exponents is "simpler" | ones-density vs random primes | 0.563 vs 0.571, p=0.66 | myth |
| 9 | Deficit of p = 3 (mod 4) (Sophie Germain kills them) | binomial test | 32:19 toward class 1, p=0.092 | direction as mechanism predicts; weak, n.s. |
| 10 | Sophie Germain pairs inside the list | enumeration | (2,5), (3,7) only | ancient only |
| 11 | Catalan-Mersenne chain is prime so far | our own Lucas-Lehmer | 2 -> 3 -> 7 -> 127 -> M127 all PRIME | confirmed; next link unknowable forever |
| 12 | GIMPS era finds MORE primes than theory | Monte Carlo vs Wagstaff rate | P(>=52)=0.26, P(slope>=2.68)=0.40 | plain luck, no excess |
| 13 | First digits follow Benford | chi-square vs log10(1+1/d) | chi2=1.72, p=0.99 | CONFIRMED (as geometric growth demands) |
| 14 | Hidden periodicity in positions | periodogram max power vs MC null | power 4.2, p=0.30 | none |
| 15 | Gap ORDER carries information | LZMA compression vs shuffles | 108 bytes = shuffles | uninformative at n=51 (LZMA overhead dominates) |
| 16 | Big/small gaps alternate non-randomly | Wald-Wolfowitz runs test | 27 runs vs 26.5, p=0.89 | random |
| 17 | Rate changed at some point (two regimes) | two-segment Poisson LRT + MC | LRT=7.28, p=0.085 | borderline; same "lucky GIMPS era" bump as #12, still noise-compatible |
| 18 | Residue classes p mod m, m=3..24 (battery, 29 tests) | chi-square, MC calibrated | only mod-12 family flagged (p=0.024), mod 19 p=0.021 = expected noise | see "Fine structure" below |
| 19 | p-1 smoother than for random primes | largest-prime-factor share, permutation | 0.542 vs 0.586, p=0.16 | no |
| 20 | Angles p mod 2pi cluster on the circle | Rayleigh test | R=0.225, p=0.071 | borderline, no mechanism; Vinogradov guarantees asymptotic uniformity - treated as noise |
| 21 | Digit-to-digit transitions differ from random primes | 10x10 transition matrix vs 20 control sets | chi2-dist 86.9 vs control 110.4, p~0.90 | no |
| 22 | Digit turtle-walks drift differently | net displacement, permutation | 2.01 vs 2.04, p=0.88 | no |
| 23 | Bit-walk profiles deviate abnormally | max cumsum deviation / sqrt(n) | 1.055 vs 1.148, p=0.25 | no |

## Fine structure of the Sophie Germain depletion (mod 12)

The strongest finding of the residue battery, and it matches the mechanism
in detail. A prime q = 2p+1 can divide M_p only when p = 3 (mod 4)
(then q = +-1 mod 8). Additionally, if p = 1 (mod 3), then 2p+1 is
divisible by 3 and can never be a prime killer. Combining both: the only
class with an ACTIVE killer is p = 11 (mod 12). Observed counts among the
48 exponents > 12 (uniform expectation: 12 per class):

| p mod 12 | killer status | observed |
|---|---|---|
| 1 | impossible (p = 1 mod 4) | 11 |
| 5 | impossible (p = 1 mod 4) | 20 |
| 7 | disarmed (3 divides 2p+1) | 12 (exactly at expectation) |
| 11 | ACTIVE | 5 (most depleted) |

The depleted class is exactly the cursed one, and the disarmed class sits
exactly at expectation. Formally p=0.024 (does not survive Bonferroni over
the battery), but this is a refinement of pre-registered hypothesis 9 with
an exact mechanism, not an independent fishing hit.

Hard check of the mechanism: among winners with p = 3 (mod 4), the value
2p+1 must be composite - and it is, for every one of them EXCEPT p = 3.
Edge case: for p = 3, 2p+1 = 7 = M_3 itself; the Sophie Germain divisor
coincides with the number, so it "divides" without compositing it. The
only legal exception in the universe.

Practical note for hunting: the curse is fully absorbed by trial factoring
(the killer 2p+1 ~ 2^29 is found instantly), so among TF-cleaned candidates
class 11 is as good as any other.

Lesson in test hygiene: the loudest battery signal, "digit sum mod 3,
p=0.000", was a bug in the test itself - digit sum mod 3 equals p mod 3,
and primes > 3 never occupy class 0, so the uniform-over-3-classes null
was impossible by arithmetic. The strongest anomaly in a mass sweep is
usually your own mistake.

## Geometric interpretation (verified numerically)

M_p equals the product of distances from the point 2 (on the real axis)
to all p vertices of the regular p-gon inscribed in the unit circle -
a direct consequence of x^p - 1 = prod (x - zeta^k). Checked to machine
precision for p = 3, 5, 7, 13 (products exactly 7, 31, 127, 8191). The
hunt, restated geometrically: find a polygon with 333 million vertices
whose distance product from the point 2 is indivisible. Beautiful, and
computationally equivalent to what we already do.

Circle visualizations (local chart "geometry"): rose diagram of p mod 12
(the depleted class is visible as the eaten petal), and exponents as
directions p mod 2pi (uniform per Rayleigh, #20).

## Local map fact (2026-07-24)

Between the currently tested exponent 333003109 and the chosen next
candidate 333003233 there are exactly five prime exponents: 333003113,
333003119, 333003127, 333003133, 333003211. All five already have known
factors in PrimeNet (composite, no test needed). So 333003233 is literally
the next unresolved Mersenne question on the number line - the rational
choice under the "lower edge" law needs no further justification.

## The two real structures

1. **Global rate.** N(p) = 2.6844 ln p - 2.268 fits with R^2 = 0.988; the
   theoretical Wagstaff slope e^gamma/ln2 = 2.5695 is inside the noise
   (Monte Carlo, hypothesis 12). Trained on the first 30 discoveries
   (through 1983), the model predicts the next 40 years with error +5.6
   at Poisson sigma 7.2 - extrapolation validated out-of-sample.
2. **Sophie Germain depletion** (hypothesis 9): the only detector that
   moved, and the only one with a causal mechanism - when p = 3 (mod 4)
   and 2p+1 is prime, 2p+1 divides M_p, so class 3 gets culled. The
   surviving list leans 32:19 toward class 1. Weak (p=0.09), but the
   mechanism is exact and is already used as a candidate filter.

Everything else is indistinguishable from a Poisson process on the log
scale. Consequence for hunting: no local signal exists to point at a
specific exponent; the only rational strategy is zone economics
(lower exponent = better per-candidate odds AND faster tests) plus hard
filters (prime p, Sophie Germain, trial factoring depth).

## Forecasts derived from the model

- 53rd Mersenne prime: median position ~176M, 80% interval 142M..321M.
- P(the 53rd lands straight in the 100M-digit zone) ~ 9%.
- Expected undiscovered primes between the record (136.3M) and 333M: ~2.4.
- First 100M-digit prime: median ~430M, 80% interval 345M..783M.
- Odds of one fully TF'd (2^81) candidate near p=333M: about 1 in 2.2M.

## Amusing verified facts

- M_p in binary is a run of p ones (a binary repunit).
- Twin exponent pairs among the 52: (3,5), (5,7), (17,19) - i.e. the
  triple 3-5-7 plus one pair; nothing since 1588.
- The Catalan-Mersenne chain's next link, M(M127) = 2^(1.7e38) - 1, has
  ~5e37 digits: no conceivable computer can ever test it.
- Mersenne's own 1644 list was likely built on the special-form illusion
  (hypothesis 7): 9 of the first 12 exponents fit 2^k+-1 / 4^k+-3, then
  the pattern dies completely.

## Charts

Rendered locally (Russian labels) into the hunt folder `gimps/charts/`;
all regenerable from scripts here: `plot_mersenne.py` (overview),
`regression_forecast.py` (fit + forecast). The zone map and
neighborhood-density strip charts were produced by session scripts;
their logic is described above.
