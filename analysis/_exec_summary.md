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

