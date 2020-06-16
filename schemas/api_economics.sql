CREATE OR REPLACE VIEW api.economics AS
  WITH last_vintage AS (
    SELECT MAX(vintage), dt, fips, variable_name
    FROM dol_ui
    GROUP BY dt, fips, variable_name
  )
  SELECT dt, fips as location, variable_name as variable, value
  FROM dol_ui ui
  LEFT JOIN last_vintage lv
    ON lv.vintage=ui.vintage
    AND lv.dt=ui.dt
    AND lv.fips=ui.fips
    AND lv.variable_name=ui.variable_name
  UNION ALL
  SELECT dt, 0 as location, 'wei'::TEXT AS variable, wei AS value
  FROM data.weeklyeconomicindex
;

COMMENT ON VIEW api.economics IS E'This table contains information on economic outcomes as time series data

These variables tend to be observed at a daily/weekly/monthly/quarterly frequency and we can use them to think
about changes in the economy as opposed to the slow moving variables included in the `economic_snapshots` table

These economic variables currently include:

* Weekly Economic Index produced by Jim Stock
* State unemployment claims (county forthcoming)

These variables are collected from a variety of sources.

Source(s):

* Department of Labor
* Weekly Economic Index, Jim Stock (https://www.jimstock.org/)
* US Census
';

COMMENT ON COLUMN api.economics.dt is E'The date of the observation';
COMMENT ON COLUMN api.economics.fips is E'The fips code';
COMMENT ON COLUMN api.economics.variable is E'A description of the variable';
COMMENT ON COLUMN api.economics.value is E'The value of the variable';

CREATE OR REPLACE VIEW api.economic_snapshots AS
    bg.fips as location,
    'GDP_'::text || bv.description AS variable,
    bg.value
   FROM data.bea_gdp bg
     LEFT JOIN meta.bea_variables bv ON bv.id = bg.id
;

COMMENT ON VIEW api.economic_snapshots IS E'This table contains information on economic characteristics of different geographic areas.

These variables are not typically collected at a sufficiently high frequency to use them as time-series data but rather we use
them to characterize the economic features of different locations. For example, while unemployment claims is observed on a
weekly basis, data on the industry make-up of a geographic region is only available at a yearly frequency.

The variables currently included here are:

* Industry specific GDP at the county/state level

These variables are collected from a variety of sources.

Source(s):

* Bureau of Economic Analysis
';

COMMENT ON COLUMN api.economic_snapshots.fips is E'The fips code';
COMMENT ON COLUMN api.economic_snapshots.variable is E'A description of the variable';
COMMENT ON COLUMN api.economics.value is E'The value of the variable';
