import pandas as pd
import datetime

df = pd.read_csv('./data/converted_MIV_Class_10_1.csv', sep=';', encoding='UTF8')
# dataframe holding location information
df_zs = pd.read_csv('./data/100038.csv', sep=';', encoding='UTF8')
# rename station code column so the name matches with
df_zs = df_zs.rename(columns={'ZST_NR': 'SiteCode'})
# link the 2 dataframes
df_merged = pd.merge(df, df_zs, on='SiteCode')
# drop unnecessary columns
#df_merged = df_merged.drop(['Geo Point', 'Geo Shape', 'DAT_INBETR', 'DBL_FORMAT', 'EIGENTUM', 'LINK_EXT', 'ANZ_ARME']
#                           , axis=1)
df_merged = df_merged[['SiteCode', 'DirectionName', 'LaneCode', 'Date', 'Total', 'MR', 'PW', 'PW+', 'Lief', 'Lief+',
                       'Lief+Aufl.', 'LW', 'LW+', 'Sattelzug', 'Bus', 'andere', 'DateTimeFrom', 'Year', 'Month', 'Day',
                       'Weekday', 'ZST_NAME', 'BREITENGR', 'LAENGENGR', 'GEMEINDE']]
#use ZST_Name which only includes the address, no code, rename it to SiteName, which was dropped in the step above, as
# it included as well the code
df_merged.rename(columns={'ZST_NAME': 'SiteName'}, inplace=True)
df_merged = df_merged.loc[(df_merged['Year'] >= 2018)]
df_merged['DateTimeFrom'] = pd.to_datetime(df['DateTimeFrom'])
df_merged['Date'] = pd.to_datetime(df_merged['DateTimeFrom']).apply(lambda x: x.date())

print(df_merged.dtypes)
df_merged.to_csv('./data/merged.csv', sep=';')

