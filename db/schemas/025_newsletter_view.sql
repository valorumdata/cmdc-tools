DROP VIEW IF EXISTS meta.us_covid_variable_start_date;

CREATE OR REPLACE VIEW meta.us_covid_variable_start_date as
with active_variables as (
    SELECT distinct on (fips, variable_id) fips, variable_id
    from data.us_covid
    where vintage >= current_date - '1 week'::INTERVAL),
     loc_var_start_date as (
         select fips, variable_id, min(vintage) as start_date
         from data.us_covid
                  inner join active_variables using (fips, variable_id)
         group by fips, variable_id
     )

select uf.fips, uf.fullname, state.name as state, cv.name as variable_name, start_date, src.source as source
from loc_var_start_date sd
         left join meta.covid_variables cv on cv.id = variable_id
         left join meta.us_fips uf on uf.fips = sd.fips
         left join meta.us_fips state on state.fips = uf.state::INT
         INNER JOIN meta.latest_covid_source src on src.location = sd.fips and src.variable_id = sd.variable_id
where src.table_name = 'us_covid';


