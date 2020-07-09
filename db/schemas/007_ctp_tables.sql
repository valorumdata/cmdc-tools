DROP TABLE IF EXISTS data.ctp_covid;

CREATE TABLE data.ctp_covid (
    vintage date,
    dt date,
    fips int REFERENCES meta.us_fips (fips),
    variable_id smallint REFERENCES meta.covid_variables (id),
    value int,
    PRIMARY KEY (fips, dt, vintage, variable_id)
);

COMMENT ON TABLE data.ctp_covid IS E'This table contains the data collected by COVID Tracking Project';

CREATE INDEX dt_idx ON data.ctp_covid (dt);

CREATE TRIGGER trig_ctp_to_us_covid
    AFTER INSERT ON data.ctp_covid
    FOR EACH ROW
    EXECUTE PROCEDURE copy_to_us_covid_table ('ctp');

