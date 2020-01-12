import dash
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objs as go
import dash_daq as daq
import dash_table

import datetime
from datetime import datetime as dt
from datetime import timedelta
import dateutil.relativedelta

import pandas as pd
import numpy as np

import warnings
warnings.filterwarnings("ignore")

# from UsedFunctions import *

#====================================================================================== Connecting to DB
import pyodbc
cnxn = pyodbc.connect("Driver={SQL Server Native Client 11.0};"
                      "Server=;"
                      "Database=;"
                      "Uid=;"
                      "Pwd=;"
                      "MARS_Connection=Yes;")

cnxn1 = pyodbc.connect("Driver={SQL Server Native Client 11.0};"
                      "Server=;"
                      "Database=;"
                      "Uid=;"
                      "Pwd=;"
                      "MARS_Connection=Yes;")

#====================================================================================== Collecting the global data
#------------ Map
TrueCodes = pd.read_csv(r'data\CountryCodes.csv')
drop_box = []
drop_box.append('All')
for country in TrueCodes.Entity.values:
    drop_box.append(country)
countries = pd.read_csv('data/CC.csv', keep_default_na=False)
prices = pd.read_csv('data/PriceChangeLog.csv', keep_default_na=False)
df_sub = pd.read_csv('data/country_data.csv')


#-------------------------------------------------------------------- Data: Retention
cohort_android = pd.read_sql_query('EXEC DS_GetRetentionAndroidData', cnxn1)
cohort_android_transpose = cohort_android.set_index('Registration Period').T

cohort_ios = pd.read_sql_query('EXEC DS_GetRetentionIOSData', cnxn1)
cohort_ios_transpose = cohort_ios.set_index('Registration Period').T

#====================================================================================== Activity colors
colors = dict(red = '#d62728', #brick red
                orange = '#ff7f0e',#safety orange
                pink = '#e377c2',#raspberry yogurt pink
                green = '#2ca02c',#cooked asparagus green
                purple = '#9467bd',#muted purple
                blue = '#1f77b4',#muted blue
                blue_teal = '#17becf', #blue-teal
                brown = '#8c564b',#chestnut brown
                gray = '#7f7f7f',#middle gray
                yellow = '#bcbd22', #curry yellow-green
              )

map_colorscale = [
        [0, "#08519c"],
        [0.5, "#6baed6"],
        [1, "#9ecae1"]
    ]

activity_color = {'Lesson': 'red',
                    'User Lesson': 'orange',
                    'Q&A': 'purple',
                    'User Post': 'green',
                    'Code': 'blue',
                    'Quiz': 'brown',
                    'Contest': 'brown',
                    'Profile': 'pink',
                    'Own Profile': 'yellow',
                    'Private Codes': 'blue_teal'}

design_colors = {
    'page_bg':            '#0f2331',
    'chart_bg':           '#0e2e43',
    'chart_box_bg':       '#0e2e43',
    'box_borders':        '#143756',
    'Android':            '#5ab4ac',
    'iOS':                '#d8b365',
    'Web':                '#f5f5f5',
    'text':               '#eaf5fc',
    'title':              '#eaf5fc',
    'chart_axis_legends': '#a1aba0',
    'chart_inside_lines': '#334d61'
}

design_padding = {
    'level_1': '5px',
    'level_2': '0 20'
}

date_format = 'MMM Do, YY'
title_size = 20

dcc_graph_height = 350

design_padding = {
    'level_1': '5px'
}

box_shadow = '0px 0px 0px 2px rgb(20, 55, 86)'

#====================================================================================== The Dash app
app = dash.Dash(__name__)
external_css = ["https://cdnjs.cloudflare.com/ajax/libs/normalize/7.0.0/normalize.min.css",
                "https://cdnjs.cloudflare.com/ajax/libs/skeleton/2.0.4/skeleton.min.css",
                "//fonts.googleapis.com/css?family=Raleway:400,300,600",
                'https://codepen.io/plotly/pen/YEYMBZ.css',
                "https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css",
                'https://codepen.io/chriddyp/pen/bWLwgP.css']

for css in external_css:
    app.css.append_css({"external_url": css})

# ------------------------------------------------------------------------------------- Used Fnctions
def get_country_code(country_name):
    country_code = TrueCodes.loc[TrueCodes.Entity == country_name, ['rand']].values[0][0]
    return str(country_code)


def get_funnel(start_date, end_date, platform, country=None):
    if country:
        subscriptions = pd.read_sql_query(
            'exec DS_Funnel @StartDate = \'' + start_date + '\', ' +
            '@EndDate = \'' + end_date + '\', ' +
            '@Platform = \'' + platform + '\',' +
            '@Country = \'' + country + '\'', cnxn)
    else:
        subscriptions = pd.read_sql_query(
            'exec DS_Funnel @StartDate = \'' + start_date + '\', ' +
            '@EndDate = \'' + end_date + '\', ' +
            '@Platform = ' + platform + ' ', cnxn)
    subs = []

    subs.append(int(subscriptions.loc[subscriptions.CountryCode.notnull(), ['TotalSignups']].sum()))

    subs.append(int(subscriptions.loc[subscriptions.CountryCode.notnull(), ['TotalSubs']].sum()))

    subs.append(int(subscriptions.loc[subscriptions.CountryCode.notnull(), ['MonthlyOld']].sum()) + \
                int(subscriptions.loc[subscriptions.CountryCode.notnull(), ['MonthlyNew']].sum()) + \
                int(subscriptions.loc[subscriptions.CountryCode.notnull(), ['AnnualOld']].sum()) + \
                int(subscriptions.loc[subscriptions.CountryCode.notnull(), ['AnnualNew']].sum()))

    text = []
    for i in range(len(subs)):
        if i == 0:
            text.append('#: ' + str(subs[i]))
        else:
            subs[0] = subs[0] if subs[0] != 0 else 1
            text.append('#: ' + str(subs[i]) + ' <br> ' + '%: ' + str(np.round(subs[i] / subs[0] * 100, 3)))
    # if platform == '1122':
    #     subs[0] = subs[0] / 10
    #     subs[1] = subs[1] * 2
    #     subs[2] = subs[2] * 6
    # else:
    #     subs[0] = subs[0] / 20
    #     subs[1] = subs[1] * 2
    #     subs[2] = subs[2] * 4
    return subs, text

def price_finder(row):
    country_code, platform, created_date, sub_type  = row[['CountryCode', 'Platform', 'CreatedDate', 'SubscriptionType']].values
    return prices[prices.CC == country_code][prices.Platform == platform][prices.Subscription_type == sub_type][prices.StartDate < created_date][prices.EndDate >= created_date].Price.values[0]

def subs_table_constructor(subs, prices, countries, signups):
    subs['CountryCode'] = subs['CountryCode'].apply(lambda x: x.upper())
    signups['CountryCode'] = signups['CountryCode'].apply(lambda x: x.upper())

    subs['CountryCode'] = subs['CountryCode'].replace(np.nan, 'NA', regex=True)
    signups['CountryCode'] = signups['CountryCode'].replace(np.nan, 'NA', regex=True)

    subs["SubscriptionType"] = subs["SubscriptionType"].map({'sololearn_pro_test': "monthly", 'sololearn_pro_annual': "annual", 'sololearn_pro_monthly': "monthly"})

    prices["StartDate"] = pd.to_datetime(prices["StartDate"], dayfirst=True)
    prices["EndDate"] = pd.to_datetime(prices["EndDate"], dayfirst=True)

    subs["SubscriptionStartDate"] = pd.to_datetime(subs["SubscriptionStartDate"], dayfirst=True)
    subs["SubscriptionEndDate"] = pd.to_datetime(subs["SubscriptionEndDate"], dayfirst=True)

    subs['Paid'] = np.where((subs.SubscriptionEndDate - subs.SubscriptionStartDate) > datetime.timedelta(days=5), 1, 0)

    subs['Annual'] = np.where((subs.SubscriptionType == "annual") & (subs.Paid == 1), 1, 0)
    subs['Monthly'] = np.where((subs.SubscriptionType == "monthly") & (subs.Paid == 1), 1, 0)

    subs["Price"] = subs.apply(price_finder, axis=1)

    subs["Revenue"] = subs.Price * subs.Paid

    subs_df = subs.groupby("CountryCode").agg({'Platform': 'count', "Paid": 'sum', "Monthly": 'sum', "Annual": 'sum', "Revenue": 'sum'})

    subs_df.rename(columns={'Platform': 'TotalSubs'}, inplace = True)

    final_df = pd.merge(pd.merge(countries, signups), subs_df, on="CountryCode")
    final_df["Revenue_per_user"] = final_df.Revenue / final_df.NumberOfSignups
    final_df["Cancel_rate"] = 1 - final_df.Paid / final_df.TotalSubs
    final_df = final_df.round(3)

    return final_df

