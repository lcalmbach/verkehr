"""
This module contains the classes .
"""

__author__ = "lcalmbach@gmail.com"

import pandas as pd
import numpy as np
import locale

import altair as alt
import pydeck as pdk
import streamlit as st
from enum import Enum

import config as cn
import tools

class Traffic:

    @st.cache(suppress_st_warning=True)
    def read_data(self):
        tools.log('start reading')
        _df = pd.read_csv('merged.csv', sep=';', encoding='UTF8')
        _df['DateTimeFrom'] = pd.to_datetime(_df['DateTimeFrom'])
        _df['DateTimeTo'] = pd.to_datetime(_df['DateTimeTo'])
        _df['Date'] = pd.to_datetime(_df['Date']).dt.date
        tools.log('done reading')
        return _df

    def render_help(self):
        """Renders a help icon linking to the <read the docs> user manual"""

        st.sidebar.markdown(
            '<a href = "{}" target = "_blank"><img border="0" alt="Help" src="{}"></a>'.format(cn.USER_MANUAL_LINK,
                cn.HELP_ICON),
                unsafe_allow_html=True)

    def show_info(self, site_names: list, first_year: int):
        f = open("info.md", "r+", encoding='UTF8')
        text = f.read().format(len(site_names), first_year, tools.get_cs_item_list(cn.vehicule_type_list,
                                                                                separator=',', quote_string=''))
        st.markdown(text)

    def info_sidebar(self):
        """Renders the about text in the sideboard."""

        st.sidebar.subheader("About")
        text = """This app has been developed by [Lukas Calmbach](mailto:lcalmbach@gmail.com) using 
            [Python](https://www.python.org/), [Streamlit](https://streamlit.io/) and [Altair]
            (https://altair-viz.github.io/). All sourcecode is published on [github](https://github.com/lcalmbach/traffic).
            """
        st.sidebar.info(text)

class Stats:

    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.parameter = 'Total'
        self.site_filter = ''
        self.site_list, self.year_list = tools.get_lists(data)
        self.min_year = self.year_list[0]
        self.max_year = self.year_list[-1:][0]
        self.year_from_filter = self.min_year
        self.year_to_filter = self.max_year

    def render_controls(self):
        st.sidebar.markdown('---')
        self.parameter = st.sidebar.selectbox('Parameter', list(cn.parameter_dic.keys()),
                                             format_func=lambda x: cn.parameter_dic[x])

        st.sidebar.markdown('---')
        self.group_by = st.sidebar.selectbox('Gruppiere Tabellen nach', list(cn.group_by_dic.keys()),
                                                 format_func=lambda x: cn.group_by_dic[x])

        st.sidebar.markdown('---')
        #self.site_filter = st.sidebar.selectbox(label='Auswahl Zählstelle', index=1, options=['Alle', ] + self.site_list)
        [self.year_from_filter, self.year_to_filter] = st.sidebar.slider('Auswahl Jahr', min_value=self.year_list[0],
                                             max_value=self.year_list[-1:][0], value=[self.year_from_filter,
                                             self.year_to_filter])
