# All 52 Known Mersenne Primes

M_p = 2^p - 1. Ranked by size. Machine-readable copy: `known_mersenne_primes.csv`.
Digit counts computed exactly (floor(p*log10(2)) + 1), cross-checked with
`analyze_exponents.py` (same exponent list, KNOWN).

| # | p | digits | year | discoverer |
|---|---|--------|------|------------|
| 1 | 2 | 1 | — | antiquity |
| 2 | 3 | 1 | — | antiquity |
| 3 | 5 | 2 | — | antiquity |
| 4 | 7 | 3 | — | antiquity |
| 5 | 13 | 4 | 1456 | anonymous manuscript |
| 6 | 17 | 6 | 1588 | Cataldi |
| 7 | 19 | 6 | 1588 | Cataldi |
| 8 | 31 | 10 | 1772 | Euler |
| 9 | 61 | 19 | 1883 | Pervushin |
| 10 | 89 | 27 | 1911 | Powers |
| 11 | 107 | 33 | 1914 | Powers |
| 12 | 127 | 39 | 1876 | Lucas (by hand; record stood 76 years) |
| 13 | 521 | 157 | 1952 | Robinson (SWAC, first computer find) |
| 14 | 607 | 183 | 1952 | Robinson (SWAC) |
| 15 | 1279 | 386 | 1952 | Robinson (SWAC) |
| 16 | 2203 | 664 | 1952 | Robinson (SWAC) |
| 17 | 2281 | 687 | 1952 | Robinson (SWAC) |
| 18 | 3217 | 969 | 1957 | Riesel (BESK) |
| 19 | 4253 | 1281 | 1961 | Hurwitz |
| 20 | 4423 | 1332 | 1961 | Hurwitz |
| 21 | 9689 | 2917 | 1963 | Gillies |
| 22 | 9941 | 2993 | 1963 | Gillies |
| 23 | 11213 | 3376 | 1963 | Gillies |
| 24 | 19937 | 6002 | 1971 | Tuckerman |
| 25 | 21701 | 6533 | 1978 | Noll & Nickel (high-school students) |
| 26 | 23209 | 6987 | 1979 | Noll |
| 27 | 44497 | 13395 | 1979 | Nelson & Slowinski |
| 28 | 86243 | 25962 | 1982 | Slowinski |
| 29 | 110503 | 33265 | 1988 | Colquitt & Welsh (found out of order) |
| 30 | 132049 | 39751 | 1983 | Slowinski |
| 31 | 216091 | 65050 | 1985 | Slowinski |
| 32 | 756839 | 227832 | 1992 | Slowinski & Gage (Cray) |
| 33 | 859433 | 258716 | 1994 | Slowinski & Gage |
| 34 | 1257787 | 378632 | 1996 | Slowinski & Gage (last supercomputer find) |
| 35 | 1398269 | 420921 | 1996 | GIMPS / Armengaud |
| 36 | 2976221 | 895932 | 1997 | GIMPS / Spence |
| 37 | 3021377 | 909526 | 1998 | GIMPS / Clarkson |
| 38 | 6972593 | 2098960 | 1999 | GIMPS / Hajratwala |
| 39 | 13466917 | 4053946 | 2001 | GIMPS / Cameron |
| 40 | 20996011 | 6320430 | 2003 | GIMPS / Shafer |
| 41 | 24036583 | 7235733 | 2004 | GIMPS / Findley |
| 42 | 25964951 | 7816230 | 2005 | GIMPS / Nowak |
| 43 | 30402457 | 9152052 | 2005 | GIMPS / Cooper & Boone |
| 44 | 32582657 | 9808358 | 2006 | GIMPS / Cooper & Boone |
| 45 | 37156667 | 11185272 | 2008 | GIMPS / Elvenich |
| 46 | 42643801 | 12837064 | 2009 | GIMPS / Strindmo |
| 47 | 43112609 | 12978189 | 2008 | GIMPS / Smith (UCLA; won EFF $100k 10M-digit award) |
| 48 | 57885161 | 17425170 | 2013 | GIMPS / Cooper |
| 49 | 74207281 | 22338618 | 2016 | GIMPS / Cooper (4th find, record holder) |
| 50 | 77232917 | 23249425 | 2017 | GIMPS / Pace |
| 51 | 82589933 | 24862048 | 2018 | GIMPS / Laroche |
| 52 | 136279841 | 41024320 | 2024 | GIMPS / Durant (GPU fleet, current record) |

Notes:

* Since 1996 every discovery belongs to GIMPS (18 in a row).
* Exponent growth is roughly geometric, average ratio ~1.42-1.48 per step
  (Wagstaff's conjecture predicts 2^(1/e^gamma) ~ 1.4757).
* Twin exponent pairs (p, p+2) occurred only at (3,5), (5,7), (17,19).
* Ranks 29-31 were found out of size order - gaps are real.
* The 100-million-digit zone (EFF award) starts at p >= 332,192,807;
  none of the 52 known primes comes close yet (record: 41M digits).