table_new = dash_table.DataTable(
                        id='table_new',
                        columns= [
                                # {'name': 'CountryCode', 'id': 'CountryCode'},
                                 {'name': 'Country', 'id': 'Country'},
                                 {'name': 'NumberOfSignups', 'id': 'NumberOfSignups'},
                                 {'name': 'TotalSubs', 'id': 'TotalSubs'},
                                 {'name': 'Paid', 'id': 'Paid'},
                                 {'name': 'Monthly', 'id': 'Monthly'},
                                 {'name': 'Annual', 'id': 'Annual'},
                                 {'name': 'Revenue', 'id': 'Revenue'},
                                 {'name': 'Revenue_per_user', 'id': 'Revenue_per_user'},
                                 {'name': 'Cancel_rate', 'id': 'Cancel_rate'}],
                        filtering=True,
                        sorting=True,
                        style_as_list_view=True,
                        style_header={
                            'backgroundColor': 'white',
                            'fontWeight': 'bold'
                        },
                        style_cell_conditional=[
                            {
                                'if': {'row_index': 'odd'},
                                'backgroundColor': 'rgb(238, 238, 238)'
                            },
                            {   'if': {'column_id': 'Country'}, 'width': '20%'},
                            {   'if': {'column_id': 'NumberOfSignups'}, 'width': '10%'},
                            {   'if': {'column_id': 'TotalSubs'}, 'width': '10%'},
                            {   'if': {'column_id': 'Paid'}, 'width': '10%'},
                            {   'if': {'column_id': 'Monthly'}, 'width': '10%'},
                            {   'if': {'column_id': 'Annual'}, 'width': '10%'},
                            {   'if': {'column_id': 'Revenue'}, 'width': '10%'},
                            {   'if': {'column_id': 'Revenue_per_user'}, 'width': '10%'},
                            {   'if': {'column_id': 'Cancel_rate'}, 'width': '10%'},
                            
                        ],
                        n_fixed_rows=1,
                        # style_cell={'width': '150px'},
                        style_table={
                            'maxHeight': '500',
                            'overflowY': 'scroll'
                        },
                        # style_data_conditional=[
                        #         {
                        #             'if': {
                        #                 'column_id': 'Number of Solar Plants',
                        #                 # 'filter': '{Number of Solar Plants} > 3.9'
                        #             },
                        #             'backgroundColor': '#3D9970',
                        #             'color': 'white',
                        #         }
                        # ]
)

# table_old = dash_table.DataTable(
#                         id='table_old',
#                         columns= [
#                                 # {'name': 'CountryCode', 'id': 'CountryCode'},
#                                  {'name': 'Country', 'id': 'Country'},
#                                  {'name': 'NumberOfSignups', 'id': 'NumberOfSignups'},
#                                  {'name': 'TotalSubs', 'id': 'TotalSubs'},
#                                  {'name': 'Paid', 'id': 'Paid'},
#                                  {'name': 'Monthly', 'id': 'Monthly'},
#                                  {'name': 'Annual', 'id': 'Annual'},
#                                  {'name': 'Revenue', 'id': 'Revenue'},
#                                  {'name': 'Revenue_per_user', 'id': 'Revenue_per_user'},
#                                  {'name': 'Cancel_rate', 'id': 'Cancel_rate'}],
#                         filtering=True,
#                         sorting=True,
#                         style_as_list_view=True,
#                         style_header={
#                             'backgroundColor': 'white',
#                             'fontWeight': 'bold'
#                         },
#                         style_cell_conditional=[
#                             {
#                                 'if': {'row_index': 'odd'},
#                                 'backgroundColor': 'rgb(238, 238, 238)'
#                             }
#                         ],
#                         n_fixed_rows=1,
#                         # style_cell={'width': '150px'},
#                         style_table={
#                             'maxHeight': '250',
#                             'overflowY': 'scroll'
#                         },
#                         # style_data_conditional=[
#                         #         {
#                         #             'if': {
#                         #                 'column_id': 'Number of Solar Plants',
#                         #                 # 'filter': '{Number of Solar Plants} > 3.9'
#                         #             },
#                         #             'backgroundColor': '#3D9970',
#                         #             'color': 'white',
#                         #         }
#                         # ]
# )

#------------------------------------------------------------------------------------Toggle switch
div0_1 = html.Div([
    daq.ToggleSwitch(
        id='toggle-switch-1',
        value=False,
        size=50,
        label={
            'label': 'Activate Filterign by Date',
            'style': {
                'backgroundColor': design_colors['page_bg'],
                'color' : design_colors['text'],
                'size' : 50
            }
        },
        labelPosition='bottom',
        color = '#5ab4ac'
    )
])
div0_2 = html.Div([
    daq.ToggleSwitch(
        id='toggle-switch-2',
        value=False,
        size=50,
        label={
            'label': 'Activate Filtering by Platform and Country',
            'style': {
                'backgroundColor': design_colors['page_bg'],
                'color' : design_colors['text'],
                'size' : 50
            }
        },
        labelPosition='bottom',
        color = '#5ab4ac'
    )
])
#====================================================================================== HTML Divs
#-------------------------------------------------------------------- Sign-ups
div1_1 = html.Div([
            dcc.DatePickerRange(
                id='sign-ups-date-picker-range',
                min_date_allowed=dt(2014, 1, 1),
                max_date_allowed=dt.now(),
                end_date=dt.now(),
                start_date=dt.now() - dateutil.relativedelta.relativedelta(days=3),
                display_format=date_format,
                style={'display': 'none'}
                )]
                     )
div1_2 = html.Div([
            dcc.Graph(id='sign-ups-barplot-container')
                ],
                style={'width': '28%', 'display': 'inline-block', 'padding': design_padding['level_1']}
            )
div1_3 = html.Div([
            dcc.Graph(id='sign-ups-map-container')
                ],
                style={'width': '55%', 'display': 'inline-block', 'padding': design_padding['level_1']}
            )
div1_4 = html.Div([
            dcc.Graph(id='top-countries-container')
                ],
                style={'width': '17%', 'display': 'inline-block', 'padding': design_padding['level_1']}
            )

#-------------------------------------------------------------------- Retention
div2_1 = html.Div([
                dcc.RadioItems(
                    id='platform_retention',
                    options=[
                        {'label': 'IOS', 'value': 'ios'},
                        {'label': 'Android', 'value': 'android'}
                    ],
                    value='android',
                    # textfont = dict(color = 'red'),
                    labelStyle={'display': 'inline-block', 'color' : design_colors['text']},
                    style={'display': 'none'}
                        )
                    ]
                )
div2_2 = html.Div([
                dcc.Graph(id='retention-heatmap-container')
                    ],
                style={'width': '50%', 'display': 'inline-block', 'padding': design_padding['level_1']}
                )
div2_3 = html.Div([
                dcc.Graph(id='retention-curve-container')
                    ],
                style={'width': '50%', 'display': 'inline-block', 'padding': design_padding['level_1']}
                )

div2 = html.Div([
                    # html.Div([html.H1("Retention summary")], className="row gs-header gs-text-header", style={'float': 'center'}),
                    div2_1,
                    div2_2,
                    div2_3
                ],
                style={
                    'borderBottom': 'thin lightgrey solid',
                    'backgroundColor': design_colors['page_bg'],
                    'padding': design_padding['level_1'],
                    'display': 'inline-block',
                    'width': '100%'}
                )

#-------------------------------------------------------------------- Active users & by platform
div4_1_1 = html.Div([
                dcc.DatePickerRange(
                        id='activity-picker-range',
                        min_date_allowed=dt(2014, 1, 1),
                        max_date_allowed=dt.now(),
                        end_date=dt.now(),
                        start_date=dt.now() - dateutil.relativedelta.relativedelta(days=3),
                        display_format='MMM Do, YY',
                        style={'display': 'none'}
                    )
                    ]
                )
div4_2 = html.Div([
                dcc.Graph(id='activity-container')
                    ],
                style={'width': '50%', 'display': 'inline-block', 'padding': design_padding['level_1']}
                )
div4_3 = html.Div([
               dcc.Graph(id='activity-pie-container')
                   ],
               style={'width': '50%', 'display': 'inline-block', 'padding': design_padding['level_1']}
               )

div4 = html.Div([
                    div4_1_1,
                    div4_2,
                    div4_3
                ],
                style={
                    'backgroundColor': design_colors['page_bg'],
                    'padding': design_padding['level_1'],
                    'display': 'inline-block',
                    'width': '67%'}
                )

#-------------------------------------------------------------------- Consumption Venn diagram
div7_1_1 = html.Div([
                dcc.DatePickerRange(
                        id='venn-picker-range',
                        min_date_allowed=dt(2014, 1, 1),
                        max_date_allowed=dt.now(),
                        end_date=dt.now(),
                        start_date=dt.now() - dateutil.relativedelta.relativedelta(days=3),
                        display_format='MMM Do, YY',
                        style={'display': 'none'}
                    )]
                )
div7_2 = html.Div([
                dcc.Graph(id='consumption-Venn-container')
                    ],
                style={'width': '100%', 'display': 'inline-block'}
                )

div7 = html.Div([
                    div7_1_1,
                    div7_2,
                ],
                style={
                    'backgroundColor': design_colors['page_bg'],
                    'padding': '0px 5px 0px 0px',
                    'display': 'inline-block',
                    'width': '33%'}
                )

#-------------------------------------------------------------------- Creation
div5_1_1 = html.Div([
                dcc.DatePickerRange(
                                    id='creation-picker-range',
                                    min_date_allowed=dt(2014, 1, 1),
                                    max_date_allowed=dt.now(),
                                    end_date=dt.now(),
                                    start_date=dt.now() - dateutil.relativedelta.relativedelta(days=3),
                                    display_format='MMM Do, YY',
                                    style={'display': 'none'}
                                )

                ])
div5_1_2 = html.Div([
                dcc.RadioItems(
                        id='platform_creation',
                        options=[
                            {'label': 'iOS', 'value': 'ios'},
                            {'label': 'Android', 'value': 'android'},
                            {'label': 'Total', 'value': 'total'},
                        ],
                        value='total',
                        labelStyle={'display': 'inline-block', 'color': design_colors['text']},
                        style={'display': 'none'}
                )

                ])
div5_3 = html.Div([
                dcc.Graph(id='creation_objects-container')
                    ],
                style={'width': '33.6%', 'display': 'inline-block', 'padding': design_padding['level_1']}
                )

#-------------------------------------------------------------------- Consumption
div6_2 = html.Div([
                dcc.Graph(id='consumption_objects-container')
                    ],
                style={'width': '33%', 'display': 'inline-block', 'padding': design_padding['level_1']}
                )
div6_3 = html.Div([
                dcc.Graph(id='consumption_average_amount-container')
                    ],
                style={'width': '33%', 'display': 'inline-block', 'padding': design_padding['level_1']}
                )

