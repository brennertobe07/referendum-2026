# DPVA Post-Election Voter-Analysis Playbook
**Reference cycle:** April 21, 2026 Virginia Constitutional Amendment Referendum
**Playbook authored:** 2026-05-25 · **Status:** complete

---

## 0. What this is

A reproducible, end-to-end playbook for analyzing a Virginia election after the
fact: loading the SBE "List of Those Who Voted" (LTV) file into SQL Server,
reconciling it against the official results / ENR / absentee data, characterizing
who voted (demographics, party, vote method, geography), measuring **drop-off and
surge** vs the prior election, and publishing a branded one-page brief plus a
private VAN-ready targeting list.

It was built around the April 2026 Referendum cycle (this repo). Hand this
document, along with the repo, to a successor to replicate for the next election.

---

## 1. Headline result (this cycle, for grounding)

- **Amendment PASSED 51.69% Yes / 48.31% No** on **51.06% turnout** (3,103,669
  votes on the question, 3,109,181 ballots cast, 6.08M active registered).
- LTV loaded **3,101,912 voter rows** (within −0.234% of SBE ballots cast;
  99.79% absentee match).
- **Base-mobilization** electorate: 75.4% voted 3-or-4 of last 4 Novembers;
  2.1% first-time.
- **Rep turnout 52.9% / Dem 45.0%** (higher Rep intensity), but Dem-leaning
  voters were **53.4% of the electorate** (1.66M vs 1.44M) — why Yes won.
- **Churn vs 2025G:** drop-off **682,378 (19.9%)**, surge **357,726 (11.5%)**,
  net **−324,652**.

If a future run lands wildly different from these in similar circumstances,
something is probably wrong.

---

## 2. Architecture & data flow

```
SBE LTV CSV ──load_LTV{cycle}.py──▶ Historic.dbo.LTV{cycle}              (raw 50 cols NVARCHAR)
                                              │
                                              ▼  (derived from Absentee.dbo.Daily_Absentee_List)
                                   LTV{cycle}_Votemethod                 (Polls / AB_Inperson / AB_Mail)
                                              │
            ┌─────────────────────────────────┼─────────────────────────────────┐
            ▼                                 ▼                                 ▼
   LTV{cycle}_Base                    Dropoff_{prior}_Base              Surge_{cycle}_Base
   (LTV ⋈ Van ⋈ RVL + age/party/      (prior-General voters + did      (referendum voters present in
   gen4/prior_vote/dem_support)       they vote this cycle)            VAN + did they vote prior General)
            │                                 │                                 │
            └──────────────────────── analyze.py ────────────────────────────────┘
                                              │
                                              ▼
                      LTV{cycle}_Analysis.md  +  LTV{cycle}_Analysis.xlsx        (§5a–5j + sheets)
                                              │
            ┌─────────────────────────────────┴─────────────────────────────────┐
            ▼                                                                   ▼
   make_publication.py                                                make_churn_brief.py
            │                                                                   │
            ▼                                                                   ▼
   {cycle}_Summary.html/pdf                                        {cycle}_Churn_Brief.html/pdf
            │                                                                   │
            └────────── git push ──▶ GitHub Pages (custom domain) ◀────────────┘

PII targeting (EXTERNAL — never in the public repo):
   export_dropoff_targets.py ──▶ C:\Absentee\{cycle}_Dropoff_Targets\*.csv      (VAN-ready)
```

**Servers / databases (this cycle):**
| | Where | Notes |
|---|---|---|
| SQL Server | `INSTANCE-1` | Windows integrated auth; ODBC Driver 17 |
| LTV + analysis tables | `Historic` DB | per-cycle LTV tables + per-cycle base tables |
| Absentee snapshots | `Absentee` DB | `Daily_Absentee_List`, `DAL_{cycle}_*`, `Cure_History`, `Historical_Daily_Totals` |
| Registered voter file | `Voter.dbo.RVL` | 6.4M rows; demographics; STATUS = Active/Inactive |
| VAN voter file (view) | `Voter.dbo.Van` | matched on `StateFileID = IDENTIFICATION_NUMBER`; party + vote history + scores |
| Locality name map | `Voter.dbo.County_Twist` | maps DAL all-caps locality → VAN CountyName |

