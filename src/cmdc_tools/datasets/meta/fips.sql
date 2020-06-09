DROP TABLE if exists data.us_counties;

CREATE TABLE data.us_counties (
    fips INT PRIMARY KEY,
    county_name TEXT,
    state_abbr CHAR(2),
    state SMALLINT,
    county SMALLINT
);

COMMENT on Table data.us_counties is 'A table containing FIPS codes for all US counties. Source: https://github.com/kjhealy/fips-codes';

COMMENT ON COLUMN data.us_counties.fips is 'The 5 digit fips code (truncated if leading zero) for the county.';
COMMENT ON COLUMN data.us_counties.county_name is 'The name of the county';
COMMENT ON COLUMN data.us_counties.state_abbr is 'The 2 letter abbreviation of the state';
COMMENT ON COLUMN data.us_counties.state is 'The two digit state fips code (truncated if leading zeros)';
COMMENT ON COLUMN data.us_counties.county is 'The three digit county fips code (truncated if leading zeros)';

CREATE INDEX state on data.us_counties (state);
CREATE INDEX county on data.us_counties (county);
CREATE INDEX fips on data.us_counties (state, county);


INSERT INTO data.us_counties (fips, county_name, state_abbr, state, county) VALUES
(60, 'American Samoa', NULL, 60, 0),
(88888, 'Diamond Princess', NULL, 88, 0),
(99999, 'Grand Princess', NULL, 99, 0),
(66, 'Guam', NULL, 66, 0),
(69, 'Northern Mariana Islands', NULL, 69, 0),
(72, 'Puerto Rico', NULL, 72, 0),
(78, 'Virgin Islands', NULL, 78, 0);


DROP TABLE IF EXISTS data.us_states;
CREATE TABLE data.us_states (
    fips smallint primary key,
    name text,
    abbreviation char(2)
);

COMMENT ON TABLE data.us_states IS E'A table containing all US State fips code, name, and postal abbreviation';


COMMENT ON COLUMN data.us_states.fips IS E'The two digit state fips code';
COMMENT ON COLUMN data.us_states.name IS E'The full name of the state';
COMMENT ON COLUMN data.us_states.abbreviation IS E'The two letter postal code abbreviation for the state';

INSERT INTO data.us_states (name, abbreviation, fips) VALUES
('Alabama','AL',01),
('Alaska','AK',02),
('Arizona','AZ',04),
('Arkansas','AR',05),
('California','CA',06),
('Colorado','CO',08),
('Connecticut','CT',09),
('Delaware','DE',10),
('Florida','FL',12),
('Georgia','GA',13),
('Hawaii','HI',15),
('Idaho','ID',16),
('Illinois','IL',17),
('Indiana','IN',18),
('Iowa','IA',19),
('Kansas','KS',20),
('Kentucky','KY',21),
('Louisiana','LA',22),
('Maine','ME',23),
('Maryland','MD',24),
('Massachusetts','MA',25),
('Michigan','MI',26),
('Minnesota','MN',27),
('Mississippi','MS',28),
('Missouri','MO',29),
('Montana','MT',30),
('Nebraska','NE',31),
('Nevada','NV',32),
('New Hampshire','NH',33),
('New Jersey','NJ',34),
('New Mexico','NM',35),
('New York','NY',36),
('North Carolina','NC',37),
('North Dakota','ND',38),
('Ohio','OH',39),
('Oklahoma','OK',40),
('Oregon','OR',41),
('Pennsylvania','PA',42),
('Rhode Island','RI',44),
('South Carolina','SC',45),
('South Dakota','SD',46),
('Tennessee','TN',47),
('Texas','TX',48),
('Utah','UT',49),
('Vermont','VT',50),
('Virginia','VA',51),
('Washington','WA',53),
('West Virginia','WV',54),
('Wisconsin','WI',55),
('Wyoming','WY',56),
('American Samoa','AS',60),
('Guam','GU',66),
('Northern Mariana Islands','MP',69),
('Puerto Rico','PR',72),
('Virgin Islands','VI',78),
('Washington DC', 'DC', 11);
