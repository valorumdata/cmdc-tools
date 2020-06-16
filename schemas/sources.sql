CREATE TABLE data.covid_sources (
    date_accessed TIMESTAMPTZ,
    LOCATION INT references meta.us_fips(fips),
    variable_id INT references meta.covid_variables(id),
    source TEXT not null,
    primary key (date_accessed, LOCATION, variable_id)
);
