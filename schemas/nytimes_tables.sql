DROP TABLE IF EXISTS data.nyt_covid;

CREATE TABLE data.nyt_covid (
    vintage DATE,
    dt date,
    fips INT references meta.us_fips(fips),
    variable_id SMALLINT REFERENCES meta.covid_variables(id),
    value INT,
    PRIMARY KEY (fips, dt, vintage, variable_id)
);

COMMENT ON TABLE data.nyt_covid IS E'This table contains the data collected by the NY Time COVID cases/deaths database';

