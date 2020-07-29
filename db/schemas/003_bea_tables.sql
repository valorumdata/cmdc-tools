DROP TABLE IF EXISTS meta.bea_variables CASCADE;

CREATE TABLE meta.bea_variables (
    "id" serial PRIMARY KEY,
    "line_code" int,
    "dataset" text,
    "tablename" text,
    "description" text
);

CREATE UNIQUE INDEX bea_ref ON meta.bea_variables ("tablename", "dataset", "line_code");

COMMENT ON TABLE meta.bea_variables IS E'A list of variables from the BEA api. This is taken from ';

COMMENT ON COLUMN meta.bea_variables.id IS E'An internal, unique identifier for this variable';

COMMENT ON COLUMN meta.bea_variables.dataset IS E'The BEA dataset from which the variable taken';

COMMENT ON COLUMN meta.bea_variables.tablename IS E'The BEA tableName within the dataset.';

COMMENT ON COLUMN meta.bea_variables.line_code IS E'The line code within the table';

COMMENT ON COLUMN meta.bea_variables.description IS E'A verbal description of the variable';

INSERT INTO meta.bea_variables (id, line_code, dataset, tablename, description)
    VALUES (1, 1, 'Regional', 'CAGDP2', 'All industry total'), (2, 10, 'Regional', 'CAGDP2', 'Utilities (NAICS:22)'), (3, 11, 'Regional', 'CAGDP2', 'Construction (NAICS:23)'), (4, 12, 'Regional', 'CAGDP2', 'Manufacturing (NAICS:31-33)'), (5, 13, 'Regional', 'CAGDP2', 'Durable goods manufacturing (NAICS:321,327-339)'), (6, 2, 'Regional', 'CAGDP2', 'Private industries'), (7, 25, 'Regional', 'CAGDP2', 'Nondurable goods manufacturing (NAICS:311-316,322-326)'), (8, 3, 'Regional', 'CAGDP2', 'Agriculture, forestry, fishing and hunting (NAICS:11)'), (9, 34, 'Regional', 'CAGDP2', 'Wholesale trade (NAICS:42)'), (10, 35, 'Regional', 'CAGDP2', 'Retail trade (NAICS:44-45)'), (11, 36, 'Regional', 'CAGDP2', 'Transportation and warehousing (NAICS:48-49)'), (12, 45, 'Regional', 'CAGDP2', 'Information (NAICS:51)'), (13, 50, 'Regional', 'CAGDP2', 'Finance, insurance, real estate, rental, and leasing (NAICS:52, 53)'), (14, 51, 'Regional', 'CAGDP2', 'Finance and insurance (NAICS:52)'), (15, 56, 'Regional', 'CAGDP2', 'Real estate and rental and leasing (NAICS:53)'), (16, 59, 'Regional', 'CAGDP2', 'Professional and business services (NAICS:54, 55, 56)'), (17, 6, 'Regional', 'CAGDP2', 'Mining, quarrying, and oil and gas extraction (NAICS:21)'), (18, 60, 'Regional', 'CAGDP2', 'Professional, scientific, and technical services (NAICS:54)'), (19, 64, 'Regional', 'CAGDP2', 'Management of companies and enterprises (NAICS:55)'), (20, 65, 'Regional', 'CAGDP2', 'Administrative and support and waste management and remediation services (NAICS:56)'), (21, 68, 'Regional', 'CAGDP2', 'Educational services, health care, and social assistance (NAICS:61, 62)'), (22, 69, 'Regional', 'CAGDP2', 'Educational services (NAICS:61)'), (23, 70, 'Regional', 'CAGDP2', 'Health care and social assistance (NAICS:62)'), (24, 75, 'Regional', 'CAGDP2', 'Arts, entertainment, recreation, accommodation, and food services (NAICS:71, 72)'), (25, 76, 'Regional', 'CAGDP2', 'Arts, entertainment, and recreation (NAICS:71)'), (26, 79, 'Regional', 'CAGDP2', 'Accommodation and food services (NAICS:72)'), (27, 82, 'Regional', 'CAGDP2', 'Other services (except government and government enterprises) (NAICS:81)'), (28, 83, 'Regional', 'CAGDP2', 'Government and government enterprises'), (29, 87, 'Regional', 'CAGDP2', 'Natural resources and mining (NAICS:11, 21)'), (30, 88, 'Regional', 'CAGDP2', 'Trade (NAICS:42, 44-45)'), (31, 89, 'Regional', 'CAGDP2', 'Transportation and utilities'), (32, 90, 'Regional', 'CAGDP2', 'Manufacturing and information'), (33, 91, 'Regional', 'CAGDP2', 'Private goods-producing industries'), (34, 92, 'Regional', 'CAGDP2', 'Private services-providing industries');

CREATE TABLE data.bea_gdp (
    "id" int REFERENCES meta.bea_variables (id),
    "year" int,
    "fips" int REFERENCES meta.us_fips (fips),
    "value" double PRECISION,
    PRIMARY KEY (id, year, fips)
);

COMMENT ON TABLE data.bea_gdp IS E'Sector level annual GDP at the county level as reported by the BEA.

This data comes from the `CAGDP2` Table in the `Regional` dataset.

See the BEA API for more information: https://apps.bea.gov/api/signup';

COMMENT ON COLUMN data.bea_gdp.id IS E'An internal ID used to identify the variable';

COMMENT ON COLUMN data.bea_gdp.year IS E'The year of the observation';

COMMENT ON COLUMN data.bea_gdp.fips IS E'The 5 digit fips code for identifying a US county.';

COMMENT ON COLUMN data.bea_gdp.value IS E'The value of the variable in the given year and county.';

