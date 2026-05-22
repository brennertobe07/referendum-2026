# Dropped DAL_26SP_Apr snapshot tables — 2026-05-21

As part of Referendum 2026 wrap-up, the residual daily-snapshot tables for the
26SP_Apr cycle were dropped from `INSTANCE-1.Absentee` to reclaim space.

**Why this is safe / where the data lives now:**
- The full daily aggregate time series (61 days, 2026-03-06 → 2026-05-09) is
  preserved in `Absentee.dbo.Historical_Daily_Totals` (ElectionName = `26SP_Apr`).
- The raw daily files are archived as 63 dated zips in
  `G:\My Drive\Absentee_Archive\Absentee26SP_Apr\Daily_File\` — a full snapshot
  can be reloaded from any of them if ever needed.
- Only 3 early-cycle snapshot tables remained (mid-March); they were not a
  complete daily series.

**Tables dropped (≈443 MB total):**

| Table | Rows | Created |
|-------|------|---------|
| DAL_26SP_Apr_20260312103651 | 506,333 | 2026-03-12 10:36:51 |
| DAL_26SP_Apr_20260312104359 | 506,333 | 2026-03-12 10:43:59 |
| DAL_26SP_Apr_20260313055539 | 520,357 | 2026-03-13 05:55:39 |
