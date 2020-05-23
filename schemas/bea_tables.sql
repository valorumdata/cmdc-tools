DROP TABLE IF EXISTS meta.bea_variables CASCADE;

CREATE TABLE meta.bea_variables (
    "id" serial primary key,
    "line_code" INT,
    "dataset" TEXT,
    "tablename" TEXT,
    "description" TEXT
);

CREATE UNIQUE INDEX bea_ref on meta.bea_variables ("tablename", "dataset", "line_code");

COMMENT ON TABLE meta.bea_variables is E'A list of variables from the BEA api. This is taken from ';

COMMENT ON COLUMN meta.bea_variables.id is E'An internal, unique identifier for this variable';
COMMENT ON COLUMN meta.bea_variables.dataset is E'The BEA dataset from which the variable taken';
COMMENT ON COLUMN meta.bea_variables.tablename is E'The BEA tableName within the dataset.';
COMMENT ON COLUMN meta.bea_variables.line_code is E'The line code within the table';
COMMENT ON COLUMN meta.bea_variables.description is E'A verbal description of the variable';



CREATE TABLE data.bea_gdp (
    "id" int references meta.bea_variables(id),
    "year" INT,
    "fips" BIGINT references meta.us_fips(fips),
    "value" DOUBLE PRECISION,
    PRIMARY KEY (id, year, fips)
);

COMMENT ON TABLE data.bea_gdp is E'Sector level annual GDP at the county level as reported by the BEA.

This data comes from the `CAGDP2` Table in the `Regional` dataset.

See the BEA API for more information: https://apps.bea.gov/api/signup';

COMMENT ON COLUMN data.bea_gdp.id is E'An internal ID used to identify the variable';
COMMENT ON COLUMN data.bea_gdp.year is E'The year of the observation';
COMMENT ON COLUMN data.bea_gdp.fips is E'The 5 digit fips code for identifying a US county.';
COMMENT ON COLUMN data.bea_gdp.value is E'The value of the variable in the given year and county.';

