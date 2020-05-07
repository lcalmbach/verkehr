# make sure all stations have a code
update slow_traffic_source set sitecode = left(sitename,3) where sitecode is null and left(sitename,3) REGEXP '^[0-9]';

insert into station_lookup_code(category_id, site_id, `code`)
select distinct 2,t2.id,t1.directionName
from slow_traffic_source t1
inner join site t2 on t2.site_code = t1.siteCode;

	update 
		slow_traffic_source t1 
		inner join slow_traffic t2 on t2.`index` = t1.`index`
		inner join station_lookup_code t3 on t3.site_id = t2.site_id and t3.code = t1.DirectionName and t3.category_id = 2 
	set 
		t2.direction_id = t3.id;
