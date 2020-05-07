import mysql.connector as mysql
import pandas as pd

# from datetime import date
import pymysql
import sqlalchemy as sql
import datetime

import query as qry
import config as cn
import db_config as dbcn
import tools

pymysql.install_as_MySQLdb()
# import MySQLdb

mydb = ''


def execute_non_query(cmd: str):
    """executes a stored procedure, without return value"""

    _cursor = mydb.cursor()
    _cursor.execute(cmd)


def execute_query(query: str):
    """Executes a query and returns a dataframe with the results"""

    tools.log('start execute sql: ' + query)
    result = pd.read_sql_query(query, mydb)
    print(result)
    tools.log('end execute')
    return result


# @st.cache(suppress_st_warning=True)
def init():
    """Reads the connection string and sets the sql_engine attribute."""

    global mydb

    print(dbcn.DB_HOST, dbcn.DATABASE)
    mydb = mysql.connect(
        host=dbcn.DB_HOST,
        user=dbcn.DB_USER,
        passwd=dbcn.DB_PASS,
        database=dbcn.DATABASE
    )


def get_distinct_values(column_name, table_name, dataset_id, criteria):
    """Returns a list of unique values from a defined code column."""


    query = "SELECT {0} FROM {1} where dataset_id = {2} {3} {4} group by {0} order by {0}".format(column_name,
                                                                                                  table_name,
                                                                                                  dataset_id, (
                                                                                                      ' AND ' if criteria > '' else ''),
                                                                                                  criteria)
    result = execute_query(query)
    result = result[column_name].tolist()
    return result


def get_id_code_dic(cat: int, order_col: str) -> dict:
    """Returns a dictionary for a given code category with lookupid and code for this category"""

    query = qry.get_gen_query('id_code_query').format(cat, order_col)
    df = execute_query(query)
    dic = dict(zip(df['id'].tolist(), df['code'].tolist()))
    return dic


def get_all_directions_dic():
    query = "select id, name from station_lookup_code where category_id = 2 order by name"
    df = execute_query(query)
    dic = dict(zip(df['id'].tolist(), df['name'].tolist()))
    return dic


def get_code_title_dic(cat: int, order_col: str) -> dict:
    query = qry.get_gen_query('code_title_query').format(cat, order_col)
    df = execute_query(query)
    dic = dict(zip(df['code'].tolist(), df['title'].tolist()))
    return dic


def get_site_dic(traffic_type: int, par_id: int):
    # sql = f"select id, `code` from site where {traffic_type + '_flag'} = 1 order by `code`"

    if traffic_type == 1:
        query = qry.get_gen_query('miv_site_list')
    elif par_id == 1:
        query = qry.get_gen_query('fuss_site_list')
    elif par_id == 2:
        query = qry.get_gen_query('velo_site_list')
    df = execute_query(query)
    return dict(zip(df['id'].tolist(), df['site_name'].tolist()))


def get_vehicle_dic(ds: int):
    if ds == 1:
        return get_code_title_dic(2, 'order_id')
    else:
        return get_id_code_dic(4, 'order_id')


def get_year_list(traffic_type: int) -> list:
    query = qry.get_gen_query('year_list_query').format(traffic_type)
    df = execute_query(query)
    year_list = list(range(df['year_from'][0], df['year_to'][0] + 1))
    return year_list


def get_direction_dic(site_id: int):
    """ include first all for all directions, then all directions for the given site"""

    dic1 = {"0": 'Alle Richtungen'}
    query = qry.get_gen_query('direction_list_query').format(site_id)
    df = execute_query(query)
    dic2 = dict(zip(df['id'].tolist(), df['name'].tolist()))
    dic1.update(dic2)
    return dic1


def get_lane_list(site_id: int) -> list:
    query = qry.get_gen_query('lanes_list_query').format(site_id)
    df = execute_query(query)
    lst = list(range(1, int(df['lanes'][0])))
    return lst


