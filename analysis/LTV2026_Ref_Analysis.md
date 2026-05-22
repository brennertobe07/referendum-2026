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
2. **Republicans voted at higher intensity, but Democrats' larger base won it.**
   Using the absentee-dashboard party rule (party ID, then Dem-support score split at 50),
   Rep turnout was **53.0%** vs Dem **45.1%** (an ~8 pp gap), yet the measure passed because
   Dem-leaning registrants outnumber Republicans ~3.6M to 2.7M and were the **majority of
   voters (52.7% vs 45.4%)** — consistent with Yes winning. Geography was sharply partisan:
   strongest Yes in urban / NoVa localities (Petersburg 87%, Charlottesville 85%, Richmond
   83%, Arlington 80%), strongest No in southwest Virginia (Lee 11%, Scott 12%, Buchanan 12%).
3. **Turnout climbs steeply with age.** 28.7% (18–24) → 72.0% (65–74), with women
   turning out 2 pp higher than men (52.8% vs 50.8%).
4. **Vote method skews old-early, young-day.** Statewide 54.9% voted election day,
   34.7% in-person early, 10.2% mail. The 65+ bands voted early/mail at far higher
   rates; under-35s concentrated on election day.
5. **Voter churn vs 2025 (re-mobilization target).** 20.1% of 2025-General voters
   (690,881) didn't return; meanwhile 332,415 referendum voters (10.8%) hadn't voted
   the 2025 General — a **net change of ≈ −358k** vs the 2025 electorate. Drop-off
   skewed **young** (42% of 18–24) and **Democratic** (22.3% vs 17.1% Rep), while the
   surge skewed young but **slightly Republican** (11.8% vs 9.8%): Democrats lost more
   of their 2025 base *and* replaced less of it, winning on base size. Highest drop-off
   volume in NoVa/urban (Fairfax 101k); highest rate in college towns (Harrisonburg 28%,
   Charlottesville/Williamsburg ~24%). Priority re-engagement universe: young, Dem-leaning
   2025 voters. See §5i–5j (and the companion churn brief).

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

> **Caveats:** turnout denominators use RVL `STATUS='Active'`; party uses the absentee-dashboard rule (SD/LD=Dem, SR/LR=Rep, then ND/U/I split by `Clarity_DemSupport_26` at 50; only no-score/no-VAN = Unknown); baseline = 2025 General (Van `General25`). COVINGTON CITY (580) and SUSSEX COUNTY (183) are under-reported in the LTV source (~1/3 of actual) — locality-level rows for them are unreliable; statewide/demographic results are unaffected (<0.1%).

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
| Unknown | 26,740 |
| Dem | 22,082 |
| Rep | 16,072 |

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
| 65-74 | 608,678 | 845,492 | 72 | 72.8 | -0.8 |
| 75+ | 441,737 | 648,585 | 68.1 | 70 | -1.9 |
| Unknown | 4,202 | 18,898 | 22.2 | 0 | 22.2 |

## 5c. Gender

| gender | voted | registered | turnout_pct | baseline_2025G_pct | vs_baseline_pp |
|---|---|---|---|---|---|
| F | 1,663,406 | 3,150,405 | 52.8 | 55.4 | -2.6 |
| M | 1,425,423 | 2,804,708 | 50.8 | 52 | -1.2 |

## 5d. Vote history pattern (last 4 Nov generals: 2022-2025)

Among LTV voters matched in Van:

| generals_voted_of_4 | voters | pct |
|---|---|---|
| 0 | 61,556 | 2 |
| 1 | 224,079 | 7.3 |
| 2 | 452,566 | 14.7 |
| 3 | 594,794 | 19.3 |
| 4 | 1,743,423 | 56.7 |

**3-of-4 or 4-of-4: 2,338,217 (76.0%)** vs **0-of-4 or 1-of-4: 285,635 (9.3%)**. This referendum is a **base mobilization** story.

## 5e. Vote method (Election day=Polls, In-person early=AB_Inperson, Mail=AB_Mail)

By age band (voter counts):

| age_band | AB_Inperson | AB_Mail | AB_Other | Polls |
|---|---|---|---|---|
| 18-24 | 37,816 | 14,250 | 268 | 124,285 |
| 25-34 | 62,521 | 26,576 | 391 | 227,821 |
| 35-44 | 90,078 | 37,895 | 637 | 314,313 |
| 45-54 | 132,525 | 36,769 | 575 | 320,894 |
| 55-64 | 242,954 | 49,345 | 638 | 326,744 |
| 65-74 | 298,414 | 69,586 | 727 | 239,951 |
| 75+ | 211,101 | 82,750 | 1,081 | 146,805 |
| Unknown | 716 | 63 | 3 | 3,420 |