#------------------------------------------------------------------- Funnel
div8 = html.Div([
                dcc.DatePickerRange(
                    id='old_date_picker_funnel_barplot',
                    min_date_allowed=dt(2014, 1, 1),
                    max_date_allowed=dt.now(),
                    end_date=dt.now() - dateutil.relativedelta.relativedelta(days=3),
                    start_date=dt.now() - dateutil.relativedelta.relativedelta(days=6),
                    display_format='MMM Do, YY',
                    style={'display': 'none'}
                        ),

                dcc.DatePickerRange(
                    id='new_date_picker_funnel_barplot',
                    min_date_allowed=dt(2014, 1, 1),
                    max_date_allowed=dt.now(),
                    end_date=dt.now(),
                    start_date=dt.now() - dateutil.relativedelta.relativedelta(days=3),
                    display_format='MMM Do, YY',
                    style={'display': 'none'}
                        ),

                dcc.RadioItems(
                    id='platform_funnel_barplot',
                    options=[
                        {'label': 'Android', 'value': '1114'},
                        {'label': 'iOS', 'value': '1122'}
                    ],
                    value='1122',
                    labelStyle={'display': 'inline-block', 'color': design_colors['text']},
                    style={'display': 'none'}
                ),

                dcc.Dropdown(
                        id='country_funnel_barplot',
                        options=[{'label':opt, 'value':opt} for opt in drop_box],
                        value = drop_box[0],
                        style={'display': 'none'}
                    ),

                html.Div([
                    dcc.Graph(id='funnel-container_barplot', style={'height': 500})
                        ],
                        style={'width': '100%', 'display': 'inline-block', 'padding': design_padding['level_1']}
                    )
                ],
                style={
                    'borderBottom': 'thin lightgrey solid',
                    'backgroundColor': design_colors['page_bg'],
                    'padding': design_padding['level_1'],
                    'display': 'inline-block',
                    'width': '34%'}
                )

# div3_1_1 = html.Div([
#                 dcc.DatePickerRange(
#                         id='funnel-picker-range',
#                         min_date_allowed=dt(2014, 1, 1),
#                         max_date_allowed=dt.now(),
#                         end_date=dt.now(),
#                         start_date=dt.now() - dateutil.relativedelta.relativedelta(days=3),
#                         display_format='MMM Do, YY',
#                         style={'display': 'none'}
#                     )
#                     ]
#                 )
# div3_1_2 = html.Div([
#                 dcc.RadioItems(
#                         id='platform_funnel',
#                         options=[
#                             {'label': 'IOS', 'value': 'ios'},
#                             {'label': 'Android', 'value': 'android'}
#                         ],
#                         value='android',
#                         labelStyle={'display': 'inline-block', 'color': design_colors['text']},
#                         style={'display': 'none'}
#                         )
#                     ])
# div3_2 = html.Div([
#                 dcc.Graph(id='funnel-container')
#                     ],
#                 style={'width': '100%', 'display': 'inline-block', 'padding': design_padding['level_1']}
#                 )

# div3 = html.Div([
#                     div3_1_1,
#                     div3_1_2,
#                     div3_2,
#                 ],
#                 style={
#                     'borderBottom': 'thin lightgrey solid',
#                     'backgroundColor': design_colors['page_bg'],
#                     'padding': design_padding['level_1'],
#                     'display': 'inline-block',
#                     'width': '50%'}
#                 )
#------------------------- Layout of the tables
div9_1 = html.Div([dcc.DatePickerRange(
                                        id='table_new-date-picker',
                                        min_date_allowed=dt(2014, 1, 1),
                                        max_date_allowed=dt.now(),
                                        end_date=dt(2019, 4, 1),
                                        start_date=dt(2019, 4, 1) - dateutil.relativedelta.relativedelta(weeks=1),
                                        display_format='MMM Do, YY',
                                        style={'display': 'none'}
                                    ),
                    dcc.RadioItems(
                                        id='table_new_platform',
                                        options=[
                                            {'label': 'Android', 'value': '1114'},
                                            {'label': 'iOS', 'value': '1122'}
                                        ],
                                        value='1122',
                                        labelStyle={'display': 'inline-block', 'color': 'white'},
                                        style={'display': 'none'}
                                    ),
                    table_new
                   ],
                    style = {'padding': design_padding['level_1'],
                             'width': '66%'
                             }
                    )

# div9_2 = html.Div([
#                     dcc.DatePickerRange(
#                                         id='table_old-date-picker',
#                                         min_date_allowed=dt(2014, 1, 1),
#                                         max_date_allowed=dt.now(),
#                                         end_date=dt(2019, 4, 1),
#                                         start_date=dt(2019, 4, 1) - dateutil.relativedelta.relativedelta(weeks=1),
#                                         display_format='MMM Do, YY',
#                                         style={'display': 'none'}
#                                     ),
#                     dcc.RadioItems(
#                                         id='table_old_platform',
#                                         options=[
#                                             {'label': 'Android', 'value': '1114'},
#                                             {'label': 'iOS', 'value': '1122'}
#                                         ],
#                                         value='1114',
#                                         labelStyle={'display': 'inline-block', 'color': 'white'},
#                                         style={'display': 'none'}
#                                     ),
#                     table_old
#                    ],
#                     style={'padding': design_padding['level_1'],
#                            'width': '50%'
#                            }
#                     )

div9 = html.Div([       
                    div8,
                    div9_1,
                    # div9_2
                    ],
                    style = {'backgroundColor': '#0e2e43',
                            'display': 'flex',
                            'flex-direction': 'row',
                            'padding': '0px 5px 0px 5px',
                            }

                )

div_img = html.Div([

html.Div([
	html.Div([
        html.H5('Messenger')
    ],style={'size': title_size,
             'color': design_colors['title'],
             'text-align': "center"
                        }),
	html.Img(src=app.get_asset_url('image_messenger.png'),
                style={
                       'width': '100%'
                       })
	], style={
	           'padding': design_padding['level_1'], 
	           'width': '33.333%',
	           'display': 'inline-block'
	           }),

html.Div([
	html.Div([
        html.H5('Comments')
    ],style={'size': title_size,
             'color': design_colors['title'],
             'text-align': "center"
                        }),
	html.Img(src=app.get_asset_url('image_comment.png'),
                style={
                       'width': '100%'
                       })
	], style={
               'padding': design_padding['level_1'], 
               'width': '33.333%',
               'display': 'inline-block'
               }),

html.Div([
	html.Div([
        html.H5('Discussion')
    ],style={'size': title_size,
             'color': design_colors['title'],
             'text-align': "center"
                        }),
	html.Img(src=app.get_asset_url('image_discussion.png'),
                style={
                       'width': '100%'
                       })
	], style={
               'padding': design_padding['level_1'], 
               'width': '33.333%',
               'display': 'inline-block'
               })
])

#====================================================================================== Combining HTML Divs into the layout form
app.layout = html.Div([
    div0_2,
    div0_1,
    div1_1,
    div1_2,
    div1_3,
    div1_4,
    div4,
    div7,
    div5_1_1,
    div5_1_2,
    div5_3,
    div6_2,
    div6_3,
    div2_1,
    div2_2,
    div2_3,
    # div3,
    # div8,
    # div_img_1,
    # div_img_2,
    # div_img_3,
    div_img,
    div9
],
    style={'backgroundColor': '#0f2331'}
)

#====================================================================================== Callbacks
@app.callback(
   dash.dependencies.Output(component_id='sign-ups-date-picker-range', component_property='style'),
   [dash.dependencies.Input(component_id='toggle-switch-1', component_property='value')])
def show_hide_element(visibility_state):
    if visibility_state:
        return {'display': 'block'}
    else:
        return {'display': 'none'}

# @app.callback(
#    dash.dependencies.Output(component_id='funnel-picker-range', component_property='style'),
#    [dash.dependencies.Input(component_id='toggle-switch-1', component_property='value')])
# def show_hide_element(visibility_state):
#     if visibility_state:
#         return {'display': 'block'}
#     else:
#         return {'display': 'none'}

@app.callback(
   dash.dependencies.Output(component_id='activity-picker-range', component_property='style'),
   [dash.dependencies.Input(component_id='toggle-switch-1', component_property='value')])
def show_hide_element(visibility_state):
    if visibility_state:
        return {'display': 'block'}
    else:
        return {'display': 'none'}

@app.callback(
   dash.dependencies.Output(component_id='venn-picker-range', component_property='style'),
   [dash.dependencies.Input(component_id='toggle-switch-1', component_property='value')])
def show_hide_element(visibility_state):
    if visibility_state:
        return {'display': 'block'}
    else:
        return {'display': 'none'}

@app.callback(
   dash.dependencies.Output(component_id='creation-picker-range', component_property='style'),
   [dash.dependencies.Input(component_id='toggle-switch-1', component_property='value')])
def show_hide_element(visibility_state):
    if visibility_state:
        return {'display': 'block'}
    else:
        return {'display': 'none'}



@app.callback(
   dash.dependencies.Output(component_id='platform_retention', component_property='style'),
   [dash.dependencies.Input(component_id='toggle-switch-2', component_property='value')])
def show_hide_element(visibility_state):
    if visibility_state:
        return {'display': 'block'}
    else:
        return {'display': 'none'}

# @app.callback(
#    dash.dependencies.Output(component_id='platform_funnel', component_property='style'),
#    [dash.dependencies.Input(component_id='toggle-switch-2', component_property='value')])
# def show_hide_element(visibility_state):
#     if visibility_state:
#         return {'display': 'block'}
#     else:
#         return {'display': 'none'}

@app.callback(
   dash.dependencies.Output(component_id='platform_creation', component_property='style'),
   [dash.dependencies.Input(component_id='toggle-switch-2', component_property='value')])
def show_hide_element(visibility_state):
    if visibility_state:
        return {'display': 'block'}
    else:
        return {'display': 'none'}


@app.callback(
   dash.dependencies.Output(component_id='new_date_picker_funnel_barplot', component_property='style'),
   [dash.dependencies.Input(component_id='toggle-switch-1', component_property='value')])
def show_hide_element(visibility_state):
    if visibility_state:
        return {'display': 'block'}
    else:
        return {'display': 'none'}
