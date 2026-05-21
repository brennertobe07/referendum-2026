SET NOCOUNT ON;
-- Dynamically count rows containing a double-quote character in each column.
DECLARE @sql NVARCHAR(MAX) = N'';
SELECT @sql = @sql +
    N'SELECT ''' + c.name + N''' AS col, COUNT(*) AS quote_rows ' +
    N'FROM Historic.dbo.LTV2026_Ref WHERE [' + c.name + N'] LIKE ''%"%'' UNION ALL '
FROM sys.columns c
WHERE c.object_id = OBJECT_ID('Historic.dbo.LTV2026_Ref');
SET @sql = LEFT(@sql, LEN(@sql) - 10);   -- strip trailing UNION ALL
SET @sql = N'SELECT col, quote_rows FROM (' + @sql + N') x WHERE quote_rows > 0 ORDER BY quote_rows DESC;';
EXEC sp_executesql @sql;
SELECT 'columns_with_quotes' AS summary, COUNT(*) AS n FROM (
    SELECT 1 AS one
) z WHERE 1=0;  -- placeholder; real result above
