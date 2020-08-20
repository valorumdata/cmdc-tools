drop view if exists api.demographics;
CREATE OR REPLACE VIEW api.demographics AS
  WITH temp AS (
    SELECT mv.id, mvs.name
    FROM meta.acs_variables mv
    RIGHT JOIN meta.acs_variables_selected mvs
    ON mv.year=mvs.year AND mv.product=mvs.product AND mv.census_id=mvs.census_id
  )
  SELECT dd.fips as location, idn.name as variable, dd.value
  FROM data.acs_data dd
  LEFT JOIN temp idn
  ON dd.id=idn.id
  ORDER BY dd.fips, idn.name
;

COMMENT ON VIEW api.demographics IS E'Demographics data from the US Census including population, age, race, and more.

This table contains information on the demographics of a particular geography

For the United States, this data comes from the American Community Survey that is administered by the US Census. Currently, the following variables are collected in the database

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

Please note that we are willing (and easily able!) to add other years or variables if there is interest --- The variables that we do include are because people have asked about them.

Source(s):

US Census American Community Survey (https://www.census.gov/programs-surveys/acs)
';

COMMENT ON COLUMN api.demographics.location is E'This value is a numerical representation of a geography. For the United States, this number is the FIPS code. See our documentation page for more information.';
COMMENT ON COLUMN api.demographics.variable is E'A description of the variable';
COMMENT ON COLUMN api.demographics.value is E'The value of the variable';
