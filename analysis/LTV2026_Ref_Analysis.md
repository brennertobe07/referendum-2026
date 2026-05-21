# Referendum 2026 — LTV Analysis

## Executive Summary (Phase 6)

**The data.** The SBE "List of Those Who Voted" file for the April 21, 2026 Virginia
Constitutional Amendment Referendum loaded cleanly: **3,101,912 voter rows**, exactly
matching the source CSV (header excluded), with no duplicate voter IDs and only **2**
records (0.00%) not matching a current RVL voter. The import reconciles to within
**−0.234%** of SBE ballots cast (3,109,181) and **99.79%** against accepted absentee
ballots in the absentee app.

**The result.** The amendment **PASSED, 51.69% Yes / 48.31% No**, on **51.06% turnout**
of 6.08M active registered voters. This was **not** the low-turnout April special the
brief anticipated — turnout was robust and broadly comparable to a November cycle
(referendum turnout ran only 1–5 pp below 2025-General levels across every age band).

**Most interesting findings:**

1. **Base mobilization, not a new electorate.** 76.0% of voters had voted in 3 or 4 of
   the last 4 November generals; only 9.3% had voted in 0 or 1. First-time voters were
   just **2.1%**. The referendum turned out the habitual electorate — it did not pull in
   new or marginal voters.
2. **Republicans voted at much higher intensity, but Democrats' larger base won it.**
   Rep-leaning turnout was **72.9%** vs Dem-leaning **59.8%** (a 13 pp gap), yet the
   measure passed because Dem-leaning registrants outnumber Rep-leaning ~2.14M to 1.24M
   and independents broke in. Geography was sharply partisan: strongest Yes in urban /
   NoVa localities (Petersburg 87%, Charlottesville 85%, Richmond 83%, Arlington 80%),
   strongest No in southwest Virginia (Lee 11%, Scott 12%, Buchanan 12%).
3. **Turnout climbs steeply with age.** 28.7% (18–24) → 72.0% (65–74), with women
   turning out 2 pp higher than men (52.8% vs 50.8%).
4. **Vote method skews old-early, young-day.** Statewide 54.9% voted election day,
   34.7% in-person early, 10.2% mail. The 65+ bands voted early/mail at far higher
   rates; under-35s concentrated on election day.

**Data-quality issues to follow up:**
- **COVINGTON CITY (580)** and **SUSSEX COUNTY (183)** are under-reported in the SBE LTV
  source — only ~⅓ of their actual recorded voters appear (codes verified against ENR;
  not a join error). Treat both as incomplete for locality-level work; statewide and
  demographic results are unaffected (<0.1% of total). See `reconciliation.md`.
- **101 precincts** fall beyond ±2 SD of the statewide precinct turnout mean (52.1% ±
  9.2 pp). The low-end outliers are the expected pockets — university precincts (UVA,
  Hampton U.), the Quantico military base, and downtown urban cores — not data errors.

---

# Referendum 2026 — Voter Pattern Analysis (Phase 5)

_Generated 2026-05-21. Base table `Historic.dbo.LTV2026_Ref_Base` = 3,101,912 LTV voters enriched with Van party/history + RVL match._

> **Caveats:** turnout denominators use RVL `STATUS='Active'`; party uses Van `LikelyParty` (SD/LD=Dem, SR/LR=Rep, ND/I/U=Unknown/Ind); baseline = 2025 General (Van `General25`). COVINGTON CITY (580) and SUSSEX COUNTY (183) are under-reported in the LTV source (~1/3 of actual) — locality-level rows for them are unreliable; statewide/demographic results are unaffected (<0.1%).

## 5a. First-time voters

- **First-time (broad): 64,894 (2.1% of voters)** = 39,400 matched in Van with no prior vote + 25,494 with no Van record (likely new registrations after the Van snapshot).
- Returning voters (≥1 prior election in Van): 3,037,018 (97.9%).

First-time voters by age band:

| age_band | first_time |
|---|---|
| 18-24 | 28,208 |
| 25-34 | 9,262 |
| 35-44 | 7,453 |
| 45-54 | 5,013 |
| 55-64 | 4,859 |
| 65-74 | 3,927 |
| 75+ | 1,971 |
| Unknown | 4,201 |

