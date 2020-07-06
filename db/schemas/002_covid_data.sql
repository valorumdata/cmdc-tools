DROP TABLE IF EXISTS meta.covid_variables;
CREATE TABLE meta.covid_variables (
    id serial primary key,
    name text UNIQUE
);

COMMENT ON TABLE meta.covid_variables IS E'This table contains a list of variables and their corresponding identifiers used in `data.us_covid`. The variables include:

* cases_suspected: The number of cases that are suspected, but not confirmed, to have COVID in the geography
* cases_confirmed: The number of cases that are confirmed to have COVID in the geography
* cases_total: Total number of cases, both confirmed and suspected, in the geography
* deaths_suspected: The total number of deaths that are suspected to have been caused, but not confirmed to have been caused, by COVID in the geography
* deaths_confirmed: Total number of deaths that have been confirmed to have been caused by COVID in the geography
* deaths_total: Total number of deaths including both suspected and confirmed
* positive_tests_total: The total number of tests that have returned positive for COVID
* negative_tests_total: The total number of tests that have returned negative for COVID
* tests_total: The total number of tests administered
* recovered_total: The total number of individuals who have recovered from COVID, to date
* active_total: The number of currently active COVID cases
* icu_beds_capacity_count: The number of ICU beds available in a particular geography
* icu_beds_in_use_any: The number of ICU beds currently occupied by a patient
* icu_beds_in_use_covid_suspected: The number of ICU beds occupied by a patient that is suspected to have COVID
* icu_beds_in_use_covid_confirmed: The number of ICU beds occupied by a patient that is confirmed to have COVID
* icu_beds_in_use_covid_total: The total number of ICU beds occupied by a patient that is suspected or confirmed to have COVID
* icu_beds_in_use_covid_new: The number of new patients admitted to the ICU that are suspected or confirmed to have COVID
* hospital_beds_capacity_count: The number of hospital beds available in a particular geography
* hospital_beds_in_use_any: The number of hospital beds currently occupied by a patient
* hospital_beds_in_use_covid_suspected: The number of hospital beds occupied by a patient that is suspected to have COVID
* hospital_beds_in_use_covid_confirmed: The number of hospital beds occupied by a patient that is confirmed to have COVID
* hospital_beds_in_use_covid_total: The total number of hospital beds occupied by a patient that is suspected or confirmed to have COVID
* hospital_beds_in_use_covid_new: The number of new patients admitted to the hospital that are suspected or confirmed to have COVID
* ventilators_capacity_count: The number of patients that can be supported by the geographies current ventilators
* ventilators_in_use_any: The number of patients currently being supported by a ventilator
* ventilators_in_use_covid_suspected: The number of patients that are suspected of having COVID that are being supported by a ventilator
* ventilators_in_use_covid_confirmed: The number of patients that are confirmed to have COVID that are being supported by a ventilator
* ventilators_in_use_covid_total: The total number of patients being supported by a ventilator who are confirmed or suspected of having COVID
* ventilators_in_use_covid_new: The number of new patients who have been put on a ventilator
';

COMMENT ON COLUMN meta.covid_variables.id is E'The variable id used in `data.us_covid`';
COMMENT ON COLUMN meta.covid_variables.name is E'The variable name as described in the table description';

INSERT INTO meta.covid_variables (name) VALUES
  ('cases_suspected'),
  ('cases_confirmed'),
  ('cases_total'),
  ('deaths_suspected'),
  ('deaths_confirmed'),
  ('deaths_total'),
  ('positive_tests_total'),
  ('negative_tests_total'),
  ('icu_beds_capacity_count'),
  ('icu_beds_in_use_any'),
  ('icu_beds_in_use_covid_suspected'),
  ('icu_beds_in_use_covid_confirmed'),
  ('icu_beds_in_use_covid_total'),
  ('icu_beds_in_use_covid_new'),
  ('hospital_beds_capacity_count'),
  ('hospital_beds_in_use_any'),
  ('hospital_beds_in_use_covid_suspected'),
  ('hospital_beds_in_use_covid_confirmed'),
  ('hospital_beds_in_use_covid_total'),
  ('hospital_beds_in_use_covid_new'),
  ('ventilators_capacity_count'),
  ('ventilators_in_use_any'),
  ('ventilators_in_use_covid_suspected'),
  ('ventilators_in_use_covid_confirmed'),
  ('ventilators_in_use_covid_total'),
  ('ventilators_in_use_covid_new'),
  ('recovered_total'),
  ('active_total'),
  ('tests_total');

DROP TABLE IF EXISTS data.covid;

CREATE TABLE data.us_covid (
    vintage DATE,
    dt date,
    fips INT references meta.us_fips(fips),
    variable_id SMALLINT REFERENCES meta.covid_variables(id),
    value INT,
    PRIMARY KEY (fips, dt, vintage, variable_id)
);

COMMENT ON TABLE data.us_covid IS E'Contains key count data for tracking COVID-19 cases across regions in the US.';

COMMENT ON COLUMN data.us_covid.vintage is E'The date when the data was accessed';
COMMENT ON COLUMN data.us_covid.dt is E'The date for which the data corresponds';
COMMENT ON COLUMN data.us_covid.fips is E'The 2 (5) digit fips code identifying us state (county)';
COMMENT ON COLUMN data.us_covid.variable_id is E'The id of the variable in this row. See table `meta.covid_variables` for more information.
';
COMMENT ON COLUMN data.us_covid.value is E'The value of the variable for the given region, on a date, and a vintage';
