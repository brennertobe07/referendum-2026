SET NOCOUNT ON;
-- Does the young surge tilt partly reflect voters who turned 18 AFTER the 2025
-- General (so they were ineligible for 2025G, not "drop-out / irregular")?
-- 2025 General: 2025-11-04. Referendum: 2026-04-21.
-- Newly eligible = 18 by 2026-04-21 but under 18 on 2025-11-04 -> DOB in (2007-11-04, 2008-04-21].
;WITH s AS (
  SELECT b.voted_2025g, b.age_band,
         TRY_CONVERT(date, l.DOB, 101) AS dob
  FROM Historic.dbo.Surge_2026_Base b
  JOIN Historic.dbo.LTV2026_Ref l ON l.IDENTIFICATION_NUMBER = b.StateFileID
)
SELECT
  COUNT(*)                                                                  AS ref_voters_in_van,
  SUM(1-voted_2025g)                                                        AS surge_total,
  SUM(CASE WHEN dob > '2007-11-04' AND dob <= '2008-04-21' THEN 1 ELSE 0 END)            AS newly_eligible,
  SUM(CASE WHEN dob > '2007-11-04' AND dob <= '2008-04-21' AND voted_2025g=0 THEN 1 ELSE 0 END) AS newly_elig_surge,
  SUM(CASE WHEN age_band='18-24' THEN 1 ELSE 0 END)                         AS b1824,
  SUM(CASE WHEN age_band='18-24' AND voted_2025g=0 THEN 1 ELSE 0 END)       AS b1824_surge,
  SUM(CASE WHEN age_band='18-24' AND dob <= '2007-11-04' THEN 1 ELSE 0 END) AS b1824_eligible2025,
  SUM(CASE WHEN age_band='18-24' AND dob <= '2007-11-04' AND voted_2025g=0 THEN 1 ELSE 0 END) AS b1824_elig_surge,
  SUM(CASE WHEN age_band='25-34' AND voted_2025g=0 THEN 1 ELSE 0 END)       AS b2534_surge
FROM s;
