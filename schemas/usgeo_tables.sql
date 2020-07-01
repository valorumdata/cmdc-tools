DROP TABLE IF EXISTS meta.us_fips CASCADE;

CREATE TABLE meta.us_fips (
    "id" SERIAL PRIMARY KEY,
    "fips" BIGINT,
    "state" TEXT,
    "county" TEXT,
    "name" TEXT,
    "fullname" TEXT,
    "area" REAL,
    "latitude" REAL,
    "longitude" REAL
);

CREATE UNIQUE INDEX fips_ind ON meta.us_fips("fips");

INSERT INTO meta.us_fips (fips, state, county, name, area, latitude, longitude)
  VALUES (0, '00', '000', 'United States', 3535948.12, 39.8283, -98.5795)
;

COMMENT ON TABLE meta.us_fips is E'This table contains the FIPS codes for states, counties, and census tracts.';

COMMENT ON COLUMN meta.us_fips.id is E'An internal, unique identifier for this geography';
COMMENT ON COLUMN meta.us_fips.fips is E'The fips code associated with this geography';
COMMENT ON COLUMN meta.us_fips.name is E'The name of the state or county. This is simply the word tract with the fips number for tracts.';
COMMENT ON COLUMN meta.us_fips.area is E'The land area measured in square miles';
COMMENT ON COLUMN meta.us_fips.latitude is E'The latitude of an interior point of the geography';
COMMENT ON COLUMN meta.us_fips.longitude is E'The longitude of an interior point of the geography';

