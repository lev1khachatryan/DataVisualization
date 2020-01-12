SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

IF OBJECT_ID('DS_GetActivityByPlatform') IS NOT NULL
BEGIN
	DROP PROCEDURE DS_GetActivityByPlatform
END
GO
-----------------------------------------
-- Creator	: LKH					   --
-- Date		: 20190423				   --
-- Getting required data for dashboard --
-----------------------------------------
CREATE PROCEDURE dbo.DS_GetActivityByPlatform
@StartDate NVARCHAR(50),
@EndDate NVARCHAR(50)
AS
BEGIN
	SET @EndDate = DATEADD(MINUTE, -1, DATEADD(DAY, 1, @EndDate))

	select Case When Metric = 'active_users_android' then 'Android' else 'iOS' end as Platform, Count(DISTINCT UC.UserId) as CountOfUsers
	from StatisticsActiveUsers as UC
	where UC.Date >= @StartDate and UC.Date <= @EndDate
	and UC.Metric in ('active_users_android', 'active_users_ios')
	group by Metric
	OPTION(MAXDOP 3)

END
GO

IF OBJECT_ID('DS_GetConsumption_DailyTotalActivities') IS NOT NULL
BEGIN
	DROP PROCEDURE DS_GetConsumption_DailyTotalActivities
END
GO
------------------------------------------
-- Creator     : GCH					--
-- Date        : 20190424				--
-- Getting required data for dashboard	--
------------------------------------------
CREATE PROCEDURE dbo.DS_GetConsumption_DailyTotalActivities
		@StartDate date,
		@EndDate date
AS BEGIN
select * from [Statistics]
where date >= @StartDate and date<= @EndDate and metric in ('course_lessons_consumed',
															'user_lessons_consumed',
															'user_codes_consumed',
															'discuss_consumed',
															'user_posts_consumed',
															'profiles_consumed',
															'own_profiles_consumed',
															'contests_played')
order by date, metric
OPTION(MAXDOP 3)
END;
GO

IF OBJECT_ID('DS_GetConsumption_DailyTotalActivities_byPlatform') IS NOT NULL
BEGIN
	DROP PROCEDURE DS_GetConsumption_DailyTotalActivities_byPlatform
END
GO
-----------------------------------------
-- Creator	: GCH					   --
-- Date		: 20190510				   --
-- Getting required data for dashboard --
-----------------------------------------
CREATE PROCEDURE dbo.DS_GetConsumption_DailyTotalActivities_byPlatform
		@StartDate date,
		@EndDate date,
		@Platform int

AS BEGIN

IF @Platform = 1
	BEGIN
		select * from [Statistics]
		where date >= @StartDate and date<= @EndDate and metric in ('course_lessons_consumed_android',
															'user_lessons_consumed_android',
															'user_codes_consumed_android',
															'discuss_consumed_android',
															'user_posts_consumed_android',
															'profiles_consumed_android',
															'own_profiles_consumed_android',
															'contests_played_android')
		order by date, metric
		OPTION (MAXDOP 3)
	END

ELSE IF  @Platform = 2
	BEGIN
		select * from [Statistics]
		where date >= @StartDate and date<= @EndDate and metric in ('course_lessons_consumed_ios',
															'user_lessons_consumed_ios',
															'user_codes_consumed_ios',
															'discuss_consumed_ios',
															'user_posts_consumed_ios',
															'profiles_consumed_ios',
															'own_profiles_consumed_ios',
															'contests_played_ios')
		order by date, metric
		OPTION (MAXDOP 3)
	END

ELSE IF @platform = 3
	BEGIN
		select * from [Statistics]
		where date >= @StartDate and date<= @EndDate and metric in ('course_lessons_consumed',
															'user_lessons_consumed',
															'user_codes_consumed',
															'discuss_consumed',
															'user_posts_consumed',
															'profiles_consumed',
															'own_profiles_consumed',
															'contests_played')
		order by date, metric
		OPTION (MAXDOP 3)
	END

