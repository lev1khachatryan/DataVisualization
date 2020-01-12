import pandas as pd
import numpy as np
from datetime import datetime, timedelta

#====================================================================================== Connecting to DB
import pyodbc
cnxn = pyodbc.connect("Driver={SQL Server Native Client 11.0};"
                      "Server=;"
                      "Database=;"
                      "Uid=;"
                      "Pwd=;"
                      "MARS_Connection=Yes;")

end_date_new = datetime.now().date()
start_date_new = (end_date_new - timedelta(days=30)).strftime('%Y-%m-%d')
end_date_new = end_date_new.strftime('%Y-%m-%d')

end_date_old = datetime.now().date()
end_date_old = end_date_old - timedelta(days=30)
start_date_old  = (end_date_old - timedelta(days=30)).strftime('%Y-%m-%d')
end_date_old = end_date_old.strftime('%Y-%m-%d')

platform_signup = '1114' # 1114 android, 1122 ios
platform_subs = '1' # 3 ios, 1 andoird

signups_old = pd.read_sql_query('exec DS_GetNumberOfSignupsByCountry @RegistrationStartDate = \'' + start_date_old + '\', ' +
         '@RegistrationEndDate = \'' + end_date_old+ '\', ' + '@Platform = '+ platform_signup, cnxn)
signups_old.to_csv(r'data\signups_old.csv')
subs_old = pd.read_sql_query('exec DS_GetSubscriptions @RegistrationStartDate = \'' + start_date_old + '\', ' +
         '@RegistrationEndDate = \'' + end_date_old+ '\', ' + '@Platform = '+ platform_subs, cnxn)
subs_old.to_csv(r'data\subs_old.csv')


signups_new = pd.read_sql_query('exec DS_GetNumberOfSignupsByCountry @RegistrationStartDate = \'' + start_date_new + '\', ' +
         '@RegistrationEndDate = \'' + end_date_new + '\', ' + '@Platform = '+ platform_signup, cnxn)
signups_new.to_csv(r'data\signups_new.csv')
subs_new = pd.read_sql_query('exec DS_GetSubscriptions @RegistrationStartDate = \'' + start_date_new + '\', ' +
         '@RegistrationEndDate = \'' + end_date_new+ '\', ' + '@Platform = '+ platform_subs, cnxn)
subs_new.to_csv(r'data\subs_new.csv')
