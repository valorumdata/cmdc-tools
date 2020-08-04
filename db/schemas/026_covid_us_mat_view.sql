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
    uc.value
   FROM data.us_covid_last_vintage lv
     LEFT JOIN data.us_covid uc USING (dt, fips, variable_id, vintage)
     LEFT JOIN meta.covid_variables cv ON cv.id = uc.variable_id;