First-time voters by party bucket:

| party_bucket | first_time |
|---|---|
| Unknown/Ind | 63,973 |
| Dem | 789 |
| Rep | 132 |

_Comparison: 108,974 of 5,984,412 active registered voters (1.8%) registered after the Nov 2025 general — the referendum's first-time share (2.1%) exceeds that baseline._

## 5b. Age and generation

Turnout % = LTV voters / RVL active registered, by age (as of 2026-04-21). Baseline = 2025 General turnout in Van.

| age_band | voted | registered | turnout_pct | baseline_2025G_pct | vs_baseline_pp |
|---|---|---|---|---|---|
| 18-24 | 176,619 | 614,479 | 28.7 | 33.5 | -4.8 |
| 25-34 | 317,309 | 984,152 | 32.2 | 34.5 | -2.3 |
| 35-44 | 442,923 | 996,216 | 44.5 | 46.9 | -2.4 |
| 45-54 | 490,763 | 906,307 | 54.1 | 57.3 | -3.2 |
| 55-64 | 619,681 | 970,283 | 63.9 | 65.6 | -1.7 |
| 65-74 | 608,678 | 845,492 | 72.0 | 72.8 | -0.8 |
| 75+ | 441,737 | 648,585 | 68.1 | 70.0 | -1.9 |
| Unknown | 4,202 | 18,898 | 22.2 | 0.0 | 22.2 |

## 5c. Gender

| gender | voted | registered | turnout_pct | baseline_2025G_pct | vs_baseline_pp |
|---|---|---|---|---|---|
| F | 1,663,406 | 3,150,405 | 52.8 | 55.4 | -2.6 |
| M | 1,425,423 | 2,804,708 | 50.8 | 52.0 | -1.2 |

## 5d. Vote history pattern (last 4 Nov generals: 2022-2025)

Among LTV voters matched in Van:

| generals_voted_of_4 | voters | pct |
|---|---|---|
| 0.0 | 61,556.0 | 2.0 |
| 1.0 | 224,079.0 | 7.3 |
| 2.0 | 452,566.0 | 14.7 |
| 3.0 | 594,794.0 | 19.3 |
| 4.0 | 1,743,423.0 | 56.7 |

**3-of-4 or 4-of-4: 2,338,217 (76.0%)** vs **0-of-4 or 1-of-4: 285,635 (9.3%)**. This referendum is a **base mobilization** story.

## 5e. Vote method (Election day=Polls, In-person early=AB_Inperson, Mail=AB_Mail)

By age band (voter counts):

| age_band | AB_Inperson | AB_Mail | AB_Other | Polls |
|---|---|---|---|---|
| 18-24 | 37,816.0 | 14,250.0 | 268.0 | 124,285.0 |
| 25-34 | 62,521.0 | 26,576.0 | 391.0 | 227,821.0 |
| 35-44 | 90,078.0 | 37,895.0 | 637.0 | 314,313.0 |
| 45-54 | 132,525.0 | 36,769.0 | 575.0 | 320,894.0 |
| 55-64 | 242,954.0 | 49,345.0 | 638.0 | 326,744.0 |
| 65-74 | 298,414.0 | 69,586.0 | 727.0 | 239,951.0 |
| 75+ | 211,101.0 | 82,750.0 | 1,081.0 | 146,805.0 |
| Unknown | 716.0 | 63.0 | 3.0 | 3,420.0 |

By party bucket:

| party_bucket | AB_Inperson | AB_Mail | AB_Other | Polls |
|---|---|---|---|---|
| Dem | 466,681.0 | 190,098.0 | 1,830.0 | 618,252.0 |
| Rep | 363,524.0 | 57,110.0 | 1,112.0 | 483,228.0 |
| Unknown/Ind | 245,920.0 | 70,026.0 | 1,378.0 | 602,753.0 |

## 5f. Geography

Top 10 localities by LTV voter count:

