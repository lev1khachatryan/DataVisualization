-----------------------------------------
-- Creator	: LKH					   --
-- Date		: 20190412				   --
-- Getting required data for dashboard --
-----------------------------------------
ALTER PROCEDURE [dbo].[DS_GetStatistics]
	@StartDate Datetime = NULL,
	@EndDate DateTime = NULL
AS
BEGIN
SELECT *
FROM(
	SELECT Metric, Value, Date
	FROM [Statistics]
	WHERE Metric in
	(
	'signups',
	'signups_fb',
	'signups_google',
	'signups_android',
	'signups_android_fb',
	'signups_android_google',
	'signups_ios',
	'signups_ios_fb',
	'signups_ios_google',
	'signups_web',
	'signups_web_fb',
	'signups_web_google'
	)
		) as Pivot_Stat
	PIVOT(
		SUM(Value)
		FOR Metric in (
			signups,
			signups_fb,
			signups_google,
			signups_android,
			signups_android_fb,
			signups_android_google,
			signups_ios,
			signups_ios_fb,
			signups_ios_google,
			signups_web,
			signups_web_fb,
			signups_web_google )
)AS PivotTable
where (@StartDate IS NUll OR Date >= @StartDate )
and (@EndDate IS NUll OR Date <= @EndDate )
OPTION(MAXDOP 3)
END
GO