#
    def filter_stats(self):
        if self.year_from_filter != self.min_year or self.year_to_filter != self.max_year:
            _df = self.data.loc[(self.data['Year'] >= self.year_from_filter) & (self.data['Year'] <= self.year_to_filter)]
        else:
            _df = self.data
        return _df

    @st.cache(suppress_st_warning=True)
    def get_stats(self, data: pd.DataFrame):
        #hourly stats
        _df_h = (data.assign(Total=data[self.parameter].abs()
            ).groupby(['SiteName'])[self.parameter].agg([('Durchschn. /Std.', 'mean'), ('Max. /Std', 'max')]))
        # daily stats
        _df_d = data[['SiteName', 'Date', self.parameter]]
        _df_d = _df_d.groupby(['SiteName', 'Date']).sum()
        #df_d = _df_d[['SiteName', self.parameter]]
        #df_d.set_index(['SiteName'])
        _df_d = (_df_d.assign(Total=_df_d[self.parameter].abs()
                           ).groupby(['SiteName'])[self.parameter].agg([('Min. /Tag', 'min'),
                                                                 ('Max. /Tag', 'max')]))
        # merge stats
        _df_dh = pd.merge(_df_h, _df_d, on='SiteName').sort_values(by=['SiteName'], ascending=True).reset_index()
        return _df_dh

    def show_stats(self):
        if self.group_by == 'keine':
            self.show_single_table()
        else:
            self.show_grouped_tables()

    def show_single_table(self):
        st.markdown('## Anzahl Fahrzeuge an Zählstelle')
        subtitle = '{}'.format(self.year_from_filter) if self.year_from_filter == self.year_to_filter \
            else '{} - {}'.format(self.year_from_filter, self.year_to_filter)
        subtitle += ', Fahrzeugtyp: {}'.format(cn.parameter_dic[self.parameter])
        st.markdown(subtitle)
        _df = self.filter_stats()
        _df = self.get_stats(_df)
        st.table(_df)
        st.markdown(tools.get_table_download_link(_df), unsafe_allow_html=True)

    def show_grouped_tables(self):
        st.markdown('## Anzahl Fahrzeuge an Zählstelle')
        subtitle = '{}'.format(self.year_from_filter) if self.year_from_filter == self.year_to_filter \
            else '{} - {}'.format(self.year_from_filter, self.year_to_filter)
        subtitle += ', Fahrzeugtyp: {}'.format(cn.parameter_dic[self.parameter])
        st.markdown(subtitle)
        _df = self.filter_stats()
        _list = tools.get_unique_values(_df, self.group_by)
        for item in _list:
            _df_group = self.data.loc[(self.data[self.group_by] == item)]
            _df_group = self.get_stats(_df_group)
            st.table(_df)
            st.markdown(tools.get_table_download_link(_df_group), unsafe_allow_html=True)




