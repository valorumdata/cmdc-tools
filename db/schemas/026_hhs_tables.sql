DROP TABLE IF EXISTS data.hhs_covid;

CREATE TABLE data.hhs_covid (
    vintage date,
    dt date,
    fips int REFERENCES meta.us_fips (fips),
    variable_id smallint REFERENCES meta.covid_variables (id),
    value int,
    PRIMARY KEY (fips, dt, vintage, variable_id)
);

COMMENT ON TABLE data.hhs_covid IS E'This table contains the data collected by HHS';

CREATE INDEX hhs_dt_idx ON data.hhs_covid (dt);

CREATE TRIGGER trig_hhs_to_us_covid
    AFTER INSERT ON data.hhs_covid
    FOR EACH ROW
    EXECUTE PROCEDURE copy_to_us_covid_table ('hhs');


create view api.hhs(dt, fips, variable, value) as
	WITH last_vintage AS (
    SELECT hhs_covid.dt,
           hhs_covid.fips,
           hhs_covid.variable_id,
           max(hhs_covid.vintage) AS vintage
    FROM data.hhs_covid
    GROUP BY hhs_covid.dt, hhs_covid.fips, hhs_covid.variable_id
)
SELECT hhs.dt,
       hhs.fips,
       cv.name AS variable,
       hhs.value
FROM last_vintage lv
         LEFT JOIN data.hhs_covid hhs USING (dt, fips, variable_id, vintage)
         LEFT JOIN meta.covid_variables cv ON cv.id = lv.variable_id;

comment on view api.hhs is 'State-level COVID-19 hospitalization data from the Department of Health & Human Services.

This table contains the data from the HHS COVID data

This table only includes the most recent observation for each date, location, and variable. If you are interested in historical revisions of this data, please reach out -- We have previous "vintages" of the HHS data but, in order to simplify our list of tables, we have chosen not to expose (but are happy to if it would be useful).
';

comment on column api.hhs.dt is 'The date of the observation';

comment on column api.hhs.fips is 'The fips code corresponding to the observation';

comment on column api.hhs.variable is 'Denotes which variable the value corresponds to';

comment on column api.hhs.value is 'The value of the observation';

alter table api.hhs owner to postgres;

grant select on api.hhs to postgrest;

grant select on api.hhs to covid_anon;

