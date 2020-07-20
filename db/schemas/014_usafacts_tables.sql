DROP TABLE IF EXISTS data.usafacts_covid;

CREATE TABLE data.usafacts_covid (
    vintage date,
    dt date,
    fips int REFERENCES meta.us_fips (fips),
    variable_id smallint REFERENCES meta.covid_variables (id),
    value int,
    PRIMARY KEY (fips, dt, vintage, variable_id)
);

COMMENT ON TABLE data.usafacts_covid IS E'This table contains the data collected by USAFacts';

CREATE INDEX usafacts_covid_dt_idx ON data.usafacts_covid (dt);

CREATE TRIGGER trig_usafacts_to_us_covid
    AFTER INSERT ON data.usafacts_covid
    FOR EACH ROW
    EXECUTE PROCEDURE copy_to_us_covid_table ('usafacts');

