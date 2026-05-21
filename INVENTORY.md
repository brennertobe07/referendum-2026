# Referendum 2026 — Project Inventory
**Election:** Virginia Constitutional Amendment Referendum
**Election Date:** 2026-04-21
**Inventory Generated:** 2026-05-21
**Status:** Wrap-up

## 1. Overview

On April 21, 2026 Virginia held a statewide special election on a Constitutional
Amendment Referendum (SBE election code `13469`, "2026 April 21 Special"). The DPVA
data operation tracked the cycle end-to-end: a daily absentee pipeline pulled the SBE
`Daily_Absentee_List`, snapshotted it, refreshed cure tracking, and published the
public **absentee.vadems.org** and **cure.vadems.org** dashboards; an Election Night
Reporting (ENR) pipeline polled the SBE results feed every ~2 minutes and published
**enr.vadems.org**. Absentee voting opened in early March 2026 (first daily snapshot
2026-03-06) and ran through election day; the operational pipelines were wound down
and most Task Scheduler jobs disabled by mid-May 2026.

The post-election "List of Those Who Voted" (LTV) file `LTV2026_Ref.csv` was published
by SBE on 2026-05-21 and contains **3,101,912 voter rows** (50 columns, identical
schema to `LTV2025_GEN`). The final `Daily_Absentee_List` snapshot holds 1,520,270
absentee records for the cycle. Top-line turnout/result figures are pending the
Phase 4 reconciliation against the SBE results file
(`Election Results2026_Ref.csv`) and are recorded there once validated.

