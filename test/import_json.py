import urllib.request
import json
import pandas as pd

def make_new_df_value(x: str = '', column_name: str = ''):
    try:
        x = x[column_name]
    except Exception as e:
        print(e)
        x = 0.0
    return x


def get_fields():
    fields = ["lief", "pw0", "sattelzug", "month", "zst_nr", "year", "total", "timefrom", "pw", "sitename",
              "lw", "directionname", "lief0", "lanename", "lief_aufl", "datetimeto", "bus", "hourfrom", "traffictype",
              "date", "day",
              "valuesapproved", "valuesedited", "lw0", "datetimefrom", "timeto", "lanecode", "weekday", "mr",
              "sitecode"]
    return fields


def get_rows(u: str) -> int:
    with urllib.request.urlopen(u) as _url:
        _json = json.loads(_url.read().decode())
    return _json['nhits']


def url_to_df(u: str) -> pd.DataFrame:
    with urllib.request.urlopen(u) as _url:
        _json = json.loads(_url.read().decode())
    df_result = pd.DataFrame(_json['records'])

    fields = get_fields()
    for fld in fields:
        df_result[fld] = df_result['fields'].transform(lambda x: make_new_df_value(x, fld))

    df_result = df_result.drop(['fields'], axis=1)
    for fld in fields:
        df_result[fld].apply(str)
        df_result[fld] = df_result[fld].astype(str)
    return df_result

# Main
url_template = """https://data.bs.ch/api/records/1.0/search/?rows={}&start={}&dataset=100006&sort=datetimefrom&facet=zst_nr&facet=sitename&facet=directionname&facet=lanename&facet=valuesapproved&facet=valuesedited&facet=year&facet=month&facet=day&facet=weekday&facet=timefrom
"""
rows = 1000
url = url_template.format(1, 1)
available_records = get_rows(url)
start = 1
data = []
result = []
for i in range(available_records % rows + 1):
    print(i)
    st.write(i)
    url = url_template.format(rows, start)
    print(url)
    df = url_to_df(url)
    if start == 1:
        result = df
    else:
        result += df
    start += rows

result.to_csv('verkehr.csv')
