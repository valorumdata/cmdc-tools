DROP TABLE IF EXISTS data.dol_ui;

/* Create and define metadata tables */
CREATE TABLE data.dol_ui (
    vintage DATE,
    dt DATE,
    fips INTEGER references meta.us_fips(fips),
    variable_name TEXT,
    value REAL,
    PRIMARY KEY (vintage, dt, fips, variable_name)
);