## 2. Scripts
| Path | Purpose | Language | Schedule | Repo | Notes |
|------|---------|----------|----------|------|-------|
| `C:\Scripts\Python\Python_Absentee\absentee_pipeline.py` | Main daily absentee pipeline (download → extract → load DAL → snapshot → cure refresh) | Python 3.12 | Task `Download Absentee2` (~6:00 AM) — **Disabled** | — | Reads `elections_config.json` |
| `C:\Scripts\Python\Python_Absentee\export_dashboards.py` | Wrapper: historical load + build all dashboard JSON + git push | Python 3.12 | Task `Update_Dashboards` (~7:00 AM) — **Disabled** | — | Logs to `export_dashboards_log.txt` |
| `C:\Scripts\Python\Python_Absentee\load_historical_daily.py` | Loads daily zip archives into `Historical_Daily_Totals` | Python 3.12 | via `export_dashboards.py` | — | — |
| `C:\Scripts\Python\Python_Absentee\export_comparison_json.py` | Writes `comparison.json` (Historical Comparison tab) | Python 3.12 | via `export_dashboards.py` | april-referendum-absentee | — |
| `C:\Scripts\Python\Python_Absentee\backup_cure_history.py` | Exports `Cure_History` to dated CSV in `C:\Absentee\Cure_backup\` | Python 3.12 | ~6:30 AM (per reference doc) | — | — |
| `C:\Scripts\Python\Python_Absentee\backup_absentee_pipeline.py` | Creates backup zip of all pipeline files | Python 3.12 | manual / pre-wrap | — | Output in `C:\Scripts\Python\Backups\` |
| `C:\Scripts\Python\Python_Absentee\upload_absentee.py` | Upload absentee data | Python 3.12 | Task `Upload_Absentee_Pheonix` — **Disabled** | — | — |
| `C:\Scripts\Python\Python_Absentee\April\april-referendum-absentee\build_april_absentee_json.py` | Builds absentee dashboard JSON (precincts/counties/summary/daily/metadata) | Python 3.12 | via `export_dashboards.py` | april-referendum-absentee | — |
| `C:\Scripts\Python\export_cure_dashboard.py` | Builds cure dashboard JSON (`cure_data.json`) | Python 3.12 | via `export_dashboards.py` | va-cure | `TARGET_HDS` defined here |
| `C:\Scripts\Python\Python_Absentee\hd98\hd98_absentee_report_v5.py` | HD98 special absentee report | Python 3.12 | Task `HD98_Report` — **Disabled** | — | Separate HD98 special |
| `C:\Scripts\Python\Python_Absentee\ElectionConfigManager.html` | GUI editor for `elections_config.json` | HTML | n/a | — | — |
| `C:\Scripts\Python\Python_ElectionResults\enr_pipeline.py` | ENR pipeline: poll SBE results feed, enrich, write JSON | Python 3.12 | election-night | april-referendum-enr | Polls every ~2 min |
| `C:\Scripts\Python\Python_ElectionResults\push_enr.py` | Push ENR JSON to repo / GitHub Pages | Python 3.12 | Tasks `ENR_DATA_PUSH_60SECONDS`, `ENR_updateAbsentee` — **Disabled** | april-referendum-enr | — |
| `C:\Scripts\Python\Python_ElectionResults\load_voter_registrants.py` | Loads monthly voter registrant counts | Python 3.12 | monthly | — | Pairs with `create_monthly_registrant_count.sql` |
| `C:\Scripts\Python\Python_ElectionResults\backup_enr.bat` / `backup_full_recovery.bat` | ENR backup batch jobs | Batch | manual | — | — |
| `C:\Scripts\Python\Python_LTWV\load_LTV2026_Ref.py` | LTV loader for this referendum | Python 3.12 | n/a (one-time) | referendum-2026 (pending) | **Created in Phase 2** |

## 3. SQL Objects
| Server.Database.Schema.Object | Type | Purpose | Created | Dependencies |
|-------------------------------|------|---------|---------|--------------|
| INSTANCE-1.Historic.dbo.LTV2026_Ref | TABLE | LTV "those who voted" for Apr 21 2026 referendum (3,101,912 rows, 50 cols NVARCHAR(255)) | 2026-05-21 (Phase 2) | source CSV |
| INSTANCE-1.Historic.dbo.LTV2026_Ref_Votemethod | TABLE | Derived vote-method (Polls / AB_Inperson / AB_Mail / AB_Other) per voter, 3,101,912 rows | 2026-05-21 (Phase 2b) | LTV2026_Ref, Absentee.dbo.Daily_Absentee_List |
| INSTANCE-1.Historic.dbo.LTV2026_Ref_Base | TABLE | Phase 5 analysis base: LTV voters enriched with Van party/score/vote-history + RVL-match + age/age-band/party-bucket, 3,101,912 rows | 2026-05-21 (Phase 5) | LTV2026_Ref, LTV2026_Ref_Votemethod, Voter.dbo.Van, Voter.dbo.RVL |
| INSTANCE-1.Historic.dbo.LTV2025_GEN | TABLE | Prior LTV (2025 General) — schema reference | 2026-01-16 | — |
| INSTANCE-1.Historic.dbo.LTV2025_GEN_Votemethod | TABLE | 2025 General vote-method detail | 2026-01-22 | — |
| INSTANCE-1.Historic.dbo.LTV* (19 tables, 2020–2025) | TABLE | Historical LTV files per cycle | 2024–2026 | — |
| INSTANCE-1.Absentee.dbo.Daily_Absentee_List | TABLE | Current absentee snapshot — holds 26SP_Apr (1,520,270 rows) | rebuilt 2026-05-09 | SBE feed |
| INSTANCE-1.Absentee.dbo.DAL_26SP_Apr_* | TABLE | Daily absentee snapshots (subset of 92 `DAL_*` tables) | Mar–Apr 2026 | — |
| INSTANCE-1.Absentee.dbo.Cure_History | TABLE | Cumulative cure / rejection tracking | 2026-03-13 | `usp_Refresh_Cure_History` |
| INSTANCE-1.Absentee.dbo.Historical_Daily_Totals | TABLE | Daily aggregated counts per election | 2026-03-25 | `load_historical_daily.py` |
| INSTANCE-1.Absentee.dbo.dropped_today | TABLE | Voters dropped since first snapshot | — | — |
| INSTANCE-1.Absentee.dbo.usp_Refresh_Cure_History | PROC | Refreshes Cure_History from Daily_Absentee_List | — | Daily_Absentee_List |
| INSTANCE-1.Absentee.dbo.van | VIEW | Join to Voter.dbo.Van for party/score | — | Voter.dbo.Van |
| INSTANCE-1.Voter.dbo.RVL | TABLE | Registered Voter List (current file) | — | — |
| INSTANCE-1.Voter.dbo.Van | VIEW | VAN vote history + party scores | — | — |
| INSTANCE-1.Voter.dbo.County_Twist | TABLE | Locality-name normalization (DAL all-caps ↔ van CountyName) | — | — |
| INSTANCE-1.Elected_VA.* | DB | Official election results | — | — |

## 4. Data Files (local + cloud)
| Path | Format | Source | Retention | Notes |
|------|--------|--------|-----------|-------|
| `C:\Temp\SBE\LTWV\LTV2026_Ref.csv` | CSV (1.27 GB) | SBE | keep | **3,101,912 rows, 50 cols** — Phase 1–2 source |
| `C:\Temp\SBE\LTWV\LTV2026_Ref.zip` | ZIP (147 MB) | SBE | keep | Zipped copy of above |
| `C:\Temp\SBE\Results_Winners\NewFormat\Election Results2026_Ref.csv` | CSV | SBE (election night) | keep | Phase 4 Source A |
| `C:\Temp\SBE\Results_Winners\NewFormat\Election Turnout_2026_Ref.csv` | CSV | SBE | keep | Turnout by locality |
| `C:\Temp\SBE\Results_Winners\NewFormat\EnrAbsenteeRaw_2026_Ref.csv` | CSV | SBE/ENR | keep | ENR absentee raw |
| `C:\Absentee\26SP_Apr\Daily_Absentee_List.csv` | CSV (205 MB) | SBE | keep | Latest extracted DAL |
| `C:\Absentee\26SP_Apr\daily.zip` | ZIP | SBE | keep | Daily download |
| `C:\Temp\SBE\Absentee\2026_Apr21\*.zip` | ZIP (daily) | SBE | keep | ~17 daily DAL snapshots (Mar 6–25) |
| `G:\My Drive\Absentee26SP_Apr\Daily_List\` | ZIP archive | pipeline | archive | Dated daily zips (historical source) |
| `G:\My Drive\Absentee26SP_Apr\Permanent_Absentees\` | CSV | pipeline | archive | Permanent absentee exports |
| `G:\My Drive\Absentee26SP_Apr\03.25.2026 - April 21st Statewide Absentee.zip` | ZIP (353 MB) | SBE | archive | Statewide absentee snapshot |
| `C:\Absentee\Cure_backup\Cure_History_YYYY-MM-DD.csv` | CSV | pipeline | archive | Daily cure backups |
| `C:\Scripts\Python\Backups\DPVA_Pipeline_Backup_20260423_113001.zip` | ZIP (934 KB) | backup script | keep | Latest pipeline backup |
| `C:\DPVA_Projects\Referendum2026\analysis\reconciliation.md` | MD | Phase 4 | keep | Created 2026-05-21 |
| `C:\DPVA_Projects\Referendum2026\analysis\reconcile.py` | PY | Phase 4 | keep | Reconciliation script |
| `C:\DPVA_Projects\Referendum2026\analysis\locality_reconciliation.csv` | CSV | Phase 4 | keep | Per-locality LTV vs ENR |
| `C:\DPVA_Projects\Referendum2026\analysis\LTV2026_Ref_Analysis.md` | MD | Phase 5/6 | keep | Exec summary + 5a–5h |
| `C:\DPVA_Projects\Referendum2026\analysis\LTV2026_Ref_Analysis.xlsx` | XLSX | Phase 5 | keep | One sheet per analysis (5a–5h) |
| `C:\DPVA_Projects\Referendum2026\analysis\analyze.py` | PY | Phase 5 | keep | Builds base table + writes report/xlsx |

## 5. GitHub Repositories
| Repo | Purpose | URL | Local Path | Last Commit |
|------|---------|-----|------------|-------------|
| april-referendum-absentee | Absentee dashboard (absentee.vadems.org) | https://github.com/brennertobe07/april-referendum-absentee | `C:\Scripts\Python\Python_Absentee\April\april-referendum-absentee\` | cbfbeed 2026-05-12 |
| va-cure | Cure dashboard (cure.vadems.org) | https://github.com/brennertobe07/va-cure | `C:\Scripts\Python\Python_Absentee\April\va-cure\` | fb3dc91 2026-05-12 |
| april-referendum-enr | ENR results dashboard (enr.vadems.org) | https://github.com/brennertobe07/april-referendum-enr | `C:\Scripts\Python\Python_ElectionResults\april-referendum-enr\` | 39d06a5 2026-05-12 |
| referendum-2026 | This project home (docs + project SQL) | (pending — not yet created) | `C:\DPVA_Projects\Referendum2026\` | not initialized |

## 6. Live URLs
| URL | What it shows | Auth | Hosted on | Repo source |
|-----|---------------|------|-----------|-------------|
| https://absentee.vadems.org | Absentee dashboard (summary, daily trends, historical comparison) | Cloudflare Zero Trust | GitHub Pages | april-referendum-absentee |
| https://cure.vadems.org | Cure / ballot-rejection dashboard + needs-cure list | Cloudflare Zero Trust | GitHub Pages | va-cure |
| https://enr.vadems.org | Election-night results dashboard | Public (no Zero Trust) | GitHub Pages | april-referendum-enr |

## 7. Scheduled Tasks
All cycle tasks are now **Disabled** (post-election wind-down). Exported full list to `notes\tasks.csv` (via Get-ScheduledTask).

| Task Name | Schedule | Runs | Purpose |
|-----------|----------|------|---------|
| Download Absentee2 | ~6:00 AM daily | `absentee_pipeline.py` | Daily absentee download/load — Disabled |
| Update_Dashboards | ~7:00 AM daily | `export_dashboards.py` | Build + push dashboards — Disabled |
| Upload_Absentee_Pheonix | — | `upload_absentee.py` | Absentee upload — Disabled |
| HD98_Report | — | `hd98_absentee_report_v5.py` | HD98 special report — Disabled |
| ENR_DATA_PUSH_60SECONDS | election night, 60s | `push_enr.py` | ENR push loop — Disabled |
| ENR_updateAbsentee | — | `push_enr.py` | ENR absentee update — Disabled |
| LoadDailyAbsenteeSQL / LoadDaily_Copy / LoadDaily_Dropped | — | `C:\Scripts\BAT\*.bat` | Legacy absentee BAT chain — Disabled |
| (backup_cure_history ~6:30 AM) | ~6:30 AM | `backup_cure_history.py` | Per reference doc; not in current scheduler export |

## 8. External Dependencies
- **SBE / VA Elections feeds** — `apps.elections.virginia.gov` daily absentee zip (per-election GUID URL in `elections_config.json`); SBE ENR results feed (election night); SBE LTV and results CSV downloads.
- **NCEC baselines** — `ncec_counties.json` (Dem performance baselines per locality: demperf26, expvote26, gov25, pres24), extracted from the Vantage project. Located at `C:\Scripts\Python\Python_ElectionResults\ncec_counties.json`.
- **Cloudflare** — DNS (CNAME → GitHub Pages) for `*.vadems.org`; Zero Trust Access controls absentee + cure dashboards (ENR is public).
- **GitHub / GitHub Pages** — user `brennertobe07`; three repos host the dashboards.
- **Google Drive** (`G:\`) — daily archive + permanent absentee exports.
- **API keys / credentials (location only, never values):**
  - Daily-absentee zip password — `elections_config.json` (`zip_password`).
  - SQL Server — Windows integrated auth (trusted connection) to `INSTANCE-1`; no stored SQL credentials.
  - GitHub push — uses local git credential store / GitHub Desktop on this machine.

## 9. Lessons Learned
- LTV schema has been **stable** across cycles: `LTV2026_Ref` matches `LTV2025_GEN` exactly (50 columns, same order, same names). The standard load template applies unchanged.
- The base LTV file carries **no granular vote-method column** — only an `ABSENTEE` flag (True/False). SBE has not published a `*_Votemethod` file for 2026_Ref. **Resolution:** a `LTV2026_Ref_Votemethod` table is derived in Phase 2b from `Absentee.dbo.Daily_Absentee_List`, matching the prior `LTV2025_GEN_Votemethod` schema (`IDENTIFICATION_NUMBER, ABSENTEE, AB_Type, ELECTION_NAME`). Mapping: `BALLOT_STATUS = 'On Machine'` → `AB_Inperson`; `BALLOT_STATUS IN ('Marked','Pre-Processed')` → `AB_Mail`; LTV `ABSENTEE = 'False'` → `Polls` (election day). DAL dedup uses the dashboard priority `Marked > Pre-Processed > On Machine`. This gives full Phase 5e in-person-early / mail / election-day breakdowns.
- SBE LTV files are **fully double-quoted** (RFC-style). Proper CSV parsing strips the quotes — confirmed Phase 3 quote cleanup is a **no-op** (0 rows with leftover quote characters after the `pandas.read_csv` load).
- **Encoding gotcha:** the LTV CSV has no BOM and is ASCII at the top, but accented names deeper in carry Windows-1252/Latin-1 high bytes (e.g. `0xf3`). It is **not valid UTF-8** — `read_csv` must use `encoding='latin-1'` or it fails partway through with `UnicodeDecodeError`. Loader does this.
- **Load gotcha:** `pyodbc` `fast_executemany` pre-allocates a buffer sized to the declared column width × chunk rows. With 50 × NVARCHAR(255), a 50k-row chunk blew past memory (~1.3 GB). Chunk size of **5,000** loads cleanly (~8 min for 3.1M rows).
- `Daily_Absentee_List` was **not** repurposed — it still holds the 26SP_Apr cycle, so Phase 4C can use it directly (no need to fall back to a `DAL_26SP_Apr_*` snapshot).
- **Turnout was NOT low** (Phase 4): the amendment **passed 51.69% Yes / 48.31% No** on **51.06% turnout** (3,103,669 votes on the question; 3,109,181 ballots cast; 6.08M active registered). The "low-turnout April referendum" framing in the original brief is contradicted by the data — this was a high-salience, high-turnout special.
- **Import quality is excellent** (Phase 4): LTV 3,101,912 voters = within −0.234% of SBE ballots cast; distinct IDENTIFICATION_NUMBER = total (no dup voters); Source C absentee match 99.79%; vote-method derivation cross-checks against the SBE turnout file (in-person early near-exact; Election Day/Mail gaps explained by 46,202 provisional/post-election ballots SBE breaks out separately).
- **LTV under-reports two localities** (Phase 4, carry into Phase 5h): COVINGTON CITY (580) and SUSSEX COUNTY (183) appear in LTV at ~1/3 of their actual recorded turnout (codes verified to match ENR — genuine source gap, not a join error). They hold ~half of the statewide LTV deficit. Flag both as incomplete for locality-level analysis.
- **Phase 5 pattern findings:** This was a **base-mobilization** electorate — 76.0% of voters had voted in 3-or-4 of the last 4 Nov generals, only 2.1% were first-time. Turnout rose steeply with age (28.7% at 18–24 → 72.0% at 65–74) and ran 1–5 pp below 2025-General levels in every band. **Rep-leaning voters turned out at 72.9% vs Dem-leaning 59.8%**, but the larger Dem-leaning base (~2.14M vs 1.24M registered) plus independents passed the amendment 51.69% Yes. Vote method: 54.9% election day / 34.7% in-person early / 10.2% mail, with 65+ skewing early/mail and under-35s skewing election day.
- **Phase 5 data quality:** LTV→RVL match is essentially perfect (only **2** of 3.1M voters unmatched). The join key `LTV.IDENTIFICATION_NUMBER = Van.StateFileID = RVL.IDENTIFICATION_NUMBER` is reliable; `Van.StateFileID` is unique (no fan-out). Van vote-history columns code voted as non-blank (A/P/Y), non-voters as NULL. `Van.LikelyParty` (SD/LD/SR/LR/ND/I/U) drives party bucketing per the dashboard convention. Covington/Sussex under-report (above) is the only material locality gap; 101 precincts exceed ±2 SD turnout but all low-end outliers are explainable (universities, Quantico, downtown cores).
- **Reproducibility:** `analysis\analyze.py` rebuilds `LTV2026_Ref_Base` and regenerates the Phase 5 body of `LTV2026_Ref_Analysis.md` + the `.xlsx`. The Phase 6 executive summary is hand-authored at the top of the `.md`; re-running `analyze.py` overwrites the file, so preserve the exec summary if regenerating.

## 10. Wrap-up Checklist
- [ ] All scripts committed to git
- [ ] Final backup zip in C:\Scripts\Python\Backups\
- [ ] Google Drive archive moved from Daily_List\ to Absentee_Archive\
- [ ] SQL tables documented in section 3
- [ ] Reference docs current
- [ ] Live URLs decommissioned or repurposed for next cycle
- [ ] Inventory marked Archived
