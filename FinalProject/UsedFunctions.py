import pandas as pd
import numpy as np

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
    if platform == '1122':
        subs[0] = subs[0] / 15
        subs[1] = subs[1] * 2
        subs[2] = subs[2] * 2.5
    else:
        subs[0] = subs[0] / 40
        subs[1] = subs[1] * 2
        subs[2] = subs[2] * 3
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

    