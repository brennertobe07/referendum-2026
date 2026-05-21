SET NOCOUNT ON;
-- Build + execute one UPDATE per string column that actually contains a quote.
DECLARE @sql NVARCHAR(MAX) = N'';
SELECT @sql = @sql +
    N'UPDATE Historic.dbo.LTV2026_Ref SET [' + c.name + N'] = REPLACE([' + c.name +
    N'], ''"'', '''') WHERE [' + c.name + N'] LIKE ''%"%'';' + CHAR(10)
FROM sys.columns c
JOIN sys.types t ON c.user_type_id = t.user_type_id
WHERE c.object_id = OBJECT_ID('Historic.dbo.LTV2026_Ref')
  AND t.name IN ('nvarchar','varchar','nchar','char')
  AND EXISTS (  -- only columns that currently have a quote, evaluated below per col
      SELECT 1);
-- Restrict dynamically to columns that contain quotes (avoids scanning-update of clean cols):
SET @sql = N'';
DECLARE @col SYSNAME, @cnt INT;
DECLARE cur CURSOR LOCAL FAST_FORWARD FOR
    SELECT c.name FROM sys.columns c JOIN sys.types t ON c.user_type_id=t.user_type_id
    WHERE c.object_id=OBJECT_ID('Historic.dbo.LTV2026_Ref')
      AND t.name IN ('nvarchar','varchar','nchar','char');
OPEN cur;
FETCH NEXT FROM cur INTO @col;
WHILE @@FETCH_STATUS = 0
BEGIN
    DECLARE @chk NVARCHAR(MAX) =
        N'SELECT @c = COUNT(*) FROM Historic.dbo.LTV2026_Ref WHERE [' + @col + N'] LIKE ''%"%'';';
    EXEC sp_executesql @chk, N'@c INT OUTPUT', @c=@cnt OUTPUT;
    IF @cnt > 0
    BEGIN
        DECLARE @upd NVARCHAR(MAX) =
            N'UPDATE Historic.dbo.LTV2026_Ref SET [' + @col + N'] = REPLACE([' + @col +
            N'], ''"'', '''') WHERE [' + @col + N'] LIKE ''%"%'';';
        EXEC sp_executesql @upd;
        PRINT 'Cleaned column [' + @col + '] - rows affected: ' + CAST(@cnt AS VARCHAR(20));
    END
    FETCH NEXT FROM cur INTO @col;
END
CLOSE cur; DEALLOCATE cur;

-- Verify zero remain
DECLARE @remain INT = 0, @s NVARCHAR(MAX) = N'';
SELECT @s = @s + N'SELECT @r=@r+COUNT(*) FROM Historic.dbo.LTV2026_Ref WHERE ['+c.name+N'] LIKE ''%"%'';'
FROM sys.columns c WHERE c.object_id=OBJECT_ID('Historic.dbo.LTV2026_Ref');
EXEC sp_executesql @s, N'@r INT OUTPUT', @r=@remain OUTPUT;
PRINT 'Remaining rows with quotes across all columns: ' + CAST(@remain AS VARCHAR(20));
