SET NOCOUNT ON;
-- 2025 General voters (still in Van) and whether they also voted the 2026 referendum.
IF OBJECT_ID('tempdb..#g25') IS NOT NULL DROP TABLE #g25;
SELECT
  v.StateFileID, v.Age, v.Sex, v.CountyName, v.CD,
  CASE WHEN v.LikelyParty IN ('SD','LD') THEN 'Dem'
       WHEN v.LikelyParty IN ('SR','LR') THEN 'Rep'
       WHEN TRY_CONVERT(float, v.Clarity_DemSupport_26) >= 50 THEN 'Dem'
       WHEN TRY_CONVERT(float, v.Clarity_DemSupport_26) < 50 THEN 'Rep'
       ELSE 'Unknown' END AS party,
  CASE WHEN EXISTS (SELECT 1 FROM Historic.dbo.LTV2026_Ref_Votemethod m
                    WHERE m.IDENTIFICATION_NUMBER = v.StateFileID) THEN 1 ELSE 0 END AS voted_ref
INTO #g25
FROM Voter.dbo.Van v
WHERE NULLIF(LTRIM(RTRIM(v.General25)),'') IS NOT NULL;

-- Overall
SELECT 'OVERALL' AS grp, COUNT(*) AS g25_voters, SUM(voted_ref) AS came_back,
  SUM(1-voted_ref) AS dropped_off,
  CAST(100.0*SUM(1-voted_ref)/COUNT(*) AS DECIMAL(5,1)) AS dropoff_pct
FROM #g25;

-- By party
SELECT party AS grp, COUNT(*) AS g25_voters, SUM(1-voted_ref) AS dropped_off,
  CAST(100.0*SUM(1-voted_ref)/COUNT(*) AS DECIMAL(5,1)) AS dropoff_pct
FROM #g25 GROUP BY party ORDER BY g25_voters DESC;

-- By age band
SELECT CASE WHEN Age BETWEEN 18 AND 24 THEN '18-24' WHEN Age BETWEEN 25 AND 34 THEN '25-34'
            WHEN Age BETWEEN 35 AND 44 THEN '35-44' WHEN Age BETWEEN 45 AND 54 THEN '45-54'
            WHEN Age BETWEEN 55 AND 64 THEN '55-64' WHEN Age BETWEEN 65 AND 74 THEN '65-74'
            WHEN Age >= 75 THEN '75+' ELSE 'Unknown' END AS grp,
  COUNT(*) AS g25_voters, SUM(1-voted_ref) AS dropped_off,
  CAST(100.0*SUM(1-voted_ref)/COUNT(*) AS DECIMAL(5,1)) AS dropoff_pct
FROM #g25 GROUP BY CASE WHEN Age BETWEEN 18 AND 24 THEN '18-24' WHEN Age BETWEEN 25 AND 34 THEN '25-34'
            WHEN Age BETWEEN 35 AND 44 THEN '35-44' WHEN Age BETWEEN 45 AND 54 THEN '45-54'
            WHEN Age BETWEEN 55 AND 64 THEN '55-64' WHEN Age BETWEEN 65 AND 74 THEN '65-74'
            WHEN Age >= 75 THEN '75+' ELSE 'Unknown' END ORDER BY grp;

-- By gender
SELECT UPPER(Sex) AS grp, COUNT(*) AS g25_voters, SUM(1-voted_ref) AS dropped_off,
  CAST(100.0*SUM(1-voted_ref)/COUNT(*) AS DECIMAL(5,1)) AS dropoff_pct
FROM #g25 WHERE UPPER(Sex) IN ('M','F') GROUP BY UPPER(Sex);

-- By Congressional District
SELECT CD AS grp, COUNT(*) AS g25_voters, SUM(1-voted_ref) AS dropped_off,
  CAST(100.0*SUM(1-voted_ref)/COUNT(*) AS DECIMAL(5,1)) AS dropoff_pct
FROM #g25 WHERE CD IS NOT NULL AND CD<>'' GROUP BY CD ORDER BY CD;
