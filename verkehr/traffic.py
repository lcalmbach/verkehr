"""
This module contains the classes .
"""

__author__ = "lcalmbach@gmail.com"
__version__ = '0.3.1'

import pandas as pd
import numpy as np
import locale

import altair as alt
import pydeck as pdk
import streamlit as st
from datetime import date, timedelta, datetime
from enum import Enum

import config as cn
import tools
import database as db
import query as qry


class Traffic:
    """
    Includes general functions to display application info, read data, render about text.
    """

    def __init__(self, result_type):
        self._result_type = result_type
        self.marker_groupby = ''
        self.plot_groupby = ''
        self.marker_groupby = 'Year'
        self.define_axis_length = False
        self.plot_width = cn.def_plot_width
        self.plot_height = cn.def_plot_height
        self.ypar = ''
        self.define_axis_limits = False
        self.xax_min = 0
        self.xax_max = 0
        self.yax_min = 0
        self.yax_max = 0
        self.marker_average_method = ''
        self.stat_line_method = ''
        self.site_filter = ''
        self.lane_filter = ''
        self.direction_filter = ''
        self.date_filter = ''
        self.month_from_filter = 0
        self.month_to_filter = []
        self.year_from_filter = 0
        self.year_to_filter = 0
        self.time_aggregation_interval = 'day'
        self.time_from_filter = 0
        self.time_to_filter = 23
        self.chart_default_fields = []
        self.moving_average_days = 0
        self._traffic_type = 1                  # slow traffic or motorized traffic
        self.parameter_dic = {}

        db.init()

        self.direction_dic = {}
        self.all_directions_dic = db.get_all_directions_dic()
        self.site_dic = {}
        self.vehicle_dic = {}
        self.year_list = []
        self.month_dic = {}
        self.sort_dic = {'weekday_from': list(cn.weekday_short_dic.values()),
                         'month_from': list(cn.month_short_dic.values()),
                         'year_from': list(range(2014, 2030)),
                         'hour_from': list(cn.time_dic.values()),
                         'site_id': list(self.site_dic.values()),
                         'direction_id': [],
                         'week_of_year': list(range(1, 52))
                         }

    @property
    def traffic_type(self):
        return self._traffic_type

    @traffic_type.setter
    def traffic_type(self, tt: int):
        self._traffic_type = tt
        self.ypar = 1 if self.ypar == '' else 'Total'
        self.site_dic = db.get_site_dic(self.traffic_type, self.ypar)
        self.vehicle_dic = db.get_vehicle_dic(self.traffic_type)
        self.parameter_dic = cn.parameter_dic[self.traffic_type]
        self.year_list = db.get_year_list(tt)
        self.month_dic = tools.month_dic(self.year_list)

    @property
    def result_type(self):
        return self._result_type

    @result_type.setter
    def result_type(self, rt: str):
        self._result_type = rt
        if rt == 'Karte':
            pass
        else:
            pass

    def show_help_icon(self):
        """Renders a help icon linking to the <read the docs> user manual"""

        st.sidebar.markdown(
            '<a href = "{}" target = "_blank"><img border="0" alt="Help" src="{}"></a>'.format(cn.USER_MANUAL_LINK,
                                                                                               cn.HELP_ICON),
            unsafe_allow_html=True)

    def show_dataset_info(self):
        """Displays general info on the application, this is the first view."""

        f = open("info.md", "r+", encoding='UTF8')
        query = qry.get_gen_query(key='dataset_query').format(self.traffic_type)
        df = db.execute_query(query)
        min_date = df['date_from'][0].strftime('%d.%m.%Y')
        max_date = df['date_to'][0].strftime('%d.%m.%Y')
        title = df['title'][0]
        num = df['number_of_sites'][0]
        text = f.read().format(title, len(self.site_dic.values()), min(self.year_list),
                               tools.get_cs_item_list(self.parameter_dic.values(), separator=', ', quote_string=''),
                               min_date, max_date)
        st.markdown(text)

    def show_about_box(self):
        """Renders the about text in the sidebar."""

        st.sidebar.subheader("About")
        text = """Diese Applikation wurde von [Lukas Calmbach](mailto:lcalmbach@gmail.com) \
        in [Python](https://www.python.org/) entwickelt. Als Frameworks wurden [Streamlit](https://streamlit.io/) \
        und [Altair](https://altair-viz.github.io/) eingesetzt. Der Quellcode ist auf \
        [github](https://github.com/lcalmbach/verkehr) publiziert."""
        st.sidebar.info(text)

    def show_sidebar_controls(self):
        def show_group_by_controls():
            """Group by controls for plots and markers"""

            _list = list(cn.group_by_dic.keys())
            _label = 'Tabellen' if self.result_type == 'Statistik' else 'Grafiken'
            if self.result_type not in ('Karte', 'Zeitreihe'):
                st.sidebar.markdown('---')
                self.plot_groupby = st.sidebar.selectbox('Gruppiere {} nach'.format(_label), _list,
                                                     format_func=lambda x: cn.group_by_dic[x])
            else:
                self.plot_groupby = 'none'

            if self.result_type not in ('Statistik', 'Karte', 'Zeitreihe'):
                # del _list[0]
                # del _list[2]
                self.marker_groupby = st.sidebar.selectbox('Gruppiere Balken nach', index=3,
                                                           options=_list,
                                                           format_func=lambda x: cn.group_by_dic[x])
            else:
                self.marker_groupby = 'none'

            if self.result_type == 'Zeitreihe':
                self.marker_groupby = 'site_id'

        def show_parameter_controls():
            st.sidebar.markdown('---')

            if self.plot_groupby != 'Fahrzeugtyp':
                self.ypar = st.sidebar.selectbox('Parameter', list(self.parameter_dic.keys()),
                                                 format_func=lambda x: self.parameter_dic[x])

            # self.__showdata_table = st.sidebar.checkbox('Show data table', value=False, key=None)
            self.time_aggregation_interval = st.sidebar.selectbox('Zeitliche Aggregation der Messungen',
                                                                  list(cn.time_aggregation_dic.keys()),
                                                                  format_func=lambda x: cn.time_aggregation_dic[x])

        def show_filter_controls():
            st.sidebar.markdown('---')
            st.sidebar.markdown('#### Filter')
            # only provide the all option for sites, if the plots are grouped by site
            if self.plot_groupby == 'site_id' or self.result_type == 'Statistik' or self.result_type == 'Karte':
                dic = {0: 'Alle'}
                dic.update(self.site_dic)
                self.site_dic = dic

            self.site_filter = st.sidebar.selectbox(label='Zählstelle', index=0,
                                                    options=list(self.site_dic.keys()),
                                                    format_func=lambda x: self.site_dic[x])
            if self.site_filter != 0:
                lane_list = db.get_lane_list(self.site_filter)
                self.lane_filter = st.sidebar.selectbox('Spur', index=0, options=['Alle', ] + lane_list)
                self.direction_dic = db.get_direction_dic(self.site_filter)
                self.direction_filter = st.sidebar.selectbox(label='Richtung', index=0,
                                                             options=list(self.direction_dic.keys()),
                                                             format_func=lambda x: self.direction_dic[x])

            self.date_filter = st.sidebar.text_input('Datum (JJJJ-MM-TT)', self.date_filter)
            if not tools.is_valid_date(self.date_filter):
                st.info(f"""Das Datum {self.date_filter} ist nicht gültig, bitte geben sie das Datum im 
                        Format JJJJ-MM-TT ein""")
                self.date_filter = ''


            self.month_from_filter = st.sidebar.selectbox(label='Auswahl Monat von', index=0,
                                                          options=list(self.month_dic.keys()),
                                                          format_func=lambda x: self.month_dic[x])
            self.month_to_filter = st.sidebar.selectbox(label='Auswahl Monat bis',
                                                        index=len(self.month_dic.keys()) - 1,
                                                        options=list(self.month_dic.keys()),
                                                        format_func=lambda x: self.month_dic[x])
            if self.month_from_filter == list(self.month_dic.keys())[0]:
                [self.year_from_filter, self.year_to_filter] = st.sidebar.slider('Auswahl Jahr',
                                                                             min_value=self.year_list[0],
                                                                             max_value=self.year_list[-1:][0],
                                                                             value=[self.year_list[0], self.year_list[
                                                                                 len(self.year_list) - 1]])
            if self.time_aggregation_interval == 'hour':
                [self.time_from_filter, self.time_to_filter] = st.sidebar.slider('Auswahl Zeit (z.B. 2 für 02-03h)',
                                                                                 min_value=0, max_value=23,
                                                                                 value=[0, 23])


        def show_plot_setting_controls():
            st.sidebar.markdown('---')
            st.sidebar.markdown('#### Grafik Einstellungen')

            if self.result_type == 'Zeitreihe':
                self.moving_average_days = st.sidebar.number_input(label='Gleitender Durchschnitt, Fenster in Tagen', value=0)

            # only provide the all option for sites, if the plots are grouped by site
            if self.result_type in ('X-Y-Plot'):
                self.xax_min = st.sidebar.number_input(label='X-Achse Minimum', value=0.0)
                self.xax_max = st.sidebar.number_input(label='X-Achse Maximum', value=0.0)
            self.yax_min = st.sidebar.number_input(label='Y-Achse Minimum', value=0.0)
            self.yax_max = st.sidebar.number_input(label='Y-Achse Maximum', value=0.0)

            self.plot_width = st.sidebar.number_input(label='X-Achse Länge (Pixel)', value=cn.def_plot_width)
            self.plot_height = st.sidebar.number_input(label='Y-Achse Länge (Pixel)', value=cn.def_plot_height)

        show_group_by_controls()
        show_parameter_controls()
        show_filter_controls()
        if self.result_type not in ('Statistik', 'Karte'):
            show_plot_setting_controls()

    def show_results(self):
        def get_number_expression():
            if self.traffic_type == 1:
                return 'Fahrzeuge'
            elif self.ypar == 1:
                return 'Fussgänger'
            else:
                return 'Velos'

        def get_info():
            info = cn.time_aggregation_dic[self.time_aggregation_interval]
            info += ('' if self.site_filter == '0' else
                     f', Zählstelle: {self.site_dic[self.site_filter]}')
            info += (', Alle Richtungen' if self.direction_filter in ('0', '') else
                     ', Richtung: {}'.format(self.direction_dic[self.direction_filter]))
            info += (', Alle Spuren' if self.lane_filter in ('Alle', '') else ', Spur {}'.format(self.lane_filter))
            if self.date_filter != '':
                info += ', Datum: {}'.format(self.date_filter)
            elif has_month_filter():
                info += ', Monate: {} - {}'.format(self.month_dic[self.month_from_filter],
                                                   self.month_dic[self.month_to_filter])
            else:
                info += str(self.year_from_filter) if self.year_from_filter == self.year_to_filter else \
                    ', {} - {}'.format(self.year_from_filter, self.year_to_filter)
            if has_time_filter():
                info += ', Zeit: {}h - {}h'.format(self.time_from_filter, self.time_to_filter + 1)

            return info

        def has_month_filter() -> bool:
            """
            Verifies if the default settings for the month filter has been changed. Default is start = first month in
            available data and to_month is last month in data.
            """

            _list = list(self.month_dic.keys())
            first_month = _list[0]
            last_month = _list[-1]
            result = self.month_from_filter != first_month or self.month_to_filter != last_month
            return result

        def has_time_filter():
            result = self.time_from_filter != 0 or self.time_to_filter != 23
            return result

        def substitute_codes(df):
            if 'site_name' in df.columns:
                df['site_name'].replace(self.site_dic, inplace=True)

            if self.marker_groupby == 'weekday_from':
                df['weekday_from'].replace(cn.weekday_short_dic, inplace=True)
            elif self.marker_groupby == 'month_from':
                df['month_from'].replace(cn.month_short_dic, inplace=True)
            elif self.marker_groupby == 'hour_from':
                df['hour_from'].replace(cn.time_dic, inplace=True)
            elif self.marker_groupby == 'site_id':
                df['site_id'].replace(self.site_dic, inplace=True)
            if 'direction_id' in df.columns:
                df['direction_id'].replace(self.all_directions_dic, inplace=True)
            return df

        def fill_stat_df(base_query: str, criteria: str) -> pd.DataFrame:
            if self.traffic_type == 1:
                query = base_query.format(self.ypar, self.vehicle_dic[self.ypar], criteria)
            else:
                query = base_query.format(self.vehicle_dic[self.ypar], criteria)
            df = db.execute_query(query)
            return df

        def fill_single_plot_df(base_query: str, par: str, criteria: str) -> pd.DataFrame:
            query = base_query.format(self.marker_groupby, par, criteria)
            df = db.execute_query(query)
            df = substitute_codes(df)
            return df

        def fill_single_map_df(base_query: str, par: str, criteria: str) -> pd.DataFrame:
            query = base_query.format(par, criteria)
            df = db.execute_query(query)
            df = substitute_codes(df)
            return df

        def show_single_result():
            title = self.site_dic[self.site_filter]
            st.markdown(f'## Anzahl {get_number_expression()} an Zählstelle')
            st.markdown(get_info())
            if self.result_type == 'Statistik':
                key = f'stats_query_{self.time_aggregation_interval}'
                query = qry.get_ds_query(key, self.traffic_type)
                df = fill_stat_df(query, get_criteria())
                st.table(df)
                st.markdown(tools.get_table_download_link(df), unsafe_allow_html=True)
            elif self.result_type == 'Balkendiagramm':
                key = 'barchart_query_' + self.time_aggregation_interval
                query = qry.get_ds_query(key, self.traffic_type)
                par = self.ypar if self.traffic_type == 1 else 'total'
                df = fill_single_plot_df(query, par, get_criteria())

                if len(df) == 0:
                    st.warning('Keine Daten gefunden, bitte ändern sie die Filter-Einstellungen')
                else:
                    if self.traffic_type == 1:
                        _par = self.ypar
                        _y_ax_label = self.parameter_dic[self.ypar]
                    else:
                        _par = self.parameter_dic[self.ypar]
                        _y_ax_label = _par
                        df.rename(columns={'total': _par}, inplace=True)
                    show_barchart(title, df, _par, _y_ax_label)

            elif self.result_type == 'Zeitreihe':
                key = 'timeseries_query_' + self.time_aggregation_interval
                query = qry.get_ds_query(key, self.traffic_type)
                par = self.ypar if self.traffic_type == 1 else 'total'
                df = fill_single_map_df(query, par, get_criteria())
                if len(df) == 0:
                    st.warning('Keine Daten gefunden, bitte ändern sie die Filter-Einstellungen')
                else:
                    if self.traffic_type == 1:
                        _par = self.ypar
                        _y_ax_label = self.parameter_dic[self.ypar]
                    else:
                        _par = self.parameter_dic[self.ypar]
                        _y_ax_label = _par
                        df.rename(columns={'total': _par}, inplace=True)
                    if len(df) == 0:
                        st.warning('Keine Daten gefunden, bitte ändern sie die Filter-Einstellungen')
                    else:
                        show_time_series(title, df, _par, _y_ax_label)
            elif self.result_type == 'Karte':
                key = 'map_query_' + self.time_aggregation_interval
                query = qry.get_ds_query(key, self.traffic_type)
                par = self.parameter_dic[self.ypar] if self.result_type == 1 else 'total'
                df = fill_single_map_df(query, par, get_criteria())
                if len(df) == 0:
                    st.warning('Keine Daten gefunden, bitte ändern sie die Filter-Einstellungen')
                else:
                    show_map(title, df, par)

        def show_grouped_result():
            def get_group_item_expression(item):
                if self.plot_groupby == 'weekday_from':
                    return cn.weekday_long_dic[item]
                elif self.plot_groupby == 'month_from':
                    return cn.month_long_dic[item]
                elif self.plot_groupby == 'hour_from':
                    return cn.time_dic[item]
                elif self.plot_groupby == 'site_id':
                    return self.site_dic[item]
                else:
                    return str(item)

            def get_list(_criteria: str) -> list:
                _query = qry.get_ds_query('group_list_query', self.traffic_type)
                _query = _query.format(self.plot_groupby, _criteria)
                _df = db.execute_query(_query)
                return _df['group'].tolist()

            st.markdown(f'## Anzahl {get_number_expression()} an Zählstelle')
            st.markdown(get_info())

            criteria = get_criteria()
            group_list = get_list(criteria)
            # clean list for nan values
            group_list = [x for x in group_list if str(x) != 'nan']

            for group_value in group_list:
                criteria_with_group = f' {criteria} and {self.plot_groupby} = {group_value}'
                title = get_group_item_expression(group_value)
                if self.result_type == 'Statistik':
                    st.markdown('### {}: {}'.format(cn.group_by_dic[self.plot_groupby],
                                                    get_group_item_expression(group_value)))

                    _query = qry.get_ds_query('stats_query_' + self.time_aggregation_interval, self.traffic_type)
                    _df = fill_stat_df(_query, criteria_with_group)
                    st.table(_df)
                    st.markdown(tools.get_table_download_link(_df), unsafe_allow_html=True)
                else:
                    if self.result_type == 'Balkendiagramm':
                        _query = qry.get_ds_query('barchart_query_' + self.time_aggregation_interval, self.traffic_type)
                        if self.traffic_type == 1:
                            _df = fill_single_plot_df(_query, self.ypar, criteria_with_group)
                            _par = self.ypar
                            _y_ax_label = self.parameter_dic[self.ypar]
                        else:
                            _df = fill_single_plot_df(_query, 'total', criteria_with_group)
                            _par = self.parameter_dic[self.ypar]
                            _y_ax_label = _par
                            _df.rename(columns={'total': _par}, inplace=True)
                        show_barchart(title, _df, _par, _y_ax_label)
                    elif self.result_type == 'Karte':
                        _query = qry.get_ds_query('map_query_' + self.time_aggregation_interval, self.traffic_type)
                        _df = fill_single_plot_df(_query, self.ypar, criteria_with_group)
                        show_map(title=title, data=_df, val_par=self.ypar)
                    elif self.result_type == 'Zeitreihe':
                        _query = qry.get_ds_query('timeseries_query_' + self.time_aggregation_interval, self.traffic_type)
                        par = self.ypar if self.traffic_type == 1 else 'total'
                        _df = fill_single_map_df(_query, par, criteria_with_group)
                        show_time_series(title, _df, self.ypar)

        def get_criteria() -> str:
            criteria = ''
            _date_is_filtered = False
            if self.site_filter != 0:
                criteria = 'site_id = {}'.format(self.site_filter)
                if self.direction_filter != '0' and self.plot_groupby != 'site_id':
                    criteria += ' and direction_id = {}'.format(self.direction_filter)
                if self.lane_filter != 'Alle':
                    criteria += ' and lane_code = {}'.format(self.lane_filter)

            if self.date_filter != '':
                _date_is_filtered = True
                logical = '' if criteria == '' else ' and '
                criteria += f"{logical}date_from = '{self.date_filter}'".format()
            elif has_month_filter() and not _date_is_filtered:
                _date_is_filtered = True
                logical = '' if criteria == '' else ' and '
                criteria += f'{logical}`year_month` >= {self.month_from_filter}'
                criteria += f' and `year_month` <= {self.month_to_filter}'
            if self.time_from_filter != 0 or self.time_to_filter != 23:
                logical = '' if criteria == '' else ' and '
                criteria += f'{logical}`hour_from` >= {self.time_from_filter}'.format()
                criteria += f' and `hour_from` <= {self.time_to_filter}'
            if self.year_from_filter > self.year_list[0] and not _date_is_filtered:
                logical = '' if criteria == '' else ' and '
                criteria += f'{logical}`year_from` >= {self.year_from_filter}'
            if self.year_to_filter < self.year_list[-1] and not _date_is_filtered:
                logical = '' if criteria == '' else ' and '
                criteria += f' and `year_from` <= {self.year_to_filter}'
            if self.traffic_type == 2:
                logical = '' if criteria == '' else ' and '
                criteria += f'{logical}`traffic_type_id` = {self.ypar}'

            # make sure criteria holds a values, otherwise the where expression may generate an invalid query
            criteria = '1=1' if criteria == '' else criteria
            return criteria

        def show_barchart(title: str, data: pd.DataFrame, val_par: str, y_axis_title: str):
            tooltips = ['site_name', val_par] if 'site_name' in data.columns else []

            if self.yax_max == self.yax_min:
                scy = alt.Scale()
            else:
                scy = alt.Scale(domain=(self.yax_min, self.yax_max))
            bar = alt.Chart(data).mark_bar().encode(
                x=alt.X('{}:O'.format(self.marker_groupby),
                        sort=self.sort_dic[self.marker_groupby],
                        title=cn.group_by_dic[self.marker_groupby]),
                y=alt.Y('{}:Q'.format(val_par), title=y_axis_title, scale=scy),
                tooltip=tooltips
            )

            # not sure why the mean is sometime lower than the minimum bar mean
            # rule = alt.Chart(data).mark_rule(color='red').encode(
            # y='mean({}):Q'.format(val_par)
            chart = bar.properties(width=self.plot_width, height=self.plot_height, title=title)
            st.altair_chart(chart)
            tools.log('end barchart')

        def show_map(title: str, data: pd.DataFrame, val_par: str):
            """Drows a map plot using deckgl"""

            midpoint = (np.average(data['lon']), np.average(data['lat']))
            tooltip_html = f"Zählstelle: {{site_name}}</br>Durchschnitt ({val_par}): {{{val_par}}}"
            data = data.reset_index()
            if title != 'Alle':
                st.markdown(title)
            data['icon_data'] = None
            for i in data.index:
                data['icon_data'][i] = cn.icon_data
            layer = pdk.Layer(
                type='IconLayer',
                data=data,
                get_icon='icon_data',
                pickable=True,
                size_scale=20,
                get_position="[lon, lat]",
            )
            view_state = pdk.ViewState(
                longitude=midpoint[0], latitude=midpoint[1], zoom=11, min_zoom=1, max_zoom=100, pitch=0, bearing=0
            )
            r = pdk.Deck(
                map_style="mapbox://styles/mapbox/light-v10",
                layers=[layer],
                initial_view_state=view_state,
                tooltip={
                    "html": tooltip_html,
                    "style": {'fontSize': cn.TOOLTIP_FONTSIZE,
                              "backgroundColor": cn.TOOLTIP_BACKCOLOR,
                              "color": cn.TOOLTIP_FORECOLOR}
                }
            )
            st.pydeck_chart(r)

        def get_time_format(start_date, end_date):
            """
            Returns an appropriate date format to be shown on a time series plot axis. see:
            https://github.com/d3/d3-time-format#locale_format
            """

            td = end_date.to_pydatetime() - start_date.to_pydatetime()
            td_days = td.total_seconds() / (3600 * 24)
            if td_days < 3:
                return '%x %H:%M'
            elif td_days < 366:
                return "%x"
            elif td_days < 5 * 366:
                return "%m.%y"
            else:
                return "%y"

        def show_time_series(title: str, df: pd.DataFrame, par: str, y_lab: str):
            """
            Plots a time series plot. for time series plots the marker group by parameter is automatically set to the
            station.

            Parameters:
            -----------
            :param title:
            :param df:
            :param par:
            :return:
            """

            x_lab = ''
            df['time'] = pd.to_datetime(df['time'])
            min_dat = df['time'].min()
            max_dat = df['time'].max()
            time_format = get_time_format(min_dat, max_dat)
            if self.yax_max == self.yax_min:
                scy = alt.Scale()
            else:
                scy = alt.Scale(domain=(self.yax_min, self.yax_max))

            if self.moving_average_days > 0:
                line = alt.Chart(df, title=title).mark_line(point=False, clip=True
                                                            ).transform_window(
                    rolling_mean='mean({})'.format(par),
                    frame=[-self.moving_average_days / 2, self.moving_average_days]
                ).encode(
                    x=alt.X('time:T',
                            axis=alt.Axis(title=x_lab)),
                    # https://github.com/d3/d3-time-format#locale_format
                    y=alt.Y('rolling_mean:Q',
                            scale=scy,
                            axis=alt.Axis(title=y_lab)
                            ),
                    color=alt.Color('direction_id',
                                    scale=alt.Scale(scheme=cn.color_schema)
                                    ),
                )
            else:
                line = alt.Chart(df).mark_line(point=True, clip=True
                                               ).encode(
                    x=alt.X(f'time:T',
                            axis=alt.Axis(title=x_lab, labelAngle=30, format=time_format)),
                    y=alt.Y('{}:Q'.format(par),
                            scale=scy,
                            axis=alt.Axis(title=y_lab)
                            ),
                    color=alt.Color('direction_id',
                                    scale=alt.Scale(scheme=cn.color_schema)
                                    ),
                )

            points = alt.Chart(df).mark_point(
            ).encode(
                x=alt.X('time:T',
                        axis=alt.Axis(title=x_lab)),
                y=alt.Y('{}:Q'.format(par),
                        scale=scy,
                        axis=alt.Axis(title=y_lab)
                        ),
                color=alt.Color('direction_id',
                                scale=alt.Scale(scheme=cn.color_schema)
                                ),
                tooltip=['site_name', 'direction_id', 'time', par],
                opacity=alt.value(0.3)
            )
            chart = (points + line).properties(width=self.plot_width, height=self.plot_height, title=title)
            st.altair_chart(chart)
            # st.table(df)

        # --------------------------------------------------------------------------------------------------------------
        # main program
        # --------------------------------------------------------------------------------------------------------------

        if self.plot_groupby == 'none':
            show_single_result()
        else:
            show_grouped_result()
