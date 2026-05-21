# Referendum 2026 — Import Reconciliation (Phase 4)

_Generated 2026-05-21. Election: 2026 April 21 Special._

## Headline result (SBE / ENR certified)

- **Yes 1,604,276 (51.69%)** vs No 1,499,393 (48.31%) — amendment **PASSED**.
- Votes on question: 3,103,669. Precincts reporting: 100.0%.
- Turnout: **51.06%** of 6,077,919 active registered (6,386,900 total registered).

## Source A — SBE official results & turnout file

| Metric | Count |
|---|---|
| LTV2026_Ref rows (voters) | 3,101,912 |
| LTV distinct IDENTIFICATION_NUMBER | 3,101,912 |
| SBE votes on question (Yes 1,604,276 + No 1,499,393) | 3,103,669 |
| SBE total ballots cast (turnout file TotalVoteTurnout) | 3,109,181 |
| Delta: LTV voters − SBE ballots cast | -7,269 |
| Delta: LTV voters − SBE votes on question | -1,757 |

LTV voters are within **-0.234%** of SBE ballots cast. Expected sign: ballots cast ≥ voters in LTV ≈ votes on question (undervotes make votes-on-question < ballots).

## Source A — vote-method cross-check (SBE turnout vs LTV derivation)

| Method | SBE turnout file | LTV2026_Ref_Votemethod | Note |
|---|---|---|---|
| Election Day | 1,686,905 | 1,704,233 | LTV 'Polls' |
| Early Voting (in-person) | 1,076,823 | 1,076,125 | LTV 'AB_Inperson' |
| Mailed Absentee | 299,251 | 317,234 | LTV 'AB_Mail' |
| Provisional + Post-Election | 46,202 | 4,320 | LTV 'AB_Other' (approx) |

## Source B — ENR app locality reconciliation

LTV voters per locality vs ENR app `total` (votes on question). Localities flagged where |Delta| > 1% of LTV voters: **2**.

| Locality | LTV_Voters | ENR_Ballots | Delta | Δ% |
|---|---|---|---|---|
| COVINGTON CITY | 507 | 1,583 | -1,076 | 212.23% |
| SUSSEX COUNTY | 1,307 | 3,531 | -2,224 | 170.16% |

Statewide: LTV 3,101,912 voters vs ENR 3,103,669 votes-on-question (Δ -1,757). Localities matched: 133.

**Diagnosis of the 2 flagged localities (verified — NOT a join error):** LTV
`LOCALITY_CODE` matches ENR `fips` exactly for both (Covington = 580, Sussex = 183),
and both names align. The gap is a **genuine under-report in the SBE LTV source**:
LTV contains only ~1/3 of the voters these localities actually recorded.

| Locality | LTV turnout implied | Actual turnout (ENR) | Missing voters |
|---|---|---|---|
| COVINGTON CITY (580) | 507 / 3,741 = 13.6% | ~42% | ~1,076 |
| SUSSEX COUNTY (183) | 1,307 / 7,046 = 18.5% | ~50% | ~2,224 |

These two localities account for ~3,300 of the statewide −7,269 LTV-vs-ballots-cast
deficit, i.e. roughly half of all "missing" LTV voters are concentrated in just two
localities. **Action:** treat Covington City and Sussex County as incomplete in
LTV2026_Ref for any locality-level Phase 5 analysis; the statewide and demographic
analyses are unaffected (0.1% of total).

## Source C — Absentee app reconciliation

| Metric | Count |
|---|---|
| LTV absentee voters (ABSENTEE = True) | 1,397,679 |
| LTV election-day voters (ABSENTEE = False) | 1,704,233 |
| DAL accepted absentee ballots (On Machine + Marked + Pre-Processed) | 1,394,745 |
| DAL accepted absentee — distinct voters | 1,394,557 |
| ENR summary ab_voted | 1,394,745 |
| **Match rate (DAL accepted / LTV absentee)** | **99.79%** |