@app.callback(
   dash.dependencies.Output(component_id='old_date_picker_funnel_barplot', component_property='style'),
   [dash.dependencies.Input(component_id='toggle-switch-1', component_property='value')])
def show_hide_element(visibility_state):
    if visibility_state:
        return {'display': 'block'}
    else:
        return {'display': 'none'}
@app.callback(
   dash.dependencies.Output(component_id='platform_funnel_barplot', component_property='style'),
   [dash.dependencies.Input(component_id='toggle-switch-2', component_property='value')])
def show_hide_element(visibility_state):
    if visibility_state:
        return {'display': 'block'}
    else:
        return {'display': 'none'}
@app.callback(
   dash.dependencies.Output(component_id='country_funnel_barplot', component_property='style'),
   [dash.dependencies.Input(component_id='toggle-switch-2', component_property='value')])
def show_hide_element(visibility_state):
    if visibility_state:
        return {'display': 'block'}
    else:
        return {'display': 'none'}


@app.callback(
   dash.dependencies.Output(component_id='table_new-date-picker', component_property='style'),
   [dash.dependencies.Input(component_id='toggle-switch-1', component_property='value')])
def show_hide_element(visibility_state):
    if visibility_state:
        return {'display': 'block'}
    else:
        return {'display': 'none'}
# @app.callback(
#    dash.dependencies.Output(component_id='table_old-date-picker', component_property='style'),
#    [dash.dependencies.Input(component_id='toggle-switch-1', component_property='value')])
# def show_hide_element(visibility_state):
#     if visibility_state:
#         return {'display': 'block'}
#     else:
#         return {'display': 'none'}
@app.callback(
   dash.dependencies.Output(component_id='table_new_platform', component_property='style'),
   [dash.dependencies.Input(component_id='toggle-switch-2', component_property='value')])
def show_hide_element(visibility_state):
    if visibility_state:
        return {'display': 'block'}
    else:
        return {'display': 'none'}
# @app.callback(
#    dash.dependencies.Output(component_id='table_old_platform', component_property='style'),
#    [dash.dependencies.Input(component_id='toggle-switch-2', component_property='value')])
# def show_hide_element(visibility_state):
#     if visibility_state:
#         return {'display': 'block'}
#     else:
#         return {'display': 'none'}
#-------------------------------------------------------------------- Sign-ups
#------------------- 1_2 Bar Plot
@app.callback(
    dash.dependencies.Output('sign-ups-barplot-container', 'figure'),
    [dash.dependencies.Input('sign-ups-date-picker-range', 'start_date'),
     dash.dependencies.Input('sign-ups-date-picker-range', 'end_date'),
     dash.dependencies.Input('toggle-switch-1', 'value')])
def update_barplot(start_date, end_date, is_live):
    start_date = str(start_date)[:10]
    end_date = str(end_date)[:10]

    if is_live == False:
        signups = pd.read_csv(r'data\signups.csv')
        signups.drop(columns=['Unnamed: 0'], inplace=True)
        signups['Date'] = pd.to_datetime(signups['Date'])
    else:
        signups = pd.read_sql_query('EXEC DS_GetStatistics\''+start_date+'\',\''+end_date+'\'', cnxn)
        signups['Date'] = pd.to_datetime(signups['Date'])
    
    return {
        'data': [
                go.Bar(x =signups['Date'], y=signups['signups_android'], name ="Android",
                        marker = dict(color=design_colors['Android'])
                       ),
                go.Bar(x =signups['Date'], y=signups['signups_ios'], name ="iOS",
                        marker = dict(color=design_colors['iOS'])
                       ),
                go.Bar(x =signups['Date'], y=signups['signups_web'], name ="Web",
                        marker = dict(color=design_colors['Web'])
                       )
                 ],
        'layout' : {
                'barmode': 'stack',
                'paper_bgcolor': design_colors['chart_box_bg'],
                'plot_bgcolor': design_colors['chart_bg'],
                'xaxis': {
                    'showgrid': False,
                    'tickfont': dict(color=design_colors['chart_axis_legends']),
                    'gridcolor': design_colors['chart_inside_lines'],
                    'tickformat': '%b %d',

                },
                'yaxis': {
                    'showgrid': True,
                    'tickfont': dict(color=design_colors['chart_axis_legends']),
                    'gridcolor': design_colors['chart_inside_lines']
                },
                'margin': go.layout.Margin(
                                            l=50,
                                            r=50,
                                            b=50,
                                            t=50,
                                            # pad=20
                                        ),
                "title": '<b>Signups<b>',
                'titlefont' : dict(
                        size=title_size,
                        color=design_colors['title']
                ),
                'legend': dict(font=dict(color=design_colors['text']))
            }
    }

#------------------- 1_3 Map
@app.callback(
    dash.dependencies.Output('sign-ups-map-container', 'figure'),
    [dash.dependencies.Input('sign-ups-date-picker-range', 'start_date'),
     dash.dependencies.Input('sign-ups-date-picker-range', 'end_date'),
     dash.dependencies.Input('toggle-switch-1', 'value')])
def update_map(start_date, end_date, is_live):
    start_date = str(start_date)[:10]
    end_date = str(end_date)[:10]
    if is_live:
        SignupsPerCountry = pd.read_sql_query('EXEC DS_GetCountryCodesForMap @RegisterStartDate = \''+start_date+'\', @RegisterEndDate = \''+end_date+'\'', cnxn)
    else:
        SignupsPerCountry = pd.read_csv(r'data\SignupsPerCountry.csv')
        SignupsPerCountry.drop(columns=['Unnamed: 0'], inplace=True)
    
    merged = pd.merge(SignupsPerCountry, TrueCodes, left_on='CountryCode', right_on='rand', how='right')
    merged.fillna(0, inplace=True)
    return {
        'data': [go.Choropleth(
                    locations = merged['STANAG'],
                    z = merged['CountOfUsers'].astype(float),
                    text = merged['Entity'],
                    autocolorscale = False,
                    colorscale = map_colorscale,
                    reversescale = True ,
                    marker = go.choropleth.Marker(
                        line = go.choropleth.marker.Line(
                            color = design_colors['chart_bg'],
                            width = 0.5
                        )),
                    colorbar = go.choropleth.ColorBar(
                       title = "# of users"),
                    showscale=False,

    )],
        'layout': go.Layout(
                        # title = '<b>Geography<b>',
                        autosize=False,
                        paper_bgcolor = design_colors['chart_box_bg'],
                        plot_bgcolor = design_colors['chart_bg'],
                        margin=go.layout.Margin(
                                            l=15,
                                            r=15,
                                            b=0,
                                            t=15,
                                            pad=3
                                        ),
                        geo = go.layout.Geo(
                            bgcolor = design_colors['chart_bg'],
                            showframe=False,
                            showlakes = False,
                        showcoastlines = False),
                    ),
    }

#------------------- 1_4 Top countries
@app.callback(
    dash.dependencies.Output('top-countries-container', 'figure'),
    [dash.dependencies.Input('sign-ups-date-picker-range', 'start_date'),
     dash.dependencies.Input('sign-ups-date-picker-range', 'end_date'),
     dash.dependencies.Input('toggle-switch-1', 'value')])
def update_top_countires(start_date, end_date, is_live):
    start_date = str(start_date)[:10]
    end_date = str(end_date)[:10]
    if is_live:
        top_countries = pd.read_sql_query('EXEC DS_GetTopCountries \''+start_date+'\',\''+end_date+'\', 1', cnxn)
    else:
        top_countries = pd.read_csv(r'data\top_countries.csv')
        top_countries.drop(columns=['Unnamed: 0'], inplace=True)

    merged = pd.merge(top_countries, TrueCodes, left_on='CountryCode', right_on='rand', how='inner').sort_values(by = 'NumberOf', ascending  = False)
    trace = go.Bar(
                x=list(merged['NumberOf'])[::-1],
                y=list(merged['CountryCode'])[::-1],
                text = list(merged['NumberOf'])[::-1],
                textposition='auto',
                orientation='h',
                marker=dict(color="#3182bd"),
                textfont=dict(
                    color=design_colors['text'],
                    size=14,
                    family='Arail',
                ),
                hoverinfo = 'none',
    )

    data = [trace]

    layout = {
        'paper_bgcolor': design_colors['chart_box_bg'],
        'plot_bgcolor': design_colors['chart_bg'],
        'xaxis': {
            'showgrid': False,
            'tickfont': dict(color=design_colors['chart_axis_legends']),
            'gridcolor': design_colors['chart_inside_lines']

        },
        'yaxis': {
            'showgrid': False,
            'tickfont': dict(color=design_colors['chart_axis_legends']),
            'gridcolor': design_colors['chart_inside_lines']
        },
        "title": '<b>Top Countries<b>',
        'titlefont' : dict(
                size=title_size,
                color=design_colors['title']
        )
    }
    return {
            'data': data,
            'layout': layout
        }

#-------------------------------------------------------------------- Active users
#------------------- 4_2 Daily active users
@app.callback(
    dash.dependencies.Output('activity-container', 'figure'),
    [dash.dependencies.Input('activity-picker-range', 'start_date'),
     dash.dependencies.Input('activity-picker-range', 'end_date'),
     dash.dependencies.Input('toggle-switch-1', 'value')])