###############################################################################
class TimeSeriesPlot:
    """This class is used to generate plots and render plot related UI controls"""

    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.marker_group_by = ''
        self.plot_groupby = ''
        self.marker_groupby = 'SiteName'
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
        self.site_filter = []
        self.lane_filter = []
        self.direction_filter = []
        self.time_filter = 'Alle'
        self.time_aggregation_interval = 'Date'

        self.site_list, self.year_list = tools.get_lists(data)

    def plot(self):
        self.render_group_by_controls()
        self.render_axis_controls()
        self.render_filter_controls()

        _df = self.filter_data(self.data)
        if self.plot_groupby == 'none':
            self.render_single_plot(_df)
        elif self.marker_groupby == 'Fahrzeugtyp':
            self.render_vehicle_type_plot_group(_df)
        else:
            self.render_attribute_plot_group(_df)

    def render_single_plot(self, df):
        title = self.site_filter
        df = self.prepare_data(df, self.ypar)
        self.render_plot(title, df, self.ypar, self.marker_groupby)

    def render_attribute_plot_group(self, df):
        _lis = df[self.marker_groupby].unique().tolist()
        for _group in _lis:
            df_grp_data = df.loc[(df[self.plot_groupby] == _group)]
            title = self.site_filter
            self.render_plot(title, df_grp_data, self.ypar, self.marker_groupby)

    def filter_data(self, data):
        if self.site_filter != 'Alle':
            df = data.loc[(data['SiteName'] == self.site_filter)]
        else:
            df = data
        if self.direction_filter != 'Alle':
            df = df.loc[(df['DirectionName'] == self.direction_filter)]
        if self.time_filter != 'Alle':
            df = df.loc[(df['Year'] == self.time_filter)]
        return df

    def prepare_data(self, data: pd.DataFrame, par: str):
        if self.marker_groupby == 'Fahrzeugtyp':
            return data
        elif self.marker_groupby == 'none':
            df = data[['SiteName', self.time_aggregation_interval, par]]
            df = df.groupby(['SiteName', self.time_aggregation_interval, self.marker_groupby]).sum().reset_index()
            df[self.time_aggregation_interval] = pd.to_datetime(df[self.time_aggregation_interval])
        else:
            df = data[['SiteName', self.time_aggregation_interval, self.marker_groupby, par]]
            df = df.groupby(['SiteName', self.time_aggregation_interval, self.marker_groupby]).sum().reset_index()
        df[self.time_aggregation_interval] = pd.to_datetime(df[self.time_aggregation_interval])
        df.sort_values(by=['SiteName', self.time_aggregation_interval])
        return df

    def render_plot(self, title: str, df: pd.DataFrame, par: str, marker_par: str) -> list:
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
        y_lab = par
        if self.yax_max == self.yax_min:
            scy = alt.Scale()
        else:
            scy = alt.Scale(domain=(self.yax_min, self.yax_max))

        line = alt.Chart(df, title=title).mark_line(point=False, clip=True
                                                    ).transform_window(
            rolling_mean='mean({})'.format(par),
            frame=[-15, 15]
        ).encode(
            x=alt.X('{}:T'.format(self.time_aggregation_interval),
                    axis=alt.Axis(title=x_lab)),
            y=alt.Y('rolling_mean:Q',
                    scale=scy,
                    axis=alt.Axis(title=y_lab)
                    ),
            color=alt.Color(marker_par,
                            scale=alt.Scale(scheme=cn.color_schema)
                            ),
        )
        points = alt.Chart(df).mark_point(
        ).encode(
            x=alt.X('{}:T'.format(self.time_aggregation_interval),
                    axis=alt.Axis(title=x_lab)),
            y=alt.Y('{}:Q'.format(par),
                    scale=scy,
                    axis=alt.Axis(title=y_lab)
                    ),
            color=alt.Color(marker_par,
                            scale=alt.Scale(scheme=cn.color_schema)
                            ),
            tooltip=[cn.STATION_NAME_COLUMN, 'DirectionName', self.time_aggregation_interval, par],
            opacity=alt.value(0.3)
        )
        chart = (points + line).properties(width=self.plot_width, height=self.plot_height, title=title)
        st.altair_chart(chart)

    def render_group_by_controls(self):
        """Group by controls for plots and markers"""

        st.sidebar.markdown('---')
        st.sidebar.markdown('#### Gruppierung von Plots und Symbolen')
        self.plot_groupby = st.sidebar.selectbox('Gruppiere Grafiken nach', list(cn.group_by_dic.keys()),
                                                 format_func=lambda x: cn.group_by_dic[x])
        self.marker_groupby = st.sidebar.selectbox('Gruppiere Symbole nach', index=6,
                                                   options=list(cn.group_by_dic.keys()),
                                                   format_func=lambda x: cn.group_by_dic[x])

    def render_axis_controls(self):

        st.sidebar.markdown('---')
        st.sidebar.markdown('#### Y Achse')
        if self.plot_groupby != 'Fahrzeugtyp':
            self.ypar = st.sidebar.selectbox('Parameter', list(cn.parameter_dic.keys()),
                                             format_func=lambda x: cn.parameter_dic[x])
        self.define_axis_length = st.sidebar.checkbox('Define axis length', value=False)
        if self.define_axis_length:
            self.plot_width = st.sidebar.number_input('Width (pixel)', value=self.plot_width)
            self.plot_height = st.sidebar.number_input('Height (pixel)', value=self.plot_height)

        # self.__show_data_table = st.sidebar.checkbox('Show data table', value=False, key=None)

        self.time_aggregation_interval = st.sidebar.selectbox('Zeitliche Aggregation der Messungen',
                                                              list(cn.time_aggregation_dic.keys()),
                                                              format_func=lambda x: cn.time_aggregation_dic[x])

    def render_filter_controls(self):

        st.sidebar.markdown('---')
        st.sidebar.markdown('#### Filter')
        self.site_filter = st.sidebar.selectbox(label='Zählstelle', index=1, options=['Alle', ] + self.site_list)
        if self.site_filter != 'Alle':
            _lst = tools.get_metadata_list_for_site(self.data, self.site_filter, 'LaneName')
            self.lane_filter = st.sidebar.selectbox('Spur', index=0, options=['Alle', ] + _lst)
            _lst = tools.get_metadata_list_for_site(self.data, self.site_filter, 'DirectionName')
            self.direction_filter = st.sidebar.selectbox('Richtung', index=0, options=['Alle', ] + _lst)

        _lst = ['Alle', ] + self.year_list + ['Gestern', 'Letzte Woche', 'Letzter Monat']
        self.time_filter = st.sidebar.selectbox('Zeitliche Einschränkung', index=0, options=_lst)

