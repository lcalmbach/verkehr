import streamlit as st
import pandas as pd
import altair as alt
import pydeck as pdk
import numpy as np
import traffic
import config as cn
import tools


def show_plot_menu(data):
    value_par = st.sidebar.selectbox("Fahrzeugtyp", index=0, options=value_fields)
    marker_par = st.sidebar.selectbox("Zeitliche Aggregierung X-Achse", index=0, options=time_aggregations)

    st.sidebar.markdown("## Gruppierung")
    plot_groupby = st.sidebar.selectbox("Gruppiere Grafiken nach",
                                        index=0, options=['keine', ] + time_aggregations)

    st.sidebar.markdown("## Filter")
    site_name = st.sidebar.selectbox("Wähle eine Messstelle", index=0, options=site_names)
    year = st.sidebar.selectbox("Wähle ein Jahr", index=0, options=['Alle'] + years)
    monat = st.sidebar.selectbox("Wähle einen Monat", index=0, options=months)
    day = st.sidebar.selectbox("Wähle einen Tag", index=0, options=days)
    hour = st.sidebar.selectbox("Wähle eine Zeit", index=0, options=time_intervals)

    if plot_type == 'Balkendiagramm':
        if plot_groupby == 'keine':
            df = data.loc[(data['SiteName'] == site_name) & (data[value_par] >= 0)]
            df = df[[value_par, marker_par]]
            df = df.groupby(marker_par).mean().reset_index()
            plot_barchart(df, value_par, marker_par, site_name)
        else:
            for group in data[plot_groupby].unique().tolist():
                df = data.loc[(data[plot_groupby] == group) & (data[value_par] >= 0)]
                df = df[[value_par, marker_par]]
                df = df.groupby(marker_par).mean().reset_index()
                plot_barchart(df, value_par, marker_par, str(group))
    elif plot_type == 'Karte':
        _title = '## Total Fahrzeuge an Zählstellen pro Tag, Monat = Jan 2020 (in Tsd)'
        df = data.loc[(data['SiteName'] == site_name) & (data[value_par] >= 0)]
        plot_map(df, value_par, marker_par, _title)





def plot_map(_data: pd.DataFrame, val_par: str, agg_par: str, title: str):
    midpoint = (np.average(_data['BREITENGR']), np.average(_data['LAENGENGR']))
    _data = data.loc[(data['Year'] == 2020) & (data['Month'] == 1)]
    _data = (_data.assign(Total=data['Total'].abs())
             .groupby(['SiteName', 'BREITENGR', 'LAENGENGR'])['Total'].agg([('Anz_pro_Tag_Tsd', 'sum')])
             )
    _data['Anz_pro_Tag_Tsd'] = _data['Anz_pro_Tag_Tsd'] / 31000
    _data = _data.reset_index()
    st.markdown(title)
    layer = pdk.Layer(
        'HexagonLayer',
        _data,
        get_position="[LAENGENGR, BREITENGR]",
        auto_highlight=True,
        elevation_scale=100,
        pickable=True,
        elevation_range=[0, 50],
        extruded=True,
        coverage=0.15,
    )
    view_state = pdk.ViewState(
        longitude=midpoint[1], latitude=midpoint[0], zoom=11, min_zoom=1, max_zoom=100, pitch=30, bearing=-40
    )
    r = pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v10",
        layers=[layer],
        initial_view_state=view_state,
        tooltip={
            "html": "<b>Value:</b> {Anz_pro_Tag_Tsd} <br/><b>Zählstelle:</b> {SiteName} <br/>",
            "style": {
                "backgroundColor": "steelblue",
                "color": "white"}
        }
    )
    st.pydeck_chart(r)
    st.table(_data)


tr = traffic.Traffic()
data = tr.read_data()
stats = traffic.Stats(data)
st.sidebar.markdown('# <span style="color:steelblue">Verkehrszählung</span>', unsafe_allow_html=True)
menu = st.sidebar.radio(label='', index=0, options=cn.menu_list)

if menu == 'Info Datensatz':
    site_names, years = tools.get_lists(data)
    tr.show_info(site_names, min(years))
    tr.info_sidebar()
elif menu == 'Statistik':
    stats.render_controls()
    stats.show_stats()
elif menu == 'Grafiken':
    plot_type = st.sidebar.selectbox("Grafik-Typ", index=0, options=cn.plot_type_list)
    if plot_type == 'Zeitreihe':
        chart = traffic.TimeSeriesPlot(data)
        chart.plot()
    elif plot_type == 'Karte':
        chart = traffic.Map(data)
        chart.plot()
    elif plot_type == 'Balkendiagramm':
        chart = traffic.BarChart(data)
        chart.plot()
tr.render_help()
