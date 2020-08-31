CREATE OR REPLACE VIEW api.covid_sources AS
select fips                                                                                 as location,
       CASE WHEN fips < 100 THEN LPAD(fips::TEXT, 2, '0') ELSE LPAD(fips::TEXT, 5, '0') END AS fips,
       fullname                                                                             as name,
       state                                                                                as state_name,
       variable_name                                                                        as variable,
       source
from meta.us_covid_variable_start_date;

COMMENT ON VIEW api.covid_sources is E'Source information for all US COVID-19 data.

The  source column will contain a URL for the location where CovidCountyData accessed the data last.

This means for each fips code and variable, we are reporting the *most recent* source used by CCD.

NOTE that this view cannot be combined with others using the Julia/Python/R client libraries.';

COMMENT ON COLUMN api.covid_sources.location IS E'An integer identifying the geography. For US states and counties this is a fips code without leading zeros.';
COMMENT ON COLUMN api.covid_sources.fips IS E'The 2 digit fips code for US states and 5 digit fips code for US counties.';
COMMENT ON COLUMN api.covid_sources.name is E'The written name for the geography. For US states this is the state name. For US counties this is the county name.';
COMMENT ON COLUMN api.covid_sources.state_name IS E'The name of the US state for the geography. For states, this will beequal to the `name` column';
COMMENT ON COLUMN api.covid_sources.variable IS E'The name of the variable for which we report the source';
COMMENT ON COLUMN api.covid_sources.source IS E'A string containing the URL pointing to where CovidCountyData accessed the data';