By party bucket:

| party_bucket | AB_Inperson | AB_Mail | AB_Other | Polls |
|---|---|---|---|---|
| Dem | 557,525 | 229,022 | 2,404 | 844,661 |
| Rep | 505,008 | 85,194 | 1,847 | 817,171 |
| Unknown | 13,592 | 3,018 | 69 | 42,401 |

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
| MATHEWS COUNTY | 4,708 | 7,356 | 64 |
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
| CHARLOTTESVILLE CITY | 85.4 | 48.4 | 56 | 2.6 |
| RICHMOND CITY | 83 | 48.8 | 56.8 | 2.1 |
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
| CRAIG COUNTY | 15.5 | 57 | 49.2 | 1.2 |
| CARROLL COUNTY | 15.7 | 58.3 | 51.3 | 2.6 |
| SMYTH COUNTY | 15.9 | 57.1 | 51.2 | 2.5 |

## 5g. Party (dashboard methodology; denominator = Van registered)

Party assigned the same way as the absentee/cure dashboards: hard party ID (SD/LD=Dem, SR/LR=Rep), then ND/U/I split by `Clarity_DemSupport_26` at 50; only no-score / no-VAN-match is Unknown. Turnout % = LTV voters / Van registered.

| party_bucket | voted | registered | turnout_pct | share_of_voters_pct |
|---|---|---|---|---|
| Dem | 1,633,612 | 3,622,724 | 45.1 | 52.7 |
| Rep | 1,409,220 | 2,659,242 | 53 | 45.4 |
| Unknown | 59,080 | 104,410 | 56.6 | 1.9 |

Rep turnout 53.0% vs Dem turnout 45.1% — skew of 7.9 pp toward Rep. But Democrats were the larger share of the electorate (52.7% of voters vs 45.4% Republican), consistent with the Yes side winning.

## 5h. Anomaly scan

Precinct turnout: statewide mean 52.1%, SD 9.2pp (precincts with >=100 active reg; Covington/Sussex excluded). **101 precincts** beyond ±2 SD (33.8% / 70.5%).

| locality | precinct | voted | reg | turnout_pct | z |
|---|---|---|---|---|---|
| PRINCE WILLIAM COUNTY | 304 - QUANTICO | 158 | 1,162 | 13.6 | -4.2 |
| RICHMOND CITY | 310 - THREE HUNDRED TEN | 125 | 859 | 14.6 | -4.1 |
| HAMPTON CITY | 113 - HAMPTON UNIVERSITY | 505 | 2,311 | 21.9 | -3.3 |
| RICHMOND CITY | 602 - SIX HUNDRED TWO | 480 | 2,180 | 22 | -3.3 |
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

## 5i. Drop-off — 2025 General voters who skipped the referendum

