DROP TABLE IF EXISTS meta.covid_variables;
CREATE TABLE meta.covid_variables (
    id serial primary key,
    name text
);

INSERT INTO meta.covid_variables (name) VALUES
('cases_total'),
('deaths_total'),
('positive_tests_total'),
('negative_tests_total'),
('icu_beds_capacity_count'),
('icu_beds_in_use_any'),
('icu_beds_in_use_covid'),
('icu_beds_in_use_covid_new'),
('hospital_beds_capacity_count'),
('hospital_beds_in_use_any'),
('hospital_beds_in_use_covid'),
('hospital_beds_in_use_covid_new'),
('ventilators_capacity_count'),
('ventilators_in_use'),
('ventilators_in_use_covid'),
('ventilators_in_use_covid_new');

DROP TABLE IF EXISTS data.covid;

CREATE TABLE data.us_covid (
    vintage DATE,
    dt date,
    fips INT references meta.us_fips(fips),
    variable_id SMALLINT REFERENCES meta.covid_variables(id),
    value INT,
    PRIMARY KEY (vintage, dt, fips, variable_id)
);

COMMENT ON TABLE data.us_covid IS E'Contains key count data for tracking COVID-19 cases across regions in the US.';

COMMENT ON COLUMN data.us_covid.vintage is E'The date when the data was accessed';
COMMENT ON COLUMN data.us_covid.dt is E'The date for which the data corresponds';
COMMENT ON COLUMN data.us_covid.fips is E'The 2 (5) digit fips code identifying us state (county)';
COMMENT ON COLUMN data.us_covid.variable_id is E'The id of the variable in this row. See table `meta.covid_variables` for more information. Variables can include:

- `cases_total`
- `deaths_total`
- `positive_tests_total`
- `negative_tests_total`
- `icu_beds_capacity_count`
- `icu_beds_in_use_any`
- `icu_beds_in_use_covid`
- `icu_beds_in_use_covid_new`
- `hospital_beds_capacity_count`
- `hospital_beds_in_use_any`
- `hospital_beds_in_use_covid`
- `hospital_beds_in_use_covid_new`
- `ventilators_capacity_count`
- `ventilators_in_use`
- `ventilators_in_use_covid`
- `ventilators_in_use_covid_new`
';
COMMENT ON COLUMN data.us_covid.value is E'The value of the variable for the given region, on a date, and a vintage';
