DROP TABLE IF EXISTS data.usafacts_covid;

CREATE TABLE data.usafacts_covid (
    vintage DATE,
    dt date,
    fips INT references meta.us_fips(fips),
    variable_id SMALLINT REFERENCES meta.covid_variables(id),
    value INT,
    PRIMARY KEY (fips, dt, vintage, variable_id)
);

COMMENT ON TABLE data.usafacts_covid IS E'This table contains the data collected by USAFacts';

CREATE INDEX dt_idx on data.usafacts_covid (dt);
