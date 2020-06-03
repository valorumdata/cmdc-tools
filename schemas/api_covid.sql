CREATE OR REPLACE VIEW api.covid_historical
 AS
 SELECT uc.vintage,
    uc.dt,
    uc.fips,
    cv.name AS variable,
    uc.value
   FROM data.us_covid uc
     LEFT JOIN meta.covid_variables cv ON cv.id = uc.variable_id;


COMMENT ON VIEW api.covid_historical IS E'This table contains relevant information on COVID-19

This table returns all vintages (data from different collection dates) of data in our system.

For only the most recent data, please use the `covid` endpoint.

Currently, the following variables are collected in the database

* `cases_suspected`: Total number of suspected cases
* `cases_confirmed`: Total number of confirmed cases
* `cases_total`: The number of suspected or confirmed cases
* `deaths_suspected`: The number of deaths that are suspected to have been caused by COVID-19
* `deaths_confirmed`: The number of deaths that are confirmed to have been caused by COVID-19
* `deaths_total`: The number of deaths that are either suspected or confirmed to have been caused by COVID-19
* `positive_tests_total`: The total number of tests that have been positive
* `negative_tests_total`: The total number of tests that have been negative
* `icu_beds_capacity_count`: The number of ICU beds available in the geography
* `icu_beds_in_use_any`: The number of ICU beds currently in use
* `icu_beds_in_use_covid_suspected`: The number of ICU beds currently in use by a patient suspected of COVID-19
* `icu_beds_in_use_covid_confirmed`: The number of ICU beds currently in use by a patient confirmed to have COVID-19
* `icu_beds_in_use_covid_total`: The number of ICU beds currently in use by a patient who is suspected of having or confirmed to have COVID-19
* `icu_beds_in_use_covid_new`: The number of ICU beds occupied by an individual suspected or confirmed of having COVID-19 that have been admitted today
* `hospital_beds_capacity_count`: The number of hospital beds available in the geography
* `hospital_beds_in_use_any`: The number of hospital beds currently in use
* `hospital_beds_in_use_covid_suspected`: The number of hospital beds currently in use by a patient suspected of COVID-19
* `hospital_beds_in_use_covid_confirmed`: The number of hospital beds currently in use by a patient confirmed to have COVID-19
* `hospital_beds_in_use_covid_total`: The number of hospital beds currently in use by a patient who is suspected of having or confirmed to have COVID-19
* `hospital_beds_in_use_covid_new`: The number of hospital beds occupied by an individual suspected or confirmed of having COVID-19 that have been admitted today
* `ventilators_capacity_count`: The number of individuals who can be supported by a ventilator
* `ventilators_in_use_any`: The number of individuals who are currently on a ventilator
* `ventilators_in_use_covid_suspected`: The number of individuals who are suspected of having COVID-19 that are currently on a ventilator
* `ventilators_in_use_covid_confirmed`: The number of individuals who are confirmed to have COVID-19 that are currently on a ventilator
* `ventilators_in_use_covid_total`: The number of individuals who are either suspected of having or confirmed to have COVID-19 that are on a ventilator
* `ventilators_in_use_covid_new`: The number of ventilators that are currently on a ventilator that are suspected of having or confirmed to have COVID-19 that started the ventilator today
* `recovered_total`: The number of individuals who tested positive for COVID-19 and no longer test positive
* `active_total`: The number of currently active COVID-19 cases

These variables are only collected from official US federal/state/county government sources
';


COMMENT ON COLUMN api.covid_historical.vintage is E'The date/time the data was collected and stored in our database';
COMMENT ON COLUMN api.covid_historical.dt is E'The date that corresponds to the observed variable';
COMMENT ON COLUMN api.covid_historical.fips is E'The fips code';
COMMENT ON COLUMN api.covid_historical.variable is E'One of the variables described in the table description';
COMMENT ON COLUMN api.covid_historical.value is E'The value of the variable';



