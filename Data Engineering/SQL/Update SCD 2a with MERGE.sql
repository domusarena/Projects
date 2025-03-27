--- 1. MERGE Type 0 SCD ---

-- Create TARGET table
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[TestBeforeTable](
	[Id] [int] NOT NULL,
	[str_col] [nvarchar](50) NULL,
	[num_col] [float] NULL,
	[date_col] [datetime] NULL
) ON [PRIMARY]
GO

-- Insert data into TARGET table
INSERT INTO [dbo].[TestBeforeTable] VALUES (1, 'hello', 1, '2024-10-30')
INSERT INTO [dbo].[TestBeforeTable] VALUES (2, 'my', 12, '1998-05-27')
INSERT INTO [dbo].[TestBeforeTable] VALUES (3, 'name', 123, '2024-01-01')
INSERT INTO [dbo].[TestBeforeTable] VALUES (4, 'is', 1234, '1900-01-01')
INSERT INTO [dbo].[TestBeforeTable] VALUES (5, 'dom', 12345, '2006-07-21')

SELECT * FROM [dbo].[TestBeforeTable]

DELETE FROM [dbo].[TestBeforeTable]

-- Create SOURCE table
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[TestUpdatesTable](
	[Id] [int] NOT NULL,
	[str_col] [nvarchar](50) NULL,
	[num_col] [float] NULL,
	[date_col] [datetime] NULL
) ON [PRIMARY]
GO

-- Insert data into SOURCE table
INSERT INTO [dbo].[TestUpdatesTable] VALUES (1, 'hello', 1, '2024-10-30')
INSERT INTO [dbo].[TestUpdatesTable] VALUES (2, 'my', 12, '1998-05-27')
INSERT INTO [dbo].[TestUpdatesTable] VALUES (3, 'name', 123, '2024-01-01')
INSERT INTO [dbo].[TestUpdatesTable] VALUES (5, 'not dom', 12345, '2006-07-21')
INSERT INTO [dbo].[TestUpdatesTable] VALUES (6, 'why', 123456, '2012-06-06')

SELECT * FROM [dbo].[TestUpdatesTable]

DELETE FROM [dbo].[TestUpdatesTable]

-- Create MERGE statment
MERGE [dbo].[TestBeforeTable] AS TARGET
    USING [dbo].[TestUpdatesTable] AS SOURCE
    ON (TARGET.Id = SOURCE.Id)

    /* UPDATE */
    WHEN MATCHED
        -- Use hash of all columns to determine if an update has occurred 
        AND HASHBYTES('MD5', CONCAT_WS('|', TARGET.Id, TARGET.str_col, TARGET.num_col, TARGET.date_col)) <>
        HASHBYTES('MD5', CONCAT_WS('|', SOURCE.Id, SOURCE.str_col, SOURCE.num_col, SOURCE.date_col)) 
    THEN UPDATE
        SET TARGET.Id = SOURCE.Id,
        TARGET.str_col = SOURCE.str_col,
        TARGET.num_col = SOURCE.num_col,
        TARGET.date_col = SOURCE.date_col
    
    /* INSERT */
    WHEN NOT MATCHED BY TARGET
    THEN INSERT (Id, str_col, num_col, date_col)
        VALUES (SOURCE.Id, SOURCE.str_col, SOURCE.num_col, SOURCE.date_col)

    /* DELETE */
    WHEN NOT MATCHED BY SOURCE
    THEN DELETE;