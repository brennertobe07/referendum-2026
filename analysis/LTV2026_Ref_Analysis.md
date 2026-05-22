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

1. **Base mobilization, not a new electorate.** 75.4% of voters had voted in 3 or 4 of
   the last 4 November generals; only 10.0% had voted in 0 or 1. First-time voters were
   just **2.1%**. The referendum turned out the habitual electorate — it did not pull in
   new or marginal voters.
2. **Republicans voted at higher intensity, but Democrats' larger base won it.**
   Using the absentee-dashboard party rule (party ID, then Dem-support score split at 50),
   Rep turnout was **52.9%** vs Dem **45.0%** (an ~8 pp gap), yet the measure passed because
   Dem-leaning registrants outnumber Republicans ~3.7M to 2.7M and were the **majority of
   voters (53.4% vs 46.6%)** — consistent with Yes winning. Geography was sharply partisan:
   strongest Yes in urban / NoVa localities (Petersburg 87%, Charlottesville 85%, Richmond
   83%, Arlington 80%), strongest No in southwest Virginia (Lee 11%, Scott 12%, Buchanan 12%).
3. **Turnout climbs steeply with age.** 28.7% (18–24) → 72.0% (65–74), with women
   turning out 2 pp higher than men (52.8% vs 50.8%).
4. **Vote method skews old-early, young-day.** Statewide 54.9% voted election day,
   34.7% in-person early, 10.2% mail. The 65+ bands voted early/mail at far higher
   rates; under-35s concentrated on election day.
5. **Voter churn vs 2025 (re-mobilization target).** 19.9% of 2025-General voters
   (682,378) didn't return; meanwhile 357,726 referendum voters (11.5%) hadn't voted
   the 2025 General — a **net change of ≈ −325k** vs the 2025 electorate. Drop-off
   skewed **young** (42% of 18–24) and **Democratic** (22.3% vs 17.0% Rep), while the
   surge skewed young but **slightly Republican** (12.6% vs 10.6%): Democrats lost more
   of their 2025 base *and* replaced less of it, winning on base size. Highest drop-off
   volume in NoVa/urban (Fairfax ~100k, ~81k of it Democratic); highest rate in college
   towns (Harrisonburg, Charlottesville, Williamsburg). Priority re-engagement universe:
   young, Dem-leaning 2025 voters. See §5i–5j (and the companion churn brief).

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

_Generated 2026-05-22 (refreshed VAN image; Dem_Support_26 score). Base table `Historic.dbo.LTV2026_Ref_Base` = 3,101,912 LTV voters enriched with Van party/history + RVL match._

> **Caveats:** turnout denominators use RVL `STATUS='Active'`; party uses the absentee-dashboard rule (SD/LD=Dem, SR/LR=Rep, then ND/U/I split by `Dem_Support_26` at 50; only no-score/no-VAN = Unknown); baseline = 2025 General (Van `General25`). COVINGTON CITY (580) and SUSSEX COUNTY (183) are under-reported in the LTV source (~1/3 of actual) — locality-level rows for them are unreliable; statewide/demographic results are unaffected (<0.1%).

## 5a. First-time voters

- **First-time (broad): 64,598 (2.1% of voters)** = 64,495 matched in Van with no prior vote + 103 with no Van record (likely new registrations after the Van snapshot).
- Returning voters (≥1 prior election in Van): 3,037,314 (97.9%).

First-time voters by age band:

| age_band | first_time |
|---|---|
| 18-24 | 28,172 |
| 25-34 | 9,213 |
| 35-44 | 7,417 |
| 45-54 | 4,975 |
| 55-64 | 4,797 |
| 65-74 | 3,885 |
| 75+ | 1,938 |
| Unknown | 4,201 |

First-time voters by party bucket:

| party_bucket | first_time |
|---|---|
| Dem | 36,174 |
| Rep | 28,315 |
| Unknown | 109 |

_Comparison: 108,974 of 5,984,412 active registered voters (1.8%) registered after the Nov 2025 general — the referendum's first-time share (2.1%) exceeds that baseline._

## 5b. Age and generation

Turnout % = LTV voters / RVL active registered, by age (as of 2026-04-21). Baseline = 2025 General turnout in Van.

| age_band | voted | registered | turnout_pct | baseline_2025G_pct | vs_baseline_pp |
|---|---|---|---|---|---|
| 18-24 | 176,619 | 614,479 | 28.7 | 32 | -3.3 |
| 25-34 | 317,309 | 984,152 | 32.2 | 34.1 | -1.9 |
| 35-44 | 442,923 | 996,216 | 44.5 | 46.4 | -1.9 |
| 45-54 | 490,763 | 906,307 | 54.1 | 57 | -2.9 |
| 55-64 | 619,681 | 970,283 | 63.9 | 65.4 | -1.5 |
| 65-74 | 608,678 | 845,492 | 72 | 72.8 | -0.8 |
| 75+ | 441,737 | 648,585 | 68.1 | 70.5 | -2.4 |
| Unknown | 4,202 | 18,898 | 22.2 | 0 | 22.2 |

