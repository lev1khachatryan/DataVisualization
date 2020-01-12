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

end_date_ = datetime.now().date()
start_date_ = (end_date_ - timedelta(days=10)).strftime('%Y-%m-%d')
end_date_ = end_date_.strftime('%Y-%m-%d')

periodicity_ = '1' # 1=day , 2=week, 3=month

venn_data = pd.read_sql_query('EXEC DS_GetConsumption_LearnSocial @StartDate = \'' + start_date_ + '\', @EndDate = \'' + end_date_ + '\'',cnxn)
venn_data.to_csv(r'data\venn_data.csv')
