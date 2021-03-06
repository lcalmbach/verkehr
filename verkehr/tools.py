"""
    Collection of useful functions.
"""

__author__ = "lcalmbach@gmail.com"

import config as cn
import streamlit as st
import pandas as pd
import numpy as np
import base64
from datetime import datetime, date
import calendar


@st.cache(suppress_st_warning=True)
def get_lists(data: pd.DataFrame):
    _site_names = data['SiteName'].unique().tolist()
    _years = data['Year'].unique().tolist()
    _years.sort()
    _site_names.sort()
    return _site_names, _years


def get_unique_values(data: pd.DataFrame, column_name: str) -> list:
    _result = data[column_name].unique().tolist()
    _result.sort()
    return _result

def get_cs_item_list(lst: list, separator: str = ',', quote_string: str = ''):
    result = ''
    for item in lst:
        result += quote_string + str(item) + quote_string + separator
    result = result[:-1]
    return result


def color_gradient(row: int, value_col: str, min_val: float, max_val: float, rgb: str) -> int:
    """
    Projects a value on a color gradient scale given the min and max value.
    the color gradient type is defined in the config, e.g. blue-green, red, blue etc.
    returns a string with rgb values
    """

    result = {'r': 0, 'g': 0, 'b': 0}
    if max_val - min_val != 0:
        x = int((row[value_col] - min_val) / (max_val - min_val) * 255)
    else:
        x = 0

    if cn.GRADIENT == 'blue-green':
        if row[value_col] > max_val:
            result['r'] = 255
        else:
            result['g'] = x
            result['b'] = abs(255 - x)
    return result[rgb]


def month_dic(year_list: list) -> list:
    """recieves dictionary years and generates for eyery year 12 entries: YYYY01 to YYYY to 12"""
    result = {}
    year_list.sort()
    for y in year_list:
        for m in range(1, 13):
            result.update({y*100 + m: '{}-{}'.format(y, m)})
    return result


def get_pivot_data(df, group_by):
    """
    Returns a pivot table from the raw data table. df must include the station name, the data column and the
    group by column. Example
    input:
    Â¦StationÂ¦date       Â¦parameter  Â¦value  Â¦
    -----------------------------------------
    Â¦MW1    Â¦1/1/2001   Â¦calcium    Â¦10     Â¦
    Â¦MW1    Â¦1/1/2001   Â¦chloride   Â¦21     Â¦

    output:
    Â¦StationÂ¦date       Â¦calcium    Â¦chloride   Â¦
    ---------------------------------------------
    Â¦MW1    Â¦1/1/2001   Â¦10         Â¦21         Â¦

    :param df:          dataframe holding the data to be pivoted
    :param group_by:
    :return:
    """

    result = pd.pivot_table(df, values=cn.VALUES_VALUE_COLUMN, index=[cn.SAMPLE_DATE_COLUMN, cn.STATION_NAME_COLUMN,
                                                                      group_by], columns=[cn.PAR_NAME_COLUMN],
                            aggfunc=np.average)
    return result


def get_unstacked(df: pd.DataFrame, index_fields: list, value_fields: list):
    df = df[index_fields + value_fields]
    st.write(index_fields)
    df.set_index(index_fields)
    st.write(df.head())
    #df = df.unstack()
    return df


def remove_nan_columns(df: pd.DataFrame):
    """
    Removes all empty columns from a data frame. This is used to reduce unnecessary columns when displaying tables.
    Since there is only one station table but different data collection may have different data fields, often not all
    fields are used in many cases. when displaying station or parameter information, empy columns can be excluded in
    order to make the table easier to read.

    :param df: dataframe from which empty dolumns should be removed
    :return:
    """

    lis = df.loc[:, df.isna().all()]
    for col in lis:
        del df[col]
    return df


def remove_columns(df: pd.DataFrame, lis: list) -> pd.DataFrame:
    """
    Removes columns specified in a list from a data frame. This is used to reduce unnecessary columns when
    displaying tables.

    :param lis: list of columns to remove from the dataframe
    :param df: dataframe with columns to be deleted
    :return: dataframe with deleted columns
    """

    for col in lis:
        del df[col]
    return df


def get_table_download_link(df: pd.DataFrame) -> str:
    """
    Generates a link allowing the data in a given panda dataframe to be downloaded

    :param df:  table with data
    :return:    link string including the data
    """

    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    href = f'<a href="data:file/csv;base64,{b64}">Als csv Datei herunterladen</a>'

    return href


def transpose_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transposes a dataframe that has exactly 1 row and n columns to a table that has 2 columns and n rows. column names
    become row headers.

    Parameters:
    -----------
    :param df:
    :return:

    :param df:  dataframe to be transposed
    :return:    transposed data frame having 2 columns and n rows
    """

    result = pd.DataFrame({"Field": [], "Value": []})
    for key, value in df.iteritems():
        df2 = pd.DataFrame({"Field": [key], "Value": [df.iloc[-1][key]]})
        result = result.append(df2)
    result = result.set_index('Field')
    return result


def log(expression: str):
    """
    Logs the expression with a timestamp to the console.

    :param expression:  string to be logged
    :return:
    """

    print(datetime.now(), expression)


def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year, month)[1])
    result = date(year, month, day)
    return result


def get_time_intervals():
    _time_intervals = ['Alle']
    for i in range(23):
        ll = '{:0>2}'.format(i)
        ul = '{:0>2}'.format(i + 1)
        _time_intervals.append('{} - {}'.format(ll, ul))
    _time_intervals.append('{} - {}'.format('23', '00'))
    return _time_intervals

def is_valid_date(dt: str) -> bool:
    if dt > '':
        try:
            frm = '%Y-%m-%d'
            _result = datetime.strptime(dt, frm)
            return True
        except ValueError:
            return False
    else:
        return True

