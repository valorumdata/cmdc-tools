DROP TABLE IF EXISTS meta.acs_variables;

/* Create and define metadata tables */
CREATE TABLE meta.acs_variables (
    "id" SERIAL PRIMARY KEY,
    "year" INTEGER,
    "product" CHAR(4),
    "census_id" VARCHAR(20),
    "label" VARCHAR(350)
);

CREATE UNIQUE INDEX acs_var_ref ON meta.acs_variables ("year", "product", "census_id");

COMMENT ON TABLE meta.acs_variables IS E'
Table Description:

This table contains information on the variables that are listed for one of the ACS products (1 and 5 year estimates):

For more information on these variables, please refer to the US Census page about the [ACS 1 year estimates](https://www.census.gov/data/developers/data-sets/acs-1year.html) and the [ACS 5 year estimates](https://www.census.gov/data/developers/data-sets/acs-5year.html)

Words of caution:

Source: US Census';

COMMENT ON COLUMN meta.acs_variables.id IS E'An internal identifier for referencing different variables.';
COMMENT ON COLUMN meta.acs_variables.year IS E'The year this product was collected/published';
COMMENT ON COLUMN meta.acs_variables.product IS E'Which ACS product this variables comes from. Can take the values `acs1` or `acs5`';
COMMENT ON COLUMN meta.acs_variables.census_id IS E'The variable name according to the Census documentation.';
COMMENT ON COLUMN meta.acs_variables.label IS E'A short label that describes what the variable includes.';


/* Create and define data tables */
CREATE TABLE data.acs_data (
    "id" INTEGER REFERENCES meta.acs_variables(id),
    "fips" INTEGER REFERENCES data.us_counties(fips),
    "value" FLOAT,
    PRIMARY KEY ("id", "fips")
);
COMMENT ON TABLE data.acs_data IS E'
**Table Description:**

The American Community Survey (ACS) is an ongoing survey that provides data every year -- giving communities the current information they need to plan investments and services. The ACS covers a broad range of topics about social, economic, demographic, and housing characteristics of the U.S. population. Much of the ACS data provided on the Census web site are available separately by age group, race, Hispanic origin, and sex.

Detailed Tables, Subject Tables, Data Profiles, Comparison Profiles and Selected Population Profiles are available for the nation, all 50 states, the District of Columbia, Puerto Rico, every congressional district, every metropolitan area, and all counties and places with populations of 65,000 or more.

This table contains the values collected by the Census -- It should be merged with the `acs_variables` to identify which variables the values are associated with.

Words of caution:

Source: US Census';

COMMENT ON COLUMN data.acs_data.id IS E'This id maps to the `meta.acs_variables` table';
COMMENT ON COLUMN data.acs_data.fips IS E'The county/state/tract fips code';
COMMENT ON COLUMN data.acs_data.value IS E'The value of the variable associated with `id` for geography `fips` in year `year`';

