import tools

weekday_long_dic = {0: 'Montag', 1: 'Dienstag', 2: 'Mittwoch', 3: 'Donnerstag', 4: 'Freitag', 5: 'Samstag',
                    6: 'Sonntag'}
weekday_short_dic = {0: 'Mo', 1: 'Di', 2: 'Mi', 3: 'Do', 4: 'Fr', 5: 'Sa', 6: 'So'}
weekday_short_list = list(weekday_short_dic.values())

weekday_long_list = list(weekday_long_dic.values())
time_dic = {0: '00-01h', 1: '01-02h', 2: '02-03h', 3: '03-04h', 4: '04-05h', 5: '05-06h', 6: '06-07h', 7: '07-08h',
            8: '08-09h', 9: '09-10h', 10: '10-11h', 11: '11-12h',
            12: '12-13h', 13: '13-14h', 14: '14-15h', 15: '15-16h', 16: '16-17h', 17: '17-18h', 18: '18-19h',
            19: '19-20h', 20: '20-21h', 21: '21-22h', 22: '22-23h', 23: '23-00h'}

month_short_dic = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'Mai', 6: 'Jun', 7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Okt',
                   11: 'Nov', 12: 'Dez'}
month_long_dic = {1: 'Januar', 2: 'Februar', 3: 'März', 4: 'April', 5: 'Mai', 6: 'Juni', 7: 'Juli', 8: 'August',
                  9: 'September', 10: 'Oktober', 11: 'November', 12: 'Dezember'}
group_by_dic = {'none': 'keine', 'year_from': 'Jahr', 'month_from': 'Monat', 'weekday_from': 'Wochentag',
                'direction_id': 'Fahrtrichtung', 'hour_from': 'Tageszeit', 'site_id': 'Zählstelle',
                'week_of_year': 'Kalenderwoche'}
traffic_type_dic = {1: 'Motorisierter Individualverkehr', 2: 'Langsamverkehr'}
parameter_dic = {
                1: {'Total': 'Alle Fahrzeugtypen', 'MR': 'Motorrad', 'PW': 'Personenwagen',
                  'PW0': 'Personenwagen mit Anhänger',
                 'Lief': 'Lieferwagen', 'Lief0': 'Lieferwagen mit Anhänger', 'LW': 'Lastwagen',
                  'LW0': 'Lastwagen mit Anhänger', 'Sattelzug': 'Sattelzug', 'Bus': 'Bus', 'andere': 'andere'},
                2: {1: 'Fussgänger', 2: 'Fahrräder'}
                }
TRAFFIC_TYPE_MIV = 1
TRAFFIC_TYPE_LV = 2
time_aggregation_dic = {'day': 'pro Tag', 'hour': 'pro Stunde'}
plot_type_list = ['Balkendiagramm', 'Karte', 'Zeitreihe']
menu_list = ['Info Datensatz', 'Statistik', 'Grafiken']
months_list = ['Alle', 'Jan', 'Feb', 'Mrz', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez']
days_list = ['Alle', 'Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So']
time_intervals_list = tools.get_time_intervals()
def_plot_width = 800
def_plot_height = 400
STATION_NAME_COLUMN = 'SiteName'
color_schema = "set1"  # https://vega.github.io/vega/docs/schemes/#reference
color_schema_alt = "tableau10"  # https://vega.github.io/vega/docs/schemes/#reference
symbol_size = 60
date_time_column = 'DateTimeFrom'
USER_MANUAL_LINK: str = 'https://verkehr.readthedocs.io/de/latest/'
HELP_ICON: str = 'https://img.icons8.com/offices/30/000000/help.png'

# sql queries
source_miv_file_name = 'https://data-bs.ch/mobilitaet/2020_MIV_Class_10_1.csv'
source_slow_file_name = 'https://data-bs.ch/mobilitaet/2020_Velo_Fuss_Count.csv'

TOOLTIP_FONTSIZE = 'x-small'
TOOLTIP_BACKCOLOR = 'white'
TOOLTIP_FORECOLOR = 'black'

icon_data = {
            "url": "https://img.icons8.com/plasticine/100/000000/marker.png",
            "width": 128,
            "height": 128,
            "anchorY": 128
            }
