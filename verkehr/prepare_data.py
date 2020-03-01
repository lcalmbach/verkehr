import pandas as pd
import datetime

df = pd.read_csv('converted_MIV_Class_10_1.csv', sep=';', encoding='UTF8')
# dataframe holding location information
df_zs = pd.read_csv('100038.csv', sep=';', encoding='UTF8')
# rename station code column so the name matches with
df_zs = df_zs.rename(columns={'ZST_NR': 'SiteCode'})
# link the 2 dataframes
df_merged = pd.merge(df, df_zs, on='SiteCode')
# drop unnecessary columns
df_merged = df_merged.drop(['Geo Point', 'Geo Shape', 'DAT_INBETR', 'DBL_FORMAT', 'EIGENTUM', 'LINK_EXT', 'ANZ_ARME']
                           , axis=1)

df['DateTimeFrom'] = pd.to_datetime(df['DateTimeFrom'])
df['Date'] = pd.to_datetime(df['DateTimeFrom']).apply(lambda x: x.date())

print(df.dtypes)
df_merged.to_csv('merged.csv', sep=';')