def update_activity(start_date, end_date, is_live):
    periodicity = '1'
    start_date = str(start_date)[:10]
    end_date = str(end_date)[:10]

    if is_live:
        UserActivities_Android = pd.read_sql_query('EXEC DS_GetUserActivities \''+start_date+'\',\''+end_date+'\','+periodicity+','+'1', cnxn)
        UserActivities_iOS = pd.read_sql_query('EXEC DS_GetUserActivities \''+start_date+'\',\''+end_date+'\','+periodicity+','+'2', cnxn)
    else:
        UserActivities_Android = pd.read_csv(r'data\UserActivities_Android.csv')
        UserActivities_Android.drop(columns=['Unnamed: 0'], inplace=True)

        UserActivities_iOS = pd.read_csv(r'data\UserActivities_iOS.csv')
        UserActivities_iOS.drop(columns=['Unnamed: 0'], inplace=True)

    trace1 = go.Scatter(x = UserActivities_Android['Date'], y=UserActivities_Android['Checkins'], name = "Android",
                     marker = dict(color=design_colors['Android']),
                     showlegend=False
                    )
    trace2 = go.Scatter(x = UserActivities_iOS['Date'], y=UserActivities_iOS['Checkins'], name = "iOS",
                     marker = dict(color=design_colors['iOS']),
                     showlegend=False
                    )

    annotations = []

    for i in range(len(UserActivities_Android)):
        annotation_1 =dict(
                        x=UserActivities_iOS['Date'].values[i],
                        y=UserActivities_iOS['Checkins'].values[i],
                        xref='x',
                        yref='y',
                        text=str(np.round(UserActivities_iOS['Checkins'].values[i]/1000.0, 1)) + 'k',
                        showarrow=False,
                        yshift = 20,

                        font = dict(
                          color = design_colors['title'],
                          size = 10
                        )
                        )
        annotation_2 =dict(
                        x=UserActivities_Android['Date'].values[i],
                        y=UserActivities_Android['Checkins'].values[i],
                        xref='x',
                        yref='y',
                        text=str(np.round(UserActivities_Android['Checkins'].values[i]/1000.0, 1)) + 'k',
                        showarrow=False,
                        yshift = 20,

                        font = dict(
                          color = design_colors['title'],
                          size = 10
                        )
                        )
        annotations.append(annotation_1)
        annotations.append(annotation_2)

    layout  = dict(title = "<b>Active Users<b>",
                    titlefont = dict(
                        size=title_size,
                        color=design_colors['title']
                    ),
                   paper_bgcolor = design_colors['chart_box_bg'],
                   plot_bgcolor = design_colors['chart_bg'],
                    margin=go.layout.Margin(
                                            l=50,
                                            r=50,
                                            b=50,
                                            t=50,
                                            # pad=20
                                        ),
                   xaxis = {
                    'showgrid': False,
                    'tickfont': dict(color=design_colors['chart_axis_legends']),
                    'gridcolor': design_colors['chart_inside_lines'],
                    'tickformat': '%b %d',

                         },
                yaxis = {
                    'showgrid': True,
                    'tickfont': dict(color=design_colors['chart_axis_legends']),
                    'gridcolor': design_colors['chart_inside_lines'],
                    'range': [0,UserActivities_Android.Checkins.max()*1.3]
                        },
                annotations=annotations
                  )

    data = [trace1, trace2]
    return {
            'data': data,
            'layout' : layout
        }

#------------------- 4_3 Active users by platform
@app.callback(
    dash.dependencies.Output('activity-pie-container', 'figure'),
    [dash.dependencies.Input('activity-picker-range', 'start_date'),
     dash.dependencies.Input('activity-picker-range', 'end_date'),
     dash.dependencies.Input('toggle-switch-1', 'value')])
def update_activity_pie(start_date, end_date, is_live):
    start_date = str(start_date)[:10]
    end_date = str(end_date)[:10]

    if is_live:
        PieActivities = pd.read_sql_query('EXEC DS_GetActivityByPlatform  \''+start_date+'\',\''+end_date+'\'', cnxn)
    else:
        PieActivities = pd.read_csv(r'data\PieActivities.csv')
        PieActivities.drop(columns=['Unnamed: 0'], inplace=True)

    trace = go.Pie(labels=PieActivities.Platform, 
                    values=PieActivities.CountOfUsers,
                    marker=dict(
                            colors=[design_colors['Android'],design_colors['iOS']]
                            ),
                    textfont=dict(
                        size=20,
                        family='Arail',
                    ),
                    )
    data = [trace]
    layout  = dict(title = "<b>Platform Share<b>",
                    titlefont = dict(
                        size=title_size,
                        color=design_colors['title']
                    ),
                    margin=go.layout.Margin(
                                            l=50,
                                            r=50,
                                            b=50,
                                            t=50,
                                            # pad=20
                                        ),
                   paper_bgcolor = design_colors['chart_box_bg'],
                   plot_bgcolor = design_colors['chart_bg'],
                   legend = dict(
                                font=dict(color=design_colors['text'],
                                           )
                                 )
                  )
    return {
            'data': data,
            'layout' : layout
        }

#------------------- 4_4 Consumption Venn diagram
@app.callback(
    dash.dependencies.Output('consumption-Venn-container', 'figure'),
    [dash.dependencies.Input('venn-picker-range', 'start_date'),
     dash.dependencies.Input('venn-picker-range', 'end_date'),
     dash.dependencies.Input('toggle-switch-1', 'value')])
def update_venn(start_date, end_date, is_live):
    start_date = str(start_date)[:10]
    end_date = str(end_date)[:10]

    if is_live:
        data = pd.read_sql_query('EXEC DS_GetConsumption_LearnSocial @StartDate = \'' + start_date + '\', @EndDate = \'' + end_date + '\'',cnxn)
    else:
        data = pd.read_csv(r'data\venn_data.csv')
        data.drop(columns=['Unnamed: 0'], inplace=True)

    data = data.fillna(0)
    data.loc[data.Lesson_Consumers > 0, 'Lesson_Consumers'] = 1
    data.loc[data.Social_Content_Consumers > 0, 'Social_Content_Consumers'] = 1
    data['LS'] = data.Lesson_Consumers + data.Social_Content_Consumers

    a = len(data[data.Lesson_Consumers == 1]) - len(data[data.LS > 1])
    b = len(data[data.Social_Content_Consumers == 1]) - len(data[data.LS > 1])
    c = len(data[data.LS > 1])
    r1 = np.sqrt((a + c) / np.pi)
    r2 = np.sqrt((b + c) / np.pi)
    dist = np.sqrt(c * 3 / np.pi)

    data = [go.Scatter(
        x=[r1 * 0.7, 2 * r1 - dist / 2, (2 * r1 + r2 - dist) * 1.3,2 * r1 - dist / 2],
        y=[r1, r1, r1, -0.2*r1],
        text=['{}({}%)'.format("Learn only<br>", np.round(a / (a + b + c) * 100, 1)),
              '({}%)'.format(np.round(c / (a + b + c) * 100, 1)),
              '{}({}%)'.format("Social only<br>", np.round(b / (a + b + c) * 100, 1)),
              '{}({}%)'.format("Nothing Doers ", np.round(len(data[data.LS == 0]) / len(data)*100,1))],
        mode='text',
        textfont=dict(
            color=design_colors['text'],
            size=18,
            family='Arail',
        )
    )]

    layout = {
        'title' : "<b>Activity<b>",
        'titlefont' : dict(
                        size=title_size,
                        color=design_colors['title']
                    ),
        'paper_bgcolor' : design_colors['chart_box_bg'],
        'plot_bgcolor' : design_colors['chart_bg'],
        'xaxis': {
            'showticklabels': False,
            'showgrid': False,
            'zeroline': False,
        },
        'yaxis': {
            'showticklabels': False,
            'showgrid': False,
            'zeroline': False,
        },
        'shapes': [
            {
                'opacity': 0.3,
                'xref': 'x',
                'yref': 'y',
                'fillcolor': '#154c75',
                'x0': 0,
                'y0': 0,
                'x1': 2 * r1,
                'y1': 2 * r1,
                'type': 'circle',
                'line': {
                    'color': '#154c75'
                },
            },
            {
                'opacity': 0.3,
                'xref': 'x',
                'yref': 'y',
                'fillcolor': '#277fc1',
                'x0': 2 * r1 - dist,
                'y0': r1 - r2,
                'x1': 2 * r1 - dist + 2 * r2,
                'y1': r1 + r2,
                'type': 'circle',
                'line': {
                    'color': '#277fc1',
                },
            }
        ],
        'margin': {
            'l': 20,
            'r': 20,
            'b': 30
        },
    }

    return {
            'data': data,
            'layout': layout
        }

#---------------------------------------- 5_2 Creation: Daily trend
@app.callback(
    dash.dependencies.Output('creation_objects-container', 'figure'),
    [dash.dependencies.Input('creation-picker-range', 'start_date'),
     dash.dependencies.Input('creation-picker-range', 'end_date'),
     dash.dependencies.Input('platform_creation', 'value'),
     dash.dependencies.Input('toggle-switch-1', 'value')])