Of **3,434,884** voters who cast a 2025 General ballot and are still registered in VAN, **2,744,003 returned (79.9%)** for the referendum and **690,881 dropped off (20.1%)**. (An ~80% hold from a Governor's-year general to an April special is high.) Drop-off rate below = skipped ÷ 2025G voters in the group.

By party (dashboard methodology):

| party_bucket | g25_voters | dropped_off | dropoff_pct |
|---|---|---|---|
| Dem | 1,898,003 | 423,852 | 22.3 |
| Rep | 1,499,364 | 256,065 | 17.1 |
| Unknown | 37,517 | 10,964 | 29.2 |

By age band:

| age_band | g25_voters | dropped_off | dropoff_pct |
|---|---|---|---|
| 18-24 | 215,728 | 90,516 | 42 |
| 25-34 | 386,335 | 125,803 | 32.6 |
| 35-44 | 507,302 | 124,584 | 24.6 |
| 45-54 | 549,620 | 113,205 | 20.6 |
| 55-64 | 666,243 | 102,423 | 15.4 |
| 65-74 | 636,905 | 71,222 | 11.2 |
| 75+ | 472,749 | 63,128 | 13.4 |
| Unknown | 2 | 0 | 0 |

By gender:

| gender | g25_voters | dropped_off | dropoff_pct |
|---|---|---|---|
| M | 1,563,439 | 302,556 | 19.4 |
| F | 1,865,930 | 386,420 | 20.7 |

By Congressional District:

| CD | g25_voters | dropped_off | dropoff_pct |
|---|---|---|---|
| 001 | 396,961 | 70,343 | 17.7 |
| 002 | 312,810 | 62,387 | 19.9 |
| 003 | 239,973 | 52,758 | 22 |
| 004 | 307,459 | 67,475 | 21.9 |
| 005 | 345,424 | 59,746 | 17.3 |
| 006 | 309,206 | 53,522 | 17.3 |
| 007 | 302,051 | 63,427 | 21 |
| 008 | 300,435 | 69,842 | 23.2 |
| 009 | 290,769 | 51,804 | 17.8 |
| 010 | 311,842 | 68,094 | 21.8 |
| 011 | 317,954 | 71,483 | 22.5 |

Top 12 localities by drop-off **count** (where the lost voters are):

| locality | g25_voters | dropped_off | dropoff_pct |
|---|---|---|---|
| Fairfax | 447,400 | 101,128 | 22.6 |
| Loudoun | 169,052 | 39,141 | 23.2 |
| Prince William | 166,160 | 37,715 | 22.7 |
| Virginia Beach (City) | 170,015 | 36,114 | 21.2 |
| Chesterfield | 170,654 | 33,429 | 19.6 |
| Henrico | 148,965 | 30,621 | 20.6 |
| Arlington | 99,732 | 23,237 | 23.3 |
| Richmond (City) | 90,278 | 21,741 | 24.1 |
| Chesapeake (City) | 96,441 | 19,838 | 20.6 |
| Alexandria (City) | 62,937 | 14,991 | 23.8 |
| Norfolk (City) | 63,595 | 14,522 | 22.8 |
| Stafford | 63,319 | 13,274 | 21 |

Top 12 localities by drop-off **rate** (min 5,000 2025G voters):

| locality | g25_voters | dropped_off | dropoff_pct |
|---|---|---|---|
| Harrisonburg (City) | 13,087 | 3,702 | 28.3 |
| Hopewell (City) | 6,662 | 1,674 | 25.1 |
| Fredericksburg (City) | 10,562 | 2,637 | 25 |
| Charlottesville (City) | 18,516 | 4,464 | 24.1 |
| Richmond (City) | 90,278 | 21,741 | 24.1 |
| Petersburg (City) | 10,009 | 2,408 | 24.1 |
| Williamsburg (City) | 6,478 | 1,544 | 23.8 |
| Alexandria (City) | 62,937 | 14,991 | 23.8 |
| Buchanan | 5,423 | 1,291 | 23.8 |
| Arlington | 99,732 | 23,237 | 23.3 |
| Loudoun | 169,052 | 39,141 | 23.2 |
| Wise | 11,092 | 2,545 | 22.9 |

Top 12 localities by drop-off **count, split by party**:

| locality | Dem | Rep | total |
|---|---|---|---|
| Fairfax | 80,994 | 18,911 | 99,905 |
| Loudoun | 25,684 | 12,959 | 38,643 |
| Prince William | 26,782 | 10,591 | 37,373 |
| Virginia Beach (City) | 19,919 | 15,660 | 35,579 |
| Chesterfield | 20,565 | 12,467 | 33,032 |
| Henrico | 22,273 | 7,984 | 30,257 |
| Arlington | 20,290 | 2,580 | 22,870 |
| Richmond (City) | 19,326 | 2,009 | 21,335 |
| Chesapeake (City) | 10,973 | 8,549 | 19,522 |
| Alexandria (City) | 12,980 | 1,740 | 14,720 |
| Norfolk (City) | 11,977 | 2,329 | 14,306 |
| Stafford | 7,353 | 5,739 | 13,092 |

By age × party — drop-off rate within each age band:

| age_band | Dem_dropoff_pct | Rep_dropoff_pct | Dem_minus_Rep_pp |
|---|---|---|---|
| 18-24 | 44.6 | 37 | 7.6 |
| 25-34 | 34.3 | 29.2 | 5.1 |
| 35-44 | 25.6 | 22.7 | 2.9 |
| 45-54 | 22.1 | 18.4 | 3.7 |
| 55-64 | 17.2 | 13.4 | 3.8 |
| 65-74 | 12.3 | 9.9 | 2.4 |
| 75+ | 14 | 12.6 | 1.4 |

**Takeaway:** drop-off skews young (42.0% of 18–24) and Democratic (22.3% Dem vs 17.1% Rep) — the re-mobilization universe is young, Dem-leaning 2025 voters, concentrated in NoVa/urban localities (by count) and college towns (by rate).

## 5j. Surge — referendum voters who skipped the 2025 General

Of **3,076,418** referendum voters present in VAN, **332,415 (10.8%)** did **not** vote in the 2025 General — the newer / irregular voters this referendum activated (vs 2,744,003 who voted both). Surge rate below = skipped-2025G ÷ referendum voters in the group. (Referendum voters with no VAN record at all — ~25k new registrations — are additional surge not counted here.)

By party (dashboard methodology):

| party_bucket | ref_voters | surge | surge_pct |
|---|---|---|---|
| Dem | 1,633,612 | 159,461 | 9.8 |
| Rep | 1,409,220 | 165,921 | 11.8 |
| Unknown | 33,586 | 7,033 | 20.9 |

By age band:

| age_band | ref_voters | surge | surge_pct |
|---|---|---|---|
| 18-24 | 166,643 | 41,431 | 24.9 |
| 25-34 | 315,837 | 55,305 | 17.5 |
| 35-44 | 441,836 | 59,118 | 13.4 |
| 45-54 | 490,247 | 53,832 | 11 |
| 55-64 | 618,722 | 54,902 | 8.9 |
| 65-74 | 605,380 | 39,697 | 6.6 |
| 75+ | 435,593 | 25,972 | 6 |
| Unknown | 2,160 | 2,158 | 99.9 |

By gender:

| gender | ref_voters | surge | surge_pct |
|---|---|---|---|
| M | 1,417,506 | 156,623 | 11 |
| F | 1,654,723 | 175,213 | 10.6 |

By Congressional District:

| CD | ref_voters | surge | surge_pct |
|---|---|---|---|
| 001 | 357,830 | 31,212 | 8.7 |
| 002 | 280,742 | 30,319 | 10.8 |
| 003 | 212,185 | 24,970 | 11.8 |
| 004 | 265,510 | 25,526 | 9.6 |
| 005 | 320,603 | 34,925 | 10.9 |
| 006 | 292,170 | 36,486 | 12.5 |
| 007 | 269,849 | 31,225 | 11.6 |
| 008 | 252,038 | 21,445 | 8.5 |
| 009 | 278,028 | 39,063 | 14.1 |
| 010 | 274,224 | 30,476 | 11.1 |
| 011 | 273,239 | 26,768 | 9.8 |

Top 12 localities by surge **count**:

| locality | ref_voters | surge | surge_pct |
|---|---|---|---|
| Fairfax | 383,154 | 36,882 | 9.6 |
| Prince William | 145,697 | 17,252 | 11.8 |
| Loudoun | 146,585 | 16,674 | 11.4 |
| Virginia Beach (City) | 150,106 | 16,205 | 10.8 |
| Chesterfield | 150,578 | 13,353 | 8.9 |
| Henrico | 128,979 | 10,635 | 8.2 |
| Chesapeake (City) | 86,216 | 9,613 | 11.1 |
| Arlington | 83,257 | 6,762 | 8.1 |
| Norfolk (City) | 55,646 | 6,573 | 11.8 |
| Richmond (City) | 74,859 | 6,322 | 8.4 |
| Spotsylvania | 54,521 | 6,304 | 11.6 |
| Newport News (City) | 50,574 | 6,265 | 12.4 |

By age × party — surge rate within each age band:

| age_band | Dem_surge_pct | Rep_surge_pct | Dem_minus_Rep_pp |
|---|---|---|---|
| 18-24 | 22.5 | 28.1 | -5.6 |
| 25-34 | 14.4 | 22.1 | -7.7 |
| 35-44 | 11.2 | 16.2 | -5 |
| 45-54 | 9.5 | 12.6 | -3.1 |
| 55-64 | 8 | 9.5 | -1.5 |
| 65-74 | 6.1 | 6.9 | -0.8 |
| 75+ | 5.5 | 6.4 | -0.9 |

**Takeaway:** surge (new-to-2025G) voters are disproportionately young (24.9% of 18–24 referendum voters skipped 2025G) and lean Rep (9.8% Dem vs 11.8% Rep). Net churn vs 2025G: ≈+358,466 (690,881 lost − 332,415 gained, VAN-matched).


> _Eligibility note: **5,375** referendum voters turned 18 after the 2025 General (2025-11-04) — eligible for the referendum but not for 2025G — so they count as surge mechanically (1.6% of all surge). Excluding them, the 18–24 surge rate is **22.8%** (vs 24.9% reported): the young tilt is overwhelmingly genuine, not an artifact of newly-eligible voters._
