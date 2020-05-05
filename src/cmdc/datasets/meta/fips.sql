DROP TABLE if exists data.us_fips;

CREATE TABLE data.us_fips (
    fips INT PRIMARY KEY,
    county_name TEXT,
    state_abbr CHAR(2),
    state INT,
    county INT
);

COMMENT on Table data.us_fips is 'A table containing FIPS codes for all US counties. Source: https://github.com/kjhealy/fips-codes';

COMMENT ON COLUMN data.us_fips.fips is 'The 5 digit fips code (truncated if leading zero) for the county.';
COMMENT ON COLUMN data.us_fips.county_name is 'The name of the county';
COMMENT ON COLUMN data.us_fips.state_abbr is 'The 2 letter abbreviation of the state';
COMMENT ON COLUMN data.us_fips.state is 'The two digit state fips code (truncated if leading zeros)';
COMMENT ON COLUMN data.us_fips.county is 'The three digit county fips code (truncated if leading zeros)';