| locality | ltv_voters |
|---|---|
| FAIRFAX COUNTY | 386,216 |
| CHESTERFIELD COUNTY | 151,882 |
| VIRGINIA BEACH CITY | 150,861 |
| LOUDOUN COUNTY | 148,108 |
| PRINCE WILLIAM COUNTY | 146,694 |
| HENRICO COUNTY | 129,781 |
| CHESAPEAKE CITY | 86,836 |
| ARLINGTON COUNTY | 84,048 |
| RICHMOND CITY | 75,424 |
| STAFFORD COUNTY | 56,473 |

Top 10 localities by turnout % (LTV voters / RVL active; Covington/Sussex excluded):

| locality | voted | reg | turnout_pct |
|---|---|---|---|
| GOOCHLAND COUNTY | 16,079 | 23,964 | 67.1 |
| POWHATAN COUNTY | 16,078 | 24,818 | 64.8 |
| HANOVER COUNTY | 56,035 | 87,325 | 64.2 |
| MATHEWS COUNTY | 4,708 | 7,356 | 64.0 |
| RAPPAHANNOCK COUNTY | 3,895 | 6,153 | 63.3 |
| HIGHLAND COUNTY | 1,146 | 1,813 | 63.2 |
| MIDDLESEX COUNTY | 5,448 | 8,618 | 63.2 |
| LANCASTER COUNTY | 5,818 | 9,225 | 63.1 |
| BOTETOURT COUNTY | 16,753 | 26,738 | 62.7 |
| NORTHUMBERLAND COUNTY | 6,420 | 10,319 | 62.2 |

Strongest YES localities — voter profile:

| name | yes_pct | avg_age | pct_female | pct_firsttime |
|---|---|---|---|---|
| PETERSBURG CITY | 87.0 | 58.2 | 61.6 | 1.4 |
| CHARLOTTESVILLE CITY | 85.4 | 48.4 | 56.0 | 2.6 |
| RICHMOND CITY | 83.0 | 48.8 | 56.8 | 2.1 |
| FALLS CHURCH CITY | 80.8 | 52.5 | 52.4 | 2.8 |
| ARLINGTON COUNTY | 79.9 | 48.8 | 52.2 | 2.9 |
| ALEXANDRIA CITY | 79.0 | 51.4 | 55.4 | 2.6 |
| NORFOLK CITY | 71.5 | 54.7 | 57.2 | 2.6 |
| HAMPTON CITY | 70.7 | 56.3 | 58.2 | 2.5 |
| PORTSMOUTH CITY | 70.7 | 56.1 | 58.6 | 1.7 |
| FAIRFAX COUNTY | 69.7 | 53.5 | 52.3 | 2.2 |

Strongest NO localities — voter profile:

| name | yes_pct | avg_age | pct_female | pct_firsttime |
|---|---|---|---|---|
| LEE COUNTY | 11.0 | 57.2 | 50.2 | 2.3 |
| SCOTT COUNTY | 11.5 | 57.6 | 49.8 | 2.1 |
| BUCHANAN COUNTY | 11.9 | 58.1 | 49.4 | 1.7 |
| TAZEWELL COUNTY | 12.4 | 58.2 | 51.6 | 1.9 |
| BLAND COUNTY | 12.4 | 57.6 | 48.7 | 1.9 |
| RUSSELL COUNTY | 13.0 | 56.3 | 50.6 | 1.9 |
| WISE COUNTY | 14.6 | 57.1 | 50.4 | 1.8 |
| CRAIG COUNTY | 15.5 | 57.0 | 49.2 | 1.2 |
| CARROLL COUNTY | 15.7 | 58.3 | 51.3 | 2.6 |
| SMYTH COUNTY | 15.9 | 57.1 | 51.2 | 2.5 |

## 5g. Party (from Van LikelyParty; denominator = Van registered)

| party_bucket | voted | registered | turnout_pct | share_of_voters_pct |
|---|---|---|---|---|
| Rep | 904,974 | 1,240,690 | 72.9 | 29.2 |
| Dem | 1,276,861 | 2,135,992 | 59.8 | 41.2 |
| Unknown/Ind | 920,077 | 3,009,694 | 30.6 | 29.7 |

Dem turnout 59.8% vs Rep turnout 72.9% — skew of 13.1 pp toward Rep.

## 5h. Anomaly scan