ELSE 
	BEGIN
	RAISERROR ('Please provide correct platform. Acceptable values: /1-Android/2-iOS/3-Total', 16, 1)
	END
END
GO

IF OBJECT_ID('DS_GetConsumption_DailyTotalActivityConsumers') IS NOT NULL
BEGIN
	DROP PROCEDURE DS_GetConsumption_DailyTotalActivityConsumers
END
GO
------------------------------------------
-- Creator     : GCH					--
-- Date        : 20190424				--
-- Getting required data for dashboard	--
------------------------------------------
CREATE PROCEDURE dbo.DS_GetConsumption_DailyTotalActivityConsumers
		@StartDate date,
		@EndDate date
AS BEGIN
select Date, Metric, count(DISTINCT UserId) as NofUsers from StatisticsActiveUsers
where date >= @StartDate and date<= @EndDate and metric in ('course_lessons_consumers',
															'user_lessons_consumers',
															'user_codes_consumers',
															'discuss_consumers',
															'user_posts_consumers',
															'profiles_consumers',
															'own_profiles_consumers',
															'contest_players')
group by date, metric
order by date, metric
OPTION(MAXDOP 3)
END;
GO

IF OBJECT_ID('DS_GetConsumption_DailyTotalActivityConsumers_byPlatform') IS NOT NULL
BEGIN
	DROP PROCEDURE DS_GetConsumption_DailyTotalActivityConsumers_byPlatform
END
GO
------------------------------------------
-- Creator     : GCH					--
-- Date        : 20190510				--
-- Getting required data for dashboard	--
------------------------------------------
CREATE PROCEDURE dbo.DS_GetConsumption_DailyTotalActivityConsumers_byPlatform
		@StartDate date,
		@EndDate date,
		@Platform int


AS BEGIN

IF @Platform = 1
	BEGIN
		select Date, Metric, count(DISTINCT UserId) as NofUsers from StatisticsActiveUsers
		where date >= @StartDate and date<= @EndDate and metric in ('course_lessons_consumers_android',
																	'user_lessons_consumers_android',
																	'user_codes_consumers_android',
																	'discuss_consumers_android',
																	'user_posts_consumers_android',
																	'profiles_consumers_android',
																	'own_profiles_consumers_android',
																	'contest_players_android')
		group by date, metric
		order by date, metric
		OPTION (MAXDOP 3)
	END

ELSE IF  @Platform = 2
	BEGIN
		select Date, Metric, count(DISTINCT UserId) as NofUsers from StatisticsActiveUsers
		where date >= @StartDate and date<= @EndDate and metric in ('course_lessons_consumers_ios',
																	'user_lessons_consumers_ios',
																	'user_codes_consumers_ios',
																	'discuss_consumers_ios',
																	'user_posts_consumers_ios',
																	'profiles_consumers_ios',
																	'own_profiles_consumers_ios',
																	'contest_players_ios')
		group by date, metric
		order by date, metric
		OPTION (MAXDOP 3)
	END

ELSE IF @platform = 3
	BEGIN
		select Date, Metric, count(DISTINCT UserId) as NofUsers from StatisticsActiveUsers
		where date >= @StartDate and date<= @EndDate and metric in ('course_lessons_consumers',
																	'user_lessons_consumers',
																	'user_codes_consumers',
																	'discuss_consumers',
																	'user_posts_consumers',
																	'profiles_consumers',
																	'own_profiles_consumers',
																	'contest_players')
		group by date, metric
		order by date, metric
		OPTION (MAXDOP 3)
	END

ELSE 
	BEGIN
	RAISERROR ('Please provide correct platform. Acceptable values: /1-Android/2-iOS/3-Total', 16, 1)
	END
END
GO

IF OBJECT_ID('DS_GetConsumption_LearnSocial') IS NOT NULL
BEGIN
	DROP PROCEDURE DS_GetConsumption_LearnSocial
END
GO
------------------------------------------
-- Creator     : GCH					--
-- Date        : 20190424				--
-- Getting required data for dashboard	--
------------------------------------------
CREATE PROCEDURE dbo.DS_GetConsumption_LearnSocial
		@StartDate date,
		@EndDate date
