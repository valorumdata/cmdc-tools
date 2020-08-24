CREATE OR REPLACE VIEW api.us_states AS
  SELECT uf.fips as location, uf.name, uf.variable, uf.value
  FROM meta.us_fips_long uf
  WHERE uf.fips < 100
;

COMMENT ON VIEW api.us_states IS E'Basic information about US states from the US census.

This table contains basic information about the U.S. states

Source(s):

US Census TIGER/Line Shapefiles (https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html)
';

COMMENT ON COLUMN api.us_states.location is E'The fips code for the state';
COMMENT ON COLUMN api.us_states.name is E'The state name';
COMMENT ON COLUMN api.us_states.variable is E'The name of the variable represented in this row. Should be one of (area, latitude, longitude)';
COMMENT ON COLUMN api.us_states.value is E'The value of the variable represented in this row';

drop view if exists api.us_counties;

CREATE OR REPLACE VIEW api.us_counties AS
SELECT uf.fips as location, uf.name as county_name, uf2.name  as state_name, variable, value
FROM meta.us_fips_long uf
         left join meta.us_fips uf2 on uf2.fips = uf.state::INT
WHERE uf.fips > 100;


COMMENT ON VIEW api.us_counties IS E'Basic information about US counties from the US census.

This table contains basic information about the U.S. counties

Source(s):

US Census TIGER/Line Shapefiles (https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html)
';
COMMENT ON COLUMN api.us_counties.location is E'The fips code for the state';
COMMENT ON COLUMN api.us_counties.county_name is E'The county name';
comment on column api.us_counties.state_name is E'The name of the state';
COMMENT ON COLUMN api.us_counties.variable is E'The name of the variable represented in this row. Should be one of (area, latitude, longitude)';
COMMENT ON COLUMN api.us_counties.value is E'The value of the variable represented in this row';

