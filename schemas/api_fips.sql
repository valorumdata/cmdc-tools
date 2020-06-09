CREATE OR REPLACE VIEW api.states AS
  SELECT uf.fips, uf.name, uf.area, uf.latitude, uf.longitude
  FROM meta.us_fips uf
  WHERE uf.fips < 100
;


COMMENT ON VIEW api.states IS E'This table contains basic information about the U.S. states

Source(s):

US Census TIGER/Line Shapefiles (https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html)
';

COMMENT ON COLUMN api.states.fips is E'The fips code for the state';
COMMENT ON COLUMN api.states.name is E'The state name';
COMMENT ON COLUMN api.states.area is E'The size of the state (measured in square miles)';
COMMENT ON COLUMN api.states.latitude is E'A latitude point interior to the state';
COMMENT ON COLUMN api.states.longitude is E'A longitude point interior to the state';


CREATE OR REPLACE VIEW api.counties AS
  SELECT uf.fips, uf.name, uf.area, uf.latitude, uf.longitude
  FROM meta.us_fips uf
  WHERE uf.fips > 100
;


COMMENT ON VIEW api.counties IS E'This table contains basic information about the U.S. counties

Source(s):

US Census TIGER/Line Shapefiles (https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html)
';

COMMENT ON COLUMN api.counties.fips is E'The fips code for the county';
COMMENT ON COLUMN api.counties.name is E'The county name';
COMMENT ON COLUMN api.counties.area is E'The size of the county (measured in square miles)';
COMMENT ON COLUMN api.counties.latitude is E'A latitude point interior to the county';
COMMENT ON COLUMN api.counties.longitude is E'A longitude point interior to the county';