AS BEGIN
select U.UserId,
		(case when LC.UserId > 0 then 1 else 0 end) as Lesson_Consumers,
		(case when SC.UserId > 0 then 1 else 0 end) as Social_Content_Consumers
			from
	(select DISTINCT UserId from StatisticsActiveUsers
		where date >= @StartDate and date<= @EndDate and metric = 'active_users' ) as U
LEFT JOIN
	(select DISTINCT UserId from StatisticsActiveUsers
		where date >= @StartDate and date<= @EndDate and metric = 'course_lessons_consumers') as LC
		on U.UserId=LC.UserId
LEFT JOIN
	(select DISTINCT UserId from StatisticsActiveUsers
		where date >= @StartDate and date<= @EndDate and metric in ('user_codes_consumers',
																	'discuss_consumers',
																	'user_posts_consumers',
																	'profiles_consumers',
																	'contest_players')) as SC
		on U.UserId=SC.UserId
OPTION(MAXDOP 1)
END;
GO

IF OBJECT_ID('DS_GetCountryCodesForMap') IS NOT NULL
BEGIN
	DROP PROCEDURE DS_GetCountryCodesForMap
END
GO
-----------------------------------------
-- Creator	: LKH					   --
-- Date		: 20190412				   --
-- Getting required data for dashboard --
-----------------------------------------
CREATE PROCEDURE dbo.DS_GetCountryCodesForMap
@RegisterStartDate NVARCHAR(50) = NULL,
@RegisterEndDate NVARCHAR(50) = NULL
AS
BEGIN
	SET @RegisterEndDate = DATEADD(MINUTE, -1, DATEADD(DAY, 1, @RegisterEndDate))
	select UPPER(CountryCode) AS CountryCode, Count(U.Id) as CountOfUsers
	from Users as U
	where (U.RegisterDate >= @RegisterStartDate or @RegisterStartDate is null)
	and   (U.RegisterDate <= @RegisterEndDate or @RegisterEndDate is null)
	and CountryCode is not null
	and CountryCode <> ''
	and CountryCode <> '***'
	group by CountryCode
	order by  CountryCode
	OPTION(MAXDOP 3)
END
GO

IF OBJECT_ID('DS_GetCreatedContent') IS NOT NULL
BEGIN
	DROP PROCEDURE DS_GetCreatedContent
END
GO
------------------------------------------
-- Creator     : GCH					--
-- Date        : 20190424				--
-- Getting required data for dashboard	--
------------------------------------------
CREATE PROCEDURE dbo.DS_GetCreatedContent
		@StartDate date,
		@EndDate date

AS BEGIN

		select Cast(CreatedDate as Date) as Date , 'Created Codes' as metric, 
		SUM(cast(IsPublic as int)) as Published,
		SUM(Case when cast(IsPublic as int) = 0 then 1 else 0 end) as NotPublished
		from UserCodes as UC
		where UC.CreatedDate between @StartDate and @EndDate
		group by Cast(CreatedDate as Date)
	UNION ALL
		select Cast(Date as Date) as Date, 'Created Posts' as metric, 
		SUM(Case when cast(Status as int) = 0 then 1 else 0 end) as Published,
		SUM(Case when cast(Status as int) <> 0 then 1 else 0 end) as NotPublished
		from UserPosts as UP
		where UP.Date between @StartDate and @EndDate
		group by Cast(Date as Date)
	UNION ALL
		select Cast(Date as Date) as Date, 'Created Discussions' as metric, 
		SUM(Case when cast(Status as int) = 0 then 1 else 0 end) as Published,
		SUM(Case when cast(Status as int) <> 0 then 1 else 0 end) as NotPublished
		from DiscussionPosts as DP
		where DP.Date between @StartDate and @EndDate and ParentId IS NULL
		group by Cast(Date as Date)
	UNION ALL
		select Cast(Date as Date) as Date, 'Created Lessons' as metric, 
		SUM(cast(Published as int)) as Published,
		SUM(Case when cast(Published as int) = 0 then 1 else 0 end) as NotPublished
		from UserLessons as UL
		where UL.Date between @StartDate and @EndDate
		group by Cast(Date as Date)
	UNION ALL
		select Cast(Date as Date) as Date, 'Created Quizzes' as metric, 
		SUM(cast(Published as int)) as Published,
		SUM(Case when cast(Published as int) = 0 then 1 else 0 end) as NotPublished
		from Challenges as C
		where C.Date between @StartDate and @EndDate
		group by Cast(Date as Date)
	order by Metric, Date
	OPTION(MAXDOP 3)

