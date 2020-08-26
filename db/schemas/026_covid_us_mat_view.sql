create materialized view data.us_covid_last_vintage as SELECT uc_1.dt,
            uc_1.fips,
            uc_1.variable_id,
            max(uc_1.vintage) AS vintage
           FROM data.us_covid uc_1
          GROUP BY uc_1.dt, uc_1.fips, uc_1.variable_id
	 	  ORDER BY dt, fips, variable_id;

CREATE INDEX us_covid_last_vintage_dt_fips_variable_id on data.us_covid_last_vintage (dt, fips, variable_id);

CREATE OR REPLACE VIEW api.covid_us AS
 SELECT uc.dt,
    uc.fips AS location,
    cv.name AS variable,
    uc.value,
    CASE WHEN fips < 100 THEN LPAD(fips::TEXT, 2, '0') ELSE LPAD(fips::TEXT, 5, '0') END AS fips
   FROM data.us_covid_last_vintage lv
     LEFT JOIN data.us_covid uc USING (dt, fips, variable_id, vintage)
     LEFT JOIN meta.covid_variables cv ON cv.id = uc.variable_id;

COMMENT ON COLUMN api.covid_us.location IS E'An integer identifying the geography. For US states and counties this is a fips code without leading zeros.';
COMMENT ON COLUMN api.covid_us.fips IS E'The 2 digit fips code for US states and 5 digit fips code for US counties.';
