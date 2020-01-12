import pandas as pd
import numpy as np
from datetime import datetime, timedelta

#====================================================================================== Connecting to DB
import pyodbc
# cnxn = pyodbc.connect("Driver={SQL Server Native Client 11.0};"
#                       "Server=;"
#                       "Database=;"
#                       "Uid=;"
#                       "Pwd=;"
#                       "MARS_Connection=Yes;")

cnxn = pyodbc.connect("Driver={SQL Server Native Client 11.0};"
                      "Server=;"
                      "Database=;"
                      "Uid=;"
                      "Pwd=;"
                      "MARS_Connection=Yes;")

end_date_ = datetime.now().date()
start_date_ = (end_date_ - timedelta(days=10)).strftime('%Y-%m-%d')
end_date_ = end_date_.strftime('%Y-%m-%d')

periodicity_ = '1' # 1=day , 2=week, 3=month

SignupsPerCountry = pd.read_sql_query('EXEC DS_GetCountryCodesForMap @RegisterStartDate = \''+start_date_+'\', @RegisterEndDate = \''+end_date_+'\'', cnxn)
SignupsPerCountry.to_csv(r'data\SignupsPerCountry.csv')

top_countries = pd.read_sql_query('EXEC DS_GetTopCountries \''+start_date_+'\',\''+end_date_+'\', 1', cnxn)
top_countries.to_csv(r'data\top_countries.csv')

UserActivities_Android = pd.read_sql_query('EXEC DS_GetUserActivities \''+start_date_+'\',\''+end_date_+'\','+periodicity_ + ',1', cnxn)
UserActivities_Android.to_csv(r'data\UserActivities_Android.csv')

UserActivities_iOS = pd.read_sql_query('EXEC DS_GetUserActivities \''+start_date_+'\',\''+end_date_+'\','+periodicity_ + ',2', cnxn)
UserActivities_iOS.to_csv(r'data\UserActivities_iOS.csv')

PieActivities = pd.read_sql_query('EXEC DS_GetActivityByPlatform  \''+start_date_+'\',\''+end_date_+'\'', cnxn)
PieActivities.to_csv(r'data\PieActivities.csv')

created_content = pd.read_sql_query('EXEC DS_GetCreatedContent_byPlatform \''+start_date_+'\',\''+end_date_+'\',' + '3', cnxn)
created_content.to_csv(r'data\created_content.csv')
created_content_android = pd.read_sql_query('EXEC DS_GetCreatedContent_byPlatform \''+start_date_+'\',\''+end_date_+'\',' + '1', cnxn)
created_content_android.to_csv(r'data\created_content_android.csv')
created_content_ios = pd.read_sql_query('EXEC DS_GetCreatedContent_byPlatform \''+start_date_+'\',\''+end_date_+'\',' + '2', cnxn)
created_content_ios.to_csv(r'data\created_content_ios.csv')

user_consumption = pd.read_sql_query('EXEC DS_GetUserConsumption_byPlatform \''+start_date_+'\',\''+end_date_+'\','+'3', cnxn)
user_consumption.to_csv(r'data\user_consumption.csv')
user_consumption_android = pd.read_sql_query('EXEC DS_GetUserConsumption_byPlatform \''+start_date_+'\',\''+end_date_+'\','+'1', cnxn)
user_consumption_android.to_csv(r'data\user_consumption_android.csv')
user_consumption_ios = pd.read_sql_query('EXEC DS_GetUserConsumption_byPlatform \''+start_date_+'\',\''+end_date_+'\','+'2', cnxn)
user_consumption_ios.to_csv(r'data\user_consumption_ios.csv')

cons1 = pd.read_sql_query('EXEC DS_GetConsumption_DailyTotalActivityConsumers_byPlatform \''+start_date_+'\',\''+end_date_+'\','+'3', cnxn)
cons2 = pd.read_sql_query('EXEC DS_GetConsumption_DailyTotalActivities_byPlatform \''+start_date_+'\',\''+end_date_+'\','+'3', cnxn)
cons1.to_csv(r'data\cons1.csv')
cons2.to_csv(r'data\cons2.csv')

cons1_android = pd.read_sql_query('EXEC DS_GetConsumption_DailyTotalActivityConsumers_byPlatform \''+start_date_+'\',\''+end_date_+'\','+'1', cnxn)
cons2_android = pd.read_sql_query('EXEC DS_GetConsumption_DailyTotalActivities_byPlatform \''+start_date_+'\',\''+end_date_+'\','+'1', cnxn)
cons1_android.to_csv(r'data\cons1_android.csv')
cons2_android.to_csv(r'data\cons2_android.csv')

cons1_ios = pd.read_sql_query('EXEC DS_GetConsumption_DailyTotalActivityConsumers_byPlatform \''+start_date_+'\',\''+end_date_+'\','+'2', cnxn)
cons2_ios = pd.read_sql_query('EXEC DS_GetConsumption_DailyTotalActivities_byPlatform \''+start_date_+'\',\''+end_date_+'\','+'2', cnxn)
cons1_ios.to_csv(r'data\cons1_ios.csv')
cons2_ios.to_csv(r'data\cons2_ios.csv')

signups = pd.read_sql_query('EXEC DS_GetStatistics \''+start_date_+'\',\''+end_date_+'\'', cnxn)
signups.to_csv(r'data\signups.csv')
