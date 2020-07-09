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

create or replace view meta.latest_covid_source(location, variable_id, date_accessed, source, table_name) as
	WITH max_date AS (
    SELECT covid_sources_1.location,
           covid_sources_1.variable_id,
           covid_sources_1.table_name,
           max(covid_sources_1.date_accessed) AS date_accessed
    FROM data.covid_sources covid_sources_1
    GROUP BY covid_sources_1.location, covid_sources_1.variable_id, covid_sources_1.table_name
)
SELECT max_date.location,
       max_date.variable_id,
       max_date.date_accessed,
       covid_sources.source,
       max_date.table_name
FROM max_date
         LEFT JOIN data.covid_sources USING (location, variable_id, date_accessed, table_name);