END;
GO

IF OBJECT_ID('DS_GetCreatedContent_byPlatform') IS NOT NULL
BEGIN
	DROP PROCEDURE DS_GetCreatedContent_byPlatform
END
GO
------------------------------------------
-- Creator     : GCH					--
-- Date        : 20190510				--
-- Getting required data for dashboard	--
------------------------------------------
CREATE PROCEDURE dbo.DS_GetCreatedContent_byPlatform
		@StartDate date,
		@EndDate date,
		@Platform int

AS BEGIN

IF @Platform = 1
	BEGIN
		select * from [Statistics]
		where date between @StartDate and @EndDate and metric in
				('codes_created_public_android',
				'codes_created_private_android',
				'discuss_questions_created_android',
				'user_posts_created_android',
				'user_lessons_created_android',
				'quizzes_created_android')
		order by date
		OPTION (MAXDOP 3)
	END

ELSE IF  @Platform = 2
	BEGIN
		select * from [Statistics]
		where date between @StartDate and @EndDate and metric in
				('codes_created_public_ios',
				'codes_created_private_ios',
				'discuss_questions_created_ios',
				'user_posts_created_ios',
				'user_lessons_created_ios',
				'quizzes_created_ios')
		order by date
		OPTION (MAXDOP 3)
	END

ELSE IF @platform = 3
	BEGIN
		select * from [Statistics]
		where date between @StartDate and @EndDate and metric in
				('codes_created_public',
				'codes_created_private',
				'discuss_questions_created',
				'user_posts_created',
				'user_lessons_created',
				'quizzes_created')
		order by date
		OPTION (MAXDOP 3)
	END

ELSE 
	BEGIN
	RAISERROR ('Please provide correct platform. Acceptable values: /1-Android/2-iOS/3-Total', 16, 1)
	END
END
GO

IF OBJECT_ID('DS_GetStatistics') IS NOT NULL
BEGIN
	DROP PROCEDURE DS_GetStatistics
END
GO
-----------------------------------------
-- Creator	: LKH					   --
-- Date		: 20190412				   --
-- Getting required data for dashboard --
-----------------------------------------
CREATE PROCEDURE dbo.DS_GetStatistics
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
OPTION(MAXDOP 3)
END
GO

IF OBJECT_ID('DS_GetTopCountries') IS NOT NULL
BEGIN
	DROP PROCEDURE DS_GetTopCountries
END
GO
-----------------------------------------
-- Creator	: LKH					   --
-- Date		: 20190419				   --
-- Getting required data for dashboard --
-----------------------------------------
-----------------------------------------
CREATE PROCEDURE dbo.DS_GetTopCountries
	@StartDate AS VARCHAR(50),
	@EndDate AS VARCHAR(50),
	@By AS INT = 1 -- 1=SignUps, 2=Activities
AS
BEGIN
	SET NOCOUNT ON;
	SET @EndDate = DATEADD(MINUTE, -1, DATEADD(DAY, 1, @EndDate));

	IF @By = 1
	BEGIN
		SELECT TOP(5) CountryCode, COUNT(U.Id) as NumberOf , ROW_NUMBER() OVER(ORDER BY COUNT(U.Id) DESC) AS Place
		FROM Users AS U
		WHERE U.RegisterDate >= @StartDate
		AND U.RegisterDate <= @EndDate
		GROUP BY CountryCode
		ORDER BY COUNT(U.Id) DESC
		OPTION(MAXDOP 3)
	END

	ELSE IF @By = 2
	BEGIN
		SELECT 1
		--SELECT TOP(5) CountryCode
		--FROM Users AS U
		--JOIN UserCheckins AS UC ON U.Id = UC.UserId
		--WHERE U.RegisterDate >= @StartDate
		--AND U.RegisterDate <= @EndDate
		--GROUP BY CountryCode
		--ORDER BY COUNT(U.Id) DESC
	END

