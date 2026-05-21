-- LTV2026_Ref_Votemethod_build.sql
-- Builds Historic.dbo.LTV2026_Ref_Votemethod (Phase 2b).
--
-- SBE did not publish a *_Votemethod file for the April 21, 2026 referendum, so
-- vote method is DERIVED from Absentee.dbo.Daily_Absentee_List (which still holds
-- the 26SP_Apr cycle) joined to Historic.dbo.LTV2026_Ref on IDENTIFICATION_NUMBER.
--
-- Output schema matches the prior cycle's Historic.dbo.LTV2025_GEN_Votemethod:
--   IDENTIFICATION_NUMBER, ABSENTEE, AB_Type, ELECTION_NAME
--
-- AB_Type mapping:
--   ABSENTEE = 'False'                                   -> 'Polls'        (election day)
--   ABSENTEE = 'True'  AND BALLOT_STATUS = 'On Machine'  -> 'AB_Inperson'  (in-person early)
--   ABSENTEE = 'True'  AND BALLOT_STATUS IN
--                          ('Marked','Pre-Processed')    -> 'AB_Mail'      (mail)
--   ABSENTEE = 'True'  (no voted-status DAL match)        -> 'AB_Other'     (late/prov/unmatched)
--
-- DAL is deduplicated to one row per voter using the absentee dashboard priority
-- Marked > Pre-Processed > On Machine > (other), then most recent ballot receipt.

IF OBJECT_ID('Historic.dbo.LTV2026_Ref_Votemethod','U') IS NOT NULL
    DROP TABLE Historic.dbo.LTV2026_Ref_Votemethod;
GO

WITH dal AS (
    SELECT
        IDENTIFICATION_NUMBER,
        BALLOT_STATUS,
        ROW_NUMBER() OVER (
            PARTITION BY IDENTIFICATION_NUMBER
            ORDER BY
                CASE BALLOT_STATUS
                    WHEN 'Marked'        THEN 1
                    WHEN 'Pre-Processed' THEN 2
                    WHEN 'On Machine'    THEN 3
                    ELSE 4
                END,
                BALLOT_RECEIPT_DATE DESC
        ) AS rn
    FROM Absentee.dbo.Daily_Absentee_List
    WHERE ELECTION_NAME = '2026 April 21 Special'
),
dal1 AS (
    SELECT IDENTIFICATION_NUMBER, BALLOT_STATUS
    FROM dal
    WHERE rn = 1
)
SELECT
    l.IDENTIFICATION_NUMBER,
    l.ABSENTEE,
    CASE
        WHEN l.ABSENTEE = 'False'                                   THEN 'Polls'
        WHEN d.BALLOT_STATUS = 'On Machine'                         THEN 'AB_Inperson'
        WHEN d.BALLOT_STATUS IN ('Marked','Pre-Processed')          THEN 'AB_Mail'
        ELSE 'AB_Other'
    END AS AB_Type,
    l.ELECTION_NAME
INTO Historic.dbo.LTV2026_Ref_Votemethod
FROM Historic.dbo.LTV2026_Ref l
LEFT JOIN dal1 d
    ON d.IDENTIFICATION_NUMBER = l.IDENTIFICATION_NUMBER;
GO

CREATE INDEX IX_LTV2026_Ref_Votemethod_ID
    ON Historic.dbo.LTV2026_Ref_Votemethod (IDENTIFICATION_NUMBER);
GO

-- Distribution report
SELECT ABSENTEE, AB_Type, COUNT(*) AS c
FROM Historic.dbo.LTV2026_Ref_Votemethod
GROUP BY ABSENTEE, AB_Type
ORDER BY c DESC;
GO