def update_creation_percentage(start_date, end_date, creation_platform, is_live):
    start_date = str(start_date)[:10]
    end_date = str(end_date)[:10]
    platform = '1' if creation_platform == 'android' else '2' if creation_platform == 'ios' else '3' if creation_platform == 'total' else '4'

    if is_live:
        data2 = pd.read_sql_query('EXEC DS_GetCreatedContent_byPlatform \''+start_date+'\',\''+end_date+'\','+platform, cnxn)
    else:
        if platform == '3':
            data2 = pd.read_csv(r'data\created_content.csv')
            data2.drop(columns=['Unnamed: 0'], inplace=True)
        elif platform == '1':
            data2 = pd.read_csv(r'data\created_content_android.csv')
            data2.drop(columns=['Unnamed: 0'], inplace=True)
        else:
            data2 = pd.read_csv(r'data\created_content_ios.csv')
            data2.drop(columns=['Unnamed: 0'], inplace=True)

    data2.Metric = data2.Metric.str.rstrip()

    creation_activities = np.unique(data2.Metric)# data2['codes_created_private', 'codes_created_public', 'discuss_questions_created', 'quizzes_ created', 'user_lessons created','user_posts_created']
    clean_platform = '_android' if creation_platform == 'android' else '_ios' if creation_platform == 'ios' else ''
    clean_activities = [act.replace(clean_platform,"") for act in creation_activities]
    creation_mapper = {'codes_created_public': 'Code',
                       'user_posts_created': 'User Post',
                       'discuss_questions_created': 'Q&A',
                       'quizzes_created': 'Quiz',
                       'user_lessons_created': 'User Lesson',
                       'codes_created_private': 'Private Codes'}
    traces = []
    for i in range(len(creation_activities)):
        trace = go.Scatter(
                        x = data2[data2.Metric == creation_activities[i]]['Date'],
                        y = data2[data2.Metric == creation_activities[i]].Value,
                        name = creation_mapper[clean_activities[i]],
                        line = dict(color = (colors[activity_color[creation_mapper[clean_activities[i]]]])),
                        # showlegend=False
        )
        traces.append(trace)

    layout = go.Layout(
                    title='<b>Content Creation<b>',
                    titlefont = dict(
                        size=title_size,
                        color=design_colors['title']
                    ),
                   paper_bgcolor = design_colors['chart_box_bg'],
                   plot_bgcolor = design_colors['chart_bg'],
                   xaxis = {
                    'showgrid': False,
                    'tickfont': dict(color=design_colors['chart_axis_legends']),
                    'gridcolor': design_colors['chart_inside_lines'],
                    'tickformat': '%b %d',

                         },
                yaxis = {
                    'showgrid': True,
                    'tickfont': dict(color=design_colors['chart_axis_legends']),
                    'gridcolor': design_colors['chart_inside_lines'],
                    'rangemode': 'tozero'
                        },
        margin=go.layout.Margin(
            l=50,
            r=30,
            b=50,
            t=50,
            pad=5
        ),
        legend = dict(font=dict(
            color=design_colors['text']
        ))
    )

    return {
            'data': traces,
            'layout': layout
        }

#---------------------------------------- 6_2 Consumption: Daily trend
@app.callback(
    dash.dependencies.Output('consumption_objects-container', 'figure'),
    [dash.dependencies.Input('creation-picker-range', 'start_date'),
     dash.dependencies.Input('creation-picker-range', 'end_date'),
     dash.dependencies.Input('platform_creation', 'value'),
     dash.dependencies.Input('toggle-switch-1', 'value')])
def update_creation_percentage(start_date, end_date, consumption_platform, is_live):
    start_date = str(start_date)[:10]
    end_date = str(end_date)[:10]
    platform = '1' if consumption_platform == 'android' else '2' if consumption_platform == 'ios' else '3' if consumption_platform == 'total' else '4'

    if is_live:
        data = pd.read_sql_query('EXEC DS_GetUserConsumption_byPlatform \''+start_date+'\',\''+end_date+'\','+platform, cnxn)
    else:
        if platform == '3':
            data = pd.read_csv(r'data\user_consumption.csv')
            data.drop(columns=['Unnamed: 0'], inplace=True)
        elif platform == '1':
            data = pd.read_csv(r'data\user_consumption_android.csv')
            data.drop(columns=['Unnamed: 0'], inplace=True)
        else:
            data = pd.read_csv(r'data\user_consumption_ios.csv')
            data.drop(columns=['Unnamed: 0'], inplace=True)

    clean_platform = '_android' if consumption_platform == 'android' else '_ios' if consumption_platform == 'ios' else ''
    data = data.rename(columns = {old_col: new_col for  old_col, new_col in zip(data.columns[1:], [act.replace(clean_platform,"") for act in data.columns[1:]])})
    activities = data.columns[2:]

    # clean_activities = [act.replace(clean_platform,"") for act in activities]
    DailyPercentages = pd.concat((data[activities].div(data.active_users, axis=0) * 100, data.Date), axis=1)
    consumption_mapper_users = {'contest_players': 'Contest',
                                'course_lessons_consumers': 'Lesson',
                                'user_codes_consumers': 'Code',
                                'discuss_consumers': 'Q&A',
                                'user_lessons_consumers': 'User Lesson',
                                'user_posts_consumers': 'User Post',
                                'profiles_consumers': 'Profile',
                                'own_profiles_consumers': 'Own Profile'}
    traces = []

    for i in range(len(activities)):
        trace = go.Scatter(
            x=DailyPercentages['Date'].values,
            y=np.round(DailyPercentages[activities[i]].values, 1),
            name=consumption_mapper_users[activities[i]],
            line = dict(color=(colors[activity_color[consumption_mapper_users[activities[i]]]])),
                        showlegend=True
        )
        traces.append(trace)

    layout = go.Layout(
        title='<b>Content Consumption %<b>',
                    titlefont = dict(
                        size=title_size,
                        color=design_colors['title']
                    ),
                   paper_bgcolor = design_colors['chart_box_bg'],
                   plot_bgcolor = design_colors['chart_bg'],
                   xaxis = {
                    'showgrid': False,
                    'tickfont': dict(color=design_colors['chart_axis_legends']),
                    'gridcolor': design_colors['chart_inside_lines'],
                    'tickformat': '%b %d',

                         },
                yaxis = {
                    'showgrid': True,
                    'tickfont': dict(color=design_colors['chart_axis_legends']),
                    'gridcolor': design_colors['chart_inside_lines'],
                    'rangemode': 'tozero'
                        },
        margin=go.layout.Margin(
            l=30,
            r=30,
            b=50,
            t=50,
            pad=5
        ),
        legend = dict(font=dict(
            color=design_colors['text']
        ))
    )

    return {
            'data': traces,
            'layout': layout
        }

# ---------------------------------------- 6_3 Consumption: Daily average amounts
@app.callback(
    dash.dependencies.Output('consumption_average_amount-container', 'figure'),
    [dash.dependencies.Input('creation-picker-range', 'start_date'),
     dash.dependencies.Input('creation-picker-range', 'end_date'),
     dash.dependencies.Input('platform_creation', 'value'),
     dash.dependencies.Input('toggle-switch-1', 'value')])
def update_creation_percentage(start_date, end_date, consumption_platform, past_live):
    start_date = str(start_date)[:10]
    end_date = str(end_date)[:10]
    platform = '1' if consumption_platform == 'android' else '2' if consumption_platform == 'ios' else '3' if consumption_platform == 'total' else '4'
    is_live = past_live

    if is_live:
        cons1 = pd.read_sql_query('EXEC DS_GetConsumption_DailyTotalActivityConsumers_byPlatform \''+start_date+'\',\''+end_date+'\','+platform, cnxn)
        cons2 = pd.read_sql_query('EXEC DS_GetConsumption_DailyTotalActivities_byPlatform \''+start_date+'\',\''+end_date+'\','+platform, cnxn)
    else:
        if platform == '3':
            cons1 = pd.read_csv(r'data\cons1.csv')
            cons1.drop(columns=['Unnamed: 0'], inplace=True)
            cons2 = pd.read_csv(r'data\cons2.csv')
            cons2.drop(columns=['Unnamed: 0'], inplace=True)
        elif platform == '1':
            cons1 = pd.read_csv(r'data\cons1_android.csv')
            cons1.drop(columns=['Unnamed: 0'], inplace=True)
            cons2 = pd.read_csv(r'data\cons2_android.csv')
            cons2.drop(columns=['Unnamed: 0'], inplace=True)
        else:
            cons1 = pd.read_csv(r'data\cons1_ios.csv')
            cons1.drop(columns=['Unnamed: 0'], inplace=True)
            cons2 = pd.read_csv(r'data\cons2_ios.csv')
            cons2.drop(columns=['Unnamed: 0'], inplace=True)
    
    # total_activity_consumption_1.Metric = total_activity_consumption_1.Metric.apply(lambda x: x.strip()[:-10] if x.strip() != 'contest_players' else 'contests')
    # total_activity_consumption_2.Metric = total_activity_consumption_2.Metric.apply(lambda x: x.strip()[:-9] if x.strip() != 'contests_played' else 'contests')
    # average_activities_df = pd.merge(total_activity_consumption_1, total_activity_consumption_2, on=['Date', 'Metric'])
    # average_activities_df['Average_activities'] = average_activities_df.Value / average_activities_df.NofUsers
    # consumption_activities = np.unique(average_activities_df.Metric)

    clean_platform = '_android' if consumption_platform == 'android' else '_ios' if consumption_platform == 'ios' else ''
    cons1.Metric = cons1.Metric.apply(lambda x: x.replace(clean_platform,""))
    cons2.Metric = cons2.Metric.apply(lambda x: x.replace(clean_platform,""))
    cons1.Metric = cons1.Metric.apply(lambda x: x.strip()[:-10] if x.strip() != 'contest_players' else 'contests')
    cons2.Metric = cons2.Metric.apply(lambda x: x.strip()[:-9] if x.strip() != 'contests_played' else 'contests')
    average_activities_df = pd.merge(cons1, cons2, on=['Date', 'Metric'])
    average_activities_df['Average_activities'] = average_activities_df.Value / average_activities_df.NofUsers
    consumption_activities = np.unique(average_activities_df.Metric)
    consumption_mapper_activities = {'contests': 'Contest',
                                'course_lessons': 'Lesson',
                                'user_codes': 'Code',
                                'discuss': 'Q&A',
                                'user_lessons': 'User Lesson',
                                'user_posts': 'User Post',
                                'profiles': 'Profile',
                                'own_profiles': 'Own Profile'}
    traces = []
    for i in range(len(consumption_activities)):
        trace = go.Scatter(
            x=average_activities_df[average_activities_df.Metric == consumption_activities[i]]['Date'].values,
            y=np.round(average_activities_df[average_activities_df.Metric == consumption_activities[i]][
                           'Average_activities'].values, 1),
            name=consumption_mapper_activities[consumption_activities[i]],
            line=dict(color=(colors[activity_color[consumption_mapper_activities[consumption_activities[i]]]]))
        )
        traces.append(trace)

    layout = go.Layout(
                    title='<b>Content Consumption Per User<b>',
                    titlefont = dict(
                        size=title_size,
                        color=design_colors['title']
                    ),
                   paper_bgcolor = design_colors['chart_box_bg'],
                   plot_bgcolor = design_colors['chart_bg'],
                   xaxis = {
                    'showgrid': False,
                    'tickfont': dict(color=design_colors['chart_axis_legends']),
                    'gridcolor': design_colors['chart_inside_lines'],
                    'tickformat': '%b %d',
                         },
                yaxis = {
                    'showgrid': True,
                    'tickfont': dict(color=design_colors['chart_axis_legends']),
                    'gridcolor': design_colors['chart_inside_lines'],
                    'rangemode': 'tozero'
                        },
        margin=go.layout.Margin(
            l=30,
            # r=30,
            b=50,
            t=50,
            pad=5
        ),
        legend = dict(font=dict(
            color=design_colors['text']
        ))
    )

    return {
            'data': traces,
            'layout': layout
        }

