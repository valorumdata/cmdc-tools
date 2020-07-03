DROP TABLE IF EXISTS data.ctp_covid;

CREATE TABLE data.ctp_covid (
    vintage DATE,
    dt DATE,
    fips INT references meta.us_fips(fips),
    variable_id SMALLINT REFERENCES meta.covid_variables(id),
    value INT,
    PRIMARY KEY (fips, dt, vintage, variable_id)
);

COMMENT ON TABLE data.ctp_covid IS E'This table contains the data collected by COVID Tracking Project';

CREATE INDEX ctp_dt_idx on data.ctp_covid (dt);