Referendum turnout by age × party (Van universe; Rep intensity higher at every age):

| age_band | Dem_turnout_pct | Rep_turnout_pct | Rep_minus_Dem_pp |
|---|---|---|---|
| 18-24 | 24.7 | 30.5 | 5.8 |
| 25-34 | 26.5 | 31 | 4.5 |
| 35-44 | 39.1 | 43.1 | 4 |
| 45-54 | 49.4 | 53.2 | 3.8 |
| 55-64 | 58.3 | 63.8 | 5.5 |
| 65-74 | 67.5 | 71.7 | 4.2 |
| 75+ | 64.3 | 67.2 | 2.9 |

## 5c. Gender

| gender | voted | registered | turnout_pct | baseline_2025G_pct | vs_baseline_pp |
|---|---|---|---|---|---|
| F | 1,663,406 | 3,150,405 | 52.8 | 55.1 | -2.3 |
| M | 1,425,423 | 2,804,708 | 50.8 | 51.6 | -0.8 |

## 5d. Vote history pattern (last 4 Nov generals: 2022-2025)

Among LTV voters matched in Van:

| generals_voted_of_4 | voters | pct |
|---|---|---|
| 0 | 86,682 | 2.8 |
| 1 | 224,150 | 7.2 |
| 2 | 452,628 | 14.6 |
| 3 | 594,892 | 19.2 |
| 4 | 1,743,457 | 56.2 |

**3-of-4 or 4-of-4: 2,338,349 (75.4%)** vs **0-of-4 or 1-of-4: 310,832 (10.0%)**. This referendum is a **base mobilization** story.

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
| Dem | 562,319 | 230,690 | 2,421 | 862,020 |
| Rep | 513,769 | 86,535 | 1,898 | 842,144 |
| Unknown | 37 | 9 | 1 | 69 |

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
| ARLINGTON COUNTY | 79.9 | 48.8 | 52.2 | 2.8 |
| ALEXANDRIA CITY | 79.0 | 51.4 | 55.4 | 2.6 |
| NORFOLK CITY | 71.5 | 54.7 | 57.2 | 2.6 |
| HAMPTON CITY | 70.7 | 56.3 | 58.2 | 2.4 |
| PORTSMOUTH CITY | 70.7 | 56.1 | 58.6 | 1.7 |
| FAIRFAX COUNTY | 69.7 | 53.5 | 52.3 | 2.2 |

Strongest NO localities — voter profile:

| name | yes_pct | avg_age | pct_female | pct_firsttime |
|---|---|---|---|---|
| LEE COUNTY | 11.0 | 57.2 | 50.2 | 2.2 |
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

Party assigned the same way as the absentee/cure dashboards: hard party ID (SD/LD=Dem, SR/LR=Rep), then ND/U/I split by `Dem_Support_26` at 50; only no-score / no-VAN-match is Unknown. Turnout % = LTV voters / Van registered.

| party_bucket | voted | registered | turnout_pct | share_of_voters_pct |
|---|---|---|---|---|
| Dem | 1,657,450 | 3,684,105 | 45 | 53.4 |
| Rep | 1,444,346 | 2,728,191 | 52.9 | 46.6 |
| Unknown | 116 | 16 | 725 | 0 |

Rep turnout 52.9% vs Dem turnout 45.0% — skew of 7.9 pp toward Rep. But Democrats were the larger share of the electorate (53.4% of voters vs 46.6% Republican), consistent with the Yes side winning.

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

