CREATE TABLE data.covid_sources (
    date_accessed TIMESTAMPTZ,
    LOCATION INT references meta.us_fips(fips),
    variable_id INT references meta.covid_variables(id),
    source TEXT not null,
    audited BOOL NOT NULL default FALSE,
    audit_success BOOL,
    primary key (date_accessed, LOCATION, variable_id)
);


alter table data.covid_sources add column table_name text not null default 'us_covid';

update data.covid_sources set table_name='jhu_daily_reports'
where source = 'https://github.com/CSSEGISandData/COVID-19';

update data.covid_sources set table_name='jhu_daily_reports_us'
where source = 'https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_daily_reports_us';

update data.covid_sources set table_name = 'usafacts_covid'
    where source = 'https://usafacts.org/issues/coronavirus/';

update data.covid_sources set table_name = 'nyt_covid'
    where source = 'https://github.com/nytimes/covid-19-data';

create index covid_sources__table_name_idx
	on data.covid_sources (table_name);

CREATE OR REPLACE VIEW meta.latest_covid_source as
with max_date as (
    select location, variable_id, table_name, max(date_accessed) as date_accessed
    from data.covid_sources
    group by location, variable_id, table_name
)
select location, variable_id, date_accessed, source, table_name
from max_date
         left join data.covid_sources using (location, variable_id, date_accessed, table_name);
