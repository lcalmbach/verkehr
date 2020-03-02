
def get_time_intervals():
    _time_intervals = ['Alle']
    for i in range(23):
        ll = '{:0>2}'.format(i)
        ul = '{:0>2}'.format(i + 1)
        _time_intervals.append('{} - {}'.format(ll, ul))
    _time_intervals.append('{} - {}'.format('23', '00'))
    return _time_intervals

group_by_dic = {'none': 'keine', 'Year': 'Jahr', 'Month': 'Monat', 'SiteName': 'Zählstelle', 'Weekday': 'Wochentag',
                'Fahrzeugtyp':'Fahrzeugtyp', 'DirectionName':'Fahrtrichtung'}
parameter_dic = {'Total': 'Total', 'MR': 'Motorrad', 'PW': 'Personenwagen', 'PW0': 'Personenwagen mit Anhänger',
                 'Lief': 'Lieferwagen','Lief0': 'Lieferwagen mit Anhänger', 'Lief0Aufl': 'Lieferwagen mit Auflieger',
                 'LW': 'Lastwagen', 'LW0': 'Lastwagen mit Anhänger', 'Sattelzug': 'Sattelzug', 'Bus': 'Bus',
                 'andere': 'andere'}
vehicule_type_list = ['Motorrad', 'Personenwagen', 'Personenwagen mit Anhänger', 'Lieferwagen',
                      'Lieferwagen mit Anhänger', 'Lieferwagen mit Auflieger', 'Lastwagen', 'Lastwagen mit Anhänger',
                      'Sattelzug', 'Bus', 'andere']
time_aggregation_dic = {'Date': 'Tag', 'DateTimeFrom': 'Stunde'}
plot_type_list = ['Balkendiagramm', 'Karte', 'Zeitreihe']
menu_list = ['Info Datensatz', 'Statistik', 'Grafiken']
months_list = ['Alle', 'Jan', 'Feb', 'Mrz', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez']
days_list = ['Alle', 'Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So']
time_intervals_list = get_time_intervals()
def_plot_width = 800
def_plot_height = 400
STATION_NAME_COLUMN = 'SiteName'
color_schema = "set1"  # https://vega.github.io/vega/docs/schemes/#reference
symbol_size = 60
date_time_column = 'DateTimeFrom'
USER_MANUAL_LINK: str = 'https://verkehr.readthedocs.io/de/latest/'
HELP_ICON: str = 'https://img.icons8.com/offices/30/000000/help.png'