Precinct turnout: statewide mean 52.1%, SD 9.2pp (precincts with >=100 active reg; Covington/Sussex excluded). **101 precincts** beyond ±2 SD (33.8% / 70.5%).

| locality | precinct | voted | reg | turnout_pct | z |
|---|---|---|---|---|---|
| PRINCE WILLIAM COUNTY | 304 - QUANTICO | 158 | 1,162 | 13.6 | -4.2 |
| RICHMOND CITY | 310 - THREE HUNDRED TEN | 125 | 859 | 14.6 | -4.1 |
| HAMPTON CITY | 113 - HAMPTON UNIVERSITY | 505 | 2,311 | 21.9 | -3.3 |
| RICHMOND CITY | 602 - SIX HUNDRED TWO | 480 | 2,180 | 22.0 | -3.3 |
| NORFOLK CITY | 104 - TITUSTOWN  | 535 | 2,392 | 22.4 | -3.2 |
| MONTGOMERY COUNTY | 603 - PRECINCT F-3 | 252 | 1,068 | 23.6 | -3.1 |
| NEWPORT NEWS CITY | 305 - DOWNTOWN | 242 | 961 | 25.2 | -2.9 |
| STAFFORD COUNTY | 406 - AQUIA | 201 | 788 | 25.5 | -2.9 |
| FAIRFAX COUNTY | 134 - UNIVERSITY | 613 | 2,394 | 25.6 | -2.9 |
| PORTSMOUTH CITY | 013 - ST. MARK MISSIONARY BAPTIST CHURCH | 343 | 1,335 | 25.7 | -2.9 |
| NORFOLK CITY | 411 - RUFFNER ACADEMY | 452 | 1,697 | 26.6 | -2.8 |
| ALBEMARLE COUNTY | 202 - UNIVERSITY | 1,155 | 4,315 | 26.8 | -2.8 |
| BRISTOL CITY | 003 - THIRD PRECINCT | 619 | 2,308 | 26.8 | -2.8 |
| RICHMOND CITY | 701 - SEVEN HUNDRED ONE | 461 | 1,672 | 27.6 | -2.7 |
| HOPEWELL CITY | 201 - WARD TWO | 553 | 1,971 | 28.1 | -2.6 |
| NEWPORT NEWS CITY | 312 - NEWSOME PARK | 269 | 956 | 28.1 | -2.6 |
| RICHMOND CITY | 610 - SIX HUNDRED TEN | 536 | 1,890 | 28.4 | -2.6 |
| PRINCE GEORGE COUNTY | 205 - JEFFERSON PARK | 874 | 3,041 | 28.7 | -2.5 |
| NORFOLK CITY | 414 - YOUNG PARK | 791 | 2,718 | 29.1 | -2.5 |
| PORTSMOUTH CITY | 016 - CRADOCK MIDDLE SCHOOL | 649 | 2,229 | 29.1 | -2.5 |
| LEE COUNTY | 501 - SAINT CHARLES | 200 | 681 | 29.4 | -2.5 |
| NEWPORT NEWS CITY | 308 - JEFFERSON | 327 | 1,111 | 29.4 | -2.5 |
| VIRGINIA BEACH CITY | 061 - PRECINCT 61 | 1,186 | 4,023 | 29.5 | -2.5 |
| EMPORIA CITY | 501 - PRECINCT 5-1 | 141 | 478 | 29.5 | -2.5 |
| EMPORIA CITY | 701 - DISTRICT 7 | 141 | 474 | 29.7 | -2.4 |
| FAIRFAX COUNTY | 736 - BEDFORD | 166 | 558 | 29.7 | -2.4 |
| ROANOKE CITY | 019 - Forest Park | 1,005 | 3,361 | 29.9 | -2.4 |
| VIRGINIA BEACH CITY | 076 - PRECINCT 76 | 1,097 | 3,666 | 29.9 | -2.4 |
| ROANOKE CITY | 008 - Lincoln Terrace | 879 | 2,908 | 30.2 | -2.4 |
| MARTINSVILLE CITY | 003 - PRECINCT #3 | 397 | 1,311 | 30.3 | -2.4 |

**Voters not matching a current RVL record: 2 (0.00%)** — pre-RVL-refresh new registrations, data-quality mismatches, or voters since removed from the roll.
