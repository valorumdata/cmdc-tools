DROP TABLE IF EXISTS data.nyt_covid;

CREATE TABLE data.nyt_covid (
    vintage date,
    dt date,
    fips int REFERENCES meta.us_fips (fips),
    variable_id smallint REFERENCES meta.covid_variables (id),
    value int,
    PRIMARY KEY (fips, dt, vintage, variable_id)
);

COMMENT ON TABLE data.nyt_covid IS E'This table contains the data collected by the NY Time COVID cases/deaths database';

CREATE TRIGGER trig_nyt_to_us_covid
    AFTER INSERT ON data.nyt_covid
    FOR EACH ROW
    EXECUTE PROCEDURE copy_to_us_covid_table ('nyt');

