query_dic = {
    'stats_query_hour': {
        1:
            """SELECT 
                t2.site_name as `Zählstelle`,
                t2.Status,
                t2.lanes as Spuren,
                t2.street_type as `Typ`,
                format(avg({0}), 1) as `{1} Mittelw.`,
                max({0}) as `{1} Max.`,
                min(date_from) as `Erster Wert`,
                max(date_from) as `Letzter Wert`,
                count(*) as `Anz Werte`
            FROM  
            miv_traffic t1
            inner join site t2 on t2.id = t1.site_id
            WHERE {2}
            group by t2.site_name, t2.street_type""",
        2:
            """SELECT 
            t2.site_name as `Zählstelle`,
            t2.Status,
            t2.lanes as Spuren,
            t2.street_type as `Typ`,
            format(avg(total), 1) as `{0} Mittelw.`,
            max(total) as `{0} Max.`,
            min(date_from) as `Erster Wert`,
            max(date_from) as `Letzter Wert`,
            count(*) as `Anz Werte`
            FROM  
            slow_traffic t1
            inner join site t2 on t2.id = t1.site_id
            WHERE {1}
            group by t2.site_name, t2.street_type""",
    },
    'stats_query_day': {
        1:
            """SELECT 
            t2.site_name as `Zählstelle`,
            t2.Status,
            t2.lanes as Spuren,
            t2.street_type as `Typ`,
            format(avg({0}), 1) as `{1} Mittelw.`,
            max({0}) as `{1} Max.`,
            min(date_from) as `Erster Wert`,
            max(date_from) as `Letzter Wert`,
            count(*) as `Anz Werte`
            FROM 
            v_miv_traffic_per_day t1
            inner join site t2 on t2.id = t1.site_id
            WHERE {2}
            group by t2.site_name, t2.street_type""",
        2:
            """SELECT 
            t2.site_name as `Zählstelle`,
            t2.Status,
            t2.street_type as `Typ`,
            format(avg(total), 1) as `{0} Mittelw.`,
            max(total) as `{0} Max.`,
            min(date_from) as `Erster Wert`,
            max(date_from) as `Letzter Wert`,
            count(*) as `Anz Werte`
            FROM 
            v_slow_traffic_per_day t1
            inner join site t2 on t2.id = t1.site_id
            WHERE {1}
            group by t2.site_name, t2.street_type""",
    },
    'barchart_query_hour': {
        1:
            """SELECT site_id as site_name, {0}, avg({1}) as {1} 
            FROM miv_traffic t1  
            where {2} group by {0}
            """,
        2:
            """SELECT site_id as site_name, {0}, avg({1}) as {1} 
            FROM slow_traffic t1  
            where {2} group by {0}
            """,
    },
    'barchart_query_day': {
        1:
            """SELECT site_id as site_name, {0}, avg({1}) as {1} 
            FROM v_miv_traffic_per_day
            where {2} group by {0}
            """,
         2:
            """SELECT site_id as site_name, {0}, avg({1}) as total 
            FROM v_slow_traffic_per_day
            where {2} group by {0}
            """,
    },
    'map_query_hour': {
        1:
            """SELECT t2.site_name, t2.lon, t2.lat, avg({0}) as {0} 
            FROM miv_traffic t1  
            inner join site t2 on t2.id = t1.site_id 
            where lat > 0 {1} group by t2.site_name, t2.lon, t2.lat
            """,
        2:
            """SELECT t2.site_name, t2.lon, t2.lat, avg({0}) as {0} 
            FROM slow_traffic t1  
            inner join site t2 on t2.id = t1.site_id 
            where lat > 0 {1} group by t2.site_name, t2.lon, t2.lat
            """
    },
    'map_query_day': {
        1:
            """SELECT t2.site_name, t2.lon, t2.lat, avg({0}) as {0} 
            FROM v_miv_traffic_per_day t1  
            inner join site t2 on t2.id = t1.site_id 
            where lat > 0 and {1} group by t2.site_name, t2.lon, t2.lat
            """,
        2:
            """SELECT t2.site_name, t2.lon, t2.lat, avg({0}) as {0} 
            FROM v_slow_traffic_per_day t1  
            inner join site t2 on t2.id = t1.site_id 
            where lat > 0 and {1} group by t2.site_name, t2.lon, t2.lat
            """
    },
    'timeseries_query_day': {
        1:
            """SELECT site_id as site_name, direction_id, site_id, date_from as time, sum({0}) as {0} 
            FROM miv_traffic t1  
            where {1} group by site_id, direction_id, date_from
            """,
        2:
            """SELECT site_id as site_name, direction_id, site_id, date_from as time, sum({0}) as {0} 
            FROM slow_traffic t1  
            where {1} group by site_id, direction_id, date_from
            """
    },
    'timeseries_query_hour': {
        1:
            """SELECT site_id as site_name, site_id, direction_id, date_time_from as time, sum({0}) as {0}
            FROM miv_traffic t1  
            where {1}
            group by direction_id, site_id, date_time_from
            """,
        2:
            """SELECT site_id as site_name, site_id, direction_id, date_time_from as time, sum({0}) as {0}
            FROM slow_traffic t1  
            where {1}
            group by direction_id, site_id, date_time_from
            """
    },
    'group_list_query': {
        1:
            "select distinct {0} as `group` from miv_traffic where {1} order by {0}",
        2:
            "select distinct {0} as `group` from slow_traffic where {1} order by {0}",
    },
    # general, dataset independant queries
    'dataset_query': 'SELECT * FROM info where id = {}',
    'id_code_query': 'select id, code from lookup_code where category_id = {} order by {}',
    'code_title_query': "select code, title from lookup_code where category_id = {} order by {}",
    'year_list_query': "SELECT year(date_from) as year_from, year(date_to) as year_to FROM info where id = {}",
    'direction_list_query': "SELECT id, name FROM station_lookup_code where category_id = 2 and site_id = {}",
    'lanes_list_query': "SELECT lanes FROM site where id = {}",
    'miv_site_list': "select id, `site_name` from site where miv_flag = 1 order by `site_name`",
    'fuss_site_list': "select id, `site_name` from site where fuss_data_flag = 1 order by `site_name`",
    'velo_site_list': "select id, `site_name` from site where velo_data_flag = 1 order by `site_name`"
}


def get_ds_query(key: str, ds: int) -> str:
    """Returns the query for a specified key and datasetid"""

    print(key,ds)
    return query_dic[key][ds]


def get_gen_query(key: str) -> str:
    """Returns the query for a specified key, for queries that independant of the dataset"""

    print(key)
    return query_dic[key]