CREATE OR REPLACE VIEW api.covid
WITH last_vintage as (
  SELECT dt, fips, variable_id, max(vintage) as vintage
  from data.us_covid uc
  group by (fips, dt, variable_id)
)
 SELECT lv.vintage,
    uc.dt,
    uc.fips,
    cv.name AS variable,
    uc.value
   FROM last_vintage lv
   LEFT JOIN data.us_covid uc using (fips, dt, vintage)
   LEFT JOIN meta.covid_variables cv ON cv.id = uc.variable_id
   where fips = 6037


COMMENT ON VIEW api.covid IS E'This table contains relevant information on COVID-19

This table only includes the most recent observation for each date, location, and variable. For a full history of all data we have collected see `covid_historical`

Currently, the following variables are collected in the database

* `cases_suspected`: Total number of suspected cases
* `cases_confirmed`: Total number of confirmed cases
* `cases_total`: The number of suspected or confirmed cases
* `deaths_suspected`: The number of deaths that are suspected to have been caused by COVID-19
* `deaths_confirmed`: The number of deaths that are confirmed to have been caused by COVID-19
* `deaths_total`: The number of deaths that are either suspected or confirmed to have been caused by COVID-19
* `positive_tests_total`: The total number of tests that have been positive
* `negative_tests_total`: The total number of tests that have been negative
* `icu_beds_capacity_count`: The number of ICU beds available in the geography
* `icu_beds_in_use_any`: The number of ICU beds currently in use
* `icu_beds_in_use_covid_suspected`: The number of ICU beds currently in use by a patient suspected of COVID-19
* `icu_beds_in_use_covid_confirmed`: The number of ICU beds currently in use by a patient confirmed to have COVID-19
* `icu_beds_in_use_covid_total`: The number of ICU beds currently in use by a patient who is suspected of having or confirmed to have COVID-19
* `icu_beds_in_use_covid_new`: The number of ICU beds occupied by an individual suspected or confirmed of having COVID-19 that have been admitted today
* `hospital_beds_capacity_count`: The number of hospital beds available in the geography
* `hospital_beds_in_use_any`: The number of hospital beds currently in use
* `hospital_beds_in_use_covid_suspected`: The number of hospital beds currently in use by a patient suspected of COVID-19
* `hospital_beds_in_use_covid_confirmed`: The number of hospital beds currently in use by a patient confirmed to have COVID-19
* `hospital_beds_in_use_covid_total`: The number of hospital beds currently in use by a patient who is suspected of having or confirmed to have COVID-19
* `hospital_beds_in_use_covid_new`: The number of hospital beds occupied by an individual suspected or confirmed of having COVID-19 that have been admitted today
* `ventilators_capacity_count`: The number of individuals who can be supported by a ventilator
* `ventilators_in_use_any`: The number of individuals who are currently on a ventilator
* `ventilators_in_use_covid_suspected`: The number of individuals who are suspected of having COVID-19 that are currently on a ventilator
* `ventilators_in_use_covid_confirmed`: The number of individuals who are confirmed to have COVID-19 that are currently on a ventilator
* `ventilators_in_use_covid_total`: The number of individuals who are either suspected of having or confirmed to have COVID-19 that are on a ventilator
* `ventilators_in_use_covid_new`: The number of ventilators that are currently on a ventilator that are suspected of having or confirmed to have COVID-19 that started the ventilator today
* `recovered_total`: The number of individuals who tested positive for COVID-19 and no longer test positive
* `active_total`: The number of currently active COVID-19 cases

These variables are only collected from official US federal/state/county government sources
';


COMMENT ON COLUMN api.covid.vintage is E'The date/time the data was collected and stored in our database. Only the most recent vintage is returned. See `covid_historical` for data with all';
COMMENT ON COLUMN api.covid.dt is E'The date that corresponds to the observed variable';
COMMENT ON COLUMN api.covid.fips is E'The fips code';
COMMENT ON COLUMN api.covid.variable is E'One of the variables described in the table description';
COMMENT ON COLUMN api.covid.value is E'The value of the variable';

