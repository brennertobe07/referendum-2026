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
