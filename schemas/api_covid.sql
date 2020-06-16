/*
CREATE OR REPLACE VIEW api.jhu_covid AS
  WITH last_vintage as (
    SELECT fips, variable_id, MAX(vintage) AS vintage
    FROM data.jhu_covid
    GROUP BY (fips, variable_id)
  )
  SELECT jhu.dt, jhu.fips, cv.name as variable, jhu.value
  FROM last_vintage lv
  LEFT JOIN data.jhu_covid nyt using (fips, variable_id, vintage)
  LEFT JOIN meta.covid_variables cv ON cv.id = uc.variable_id;
*/

CREATE OR REPLACE VIEW api.nytimes_covid AS
  WITH last_vintage as (
    SELECT fips, variable_id, MAX(vintage) AS vintage
    FROM data.nyt_covid
    GROUP BY (fips, variable_id)
  )
  SELECT nyt.dt, nyt.fips, cv.name as variable, nyt.value
  FROM last_vintage lv
  LEFT JOIN data.nyt_covid nyt using (fips, variable_id, vintage)
  LEFT JOIN meta.covid_variables cv ON cv.id = uc.variable_id;

COMMENT ON VIEW api.nytimes_covid IS E'This table contains the data from the NY Times COVID data

This table only includes the most recent observation for each date, location, and variable. If you are interested in historical revisions of this data, please reach out -- We have previous "vintages" of the NYT data but, in order to simplify our list of tables, we have chosen not to expose (but are happy to if it would be useful).

The data only includes total number of cases and total number of COVID related deaths. If you use this data, we recommend that you read the corresponding documentation on their github site as it provides useful insights to when certain variables changed how they were collected etc...

The NYTimes COVID data can be found online at https://github.com/nytimes/covid-19-data and is released under the following license:

Copyright 2020 by The New York Times Company

In light of the current public health emergency, The New York Times Company is
providing this database under the following free-of-cost, perpetual,
non-exclusive license. Anyone may copy, distribute, and display the database, or
any part thereof, and make derivative works based on it, provided  (a) any such
use is for non-commercial purposes only and (b) credit is given to The New York
Times in any public display of the database, in any publication derived in part
or in full from the database, and in any other public use of the data contained
in or derived from the database.

By accessing or copying any part of the database, the user accepts the terms of
this license. Anyone seeking to use the database for other purposes is required
to contact The New York Times Company at covid-data@nytimes.com to obtain
permission.

The New York Times has made every effort to ensure the accuracy of the
information. However, the database may contain typographic errors or
inaccuracies and may not be complete or current at any given time. Licensees
further agree to assume all liability for any claims that may arise from or
relate in any way to their use of the database and to hold The New York Times
Company harmless from any such claims.
';

COMMENT ON COLUMN api.nytimes_covid.dt is E'The date of the observation';
COMMENT ON COLUMN api.nytimes_covid.fips is E'The fips code corresponding to the observation';
COMMENT ON COLUMN api.nytimes_covid.variable is E'Denotes whether observation is total cases or total deaths';
COMMENT ON COLUMN api.nytimes_covid.value is E'The value of the observation';


/* The covid view */
CREATE OR REPLACE VIEW api.covid AS
WITH last_vintage as (
  SELECT dt, fips, variable_id, max(vintage) as vintage
  from data.us_covid uc
  group by (dt, fips, variable_id)
)
 SELECT lv.vintage,
    uc.dt,
    uc.fips,
    cv.name AS variable,
    uc.value
   FROM last_vintage lv
   LEFT JOIN data.us_covid uc using (dt, fips, variable_id, vintage)
   LEFT JOIN meta.covid_variables cv ON cv.id = uc.variable_id;


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


/* Historical view with vintages */

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
