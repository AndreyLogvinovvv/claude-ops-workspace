"""Rank untested Mersenne candidates by expected value per GPU-day.

Fetches exponent statuses from mersenne.org public reports (in chunks,
respecting the ~1000-row page limit), keeps only clean candidates
(no factor to target TF depth, no primality test), and ranks them by

    score = pm1_bonus * ln(p) / p^3

which is P(M_p prime | cleaning) / test_time up to constants:
probability ~ ln(p)/p, PRP test time ~ p^2, and candidates without a
completed P-1 run carry a ~3% residual chance of a cheaply-findable
factor (bonus 0.97 vs 1.0).

After 20 statistical tests (see RESEARCH_NOTES.md) no signal exists to
rank equally-cleaned candidates beyond this: lower exponent wins, deeper
cleaning breaks ties. This script just automates that conclusion.

Usage:
    python pick_candidate.py [lo] [hi] [top]
    python pick_candidate.py 333003110 333060000 10
"""
import math
import re
import sys
import urllib.request

CHUNK = 10000  # keeps each report page well under the ~1000-row limit

def fetch_chunk(lo, hi, tries=3):
    url = (f"https://www.mersenne.org/report_exponent/"
           f"?exp_lo={lo}&exp_hi={hi}&full=1")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    for attempt in range(tries):
        try:
            with opener.open(req, timeout=300) as r:
                html = r.read().decode("utf-8", "replace")
            break
        except Exception as e:
            if attempt == tries - 1:
                raise
            print(f"  retry {lo}-{hi} after: {e}", flush=True)
    text = re.sub(r"<[^>]+>", " ", html)
    return re.sub(r"\s+", " ", text)

def clean_candidates(lo, hi):
    """Yield (p, pm1_done) for clean untested exponents in [lo, hi]."""
    for start in range(lo, hi, CHUNK):
        text = fetch_chunk(start, min(start + CHUNK - 1, hi))
        pat = re.compile(
            r"(\d{3} \d{3} \d{3}) No known factors, not tested for primality"
            r"(.{0,200}?)(?=\d{3} \d{3} \d{3}|$)")
        for m in pat.finditer(text):
            p = int(m.group(1).replace(" ", ""))
            pm1 = "P-1 B1" in m.group(2) or "B1 =" in m.group(2)
            yield p, pm1

def main():
    lo = int(sys.argv[1]) if len(sys.argv) > 1 else 333003110
    hi = int(sys.argv[2]) if len(sys.argv) > 2 else 333060000
    top = int(sys.argv[3]) if len(sys.argv) > 3 else 10
    cands = sorted(set(clean_candidates(lo, hi)))
    print(f"clean untested candidates in [{lo}, {hi}]: {len(cands)}")
    scored = []
    for p, pm1 in cands:
        score = (1.0 if pm1 else 0.97) * math.log(p) / p ** 3
        scored.append((score, p, pm1))
    scored.sort(reverse=True)
    print(f"\n{'rank':>4} {'exponent':>12} {'P-1':>5}   relative EV")
    best = scored[0][0]
    for i, (s, p, pm1) in enumerate(scored[:top], 1):
        print(f"{i:>4} {p:>12} {'yes' if pm1 else 'no':>5}   {s/best:.6f}")
    print("\nReserve the winner at https://www.mersenne.org/manual_assignment/")
    print("(worktype: PRP first-time; paste the assignment line into worktodo)")

if __name__ == "__main__":
    main()
