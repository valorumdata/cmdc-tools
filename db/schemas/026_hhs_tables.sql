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