Of **3,426,461** voters who cast a 2025 General ballot and are still registered in VAN, **2,744,083 returned (80.1%)** for the referendum and **682,378 dropped off (19.9%)**. (An ~80% hold from a Governor's-year general to an April special is high.) Drop-off rate below = skipped ÷ 2025G voters in the group.

By party (dashboard methodology):

| party_bucket | g25_voters | dropped_off | dropoff_pct |
|---|---|---|---|
| Dem | 1,906,755 | 424,409 | 22.3 |
| Rep | 1,519,706 | 257,969 | 17 |

By age band:

| age_band | g25_voters | dropped_off | dropoff_pct |
|---|---|---|---|
| 18-24 | 208,637 | 87,710 | 42 |
| 25-34 | 384,234 | 125,706 | 32.7 |
| 35-44 | 505,280 | 124,465 | 24.6 |
| 45-54 | 547,394 | 112,808 | 20.6 |
| 55-64 | 664,346 | 101,967 | 15.3 |
| 65-74 | 638,302 | 70,058 | 11 |
| 75+ | 478,267 | 59,664 | 12.5 |
| Unknown | 1 | 0 | 0 |

By gender:

| gender | g25_voters | dropped_off | dropoff_pct |
|---|---|---|---|
| M | 1,558,834 | 297,910 | 19.1 |
| F | 1,862,184 | 382,591 | 20.5 |

By Congressional District:

| CD | g25_voters | dropped_off | dropoff_pct |
|---|---|---|---|
| 001 | 396,228 | 69,469 | 17.5 |
| 002 | 311,946 | 61,597 | 19.7 |
| 003 | 239,107 | 51,960 | 21.7 |
| 004 | 306,713 | 66,709 | 21.7 |
| 005 | 345,044 | 58,803 | 17 |
| 006 | 308,674 | 52,728 | 17.1 |
| 007 | 301,386 | 62,801 | 20.8 |
| 008 | 299,251 | 69,103 | 23.1 |
| 009 | 290,026 | 50,919 | 17.6 |
| 010 | 310,993 | 67,486 | 21.7 |
| 011 | 317,093 | 70,803 | 22.3 |

Top 12 localities by drop-off **count** (where the lost voters are):

| locality | g25_voters | dropped_off | dropoff_pct |
|---|---|---|---|
| Fairfax | 446,083 | 100,138 | 22.4 |
| Loudoun | 168,650 | 38,862 | 23 |
| Prince William | 165,513 | 37,313 | 22.5 |
| Virginia Beach (City) | 169,391 | 35,630 | 21 |
| Chesterfield | 170,422 | 33,114 | 19.4 |
| Henrico | 148,487 | 30,238 | 20.4 |
| Arlington | 99,223 | 22,954 | 23.1 |
| Richmond (City) | 90,011 | 21,517 | 23.9 |
| Chesapeake (City) | 96,216 | 19,609 | 20.4 |
| Alexandria (City) | 62,719 | 14,852 | 23.7 |
| Norfolk (City) | 63,393 | 14,321 | 22.6 |
| Stafford | 63,115 | 13,138 | 20.8 |

Top 12 localities by drop-off **rate** (min 5,000 2025G voters):

| locality | g25_voters | dropped_off | dropoff_pct |
|---|---|---|---|
| Harrisonburg (City) | 13,140 | 3,634 | 27.7 |
| Hopewell (City) | 6,646 | 1,659 | 25 |
| Fredericksburg (City) | 10,559 | 2,625 | 24.9 |
| Richmond (City) | 90,011 | 21,517 | 23.9 |
| Charlottesville (City) | 18,646 | 4,428 | 23.7 |
| Petersburg (City) | 9,956 | 2,363 | 23.7 |
| Alexandria (City) | 62,719 | 14,852 | 23.7 |
| Buchanan | 5,406 | 1,275 | 23.6 |
| Williamsburg (City) | 6,572 | 1,537 | 23.4 |
| Arlington | 99,223 | 22,954 | 23.1 |
| Loudoun | 168,650 | 38,862 | 23 |
| Wise | 11,056 | 2,510 | 22.7 |

Top 12 localities by drop-off **count, split by party**:

| locality | Dem | Rep | total |
|---|---|---|---|
| Fairfax | 81,345 | 18,793 | 100,138 |
| Loudoun | 25,817 | 13,045 | 38,862 |
| Prince William | 26,763 | 10,550 | 37,313 |
| Virginia Beach (City) | 19,901 | 15,729 | 35,630 |
| Chesterfield | 20,615 | 12,499 | 33,114 |
| Henrico | 22,285 | 7,953 | 30,238 |
| Arlington | 20,390 | 2,564 | 22,954 |
| Richmond (City) | 19,507 | 2,010 | 21,517 |
| Chesapeake (City) | 10,984 | 8,625 | 19,609 |
| Alexandria (City) | 13,130 | 1,722 | 14,852 |
| Norfolk (City) | 11,993 | 2,328 | 14,321 |
| Stafford | 7,375 | 5,763 | 13,138 |

By age × party — drop-off rate within each age band:

| age_band | Dem_dropoff_pct | Rep_dropoff_pct | Dem_minus_Rep_pp |
|---|---|---|---|
| 18-24 | 44.8 | 37.1 | 7.7 |
| 25-34 | 34.5 | 29.3 | 5.2 |
| 35-44 | 25.7 | 22.9 | 2.8 |
| 45-54 | 22.2 | 18.5 | 3.7 |
| 55-64 | 17.2 | 13.5 | 3.7 |
| 65-74 | 12.2 | 9.7 | 2.5 |
| 75+ | 13.2 | 11.8 | 1.4 |

**Takeaway:** drop-off skews young (42.0% of 18–24) and Democratic (22.3% Dem vs 17.0% Rep) — the re-mobilization universe is young, Dem-leaning 2025 voters, concentrated in NoVa/urban localities (by count) and college towns (by rate).

## 5j. Surge — referendum voters who skipped the 2025 General

Of **3,101,809** referendum voters present in VAN, **357,726 (11.5%)** did **not** vote in the 2025 General — the newer / irregular voters this referendum activated (vs 2,744,083 who voted both). Surge rate below = skipped-2025G ÷ referendum voters in the group. (A further 103 referendum voters have no VAN record at all — down from ~25k before the VAN refresh now ingested the new registrations.)

By party (dashboard methodology):

| party_bucket | ref_voters | surge | surge_pct |
|---|---|---|---|
| Dem | 1,657,450 | 175,104 | 10.6 |
| Rep | 1,444,346 | 182,609 | 12.6 |
| Unknown | 13 | 13 | 100 |

By age band:

| age_band | ref_voters | surge | surge_pct |
|---|---|---|---|
| 18-24 | 175,031 | 54,104 | 30.9 |
| 25-34 | 316,406 | 57,878 | 18.3 |
| 35-44 | 442,097 | 61,282 | 13.9 |
| 45-54 | 489,973 | 55,387 | 11.3 |
| 55-64 | 619,188 | 56,809 | 9.2 |
| 65-74 | 609,813 | 41,569 | 6.8 |
| 75+ | 445,911 | 27,308 | 6.1 |
| Unknown | 3,390 | 3,389 | 100 |

By gender:

| gender | ref_voters | surge | surge_pct |
|---|---|---|---|
| M | 1,429,269 | 168,345 | 11.8 |
| F | 1,668,186 | 188,593 | 11.3 |

By Congressional District:

| CD | ref_voters | surge | surge_pct |
|---|---|---|---|
| 001 | 361,010 | 34,251 | 9.5 |
| 002 | 282,484 | 32,135 | 11.4 |
| 003 | 213,583 | 26,436 | 12.4 |
| 004 | 267,204 | 27,200 | 10.2 |
| 005 | 324,222 | 37,981 | 11.7 |
| 006 | 294,703 | 38,757 | 13.2 |
| 007 | 271,855 | 33,270 | 12.2 |
| 008 | 254,465 | 24,317 | 9.6 |
| 009 | 280,295 | 41,188 | 14.7 |
| 010 | 276,618 | 33,111 | 12 |
| 011 | 275,370 | 29,080 | 10.6 |

Top 12 localities by surge **count**:

| locality | ref_voters | surge | surge_pct |
|---|---|---|---|
| Fairfax | 386,306 | 40,361 | 10.4 |
| Prince William | 146,725 | 18,525 | 12.6 |
| Loudoun | 148,031 | 18,243 | 12.3 |
| Virginia Beach (City) | 150,889 | 17,128 | 11.4 |
| Chesterfield | 151,895 | 14,587 | 9.6 |
| Henrico | 129,799 | 11,550 | 8.9 |
| Chesapeake (City) | 86,819 | 10,212 | 11.8 |
| Arlington | 84,105 | 7,836 | 9.3 |
| Norfolk (City) | 56,069 | 6,997 | 12.5 |
| Richmond (City) | 75,402 | 6,908 | 9.2 |
| Spotsylvania | 54,899 | 6,655 | 12.1 |
| Newport News (City) | 50,804 | 6,557 | 12.9 |

By age × party — surge rate within each age band:

| age_band | Dem_surge_pct | Rep_surge_pct | Dem_minus_Rep_pp |
|---|---|---|---|
| 18-24 | 28.2 | 34.8 | -6.6 |
| 25-34 | 15.3 | 23 | -7.7 |
| 35-44 | 11.8 | 16.8 | -5 |
| 45-54 | 9.9 | 13.1 | -3.2 |
| 55-64 | 8.4 | 10 | -1.6 |
| 65-74 | 6.4 | 7.3 | -0.9 |
| 75+ | 5.6 | 6.6 | -1 |

**Takeaway:** surge (new-to-2025G) voters are disproportionately young (30.9% of 18–24 referendum voters skipped 2025G) and lean Rep (10.6% Dem vs 12.6% Rep). Net churn vs 2025G: ≈+324,652 (682,378 lost − 357,726 gained, VAN-matched).


> _Eligibility note: **13,050** referendum voters turned 18 after the 2025 General (2025-11-04) — eligible for the referendum but not for 2025G — so they count as surge mechanically (3.6% of all surge). Excluding them, the 18–24 surge rate is **25.0%** (vs 30.9% reported): the young tilt is overwhelmingly genuine, not an artifact of newly-eligible voters._
