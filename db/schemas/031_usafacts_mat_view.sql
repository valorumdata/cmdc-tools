create materialized view data.usafacts_covid_last_vintage as SELECT uc_1.dt,
            uc_1.fips,
            uc_1.variable_id,
            max(uc_1.vintage) AS vintage
           FROM data.usafacts_covid uc_1
          GROUP BY uc_1.dt, uc_1.fips, uc_1.variable_id
	 	  ORDER BY dt, fips, variable_id;

CREATE INDEX usafacts_covid_last_vintage_dt_fips_variable_id on data.usafacts_covid_last_vintage (dt, fips, variable_id);

CREATE OR REPLACE VIEW api.usafacts_covid AS
SELECT
  ufc.dt,
  ufc.fips,
  cv.name AS variable,
  ufc.value
FROM
  data.usafacts_covid_last_vintage lv
  LEFT JOIN data.usafacts_covid ufc USING (dt, fips, variable_id, vintage)
  LEFT JOIN meta.covid_variables cv ON cv.id = ufc.variable_id;

