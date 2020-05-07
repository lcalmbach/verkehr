truncate table `traffic`.`miv`;
INSERT INTO `traffic`.`miv`
(`index`,
`site_code`,
`lane_code`,
`values_approved`,
`values_edited`,
`total`,
`mr`,
`pw`,
`pw0`,
`lief`,
`lief0`,
`lief_aufl`,
`lw`,
`lw0`,
`sattelzug`,
`bus`,
`andere`,
`date_time_from`)
select
	`index`,
    `sitecode`,
    `lanecode`,
    `valuesapproved`,
    `valuesedited`,
    `total`,
    `mr`,
    `pw`,
    `pw+`,
    `lief`,
    `lief+`,
    `lief+aufl.`,
    `lw`,
    `lw+`,
    `sattelzug`,
    `bus`,
    `andere`,
    replace(DateTimeFrom,'+00:00','')
from traffic_source;

update traffic t1 inner join station_lookup_code t2 on t2.site_id = t1.site_id and t2.category_id = 2
set t1.direction_id = t2.id;

update traffic set 
	hour_from = hour(date_time_from)
    , day_from = day(date_time_from)
    , month_from = month(date_time_from)
    , year_from = year(date_time_from)
    , weekday_from = weekday(date_time_from)
    , date_from = date_time_from;

update traffic set `year_month` = 100 * year_from + month_from;
    
update traffic t1 inner join traffic_station t2 on t2.SiteCode = t1.site_code
set t1.site_id = t2.id;