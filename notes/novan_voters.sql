SET NOCOUNT ON;
-- Referendum voters with NO VAN match (in_van=0). They ARE in LTV (and RVL),
-- so we have demographics; we lack VAN party/vote-history. Are they new regs?
PRINT '--- Overall ---';
SELECT COUNT(*) AS total,
  SUM(in_rvl) AS in_rvl,
  SUM(CASE WHEN reg_date > '2026-03-01' THEN 1 ELSE 0 END) AS reg_after_van_snapshot,
  SUM(CASE WHEN reg_date > '2025-11-04' THEN 1 ELSE 0 END) AS reg_after_2025_general,
  SUM(CASE WHEN reg_date IS NULL THEN 1 ELSE 0 END) AS reg_date_null,
  MIN(reg_date) AS earliest_reg, MAX(reg_date) AS latest_reg
FROM Historic.dbo.LTV2026_Ref_Base WHERE in_van = 0;

PRINT '--- Registration timing buckets ---';
SELECT CASE
         WHEN reg_date > '2026-03-01' THEN 'after VAN snapshot (>2026-03-01)'
         WHEN reg_date > '2025-11-04' THEN 'Nov 2025 G .. Mar 2026'
         WHEN reg_date IS NULL THEN 'no/unparseable date'
         ELSE 'on/before 2025-11-04' END AS reg_bucket,
       COUNT(*) AS voters
FROM Historic.dbo.LTV2026_Ref_Base WHERE in_van = 0
GROUP BY CASE
         WHEN reg_date > '2026-03-01' THEN 'after VAN snapshot (>2026-03-01)'
         WHEN reg_date > '2025-11-04' THEN 'Nov 2025 G .. Mar 2026'
         WHEN reg_date IS NULL THEN 'no/unparseable date'
         ELSE 'on/before 2025-11-04' END
ORDER BY voters DESC;

PRINT '--- Age band ---';
SELECT CASE WHEN age BETWEEN 18 AND 24 THEN '18-24' WHEN age BETWEEN 25 AND 34 THEN '25-34'
            WHEN age BETWEEN 35 AND 44 THEN '35-44' WHEN age BETWEEN 45 AND 54 THEN '45-54'
            WHEN age BETWEEN 55 AND 64 THEN '55-64' WHEN age BETWEEN 65 AND 74 THEN '65-74'
            WHEN age >= 75 THEN '75+' ELSE 'Unknown' END AS age_band, COUNT(*) AS voters
FROM Historic.dbo.LTV2026_Ref_Base WHERE in_van = 0
GROUP BY CASE WHEN age BETWEEN 18 AND 24 THEN '18-24' WHEN age BETWEEN 25 AND 34 THEN '25-34'
            WHEN age BETWEEN 35 AND 44 THEN '35-44' WHEN age BETWEEN 45 AND 54 THEN '45-54'
            WHEN age BETWEEN 55 AND 64 THEN '55-64' WHEN age BETWEEN 65 AND 74 THEN '65-74'
            WHEN age >= 75 THEN '75+' ELSE 'Unknown' END
ORDER BY age_band;

PRINT '--- Gender / vote method ---';
SELECT gender, COUNT(*) AS voters FROM Historic.dbo.LTV2026_Ref_Base WHERE in_van=0 GROUP BY gender;
SELECT AB_Type, COUNT(*) AS voters FROM Historic.dbo.LTV2026_Ref_Base WHERE in_van=0 GROUP BY AB_Type ORDER BY voters DESC;

PRINT '--- Top 10 localities ---';
SELECT TOP 10 LOCALITYNAME, COUNT(*) AS voters FROM Historic.dbo.LTV2026_Ref_Base WHERE in_van=0
GROUP BY LOCALITYNAME ORDER BY COUNT(*) DESC;