---

## 3. The six phases (replicate this order for any cycle)

### Phase 0 — Project inventory
**Goal:** establish the project home and a single-source-of-truth `INVENTORY.md`.

- Create `C:\DPVA_Projects\{Cycle}\` with subfolders: `sql/`, `notes/`, `analysis/`, `handoff/`, `assets/`.
- Copy the templates `CLAUDE.md` + `INVENTORY.md` from this repo; fill in the
  10 sections (overview, scripts, SQL objects, data files, repos, URLs, tasks,
  external deps, lessons learned, wrap-up checklist).
- Scan: `C:\Scripts\Python\Python_Absentee\`, `Python_ElectionResults\`,
  `Python_LTWV\`; `C:\Temp\SBE\`; `C:\Absentee\`; `G:\My Drive\Absentee*\`;
  Task Scheduler (`Get-ScheduledTask` to a CSV); the relevant `brennertobe07` GitHub repos.
- Drop a small breadcrumb `CLAUDE.md` in each operational folder pointing
  at the project home.

### Phase 1 — Inspect the source LTV file
Source: `C:\Temp\SBE\LTWV\LTV{cycle}.csv`.
- Header, last 3 lines, line count.
- **Encoding:** *not* UTF-8 — accented names (e.g. `0xf3` = ó) are in
  Windows‑1252 / Latin‑1. **Always read with `encoding="latin-1"`** or `read_csv`
  fails partway through.
- Delimiter: comma. Quoting: every field is RFC double-quoted (proper CSV
  parsers strip them; expect no literal `"` to persist into SQL).
