CREATE TABLE data.covid_sources (
    date_accessed TIMESTAMPTZ,
    LOCATION INT references meta.us_fips(fips),
    variable_id INT references meta.covid_variables(id),
    source TEXT not null,
    audited BOOL NOT NULL default FALSE,
    audit_success BOOL,
    primary key (date_accessed, LOCATION, variable_id)
);


CREATE OR REPLACE VIEW meta.latest_covid_source as
    with max_date as (
    select location, variable_id, max(date_accessed) as date_accessed
    from data.covid_sources
    group by location, variable_id
    )
    select location, variable_id, date_accessed, source
from max_date
left join data.covid_sources using (location, variable_id, date_accessed);
