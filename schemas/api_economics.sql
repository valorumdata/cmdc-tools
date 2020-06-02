CREATE OR REPLACE VIEW api.economics AS
    /* TODO: Update this to latest version... */
    SELECT to_date(bg.year::text, 'YYYY') as dt, bg.fips, 'GDP_' || bv.description, bg.value
    FROM data.bea_gdp bg
    LEFT JOIN meta.bea_variables bv
    on bv.id=bg.id
    UNION
    SELECT dt, 0::INT, 'wei'::TEXT, wei
    FROM data.weeklyeconomicindex
;

COMMENT ON VIEW api.economics IS E'This table contains information on economic outcomes at different geographic levels.

These economic variables include:

* Weekly Economic Index produced by Jim Stock
* State unemployment claims (county forthcoming)
* Spending


These variables are collected from a variety of sources.

Source(s):

* Department of Labor
* Weekly Economic Index, Jim Stock (https://www.jimstock.org/)
* US Census
';

COMMENT ON COLUMN api.economics.vintage is E'The date/time the data was collected and stored in our database';
COMMENT ON COLUMN api.economics.dt is E'The date of the observation';
COMMENT ON COLUMN api.economics.fips is E'The fips code';
COMMENT ON COLUMN api.economics.variable is E'A description of the variable';
COMMENT ON COLUMN api.economics.value is E'The value of the variable';
