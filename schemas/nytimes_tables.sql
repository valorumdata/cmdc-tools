DROP TABLE IF EXISTS data.covid_nytimes;

CREATE TABLE data.covid_nytimes (
    vintage DATE,
    dt date,
    fips INT references meta.us_fips(fips),
    variable_id SMALLINT REFERENCES meta.covid_variables(id),
    value INT,
    PRIMARY KEY (fips, dt, vintage, variable_id)
);