END
GO

IF OBJECT_ID('DS_GetUserActivities') IS NOT NULL
BEGIN
	DROP PROCEDURE DS_GetUserActivities
END
GO
-----------------------------------------
-- Creator	: LKH					   --
-- Date		: 20190412				   --
-- Getting required data for dashboard --
-----------------------------------------
CREATE PROCEDURE dbo.DS_GetUserActivities
@StartDate NVARCHAR(50),
@EndDate NVARCHAR(50),
@TimePeriod int = 1,  --  1=per day, 2=per week, 3=per month
@Platform int = 1 -- 1=Android, 2=iOS
AS
BEGIN
	SET @EndDate = DATEADD(MINUTE, -1, DATEADD(DAY, 1, @EndDate))
	IF @TimePeriod = 1
	BEGIN
		IF @Platform = 1
		BEGIN
			select cast(cast(UC.Date as date) as varchar(50)) as Date, Count(DISTINCT UC.UserId) as Checkins
			from StatisticsActiveUsers as UC
			where UC.Metric = 'active_users_android'
			and UC.Date >= @StartDate
			and UC.Date <= @EndDate
			group by cast(UC.Date as date)
			order by cast(UC.Date as date)
			OPTION(MAXDOP 3)
		END
		ELSE IF @Platform = 2
		BEGIN
			select cast(cast(UC.Date as date) as varchar(50)) as Date, Count(DISTINCT UC.UserId) as Checkins
			from StatisticsActiveUsers as UC
			where UC.Metric = 'active_users_ios'
			and UC.Date >= @StartDate
			and UC.Date <= @EndDate
			group by cast(UC.Date as date)
			order by cast(UC.Date as date)
			OPTION(MAXDOP 3)
		END
	END
	ELSE IF @TimePeriod = 2
	BEGIN
			SELECT year(UC.Date) as yr, datepart(wk, Date) as wk,
				cast(year(Date) as varchar(8)) + ' - Week ' + cast(datepart(wk, Date) as varchar(2)) as Date,
				Count(DISTINCT UC.UserID) as Checkins
			from StatisticsActiveUsers as UC
			where UC.Metric = 'active_users'
			and UC.Date >= @StartDate
			and UC.Date <= @EndDate
			group by year(UC.Date), datepart(wk, Date)
			order by yr, wk
			OPTION(MAXDOP 3)
	END
	ELSE IF @TimePeriod = 3
	BEGIN
			SELECT year(Date) as yr, 
				datename(mm, Date) as mm,   
				cast(year(Date) as varchar(8)) + ' - ' + cast(datename(mm, Date) as varchar(20)) as Date,
				Count(DISTINCT UC.UserID) as Checkins
			from StatisticsActiveUsers as UC
			where UC.Metric = 'active_users'
			and UC.Date >= @StartDate
			and UC.Date <= @EndDate
			group by year(Date), datename(mm, Date)
			order by yr, mm
			OPTION(MAXDOP 3)
	END

END
GO

IF OBJECT_ID('DS_GetUserConsumption') IS NOT NULL
BEGIN
	DROP PROCEDURE DS_GetUserConsumption
END
GO
-----------------------------------------
-- Creator	: LKH					   --
-- Date		: 20190412				   --
-- Getting required data for dashboard --
-----------------------------------------
CREATE PROCEDURE dbo.DS_GetUserConsumption
	@startDate as nvarchar(100),
	@endDate as nvarchar(100)
AS
BEGIN
select *
FROM(select Date, Metric, UserId
	from StatisticsActiveUsers
	where date >= @startDate and date<= @endDate and metric  in (
	'active_users',
	'course_lessons_consumers',
	'user_lessons_consumers',
	'user_codes_consumers',
	'user_posts_consumers',
	'discuss_consumers',
	'contest_players',
	'profiles_consumers',
	'own_profiles_consumers'
	)
	) as ddxk
