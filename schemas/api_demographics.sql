CREATE OR REPLACE VIEW api.demographics AS
  /* TODO: Add new definition here...*/
;

COMMENT ON VIEW api.demographics IS E'This table contains information on the demographics of a particular region and is based on the American Community Survey.

Currently, the following variables are collected in the database

* Total population
* Median age
* Fraction of the population over 65
* Fraction of the population who identify as various races or as Hispanic/Latino
* Fraction of the population with various degrees of education
* Fraction of the population that commutes in various ways
* Mean travel time to work (minutes)
* Median household income
* Mean household income
* Fraction of the (civilian) population with/without health insurance
* Fraction of families who had an income less than poverty level in the last year

These variables are collected from the 2018 American Community Survey (5 year) in order to ensure that we have data for each county.
Please note that we are willing (and easily able!) to add other years or variables if there is interest --- The variables that we do include are because people have asked about them.

Source(s):

US Census American Community Survey (https://www.census.gov/programs-surveys/acs)
';

COMMENT ON COLUMN api.demographics.fips is E'The fips code';
COMMENT ON COLUMN api.demographics.variable is E'A description of the variable';
COMMENT ON COLUMN api.demographics.value is E'The value of the variable';