#-------------------------------------------------------------------- Retention
#------------------- 2_2 Monthly Retention
@app.callback(
    dash.dependencies.Output('retention-heatmap-container', 'figure'),
    [dash.dependencies.Input('platform_retention', 'value')])
def update_retention_heatmap(value):
    colorscale = [[0, '#c6dbef'], [1, '#08306b']]
    annotations_android = []
    for cohort in cohort_android_transpose.columns:
        for month in range(12):
                annotations_android.append({
                "x": month,
                "y": cohort,
                "font": {"color": "white"},
                "showarrow": False,
                "text": cohort_android_transpose.replace(np.nan, '', regex=True).applymap(str)[cohort].iloc[month],
                "xref": "x",
                "yref": "y"
                })

    annotations_ios = []
    for cohort in cohort_ios_transpose.columns:
        for month in range(12):
            annotations_ios.append({
                "x": month,
                "y": cohort,
                "font": {"color": "white"},
                "showarrow": False,
                "text": cohort_ios_transpose.replace(np.nan, '', regex=True).applymap(str)[cohort].iloc[month],
                "xref": "x",
                "yref": "y"
            })

    if value == 'android':
        return {
            'data': [go.Heatmap(z=cohort_android_transpose.T,
                                 x=[str(i)+'-m' for i in list(range(1,13))],
                                 y=cohort_android_transpose.columns.values,
                                 hoverinfo = "z",
                                 showscale = False,
                                 zauto = True,
                                 colorscale=colorscale
                         )],
            'layout': go.Layout(
                                paper_bgcolor=design_colors['chart_box_bg'],
                                plot_bgcolor=design_colors['chart_bg'],
                                title='<b>Monthly Retention<b>',
                                titlefont=dict(
                                    size=title_size,
                                    color=design_colors['title']
                                ),
                                xaxis = dict(ticks='',
                                             nticks=36,
                                             showgrid= False,
                                             tickfont=  dict(color=design_colors['chart_axis_legends']),
                                             gridcolor= design_colors['chart_inside_lines'],
                                             ),
                                yaxis = dict(ticks='',
                                             showgrid= False,
                                             tickfont=dict(color=design_colors['chart_axis_legends']),
                                             gridcolor=design_colors['chart_inside_lines'],
                                             ),

                                annotations=annotations_android
                            )
        }
    else:
        return {
            'data': [go.Heatmap(z=cohort_ios_transpose.T,
                                 x=[str(i)+'-m' for i in list(range(1,13))],
                                 y=cohort_ios_transpose.columns.values,
                                 hoverinfo = "z",
                                 showscale = False,
                                 zauto = True,
                                 colorscale=colorscale
                         )],
            'layout': go.Layout(
                                paper_bgcolor=design_colors['chart_box_bg'],
                                plot_bgcolor=design_colors['chart_bg'],
                                title='<b>Monthly Retention<b>',
                                titlefont=dict(
                                    size=title_size,
                                    color=design_colors['title']
                                ),
                                xaxis = dict(ticks='',
                                             nticks=36,
                                             showgrid= False,
                                             tickfont=dict(color=design_colors['chart_axis_legends']),
                                             gridcolor=design_colors['chart_inside_lines'],
                                             ),
                                yaxis = dict(ticks='',
                                             showgrid= False,
                                             tickfont=dict(color=design_colors['chart_axis_legends']),
                                             gridcolor=design_colors['chart_inside_lines'],
                                             ),

                                annotations=annotations_ios
                            )
        }

#------------------- 2_2 Retention Curve
@app.callback(
    dash.dependencies.Output('retention-curve-container', 'figure'),
    [dash.dependencies.Input('platform_retention', 'value')])
def update_retention_curve(value):
    if value == 'android':
        return {
            'data': [ go.Scatter(
                        y = cohort_android_transpose.mean(axis=1),
                        x = [str(i)+'-m' for i in list(range(1,13))],
                        name = 'mean retention',
                        hoverinfo = "y",
                        mode='lines',
                        line=dict(color=('#99d8c9'),
                                          width=4)
                    ),
                      go.Scatter(
                        y = cohort_android_transpose.mean(axis=1) - 2 * cohort_android_transpose.sem(axis=1),
                        x=[str(i) + '-m' for i in list(range(1, 13))],
                        name='95% low bound',
                        hoverinfo="y",
                        mode='lines',
                        line = dict(color=('#f7fcfd'),
                                width=0.5)
                    ),
                      go.Scatter(
                        y = cohort_android_transpose.mean(axis=1) + 2 * cohort_android_transpose.sem(axis=1),
                        x=[str(i) + '-m' for i in list(range(1, 13))],
                        name='95% high bound',
                        hoverinfo="y",
                        mode='lines',
                        line=dict(color=('#f7fcfd'),
                                    width=0.5),
                        showlegend=False
                    )
        ],
            'layout' : go.Layout(
                            paper_bgcolor=design_colors['chart_box_bg'],
                            plot_bgcolor=design_colors['chart_bg'],
                            title = '<b>Retention Curve<b>',
                            titlefont= dict(
                                    size=title_size,
                                    color=design_colors['title']
                             ),
                            yaxis=dict(
                                    ticksuffix='%',
                                       tickfont=dict(color=design_colors['chart_axis_legends']),
                                       gridcolor=design_colors['chart_inside_lines'],
                            ),
                            xaxis=dict(rangemode='tozero',
                                       tickfont=dict(color=design_colors['chart_axis_legends']),
                                       gridcolor=design_colors['chart_inside_lines'],
                                       ),
                            showlegend=False
                        )
        }
    else:
        return {
            'data': [ go.Scatter(
                        y = cohort_ios_transpose.mean(axis=1),
                        x = [str(i)+'-m' for i in list(range(1,13))],
                        name = 'mean retention',
                        hoverinfo = "y",
                        mode='lines',
                        line=dict(color=('#99d8c9'),
                                          width=4)
                    ),
                      go.Scatter(
                        y = cohort_ios_transpose.mean(axis=1) - 2 * cohort_android_transpose.sem(axis=1),
                        x=[str(i) + '-m' for i in list(range(1, 13))],
                        name='95% low bound',
                        hoverinfo="y",
                        mode='lines',
                        line = dict(color=('#f7fcfd'),
                                width=0.5)
                    ),
                      go.Scatter(
                        y = cohort_ios_transpose.mean(axis=1) + 2 * cohort_android_transpose.sem(axis=1),
                        x=[str(i) + '-m' for i in list(range(1, 13))],
                        name='95% high bound',
                        hoverinfo="y",
                        mode='lines',
                        line=dict(color=('#f7fcfd'),
                                    width=0.5),
                        showlegend=False
                    )
        ],
            'layout' : go.Layout(
                            paper_bgcolor=design_colors['chart_box_bg'],
                            plot_bgcolor=design_colors['chart_bg'],
                            title = '<b>Retention Curve<b>',
                            titlefont= dict(
                                    size=title_size,
                                    color=design_colors['title']
                             ),
                            yaxis=dict(
                                    ticksuffix='%',
                                       tickfont=dict(color=design_colors['chart_axis_legends']),
                                       gridcolor=design_colors['chart_inside_lines'],
                            ),
                            xaxis=dict(rangemode='tozero',
                                       tickfont=dict(color=design_colors['chart_axis_legends']),
                                       gridcolor=design_colors['chart_inside_lines'],
                                       ),
                            showlegend=False
                        )
        }

# # -------------------------------------------------------------------- 3_2 Funnel
# @app.callback(
#     dash.dependencies.Output('funnel-container', 'figure'),
#     [dash.dependencies.Input('funnel-picker-range', 'start_date'),
#      dash.dependencies.Input('funnel-picker-range', 'end_date'),
#      dash.dependencies.Input('platform_funnel', 'value')])
# def update_funnel(start_date, end_date, value):
#     platform = '1' if value == 'android' else '3'
#     funnel_data = pd.read_sql_query('EXEC DS_GetFunnelDataFunc \''+start_date+'\',\''+end_date+'\','+platform, cnxn1)

#     # chart stages data
#     phases = ['Signups', 'Pro Page Views', 'Subscribers', 'Paying Users']
#     values = list(funnel_data.values[0])

#     # funnel percentages: percentages of the phase from previous phase
#     f_p_from_previous = [100]+[np.round(values[i+1]/values[i]*100,2) for i in range(len(values)-1)]
#     # funnel percentages: percentages of the phase from the first phase/ max value
#     f_p_from_max = [100]+[np.round(values[i+1]/values[0]*100,2) for i in range(len(values)-1)]

#     # color of each funnel section
#     colors = ['rgb(148,148,148)', 'rgb(180,180,180)', 'rgb(212,212,212)', 'rgb(244,244,244)']

#     n_phase = len(phases)
#     plot_width = 400

#     # height of a section and difference between sections
#     section_h = 100
#     section_d = 10

#     # multiplication factor to calculate the width of other sections
#     unit_width = plot_width / max(values)