###############################################################################
class Map:
    """This class is used to generate maps."""

    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.marker_group_by = ''
        self.plot_groupby = ''
        self.marker_groupby = 'SiteName'
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
        self.site_filter = []
        self.lane_filter = []
        self.direction_filter = []
        self.time_filter = 'Alle'
        self.time_aggregation_interval = 'Date'

        self.site_list, self.year_list = tools.get_lists(data)

    def plot(self):
        self.render_group_by_controls()
        self.render_axis_controls()
        self.render_filter_controls()

        _df = self.filter_data(self.data)
        if self.plot_groupby == 'none':
            self.render_single_plot(_df)
        elif self.marker_groupby == 'Fahrzeugtyp':
            self.render_vehicle_type_plot_group(_df)
        else:
            self.render_attribute_plot_group(_df)

    def render_single_plot(self, df):
        title = self.site_filter
        df = self.prepare_data(df, self.ypar)
        self.render_plot(title, df, self.ypar, self.marker_groupby)

    def render_attribute_plot_group(self, df):
        _lis = df[self.marker_groupby].unique().tolist()
        for _group in _lis:
            df_grp_data = df.loc[(df[self.plot_groupby] == _group)]
            title = self.site_filter
            self.render_plot(title, df_grp_data, self.ypar, self.marker_groupby)

    def filter_data(self, data):
        if self.site_filter != 'Alle':
            df = data.loc[(data['SiteName'] == self.site_filter)]
        else:
            df = data
        if self.direction_filter != 'Alle':
            df = df.loc[(df['DirectionName'] == self.direction_filter)]
        if self.time_filter != 'Alle':
            df = df.loc[(df['Year'] == self.time_filter)]
        return df

    def prepare_data(self, data: pd.DataFrame, par: str):
        if self.marker_groupby == 'Fahrzeugtyp':
            return data
        elif self.marker_groupby == 'none':
            df = data[['SiteName', self.time_aggregation_interval, par]]
            df = df.groupby(['SiteName', self.time_aggregation_interval, self.marker_groupby]).sum().reset_index()
            df[self.time_aggregation_interval] = pd.to_datetime(df[self.time_aggregation_interval])
        else:
            df = data[['SiteName', self.time_aggregation_interval, self.marker_groupby, par]]
            df = df.groupby(['SiteName', self.time_aggregation_interval, self.marker_groupby]).sum().reset_index()
        df[self.time_aggregation_interval] = pd.to_datetime(df[self.time_aggregation_interval])
        df.sort_values(by=['SiteName', self.time_aggregation_interval])
        return df

    def render_plot(self, title: str, df: pd.DataFrame, par: str, marker_par: str) -> list:
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
        y_lab = par
        if self.yax_max == self.yax_min:
            scy = alt.Scale()
        else:
            scy = alt.Scale(domain=(self.yax_min, self.yax_max))

        line = alt.Chart(df, title=title).mark_line(point=False, clip=True
                                                    ).transform_window(
            rolling_mean='mean({})'.format(par),
            frame=[-15, 15]
        ).encode(
            x=alt.X('{}:T'.format(self.time_aggregation_interval),
                    axis=alt.Axis(title=x_lab)),
            y=alt.Y('rolling_mean:Q',
                    scale=scy,
                    axis=alt.Axis(title=y_lab)
                    ),
            color=alt.Color(marker_par,
                            scale=alt.Scale(scheme=cn.color_schema)
                            ),
        )
        points = alt.Chart(df).mark_point(
        ).encode(
            x=alt.X('{}:T'.format(self.time_aggregation_interval),
                    axis=alt.Axis(title=x_lab)),
            y=alt.Y('{}:Q'.format(par),
                    scale=scy,
                    axis=alt.Axis(title=y_lab)
                    ),
            color=alt.Color(marker_par,
                            scale=alt.Scale(scheme=cn.color_schema)
                            ),
            tooltip=[cn.STATION_NAME_COLUMN, 'DirectionName', self.time_aggregation_interval, par],
            opacity=alt.value(0.3)
        )
        chart = (points + line).properties(width=self.plot_width, height=self.plot_height, title=title)
        st.altair_chart(chart)

    def render_group_by_controls(self):
        """Group by controls for plots and markers"""

        st.sidebar.markdown('---')
        st.sidebar.markdown('#### Gruppierung von Plots und Symbolen')
        self.plot_groupby = st.sidebar.selectbox('Gruppiere Grafiken nach', list(cn.group_by_dic.keys()),
                                                 format_func=lambda x: cn.group_by_dic[x])
        self.marker_groupby = st.sidebar.selectbox('Gruppiere Symbole nach', index=6,
                                                   options=list(cn.group_by_dic.keys()),
                                                   format_func=lambda x: cn.group_by_dic[x])

    def render_axis_controls(self):

        st.sidebar.markdown('---')
        st.sidebar.markdown('#### Y Achse')
        if self.plot_groupby != 'Fahrzeugtyp':
            self.ypar = st.sidebar.selectbox('Parameter', list(cn.parameter_dic.keys()),
                                             format_func=lambda x: cn.parameter_dic[x])
        self.define_axis_length = st.sidebar.checkbox('Define axis length', value=False)
        if self.define_axis_length:
            self.plot_width = st.sidebar.number_input('Width (pixel)', value=self.plot_width)
            self.plot_height = st.sidebar.number_input('Height (pixel)', value=self.plot_height)

        # self.__show_data_table = st.sidebar.checkbox('Show data table', value=False, key=None)

        self.time_aggregation_interval = st.sidebar.selectbox('Zeitliche Aggregation der Messungen',
                                                              list(cn.time_aggregation_dic.keys()),
                                                              format_func=lambda x: cn.time_aggregation_dic[x])

    def render_filter_controls(self):

        st.sidebar.markdown('---')
        st.sidebar.markdown('#### Filter')
        self.site_filter = st.sidebar.selectbox(label='Zählstelle', index=1, options=['Alle', ] + self.site_list)
        if self.site_filter != 'Alle':
            _lst = tools.get_metadata_list_for_site(self.data, self.site_filter, 'LaneName')
            self.lane_filter = st.sidebar.selectbox('Spur', index=0, options=['Alle', ] + _lst)
            _lst = tools.get_metadata_list_for_site(self.data, self.site_filter, 'DirectionName')
            self.direction_filter = st.sidebar.selectbox('Richtung', index=0, options=['Alle', ] + _lst)

        _lst = ['Alle', ] + self.year_list + ['Gestern', 'Letzte Woche', 'Letzter Monat']
        self.time_filter = st.sidebar.selectbox('Zeitliche Einschränkung', index=0, options=_lst)

