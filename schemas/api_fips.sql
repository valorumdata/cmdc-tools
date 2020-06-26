CREATE OR REPLACE VIEW api.us_states AS
  SELECT uf.fips as location, uf.name, uf.area, uf.latitude, uf.longitude
  FROM meta.us_fips uf
  WHERE uf.fips < 100
;


COMMENT ON VIEW api.us_states IS E'This table contains basic information about the U.S. states

Source(s):

US Census TIGER/Line Shapefiles (https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html)
';

COMMENT ON COLUMN api.us_states.location is E'The fips code for the state';
COMMENT ON COLUMN api.us_states.name is E'The state name';
COMMENT ON COLUMN api.us_states.area is E'The size of the state (measured in square miles)';
COMMENT ON COLUMN api.us_states.latitude is E'A latitude point interior to the state';
COMMENT ON COLUMN api.us_states.longitude is E'A longitude point interior to the state';


CREATE OR REPLACE VIEW api.us_counties AS
  SELECT uf.fips as location, uf.name, uf.area, uf.latitude, uf.longitude
  FROM meta.us_fips uf
  WHERE uf.fips > 100
;


COMMENT ON VIEW api.us_counties IS E'This table contains basic information about the U.S. counties

Source(s):

US Census TIGER/Line Shapefiles (https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html)
';

COMMENT ON COLUMN api.us_counties.location is E'The fips code for the county';
COMMENT ON COLUMN api.us_counties.name is E'The county name';
COMMENT ON COLUMN api.us_counties.area is E'The size of the county (measured in square miles)';
COMMENT ON COLUMN api.us_counties.latitude is E'A latitude point interior to the county';
COMMENT ON COLUMN api.us_counties.longitude is E'A longitude point interior to the county';