def save_db_table(table_name: str, df: pd.DataFrame, fields: list):
    connect_string = f'mysql+pymysql://{dbcn.DB_USER}:{dbcn.DB_PASS}@{dbcn.DB_HOST}:{dbcn.DB_PORT}/{dbcn.DATABASE}?charset=utf8'
    sql_engine = sql.create_engine(connect_string, pool_recycle=3600)
    db_connection = sql_engine.connect()

    try:
        if len(fields) > 0:
            df = df[fields]
            print(len(df))
            print(df.head())
        frame = df.to_sql(table_name, db_connection, if_exists='append')
        print(f'{table_name} saved successfully')
    except ValueError as vx:
        print(vx)
    except Exception as ex:
        print(ex)
    else:
        print(f'Table {table_name} created successfully.')
    finally:
        db_connection.close()


def daily_import_miv():
    """
    Replaces the table traffic_source with new data. Truncates first all data, then loads the all data from
    data.bs.ch in a dataframe and filters for rows with year > currentyear -2. this is to reduce the amount of data
    replaced in the target table miv.
    """
    source_file_name = cn.source_miv_file_name
    cmd = "truncate table miv_traffic_source"
    tools.log(f'executing {cmd}')
    execute_non_query(cmd)
    tools.log('done')
    tools.log(f'reading {cn.source_miv_file_name}')
    df = pd.read_csv(cn.source_miv_file_name, sep=';', encoding='UTF8')
    tools.log(f'{len(df)} rows read')
    tools.log('saving table')
    fields = ['SiteCode', 'SiteName', 'DirectionName', 'LaneCode', 'LaneName', 'Date', 'TimeFrom', 'TimeTo',
              'ValuesApproved', 'ValuesEdited', 'TrafficType', 'Total', 'MR', 'PW', 'PW+', 'Lief', 'Lief+',
              'Lief+Aufl.', 'LW', 'LW+', 'Sattelzug', 'Bus', 'andere', 'DateTimeFrom']
    save_db_table('miv_traffic_source', df, fields)
    
    tools.log('appending imported rows from table traffic_source to miv')
    mydb.cursor().callproc('daily_miv_import', [])
    tools.log('done')
    tools.log('filling time columns')
    mydb.cursor().callproc('miv_traffic_update_columns', [])
    tools.log('done')
    tools.log('copy records from staging to miv_traffic')
    mydb.cursor().callproc('miv_copy_records', [])
    tools.log('done')


def daily_import_slow():
    """
    Replaces the table traffic_source with new data. Truncates first all data, then loads the all data from
    data.bs.ch in a dataframe and filters for rows with year > currentyear -2. this is to reduce the amount of data
    replaced in the target table miv.
    """
    a = """
    source_file_name = cn.source_slow_file_name
    cmd = "truncate table slow_traffic_source"
    tools.log(f'executing {cmd}')
    execute_non_query(cmd)
    tools.log('done')
    tools.log(f'reading {source_file_name}')
    df = pd.read_csv(source_file_name, sep=';', encoding='UTF8')
    tools.log(f'{len(df)} rows read')
    tools.log('saving table')
    fields = ['SiteCode', 'SiteName', 'DirectionName', 'LaneCode', 'LaneName', 'ValuesApproved', 'ValuesEdited',
              'TrafficType', 'Total', 'DateTimeFrom']
    save_db_table('slow_traffic_source', df, fields)
    tools.log('done')
    tools.log('appending imported rows from table traffic_source to slow')
    mydb.cursor().callproc('slow_traffic_import', [])
    tools.log('done')
    
    tools.log('filling time columns')
    mydb.cursor().callproc('slow_traffic_update_columns', [])
    tools.log('done')
    """
    tools.log('copy records from staging to miv_traffic')
    mydb.cursor().callproc('slow_traffic_copy_records', [])
    tools.log('done')


def daily_import2():
    """
    Replaces the table traffic_source with new data. Truncates first all data, then loads the all data from
    data.bs.ch in a dataframe and filters for rows with year > currentyear -2. this is to reduce the amount of data
    replaced in the target table miv.
    """
    source_file_name = 'https://data.bs.ch/explore/dataset/100006/download/?format=csv&timezone=Europe/Berlin&lang=en&use_labels_for_header=true&csv_separator=%3B'
    cmd = "truncate table traffic_source"
    tools.log(f'executing {cmd}')
    execute_non_query(cmd)
    tools.log('done')
    tools.log(f'reading {source_file_name}')
    df = pd.read_csv(source_file_name, sep=';', encoding='UTF8')
    tools.log('done')
    # tools.log('filtering')
    # df = df[df.Year.gt(date.today().year - 2)]
    # tools.log('done')
    print(df.head())
