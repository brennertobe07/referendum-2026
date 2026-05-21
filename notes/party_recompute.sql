SET NOCOUNT ON;
-- Dashboard methodology: hard party ID first, then split ND/U/I by Clarity_DemSupport_26 at 50.
-- VOTED side (from analysis base table)
SELECT 'VOTED' AS side,
  CASE
    WHEN LikelyParty IN ('SD','LD') THEN 'Dem'
    WHEN LikelyParty IN ('SR','LR') THEN 'Rep'
    WHEN dem_support >= 50 THEN 'Dem'
    WHEN dem_support < 50 THEN 'Rep'
    ELSE 'Unknown' END AS party2,
  COUNT(*) AS n
FROM Historic.dbo.LTV2026_Ref_Base
GROUP BY CASE
    WHEN LikelyParty IN ('SD','LD') THEN 'Dem'
    WHEN LikelyParty IN ('SR','LR') THEN 'Rep'
    WHEN dem_support >= 50 THEN 'Dem'
    WHEN dem_support < 50 THEN 'Rep'
    ELSE 'Unknown' END;

-- REGISTERED side (from Van)
SELECT 'REGISTERED' AS side,
  CASE
    WHEN LikelyParty IN ('SD','LD') THEN 'Dem'
    WHEN LikelyParty IN ('SR','LR') THEN 'Rep'
    WHEN TRY_CONVERT(float, Clarity_DemSupport_26) >= 50 THEN 'Dem'
    WHEN TRY_CONVERT(float, Clarity_DemSupport_26) < 50 THEN 'Rep'
    ELSE 'Unknown' END AS party2,
  COUNT(*) AS n
FROM Voter.dbo.Van
GROUP BY CASE
    WHEN LikelyParty IN ('SD','LD') THEN 'Dem'
    WHEN LikelyParty IN ('SR','LR') THEN 'Rep'
    WHEN TRY_CONVERT(float, Clarity_DemSupport_26) >= 50 THEN 'Dem'
    WHEN TRY_CONVERT(float, Clarity_DemSupport_26) < 50 THEN 'Rep'
    ELSE 'Unknown' END;
