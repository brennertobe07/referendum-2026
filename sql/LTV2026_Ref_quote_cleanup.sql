-- LTV2026_Ref_quote_cleanup.sql  (Phase 3, reference)
--
-- Sometimes literal double-quote characters survive into LTV data (e.g. "SMITH"
-- stored as a literal string with quote chars). This script removes them from
-- every string column dynamically.
--
-- RESULT for LTV2026_Ref: nearly a no-op. The source CSV is fully RFC-quoted and
-- was loaded with pandas.read_csv (which strips field quotes), so only ONE row had
-- a literal " character: APT_NUM = 'box#693 Jennings Hall""' (source data-entry
-- artifact where address overflow with escaped quotes landed in the apt field).
-- The cleanup removed those quote chars from that 1 row; 0 quotes remain in any
-- column. Kept for reference / future loads that used a quote-naive loader.
--
-- Detection (per column): see notes\quote_detect.sql
-- Cleanup builds one UPDATE per affected NVARCHAR/VARCHAR column.

SET NOCOUNT ON;

DECLARE @sql NVARCHAR(MAX) = N'';

SELECT @sql = @sql +
    N'UPDATE Historic.dbo.LTV2026_Ref SET [' + c.name + N'] = REPLACE([' + c.name +
    N'], ''"'', '''') WHERE [' + c.name + N'] LIKE ''%"%'';' + CHAR(10)
FROM sys.columns c
JOIN sys.types t ON c.user_type_id = t.user_type_id
WHERE c.object_id = OBJECT_ID('Historic.dbo.LTV2026_Ref')
  AND t.name IN ('nvarchar','varchar','nchar','char');

-- Review then execute. Uncomment to run:
-- EXEC sp_executesql @sql;
PRINT @sql;