PIVOT(
	COUNT(UserId)
	FOR Metric in (
	active_users,
	course_lessons_consumers,
	user_lessons_consumers,
	user_codes_consumers,
	user_posts_consumers,
	discuss_consumers,
	contest_players,
	profiles_consumers,
	own_profiles_consumers
	)
)AS PivotTable
OPTION(MAXDOP 3)
end
GO

IF OBJECT_ID('DS_GetUserConsumption_byPlatform') IS NOT NULL
BEGIN
	DROP PROCEDURE DS_GetUserConsumption_byPlatform
END
GO
-----------------------------------------
-- Creator	: GCH					   --
-- Date		: 20190510			   --
-- Getting required data for dashboard --
-----------------------------------------
CREATE PROCEDURE dbo.DS_GetUserConsumption_byPlatform
		@StartDate date,
		@EndDate date,
		@Platform int

AS BEGIN

IF @Platform = 1
	BEGIN
			select * from (select Date, Metric, UserId from StatisticsActiveUsers
					where date >= @StartDate and date<= @EndDate and metric  in (
											'active_users_android',
											'course_lessons_consumers_android',
											'user_lessons_consumers_android',
											'user_codes_consumers_android',
											'user_posts_consumers_android',
											'discuss_consumers_android',
											'contest_players_android',
											'profiles_consumers_android',
											'own_profiles_consumers_android'
												)) as ddxk
			PIVOT(
				COUNT(UserId)
				FOR Metric in (
						active_users_android,
						course_lessons_consumers_android,
						user_lessons_consumers_android,
						user_codes_consumers_android,
						user_posts_consumers_android,
						discuss_consumers_android,
						contest_players_android,
						profiles_consumers_android,
						own_profiles_consumers_android
						)
			)AS PivotTable
		OPTION (MAXDOP 3)
	END

ELSE IF  @Platform = 2
	BEGIN
			select * from (select Date, Metric, UserId from StatisticsActiveUsers
					where date >= @StartDate and date<= @EndDate and metric  in (
											'active_users_ios',
											'course_lessons_consumers_ios',
											'user_lessons_consumers_ios',
											'user_codes_consumers_ios',
											'user_posts_consumers_ios',
											'discuss_consumers_ios',
											'contest_players_ios',
											'profiles_consumers_ios',
											'own_profiles_consumers_ios'
												)) as ddxk
			PIVOT(
				COUNT(UserId)
				FOR Metric in (
						active_users_ios,
						course_lessons_consumers_ios,
						user_lessons_consumers_ios,
						user_codes_consumers_ios,
						user_posts_consumers_ios,
						discuss_consumers_ios,
						contest_players_ios,
						profiles_consumers_ios,
						own_profiles_consumers_ios
						)
			)AS PivotTable
		OPTION (MAXDOP 3)
	END

ELSE IF @platform = 3
	BEGIN
			select * from (select Date, Metric, UserId from StatisticsActiveUsers
					where date >= @StartDate and date<= @EndDate and metric  in (
											'active_users',
											'course_lessons_consumers',
											'user_lessons_consumers',
											'user_codes_consumers',
											'user_posts_consumers',
											'discuss_consumers',
											'contest_players',
											'profiles_consumers',
											'own_profiles_consumers'
												)) as ddxk
			PIVOT(
				COUNT(UserId)
				FOR Metric in (
						active_users,
						course_lessons_consumers,
						user_lessons_consumers,
						user_codes_consumers,
						user_posts_consumers,
						discuss_consumers,
						contest_players,
						profiles_consumers,
						own_profiles_consumers
						)
			)AS PivotTable
		OPTION (MAXDOP 3)
	END

ELSE 
	BEGIN
	RAISERROR ('Please provide correct platform. Acceptable values: /1-Android/2-iOS/3-Total', 16, 1)
	END
END
GO
