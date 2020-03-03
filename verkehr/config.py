
def get_time_intervals():
    _time_intervals = ['Alle']
    for i in range(23):
        ll = '{:0>2}'.format(i)
        ul = '{:0>2}'.format(i + 1)
        _time_intervals.append('{} - {}'.format(ll, ul))
    _time_intervals.append('{} - {}'.format('23', '00'))
    return _time_intervals


weekday_long_dic = {0: 'Montag', 1: 'Dienstag', 2: 'Mittwoch', 3: 'Donnerstag', 4: 'Freitag', 5: 'Sammstag',
                    6: 'Sonntag'}
weekday_short_dic = {0: 'Mo', 1: 'Di', 2: 'Mi', 3: 'Do', 4: 'Fr', 5: 'Sa', 6: 'So'}
month_short_dic = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'Mai', 6: 'Jun', 7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Okt',
                   11: 'Nov', 12: 'Dez'}
month_long_dic = {1: 'Januar', 2: 'Februar', 3: 'März', 4: 'April', 5: 'Mai', 6: 'Juni', 7: 'Juli', 8: 'August',
                  9: 'September', 10: 'Oktober', 11: 'November', 12: 'Dezember'}
group_by_dic = {'none': 'keine', 'Year': 'Jahr', 'Month': 'Monat', 'SiteName': 'Zählstelle', 'Weekday': 'Wochentag',
                'DirectionName': 'Fahrtrichtung'}
parameter_dic = {'Total': 'Total', 'MR': 'Motorrad', 'PW': 'Personenwagen', 'PW+': 'Personenwagen mit Anhänger',
                 'Lief': 'Lieferwagen','Lief+': 'Lieferwagen mit Anhänger', 'Lief+ufl': 'Lieferwagen mit Auflieger',
                 'LW': 'Lastwagen', 'LW+': 'Lastwagen mit Anhänger', 'Sattelzug': 'Sattelzug', 'Bus': 'Bus',
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