###############################################################################

class BarChart:
    """This class is used to generate plots and render plot related UI controls"""

    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.marker_group_by = ''
        self.plot_groupby = ''
        self.marker_groupby = 'SiteName'
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
        self.site_filter = []
        self.lane_filter = []
        self.direction_filter = []
        self.time_filter = 'Alle'
        self.time_aggregation_interval = 'Date'

        self.site_list, self.year_list = tools.get_lists(data)

    def plot(self):
        self.render_group_by_controls()
        self.render_axis_controls()
        self.render_filter_controls()

        _df = self.filter_data(self.data)
        if self.plot_groupby == 'none':
            self.render_single_plot(_df)
        elif self.marker_groupby == 'Fahrzeugtyp':
            self.render_vehicle_type_plot_group(_df)
        else:
            self.render_attribute_plot_group(_df)

    def render_single_plot(self, df):
        title = self.site_filter
        df = self.prepare_data(df, self.ypar)
        self.render_plot(title, df, self.ypar, self.marker_groupby)

    def render_attribute_plot_group(self, df):
        _lis = df[self.plot_groupby].unique().tolist()
        for _group in _lis:
            df_grp_data = df.loc[(df[self.plot_groupby] == _group)]
            title = "{}, {}".format(self.site_filter, _group)
            self.render_plot(title, data=df_grp_data, val_par=self.ypar, marker_par=self.marker_groupby)

    def filter_data(self, data):
        if self.site_filter != 'Alle':
            df = data.loc[(data['SiteName'] == self.site_filter)]
        else:
            df = data
        if self.direction_filter != 'Alle':
            df = df.loc[(df['DirectionName'] == self.direction_filter)]
        if self.time_filter != 'Alle':
            df = df.loc[(df['Year'] == self.time_filter)]
        return df

    def prepare_data(self, data: pd.DataFrame, par: str):
        if self.marker_groupby == 'Fahrzeugtyp':
            return data
        elif self.marker_groupby == 'none':
            df = data[['SiteName', self.time_aggregation_interval, par]]
            df = df.groupby(['SiteName', self.time_aggregation_interval, self.marker_groupby]).sum().reset_index()
            df[self.time_aggregation_interval] = pd.to_datetime(df[self.time_aggregation_interval])
        else:
            df = data[['SiteName', self.time_aggregation_interval, self.marker_groupby, par]]
            df = df.groupby(['SiteName', self.time_aggregation_interval, self.marker_groupby]).sum().reset_index()
        df[self.time_aggregation_interval] = pd.to_datetime(df[self.time_aggregation_interval])
        df.sort_values(by=['SiteName', self.time_aggregation_interval])
        return df

    def render_plot(self, title: str, data: pd.DataFrame, val_par: str, marker_par: str):
        tooltips = ['SiteName', val_par]
        tooltips = tooltips + ['DirectionName',] + tooltips if self.direction_filter != 'Alle' else tooltips
        tooltips = tooltips + ['LaneName', ] + tooltips if self.lane_filter != 'Alle' else tooltips
        bar = alt.Chart(data).mark_bar().encode(
            x='{}:O'.format(marker_par),
            y='{}:Q'.format(val_par),
            tooltip=tooltips
        )
        # not sure why the mean is sometime lower than the minimum bar mean
        # rule = alt.Chart(data).mark_rule(color='red').encode(
        # y='mean({}):Q'.format(val_par)
        #)

        chart = bar.properties(width=self.plot_width, height=self.plot_height, title=title)
        st.altair_chart(chart)

    def render_group_by_controls(self):
        """Group by controls for plots and markers"""

        st.sidebar.markdown('---')
        st.sidebar.markdown('#### Gruppierung von Plots und Symbolen')
        self.plot_groupby = st.sidebar.selectbox('Gruppiere Grafiken nach', list(cn.group_by_dic.keys()),
                                                 format_func=lambda x: cn.group_by_dic[x])
        self.marker_groupby = st.sidebar.selectbox('Gruppiere Symbole nach', index=6,
                                                   options=list(cn.group_by_dic.keys()),
                                                   format_func=lambda x: cn.group_by_dic[x])

    def render_axis_controls(self):

        st.sidebar.markdown('---')
        st.sidebar.markdown('#### Y Achse')
        if self.plot_groupby != 'Fahrzeugtyp':
            self.ypar = st.sidebar.selectbox('Parameter', list(cn.parameter_dic.keys()),
                                             format_func=lambda x: cn.parameter_dic[x])
        self.define_axis_length = st.sidebar.checkbox('Define axis length', value=False)
        if self.define_axis_length:
            self.plot_width = st.sidebar.number_input('Width (pixel)', value=self.plot_width)
            self.plot_height = st.sidebar.number_input('Height (pixel)', value=self.plot_height)

        # self.__show_data_table = st.sidebar.checkbox('Show data table', value=False, key=None)

        self.time_aggregation_interval = st.sidebar.selectbox('Zeitliche Aggregation der Messungen',
                                                              list(cn.time_aggregation_dic.keys()),
                                                              format_func=lambda x: cn.time_aggregation_dic[x])

    def render_filter_controls(self):

        st.sidebar.markdown('---')
        st.sidebar.markdown('#### Filter')
        self.site_filter = st.sidebar.selectbox(label='Zählstelle', index=1, options=['Alle', ] + self.site_list)
        if self.site_filter != 'Alle':
            _lst = tools.get_metadata_list_for_site(self.data, self.site_filter, 'LaneName')
            self.lane_filter = st.sidebar.selectbox('Spur', index=0, options=['Alle', ] + _lst)
            _lst = tools.get_metadata_list_for_site(self.data, self.site_filter, 'DirectionName')
            self.direction_filter = st.sidebar.selectbox('Richtung', index=0, options=['Alle', ] + _lst)

        _lst = ['Alle', ] + self.year_list + ['Gestern', 'Letzte Woche', 'Letzter Monat']
        self.time_filter = st.sidebar.selectbox('Zeitliche Einschränkung', index=0, options=_lst)