#     # width of each funnel section relative to the plot width
#     phase_pre_percentages = [0.25, 0.02, 0.3, 0.2]
#     phase_w = [values[0]]
#     phase_real_p = [100] # used for debugging purposes
#     for i in range(len(values) - 1):
#         tmp_val = phase_w[i] * 0.75 * values[i + 1] / values[i] * (1 / phase_pre_percentages[i])
#         tmp_val = np.minimum(np.maximum(tmp_val, phase_w[i] * 0.75 * 0.9), phase_w[i] * 0.75 * 1.1)
#         phase_w.append(tmp_val)
#         phase_real_p.append(int(np.round(phase_w[i+1]/phase_w[i]*100,0))) # used for debugging purposes
#     # phase_w = [300, 200, 150, 100, 50]

#     # plot height based on the number of sections and the gap in between them
#     height = section_h * n_phase + section_d * (n_phase - 1)

#     # list containing all the plot shapes
#     shapes = []

#     # list containing the Y-axis location for each section's name and value text
#     label_y = []

#     for i in range(n_phase):
#             if (i == n_phase-1):
#                     points = [phase_w[i] / 2, height, phase_w[i] / 2, height - section_h]
#             else:
#                     points = [phase_w[i] / 2, height, phase_w[i+1] / 2, height - section_h]

#             path = 'M {0} {1} L {2} {3} L -{2} {3} L -{0} {1} Z'.format(*points)

#             shape = {
#                     'opacity': 0.3,
#                     'xref': 'x',
#                     'yref': 'y',
#                     'type': 'path',
#                     'path': path,
#                     'fillcolor': colors[i],
#                     'line': {
#                         'width': 1,
#                         'color': colors[i]
#                     }
#             }
#             shapes.append(shape)

#             # Y-axis location for this section's details (text)
#             label_y.append(height - (section_h / 2))

#             height = height - (section_h + section_d)



#     # For phase names

#     text_for_funnel = []
#     text_for_funnel.append("{} <b>{}<b>".format(phases[0], values[0]))
#     text_for_funnel.extend(["{} <b>{} ({}%)<b>".format(ph, v, f_p_p) for ph, v, f_p_p  in zip(phases, values, f_p_from_previous)][1:])

#     trace = go.Scatter(
#         x=[0]*n_phase,
#         y=label_y,
#         mode='text',
#         text=text_for_funnel,# ["{} <b>{} ({}%)<b>".format(ph, v, f_p_p) for ph, v, f_p_p  in zip(phases, values, f_p_from_previous)],
#         textfont=dict(
#             color=design_colors['text'],
#             size=16,
#             family='Arail'
#         ),
#         hoverinfo = 'none'
#     )

#     data = [trace]

#     layout = go.Layout(
#         paper_bgcolor=design_colors['chart_box_bg'],
#         plot_bgcolor=design_colors['chart_bg'],
#         title="<b>Subscription Funnel</b>",
#         titlefont=dict(
#             size=title_size,
#             color=design_colors['title']
#         ),
#         shapes=shapes,
#         showlegend=False,
#         xaxis=dict(
#             showticklabels=False,
#             zeroline=False,
#             showgrid= False
#             ),
#         yaxis=dict(
#             showticklabels=False,
#             zeroline=False,
#             showgrid=False
#             )
#     )
#     return {
#             'data': data,
#             'layout' : layout
#         }

# ------------------------------------- Graph callbacks
@app.callback(
    dash.dependencies.Output('funnel-container_barplot', 'figure'),
    [dash.dependencies.Input('old_date_picker_funnel_barplot', 'start_date'),
     dash.dependencies.Input('old_date_picker_funnel_barplot', 'end_date'),
     dash.dependencies.Input('new_date_picker_funnel_barplot', 'start_date'),
     dash.dependencies.Input('new_date_picker_funnel_barplot', 'end_date'),
     dash.dependencies.Input('platform_funnel_barplot', 'value'),
     dash.dependencies.Input('country_funnel_barplot', 'value')])
def update_barplot(old_start_date, old_end_date, new_start_date, new_end_date, platform, country):
    old_start_date = str(old_start_date)[:10]
    old_end_date = str(old_end_date)[:10]
    new_start_date = str(new_start_date)[:10]
    new_end_date = str(new_end_date)[:10]
    if country == 'All':
        new_subs, new_text = get_funnel(new_start_date, new_end_date, platform)
        old_subs, old_text = get_funnel(old_start_date, old_end_date, platform)
    else:
        country = get_country_code(country)
        new_subs, new_text = get_funnel(new_start_date, new_end_date, platform, country)
        old_subs, old_text = get_funnel(old_start_date, old_end_date, platform, country)

    trace1 = go.Bar(
        x=['Signups', 'Purchase', 'Paid'],
        y=new_subs,
        name='new subs',
        text=new_text,
        textposition = 'inside',
        hoverinfo = "none",
        marker = dict(color='#fc8d62')
    )
    trace2 = go.Bar(
        x=['Signups', 'Purchase', 'Paid'],
        y=old_subs,
        name='old subs',
        text = old_text,
        textposition = 'inside',
        hoverinfo = "none",
        marker = dict(color='#8da0cb')
    )
    data = [trace1, trace2]

    return {
            'data': data,
            'layout' : {
                'barmode': 'stack',
                'paper_bgcolor': design_colors['chart_box_bg'],
                'plot_bgcolor': design_colors['chart_bg'],
                'xaxis': {
                    'showgrid': False,
                    'tickfont': dict(color=design_colors['chart_axis_legends']),
                    'gridcolor': design_colors['chart_inside_lines'],
                    'tickformat': '%b %d',

                },
                'yaxis': {
                    'showgrid': True,
                    'tickfont': dict(color=design_colors['chart_axis_legends']),
                    'gridcolor': design_colors['chart_inside_lines'],
                    'type': 'log',
                },
                'margin': go.layout.Margin(
                                            l=50,
                                            r=50,
                                            b=50,
                                            t=50,
                                            # pad=20
                                        ),
                "title": '<b>Subscriptions<b>',
                'titlefont' : dict(
                        size=title_size,
                        color=design_colors['title']
                ),
                'legend': dict(font=dict(color=design_colors['text']))
            }
        }

# ------------------------------------- Table callbacks
#------------------ New
@app.callback(
    dash.dependencies.Output('table_new', 'data'),
    [dash.dependencies.Input('table_new-date-picker', 'start_date'),
     dash.dependencies.Input('table_new-date-picker', 'end_date'),
     dash.dependencies.Input('table_new_platform', 'value'),
     dash.dependencies.Input('toggle-switch-1', 'value'),
     dash.dependencies.Input('toggle-switch-2', 'value')])
def update_table(start_date, end_date, platform, is_live, is_live2):
    start_date = str(start_date)[:10]
    end_date = str(end_date)[:10]

    if platform == '1114':
        platform_signup = '1114'
        platform_subs = '1'
    else:
        platform_signup = '1122'
        platform_subs = '3'

    if (is_live or is_live2):
        print("Reading signups new.................................")
        signups = pd.read_sql_query('exec DS_GetNumberOfSignupsByCountry @RegistrationStartDate = \'' + start_date + '\', ' +
             '@RegistrationEndDate = \'' + end_date+ '\', ' + '@Platform = '+ platform_signup, cnxn)
        print("Reading signups new.................................DONE")
        print("Reading subs new.................................")

        subs = pd.read_sql_query('exec DS_GetSubscriptions @RegistrationStartDate = \'' + start_date + '\', ' +
             '@RegistrationEndDate = \'' + end_date+ '\', ' + '@Platform = '+ platform_subs, cnxn)
        print("Reading subs new.................................DONE")
    else:
        signups = pd.read_csv(r'data\signups_new.csv', keep_default_na=False)
        signups.drop(columns=['Unnamed: 0'], inplace=True)
        subs = pd.read_csv(r'data\subs_new.csv', keep_default_na=False)
        subs.drop(columns=['Unnamed: 0'], inplace=True)

    print("Constructing tables new.................................")
    data = subs_table_constructor(subs, prices, countries, signups)
    print("Constructing tables new.................................DONE")

    data.to_csv ('exports/{}_{}_{}.csv'.format(platform, start_date,end_date))
    return data.to_dict('records')

# #------------------ Old
# @app.callback(
#     dash.dependencies.Output('table_old', 'data'),
#     [dash.dependencies.Input('table_old-date-picker', 'start_date'),
#      dash.dependencies.Input('table_old-date-picker', 'end_date'),
#      dash.dependencies.Input('table_old_platform', 'value'),
#      dash.dependencies.Input('toggle-switch-1', 'value')])
# def update_table(start_date, end_date, platform, is_live):
#     start_date = str(start_date)[:10]
#     end_date = str(end_date)[:10]

#     if platform == '1114':
#         platform_signup = '1114'
#         platform_subs = '1'
#     else:
#         platform_signup = '1122'
#         platform_subs = '3'

#     if is_live:
#         print("Reading signups old.................................")
#         signups = pd.read_sql_query('exec DS_GetNumberOfSignupsByCountry @RegistrationStartDate = \'' + start_date + '\', ' +
#              '@RegistrationEndDate = \'' + end_date + '\', ' + '@Platform = '+ platform_signup, cnxn)
#         print("Reading signups old.................................DONE")
#         print("Reading subs old.................................")

#         subs = pd.read_sql_query('exec DS_GetSubscriptions @RegistrationStartDate = \'' + start_date + '\', ' +
#              '@RegistrationEndDate = \'' + end_date+ '\', ' + '@Platform = '+ platform_subs, cnxn)
#         print("Reading subs old.................................DONE")
#     else:
#         signups = pd.read_csv(r'data\signups_old.csv', keep_default_na=False)
#         signups.drop(columns=['Unnamed: 0'], inplace=True)
#         subs = pd.read_csv(r'data\subs_old.csv', keep_default_na=False)
#         subs.drop(columns=['Unnamed: 0'], inplace=True)
#         print(subs.info())


#     print("Constructing tables old.................................")
#     data = subs_table_constructor(subs, prices, countries, signups)
#     print("Constructing tables old.................................DONE")
#     data.to_csv ('exports/{}_{}_{}.csv'.format(platform, start_date,end_date))
#     return data.to_dict('records')

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port='8080')