- Compare column list against the most recent prior `LTV*` table in `Historic`
  (Virginia's LTV schema has been stable; 50 columns).

### Phase 2 — Load to `Historic.dbo.LTV{cycle}`
Script: `C:\Scripts\Python\Python_LTWV\load_LTV{cycle}.py` (clone the prior loader).
- Drop + create with **all columns `NVARCHAR(255)`** (safe raw load).
- Load via `pandas.read_csv(..., dtype=str, keep_default_na=False, encoding="latin-1", chunksize=5_000)` + `pyodbc fast_executemany`.
- **Gotcha:** with `fast_executemany`, the chunk × column-width buffer can blow past
  memory. 50 cols × NVARCHAR(255) × **5,000** chunk loads cleanly; 50k chunks failed with `MemoryError`.
- Verify: SQL `COUNT(*)` matches source `wc -l - 1`.

**Phase 2b — derive vote-method table** (`LTV{cycle}_Votemethod`):
SBE often doesn't ship a `*_Votemethod` file the same day. Derive it from
`Absentee.dbo.Daily_Absentee_List` (still holding the cycle's data):

| Source rule | `AB_Type` |
|---|---|
| `ABSENTEE = 'False'` | `Polls` (election day) |
| `BALLOT_STATUS = 'On Machine'` | `AB_Inperson` (in-person early) |
| `BALLOT_STATUS IN ('Marked','Pre-Processed')` | `AB_Mail` |
| `ABSENTEE = 'True'` else | `AB_Other` (provisional/late) |

Dedup DAL with `ROW_NUMBER()` priority `Marked > Pre-Processed > On Machine`.
See `sql/LTV2026_Ref_Votemethod_build.sql` for the canonical pattern.

### Phase 3 — Quote cleanup
For LTV files loaded via `pandas.read_csv` the quotes are stripped by the
parser, so this is **nearly a no-op** — but always run the dynamic check
across every string column. (For 2026 it cleaned one `APT_NUM` cell.)
See `sql/LTV2026_Ref_quote_cleanup.sql`.

### Phase 4 — Reconcile vs three sources
Script: `analysis/reconcile.py` → writes `analysis/reconciliation.md`.

| Source | What you compare | Sign |
|---|---|---|
| **A. SBE official results** (`Election Results{cycle}.csv`) + **turnout file** | LTV rows vs SBE ballots-cast; LTV rows vs SBE votes-on-question | LTV should be within ~0.3% of ballots cast and slightly above votes-on-question (undervotes) |
| **B. ENR app data** (`april-referendum-enr/data/localities.json`) | LTV locality counts vs ENR `total` (votes on question) per locality | Δ should be small; flag >1% |
| **C. Absentee app** (`Daily_Absentee_List`) | DAL "accepted absentee" (`On Machine` + `Marked` + `Pre-Processed`) vs LTV `ABSENTEE='True'` | should match ~99.8% |

**Locality-code join:** LTV `LOCALITY_CODE` (3-digit, zero-padded) = ENR `fips`. No name normalization needed for the join.

> **Watch-outs surfaced this cycle:** SBE LTV under-reported **Covington City (580)** and **Sussex County (183)** at ~⅓ of actual turnout (verified not a join error). Flag any locality where Δ > 1% and treat them as incomplete for locality-level Phase 5 cuts.

### Phase 5 — Voter pattern analysis (the analytical heart)
Script: `analysis/analyze.py` → writes `analysis/LTV{cycle}_Analysis.md` + `.xlsx`
(one sheet per analysis). Default reuses existing base tables; `set REBUILD=1` to
rebuild them (the slow step — the LTV ⋈ Van ⋈ RVL join with the prior-vote
expression takes ~8–10 min).

Sections produced:
| § | What |
|---|---|
| 5a | First-time voters (no prior vote in any Van history column) |
| 5b | Turnout by age band (RVL active denominator), with 2025-General baseline; **+ turnout by age × party** (Dem vs Rep, Van denominator) |
| 5c | Turnout by gender (with baseline) |
| 5d | Vote-history pattern — # of last 4 Novembers voted (0/1/2/3/4) |
| 5e | Vote method (Polls / AB_Inperson / AB_Mail) by age and by party |
| 5f | Geography — top localities by LTV count, by turnout %, and strongest Yes/No localities w/ profile |
| 5g | Party turnout + share of electorate (dashboard methodology) |
| 5h | Anomaly scan — precinct turnout outliers (±2 SD); voters not in RVL |
| 5i | **Drop-off** — prior-General voters who skipped this cycle (by party, age, gender, CD, county; age × party; county × party) |
| 5j | **Surge** — this-cycle voters who skipped the prior General (mirror of 5i; eligibility-note caveat for came-of-age) |

### Phase 6 — Executive summary + briefs + publish
- The hand-authored exec summary lives in `analysis/_exec_summary.md` and is
  auto-prepended to the report on every regeneration (so re-running can't
  clobber it; edit that file to change the summary).
- Build the two one-page briefs:
  - `python analysis/make_publication.py` → `Referendum2026_Summary.html`
  - `python analysis/make_churn_brief.py` → `Referendum2026_Churn_Brief.html`
- Print to PDF (see §6 below for the reliable command — there's a Chromium
  caching gotcha).
- Update README/inventory; commit; push. GitHub Pages auto-rebuilds.

---

## 4. SQL objects to clone for the next cycle

| Object | Rename pattern | Notes |
|---|---|---|
| `Historic.dbo.LTV2026_Ref` | `LTV{cycle}` | raw load, NVARCHAR(255) × 50 cols |
| `Historic.dbo.LTV2026_Ref_Votemethod` | `LTV{cycle}_Votemethod` | derived; `IDENTIFICATION_NUMBER, ABSENTEE, AB_Type, ELECTION_NAME` |
| `Historic.dbo.LTV2026_Ref_Base` | `LTV{cycle}_Base` | analysis base; index on `LOCALITY_CODE` |
| `Historic.dbo.Dropoff_{prior}_Base` | parameter the prior-General name | index on `StateFileID` |
| `Historic.dbo.Surge_{cycle}_Base` | parameter the cycle | index on `StateFileID` |

DDL of the LTV table is in `sql/LTV2026_Ref_table.sql`. The two derived
tables build themselves from `analyze.py` helpers (`build_base`,
`build_dropoff_base`, `build_surge_base`).

---

## 5. Scripts in the project (alphabetical)

| Script | Folder | Purpose |
|---|---|---|
| `load_LTV2026_Ref.py` | `C:\Scripts\Python\Python_LTWV\` | Phase 2 — raw load LTV CSV → `Historic.dbo.LTV{cycle}` |
| `reconcile.py` | `analysis/` | Phase 4 — writes `reconciliation.md` + locality CSV |
| `analyze.py` | `analysis/` | Phase 5 — builds base tables; writes `LTV{cycle}_Analysis.md` + `.xlsx` |
| `make_publication.py` | `analysis/` | Phase 6 — builds the summary one-page brief (HTML; PDF via Edge) |
| `make_churn_brief.py` | `analysis/` | Phase 6 — builds the drop-off/surge churn one-pager |
| `export_dropoff_targets.py` | `analysis/` | builds VAN-ready CSVs of drop-off voters → **external** PII folder |

Operational pipeline scripts (kept in their original locations, *not* moved
into the project repo, because Task Scheduler depends on those paths):
| Script | What | Where |
|---|---|---|
| `absentee_pipeline.py` | daily absentee download + SQL load | `Python_Absentee\` |
| `export_dashboards.py` | wrapper: historical load + JSON exports + git push | `Python_Absentee\` |
| `load_historical_daily.py` | daily aggregates → `Historical_Daily_Totals` | `Python_Absentee\` |
| `enr_pipeline.py` / `push_enr.py` | election-night results poll + push | `Python_ElectionResults\` |
| `backup_absentee_pipeline.py` | end-of-cycle backup zip | `Python_Absentee\` |

---

## 6. Methodology — the rules to keep consistent

### Party bucketing (the "dashboard rule")
Use the same rule the `absentee.vadems.org` / `cure.vadems.org` dashboards use,
so all DPVA artifacts agree:

```
CASE WHEN LikelyParty IN ('SD','LD')                THEN 'Dem'
     WHEN LikelyParty IN ('SR','LR')                THEN 'Rep'
     WHEN <dem_support_column> >= 50                THEN 'Dem'   -- ND/I/U with score
     WHEN <dem_support_column> <  50                THEN 'Rep'   -- ND/I/U with score
     ELSE 'Unknown'                                              -- no-score / no-VAN
END
```

**The score column changes between VAN images.** Current name: `Dem_Support_26`
(0–100, threshold 50). Prior images used `Clarity_DemSupport_26`. On a new VAN
image, **check the column name** in the Van view and update the one place in
`analyze.py` (the `PARTY_VAN` constant and `build_base` reference).

### Drop-off (§5i)
*Universe:* voters who voted the prior General **and** are still registered
(present in `Voter.dbo.Van`).
*Drop-off:* among that universe, those who did **not** also vote this cycle
(no match in `LTV{cycle}_Votemethod`).
*Drop-off rate:* dropped ÷ prior-general voters in the group.

### Surge (§5j)
*Universe:* this-cycle voters who are present in `Voter.dbo.Van`.
*Surge:* among that universe, those who did **not** vote the prior General
(blank `General25`).
*Surge rate:* surge ÷ this-cycle voters in the group.

### The two communication pitfalls (read this before publishing)

**1. Rate ≠ volume.** In Virginia, Republicans turn out at a higher *rate*
than Democrats. A turnout-rate chart by party will show Rep bars taller —
**this does not mean Republicans cast more votes**, because the Dem-leaning
registered base is larger. **Always pair a rate chart with a votes-cast
(volume) chart** so the reader doesn't conclude "No outperformed" when in fact
Yes won. The summary brief does this deliberately (chart 1 is rate, chart 3
is votes).

**2. Coming-of-age inflates the youngest surge band.** Anyone who turned 18
between the prior General and this election is "surge" mechanically — they
couldn't have voted before. Report it as a footnote with the eligibility-
adjusted 18–24 surge rate (this cycle: 30.9% raw → 25.0% eligibility-adjusted).
`analyze.py` computes this automatically.

### Locality under-report (treat as incomplete)
`COVINGTON CITY (580)` and `SUSSEX COUNTY (183)` were under-reported in the
SBE LTV source at ~⅓ of actual turnout. Exclude them from locality rankings;
keep statewide/demographic results intact. Each new cycle, **re-check Phase 4
flagged localities** — the SBE may miss different localities next time.

---

## 7. Publishing the briefs — the technical gotchas

### Self-contained HTML + inline SVG
The briefs are **single HTML files** with all chart SVG, CSS, and the VADEMS
logo (base64-encoded JPEG) inline — no external assets, so they print to PDF
identically anywhere and load cleanly on Pages or from a flash drive. The
chart helpers (`svg_bars`, `svg_grouped`, `svg_donut`, `svg_result`) are in
`make_publication.py`; `make_churn_brief.py` imports them.

### Print CSS — making the PDF fit one US Letter page
```css
@page  { size: letter; margin: 0; }                  /* zero margin kills the */
@media print {                                       /* browser header/footer */
  body { background: #fff; }
  .page { padding: 8–12mm; max-width: none; zoom: <0.7–0.82>; }
  .nav  { display: none !important; }                /* hide web tabs in print */
}
```
- `@page { margin: 0 }` is what removes the default Chromium header/footer
  (`--print-to-pdf-no-header` is **not** honored by all Edge builds).
- `zoom:` is the per-brief lever to fit one page. Use the cache-isolated test
  loop below before committing.
- `page-break-inside: avoid` on `.findings` and `.panel` keeps boxes intact.

### Auto-scaled y-axis
Don't hardcode `ymax`. Compute it from the data each run with headroom for the
value labels:
```python
def rmax(*series):
    m = max(max(s) for s in series)
    return ((int(m * 1.08) // 10) + 1) * 10
```
Otherwise a small data shift (e.g., after a VAN refresh) clips the tallest bar's value label off the top.

### Generating the PDFs — *use a fresh Edge profile*
Edge's `--print-to-pdf` and `--screenshot` cache the source HTML by file path
through the user data directory. If you generate from the same path twice
during edits, the second PDF can be a stale render and you'll chase a "why
won't it update" problem for an hour. **Always use a temp copy + an isolated
`--user-data-dir`:**

```powershell
$tmp="C:\Temp\b_$(Get-Random).html"; $ud="C:\Temp\u_$(Get-Random)"
Copy-Item $html $tmp
& msedge --headless --disable-gpu --user-data-dir="$ud" --print-to-pdf="$pdf" "file:///$($tmp -replace '\\','/')"
Remove-Item $tmp,$ud -Recurse -Force
```
Then **verify with `pypdf`**, not by reading the PDF (which can also be cached):
```python
from pypdf import PdfReader; print(len(PdfReader('....pdf').pages))
```

### The 2-tile landing + tab nav
`index.html` at repo root is a static 2-tile landing (summary brief + churn brief)
with `.nojekyll` next to it so Pages serves files as-is. Each brief carries a
`Summary | Voter Churn | All briefs ↑` nav bar at top, **web-only** (hidden in
print) so PDFs stay clean. The nav helper is in `make_publication.py` (shared
across both briefs).

### Branding
- VADEMS logo at `assets/vadems_logo.jpg` (extracted from the ENR/cure
  dashboards). The brief generators read it, base64-embed it, and emit a
  `<div class="brand">` at the top of each brief (visible in web *and* print).
- The landing `index.html` references `assets/vadems_logo.jpg` directly.

### Custom domain
Pages serves at `https://referendum-2026.vadems.org/` via a one-line `CNAME`
file at repo root + a Cloudflare DNS record at `vadems.org`. New cycles:
create a new repo, add `CNAME`, point Cloudflare. Cert provisioning takes a
minute or two.

---

## 8. Privacy & data handling

This repo is **public**. Aggregate analysis (counts, rates, locality tables) is
fine to publish. **Individual voter records (PII) are not.**

| What | Where | Public? |
|---|---|---|
| Report, briefs, xlsx with aggregates | `analysis/` (in repo) | ✅ yes |
| Targeting CSVs with name/phone/address | `C:\Absentee\Referendum2026_Dropoff_Targets\` (**outside** the repo) | ❌ no |
| `.gitignore` guard for PII patterns | `dropoff_*.csv`, `**/dropoff_*.csv`, `notes/*.pdf`, `__pycache__/` | belt-and-suspenders |
| `export_dropoff_targets.py` | code only, no PII — fine to commit | ✅ code yes / output no |

Before committing, `grep -rIi "password|secret|token"` (or equivalent). The
only matches should be **location-only** references in `INVENTORY.md` §8
(never the value). The full audit was clean for the 2026 cycle.

---

## 9. The non-obvious things that bit us (collected lessons)

Group these by category — none is theoretical, every one cost time:

**Data / encoding**
- LTV CSVs are **Latin-1**, not UTF-8. `pandas.read_csv(..., encoding="latin-1")`. Failing without it is silent until you hit an accented name.
- LTV files are RFC-quoted (every field). `pandas.read_csv` strips the quotes; BULK INSERT does not — use `pandas`.
- Two VA localities (Covington 580, Sussex 183) were under-reported in the LTV by ~⅔ of their actual turnout. Always re-check Phase 4 flags.

**SQL / load**
- `pyodbc.fast_executemany` allocates a buffer sized to (declared column width × chunk rows). 50 × NVARCHAR(255) × 50k blew memory. **Chunk = 5,000** loads cleanly.
- `sqlcmd -i` is fussy about path separators; use **backslashes** on Windows.
- Use a temp table (`#g25`, `#g25_by_county`, etc.) for multi-aggregation queries to avoid re-evaluating expensive `EXISTS` joins.

**VAN file**
- The Dem-support column name **changes between images** (`Clarity_DemSupport_26` → `Dem_Support_26`). One constant in `analyze.py` (`PARTY_VAN`) holds the column name; update it on a fresh image.
- A VAN snapshot may lag this-cycle registrations by weeks/months. The Apr 2026 snapshot (2026-03-01) was missing ~25k referendum voters. **A fresh VAN image after the election is the fix** — the no-VAN count dropped from 25,494 → 103.
- `Voter.dbo.Van.StateFileID` is **unique** (no fan-out from the LTV ↔ Van join). Verify this when adding a new column — a non-unique key would double-count.

**Publication / PDFs**
- Edge headless `--print-to-pdf` and `--screenshot` cache by file path through the shared profile. **Use `--user-data-dir=<temp>`** and a temp copy of the HTML — otherwise you get stale renders.
- `--print-to-pdf-no-header` is unreliable across Edge builds. **`@page { margin: 0 }` is the portable way** to remove the timestamp/URL header/footer.
- `zoom:` is the cleanest way to fit one page; `transform: scale()` doesn't affect pagination.
- `pypdf` page count is the only trustworthy way to verify "one page" (the Read tool also caches PDF renders).
- If the brief PDF won't overwrite, **someone has it open in Acrobat**. Ask them to close it, don't kill their process.

**Communications**
- Rate ≠ volume. **Always pair partisan rate charts with vote-count charts.**
- Came-of-age inflates the youngest surge bar by ~2 pp. **Always footnote it.**
- Drop-off/surge are computed on the **VAN universe** (excludes the no-VAN new registrants). State this in the brief footer.

**Repo hygiene**
- Don't commit `__pycache__/`, `_headline.json`, scratch `notes/*.png`, `notes/*.pdf`. All gitignored.
- Don't commit voter PII. The `dropoff_*.csv` ignore patterns are the safety net; the **real** safeguard is writing them outside the repo.

---

## 10. Next-cycle quick-start

When the next post-election analysis is needed:

1. **Pre-flight inventory.** Confirm the new LTV file landed in `C:\Temp\SBE\LTWV\`; the SBE Results + Turnout files are in `Results_Winners\NewFormat\`; the ENR repo for this cycle (if any) is up to date; the VAN snapshot is reasonably fresh.

2. **Make a copy of this repo,** rename for the new cycle (`referendum-2026` → `general-2027`, etc.). Update:
   - All `LTV2026_Ref` → `LTV{newcycle}` in `load_LTV…py`, `analyze.py`, `make_publication.py`, `make_churn_brief.py`, `INVENTORY.md`, the SQL DDL.
   - `ELECTION_NAME = '2026 April 21 Special'` → the new SBE election name (check `Daily_Absentee_List.ELECTION_NAME`).
   - Election date constant in `make_publication.py` and `analyze.py` (`'2026-04-21'`).
   - The baseline-election column (`General25` → `General26` or whichever Nov General precedes the new cycle) in the §5b/§5d/§5i/§5j queries.
   - The eligibility-window dates (`'2025-11-04'`, `'2026-04-21'`) in the §5j eligibility query.
   - Headings/sub-text in the briefs and exec summary (election name/date).

3. **Run the six phases.** Each command:
   ```
   python C:\Scripts\Python\Python_LTWV\load_LTV{cycle}.py
   sqlcmd -S INSTANCE-1 -d Historic -E -i sql\LTV{cycle}_Votemethod_build.sql
   sqlcmd -S INSTANCE-1 -d Historic -E -i sql\LTV{cycle}_quote_cleanup.sql   (run cleanup_run.sql)
   python analysis\reconcile.py
   set REBUILD=1 && python analysis\analyze.py                                 (first time, ~10 min)
   python analysis\make_publication.py
   python analysis\make_churn_brief.py
   (regenerate PDFs via the cache-isolated Edge command in §7)
   python analysis\export_dropoff_targets.py                                   (writes outside the repo)
   ```
   Then update `_exec_summary.md` with the headline numbers (read them from the printed log line and the new report sections).

4. **Publish.** `git init` (if new repo), commit everything, `gh repo create … --public`, add `CNAME` for the new sub-domain, point Cloudflare DNS, push. Pages auto-builds. Verify both briefs return HTTP 200.

5. **Wrap.** Run `backup_absentee_pipeline.py` for the final backup zip. Move Drive `Daily_List\` → `Absentee_Archive\Absentee{cycle}\Daily_File\`. Drop the loose LTV CSV (keep the zip + SQL table). Drop residual DAL snapshot tables (record names/rows in `handoff/`). Update `INVENTORY.md` Status → `Archived`.

---

## 11. Key files & paths (cheat sheet for this cycle)

| What | Path |
|---|---|
| Project home | `C:\DPVA_Projects\Referendum2026\` |
| Source LTV (zip) | `C:\Temp\SBE\LTWV\LTV2026_Ref.zip` (loose CSV deleted) |
| Loader | `C:\Scripts\Python\Python_LTWV\load_LTV2026_Ref.py` |
| Report (Markdown) | `analysis/LTV2026_Ref_Analysis.md` |
| Workbook (sheets) | `analysis/LTV2026_Ref_Analysis.xlsx` |
| Summary brief | `analysis/Referendum2026_Summary.{html,pdf,_preview.png}` |
| Churn brief | `analysis/Referendum2026_Churn_Brief.{html,pdf,_preview.png}` |
| Reconciliation | `analysis/reconciliation.md`, `analysis/locality_reconciliation.csv` |
| Exec summary source | `analysis/_exec_summary.md` (hand-authored, prepended) |
| Targeting CSVs (PII, **external**) | `C:\Absentee\Referendum2026_Dropoff_Targets\` |
| Final pipeline backup zip | `C:\Scripts\Python\Backups\DPVA_Pipeline_Backup_20260521_141527.zip` |
| Repo | `https://github.com/brennertobe07/referendum-2026` (public) |
| Live site | `https://referendum-2026.vadems.org/` |
| Custom-domain CNAME | `CNAME` at repo root |
| VADEMS logo asset | `assets/vadems_logo.jpg` |

---

## 12. What's still open (deliberately) for this cycle

- **Live URLs kept up** — `absentee.vadems.org`, `cure.vadems.org`, `enr.vadems.org`,
  `referendum-2026.vadems.org` — frozen on the final 2026-05-12 data as a
  historical reference. Decommission when the next cycle reuses the dashboards.
- The targeting list at `C:\Absentee\Referendum2026_Dropoff_Targets\` —
  available for VAN upload / outreach. Not in the repo (PII).

Everything else in the §10 wrap-up checklist is done.
