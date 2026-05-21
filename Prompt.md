# Referendum 2026 — Project Inventory + LTV2026_Ref Import & Analysis
## Claude Code Prompt for DPVA Data Pipeline

---

## How to launch Claude Code with minimal permission prompts

Pick one of the following — both reduce friction during this session.

### Option A — broad bypass (fastest, less safe)
```
claude --dangerously-skip-permissions
```

### Option B — targeted allowlist (recommended)
Run from `C:\DPVA_Projects\Referendum2026\` (create if needed):
```
claude --allowedTools "Bash Edit Read Write Glob Grep"
```

### Option C — settings file (persistent across sessions)
Create `.claude/settings.local.json` in your working folder:
```json
{
  "permissions": {
    "allow": [
      "Bash(python:*)",
      "Bash(sqlcmd:*)",
      "Bash(bcp:*)",
      "Bash(dir:*)",
      "Bash(type:*)",
      "Bash(git:*)",
      "Edit",
      "Read",
      "Write",
      "Glob",
      "Grep"
    ]
  }
}
```
Then just run `claude` normally.

---

## PROMPT — paste everything below into Claude Code

You are working in my DPVA data environment. Standard stack:

- **SQL Server:** `INSTANCE-1`
- **Target database for LTV:** `Historic`
- **Python:** 3.12 with `pyodbc`, `pandas`, `sqlalchemy`
- **ODBC driver:** `ODBC Driver 17 for SQL Server`
- **OS:** Windows
- **Reference databases on INSTANCE-1:** `Voter` (RVL, Van view, County_Twist), `Absentee` (Daily_Absentee_List, DAL_26SP_Apr_* snapshots, Historical_Daily_Totals, Cure_History), `Elected_VA` (election results), `Historic` (LTV tables)
- **GitHub user:** `brennertobe07`

Work autonomously. Do not ask me to confirm routine steps — only stop if you hit an actual blocker (file missing, schema mismatch you can't resolve, an ambiguous business question). Show me a summary at the end of each phase; don't narrate each step.

---

### PHASE 0 — Build the Referendum 2026 project inventory

Before any LTV work, build a master inventory of everything related to the April 21, 2026 Constitutional Amendment Referendum. This is a one-time effort that becomes the template for every future election cycle.

**Create the project home:**
```
C:\DPVA_Projects\Referendum2026\
```

**Scan these locations for referendum-related artifacts:**

- `C:\Scripts\Python\Python_Absentee\` — daily absentee + cure pipeline
- `C:\Scripts\Python\Python_ElectionResults\` — ENR push and pipeline scripts
- `C:\Scripts\Python\Python_LTWV\` — LTV loaders (if it exists yet)
- `C:\Scripts\Python\Backups\` — pipeline backup zips
- `C:\Temp\SBE\` — all subfolders (LTWV, Results_Winners, Absentee\2026_Apr21, etc.)
- `C:\Absentee\` — operational data including 26SP_Apr and Cure_backup
- `G:\My Drive\Absentee26SP_Apr\` — Google Drive archive
- All `brennertobe07` GitHub repos with "referendum", "april", "cure", or "enr" in the name (`april-referendum-absentee`, `april-referendum-enr`, `va-cure`, and any others — use `gh repo list brennertobe07` if `gh` CLI is available, otherwise check git remotes in known local repo folders)
- SQL Server: enumerate referendum-related tables across `Absentee`, `Voter`, `Historic`, and `Elected_VA` databases. Look for: anything with `26SP_Apr` in the name, anything modified after 2026-03-01, the views and stored procedures supporting the dashboards
- Task Scheduler: export the list of scheduled tasks (`schtasks /query /fo CSV /v > tasks.csv`) and identify any task running scripts in the folders above
- Cloudflare Zero Trust subdomains under `vadems.org` related to the referendum (absentee, cure, enr) — note these from existing knowledge or `DPVA_Absentee_Reference.md` if found

**Produce these files at `C:\DPVA_Projects\Referendum2026\`:**

#### `INVENTORY.md`

Use this exact structure. Every project from here on will use the same template.

```markdown
# Referendum 2026 — Project Inventory
**Election:** Virginia Constitutional Amendment Referendum
**Election Date:** 2026-04-21
**Inventory Generated:** [today's date]
**Status:** [Active | Wrap-up | Archived]

## 1. Overview
Two-paragraph summary: what the election was, key dates (absentee window opened, election day, certification),
final turnout numbers, top-line result.

## 2. Scripts
| Path | Purpose | Language | Schedule | Repo | Notes |
|------|---------|----------|----------|------|-------|

## 3. SQL Objects
| Server.Database.Schema.Object | Type | Purpose | Created | Dependencies |
|-------------------------------|------|---------|---------|--------------|
(Type = TABLE, VIEW, PROC, FUNCTION)

## 4. Data Files (local + cloud)
| Path | Format | Source | Retention | Notes |
|------|--------|--------|-----------|-------|

## 5. GitHub Repositories
| Repo | Purpose | URL | Local Path | Last Commit |
|------|---------|-----|------------|-------------|

## 6. Live URLs
| URL | What it shows | Auth | Hosted on | Repo source |
|-----|---------------|------|-----------|-------------|

## 7. Scheduled Tasks
| Task Name | Schedule | Runs | Purpose |
|-----------|----------|------|---------|

## 8. External Dependencies
- Vendors / services used (SBE feeds, NCEC data, BigQuery, Cloudflare, etc.)
- API keys / credentials (location only, never values)

## 9. Lessons Learned
Free-form notes on what worked, what didn't, what to do differently next cycle.

## 10. Wrap-up Checklist
- [ ] All scripts committed to git
- [ ] Final backup zip in C:\Scripts\Python\Backups\
- [ ] Google Drive archive moved from Daily_List\ to Absentee_Archive\
- [ ] SQL tables documented in section 3
- [ ] Reference docs current
- [ ] Live URLs decommissioned or repurposed for next cycle
- [ ] Inventory marked Archived
```

#### `CLAUDE.md`

```markdown
# Referendum 2026 — Claude Code Context

This folder is the project home for the April 21, 2026 Virginia Constitutional Amendment Referendum.
The full project inventory is in INVENTORY.md.

## Standing Context
- SQL Server: INSTANCE-1
- Databases used: Absentee, Voter, Historic, Elected_VA
- Python: 3.12, pyodbc + sqlalchemy + pandas
- GitHub user: brennertobe07
- Operational scripts remain in their original locations (C:\Scripts\Python\Python_Absentee\,
  Python_ElectionResults\, Python_LTWV\). They are NOT moved here — Task Scheduler depends on those paths.
  This folder is documentation and project-level SQL only.

## Folder Conventions
- INVENTORY.md — master index, source of truth
- sql/ — DDL for tables and views specific to this election
- notes/ — running notes, decisions, screenshots
- analysis/ — post-election analytical outputs (LTV2026_Ref_Analysis.md, etc.)
- handoff/ — backup zips, archive manifests

## Companion Folders (operational, not in this repo)
- C:\Scripts\Python\Python_Absentee\ — absentee pipeline
- C:\Scripts\Python\Python_ElectionResults\ — ENR pipeline
- C:\Scripts\Python\Python_LTWV\ — LTV loaders
```

#### Create the subfolders

```
C:\DPVA_Projects\Referendum2026\
├── INVENTORY.md
├── CLAUDE.md
├── sql\
├── notes\
├── analysis\
└── handoff\
```

#### Drop `CLAUDE.md` breadcrumbs in operational folders

In each of these folders, create a short `CLAUDE.md` if one does not already exist:
- `C:\Scripts\Python\Python_Absentee\CLAUDE.md`
- `C:\Scripts\Python\Python_ElectionResults\CLAUDE.md`
- `C:\Scripts\Python\Python_LTWV\CLAUDE.md`

Each contains:
```markdown
# Operational folder — see project home

Scripts in this folder are part of the Referendum 2026 project.
Full inventory and context: C:\DPVA_Projects\Referendum2026\INVENTORY.md

When working in this folder, refer to the project home for related scripts,
SQL objects, and decisions across the broader pipeline.
```

#### Optionally — initialize a git repo

If I confirm later, initialize `C:\DPVA_Projects\Referendum2026\` as a git repo and prepare a `brennertobe07/referendum-2026` GitHub repo. For now, just create the folder and files. Do not push to GitHub in this session unless I explicitly ask.

**Report at end of Phase 0:**
- Total artifacts inventoried (count of scripts, SQL objects, data files, repos, URLs, tasks)
- Anything found that surprised you or doesn't have an obvious home
- Anything you couldn't access or enumerate (so I can fill it in manually)

---

### PHASE 1 — Inspect the source LTV file

File: `C:\Temp\SBE\LTWV\LTV2026_Ref.csv`

1. Read the first 20 lines and the last 5 lines.
2. Get total row count, encoding (UTF-8 vs UTF-16 BOM), delimiter, and whether fields are quoted.
3. Report column list, sample values, and any obvious quote-wrapping that would persist into the database (e.g. `"123456789"` stored as a literal string with quote characters).
4. Compare column names against any prior `LTV` table that already exists in `Historic` (run `SELECT name FROM Historic.sys.tables WHERE name LIKE 'LTV%'` and inspect column structure of the most recent one). Note any added/dropped/renamed columns.

**Checkpoint:** show me Phase 0 and Phase 1 summaries before continuing.

---

### PHASE 2 — Load to `Historic.dbo.LTV2026_Ref`

1. Drop the table if it exists: `IF OBJECT_ID('Historic.dbo.LTV2026_Ref','U') IS NOT NULL DROP TABLE Historic.dbo.LTV2026_Ref;`
2. Create the table with all columns as `NVARCHAR(255)` initially (safer for a raw load — typing comes later if needed). Use the column names from the CSV header.
3. Load via Python with `pyodbc` + `pandas.read_csv` + `executemany`, OR via `BULK INSERT` with a format file. Use whichever matches what's worked in prior `LTV` loads in this environment — check `C:\Scripts\Python\Python_LTWV\` for an existing loader template first.
4. After load, report row count and verify it matches the source CSV (header excluded).
5. Save the loader script to `C:\Scripts\Python\Python_LTWV\load_LTV2026_Ref.py` and the table DDL to `C:\DPVA_Projects\Referendum2026\sql\LTV2026_Ref_table.sql`.

---

### PHASE 3 — Quote cleanup (conditional)

Sometimes literal double-quote characters survive into the data (e.g. `"SMITH"` instead of `SMITH`).

1. For every string column, run:
   ```sql
   SELECT TOP 5 [col] FROM Historic.dbo.LTV2026_Ref
   WHERE [col] LIKE '"%' OR [col] LIKE '%"';
   ```
2. If ANY column has leftover quotes, run a single cleanup pass:
   ```sql
   UPDATE Historic.dbo.LTV2026_Ref
   SET [col] = REPLACE([col], '"', '')
   WHERE [col] LIKE '%"%';
   ```
   for each affected column. Build this dynamically — don't hardcode column names.
3. Report which columns were cleaned and how many rows were affected.
4. Save the cleanup script to `C:\DPVA_Projects\Referendum2026\sql\LTV2026_Ref_quote_cleanup.sql` for reference.

---

### PHASE 4 — Count validation against external sources

Validate the import by cross-checking total voter counts against:

**Source A — SBE official results file**
- File: `C:\Temp\SBE\Results_Winners\NewFormat\Election Results2026_Ref.csv`
- This is the election-night final results from SBE. Sum total ballots cast (YES + NO + write-in/blank if present).
- Compare to row count in `Historic.dbo.LTV2026_Ref` (each row = one voter who voted).
- These should be close but not identical — LTV counts voters, results count ballots. Note the delta.

**Source B — Our ENR app data**
- Look in `brennertobe07/april-referendum-enr` repo and any data in `C:\Scripts\Python\Python_ElectionResults\`.
- Pull the final locality-level totals and compare against locality counts in LTV2026_Ref.
- Produce a locality-by-locality reconciliation table with columns: `Locality | LTV_Voters | ENR_Ballots | Delta`. Flag any locality where the delta is more than 1% of LTV_Voters.

**Source C — Absentee app data**
- Database: `Absentee` on INSTANCE-1.
- Tables: `Daily_Absentee_List` (current snapshot — may have been cleared/repurposed by now), historical `DAL_26SP_Apr_*` daily snapshots.
- From the final snapshot before election day, count voters who returned absentee ballots that were ACCEPTED. Compare against the count of voters in LTV2026_Ref who voted via absentee (the LTV vote-method column will identify these — figure out the right code value from the data).
- Report match rate.

Output a single reconciliation summary table at the end of Phase 4 and save it to `C:\DPVA_Projects\Referendum2026\analysis\reconciliation.md`.

---

### PHASE 5 — Voter pattern analysis

Goal: characterize who actually showed up for a low-turnout April referendum and surface anything interesting.

For each section, write a SQL query that joins `Historic.dbo.LTV2026_Ref` to `Voter.dbo.RVL` (current voter file) on `IDENTIFICATION_NUMBER` (or whatever the LTV ID column is called — confirm in Phase 1) to pull demographic/registration fields, and to `Voter.dbo.Van` (view) for vote history.

Produce a markdown report at `C:\DPVA_Projects\Referendum2026\analysis\LTV2026_Ref_Analysis.md`, with each section as a heading and a small table or summary under it. Also save the underlying numbers to `LTV2026_Ref_Analysis.xlsx` with one sheet per analysis.

#### 5a. First-time voters
- Definition: voters in LTV2026_Ref with NO prior election in Van vote history (or registration date after the most recent prior election they'd have been eligible for).
- Count and % of total.
- Break down by age band, gender, party (if VAN party ID is present), and locality.
- Compare first-time-voter rate to overall registered voter base — is the referendum disproportionately pulling new voters in or not?

#### 5b. Age and generation
- Calculate age from DOB at 2026-04-21.
- Age bands: 18–24, 25–34, 35–44, 45–54, 55–64, 65–74, 75+.
- For each band: count voted, registered total, turnout %.
- Compare to a recent baseline election in Van (e.g. 2025 General if available, otherwise 2024 General) — same age-band turnout %.
- Surface bands where turnout was unusually high or low relative to baseline.

#### 5c. Gender
- Same structure as age: count, registered, turnout %, vs baseline.

#### 5d. Vote history pattern
- For each voter in LTV2026_Ref, count how many of the last 4 general elections they voted in (using Van).
- Bucket: 0-of-4, 1-of-4, 2-of-4, 3-of-4, 4-of-4.
- Report the distribution. A referendum that pulls 3-of-4 and 4-of-4 voters is a "base mobilization" story; one that pulls 0-of-4 and 1-of-4 is a "new electorate" story. Tell me which it is.

#### 5e. Vote method
- In-person early, mail absentee, election day. Break down by age and party.
- Note any sharp differences (e.g. is the youngest band voting mail at unusually high rates?).

#### 5f. Geography
- Top 10 localities by total LTV count.
- Top 10 localities by turnout % (LTV voters / RVL active registered).
- Top 10 localities by Yes% from the SBE results file, joined to LTV demographic profile — what does the voter base look like in the strongest Yes localities vs the strongest No localities? Use age, gender, first-time-voter rate.

#### 5g. Party (where derivable from VAN)
- LTV doesn't carry party. Use VAN's party score / party ID joined on voter ID.
- Three buckets: Dem-leaning, Rep-leaning, Unknown/Independent.
- Turnout % for each.
- Did this referendum's electorate skew partisan? By how much?

#### 5h. Anomaly scan
- Find any locality or precinct where LTV turnout was more than 2 standard deviations above or below the statewide mean. List them.
- Flag any voter records in LTV2026_Ref where the IDENTIFICATION_NUMBER does NOT match a current RVL record. Count these — they're either pre-RVL-refresh new registrations, data quality issues, or interesting edge cases.

---

### PHASE 6 — Wrap up and update the inventory

1. Produce a final one-page executive summary at the top of `LTV2026_Ref_Analysis.md` covering:
   - Total LTV rows loaded, source row count, match
   - Reconciliation result vs SBE / ENR / Absentee
   - 3–5 most interesting findings from Phase 5, in plain language
   - Any data quality issues that need follow-up

2. Update `C:\DPVA_Projects\Referendum2026\INVENTORY.md`:
   - Add the new LTV table to section 3 (SQL Objects)
   - Add the loader script to section 2 (Scripts)
   - Add the analysis files to section 4 (Data Files)
   - Add a Phase 5 / 6 note in section 9 (Lessons Learned) capturing anything notable about the data quality or pattern findings

3. Commit Phase 0 inventory + Phase 6 updates as a single git commit in `C:\DPVA_Projects\Referendum2026\` if I have initialized the repo by then. Otherwise just save the files.

---

### Notes for working efficiently

- Use `sqlalchemy` `create_engine` for pandas SQL reads (avoids the pyodbc warning).
- For Van vote history, the table is large — filter to the relevant date range first, don't pull all history into memory.
- If `Daily_Absentee_List` has been overwritten with a newer election, use the most recent `DAL_26SP_Apr_*` daily snapshot table instead.
- Use County_Twist in Voter for any locality name normalization (SBE uses one set of names, RVL uses another).
- The operational scripts stay where they are. Do not move scripts into `C:\DPVA_Projects\Referendum2026\` — Task Scheduler depends on the original paths.

Start with Phase 0 and proceed through to Phase 6. Show me the Phase 0 + Phase 1 summaries before continuing into the load — that's the only checkpoint I need.
