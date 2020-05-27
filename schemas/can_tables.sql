
DROP TABLE IF EXISTS meta.actnow_intervention_types;
CREATE TABLE meta.actnow_intervention_types (
    id smallint primary key,
    name text
);

INSERT INTO meta.actnow_intervention_types (id, name) VALUES
  (1, 'NO_INTERVENTION'), (2, 'WEAK_INTERVENTION'),
  (3, 'STRONG_INTERVENTION'), (4, 'OBSERVED_INTERVENTION');

create table meta.actnow_timeseries_variables (
    id serial primary key,
    name text
);

INSERT INTO meta.actnow_timeseries_variables (id, name) VALUES
(1, 'cumulative_deaths'),
(2, 'cumulative_infected'),
(3, 'cumulative_negative_tests'),
(4, 'cumulative_positive_tests'),
(5, 'hospital_bed_capacity'),
(6, 'hospital_beds_required'),
(7, 'icu_bed_capacity'),
(8, 'icu_beds_in_use'),
(9, 'rt_indicator'),
(10, 'rt_indicator_ci_90'),
(11, 'ventilator_capacity'),
(12, 'ventilators_in_use');

create table meta.actnow_actual_variables (
    id serial primary key,
    name text
);

INSERT INTO meta.actnow_actual_variables (id, name) VALUES
(1, 'cumulative_confirmed_cases'),
(2, 'cumulative_deaths'),
(3, 'cumulative_negative_tests'),
(4, 'cumulative_positive_tests'),
(5, 'hospital_beds_capacity'),
(6, 'hospital_beds_current_usage_covid'),
(7, 'hospital_beds_current_usage_total'),
(8, 'hospital_beds_total_capacity'),
(9, 'hospital_beds_typical_usage_rate'),
(10, 'icu_beds_capacity'),
(11, 'icu_beds_current_usage_covid'),
(12, 'icu_beds_current_usage_total'),
(13, 'icu_beds_total_capacity'),
(14, 'icu_beds_typical_usage_rate');

DROP TABLE IF EXISTS data.actnow_timeseries;
CREATE TABLE data.actnow_timeseries (
    "date" DATE,
    "vintage" DATE,
    "intervention_id" smallint references meta.actnow_intervention_types(id),
    "fips" int references meta.us_fips(fips),
    "variable_id" smallint references meta.actnow_timeseries_variables,
    "value" INT,
    PRIMARY KEY (vintage, intervention_id, date, fips, variable_id)
);

COMMENT ON TABLE data.actnow_timeseries is E'This table includes the output of the COVID ActNow model for COVID-19. The model is built by a cross-disciplinary team of experts and provides projected values for the number of cases, deaths, hopsital load, and transmission rate at state and county levels.

For more information see the Covid ActNow website at https://covidactnow.org/

NOTE that all data in this table is the output of a model. Even for rows where date <= vintage the reported values are an interpolation to the real data by the model.

To see actual values as an input to the model please see the `data.actnow_actual` table.
';

COMMENT ON COLUMN data.actnow_timeseries.date is E'The projection date.';
COMMENT ON COLUMN data.actnow_timeseries.vintage is E'The date on which all projections were made.';
COMMENT ON COLUMN data.actnow_timeseries.intervention_id is E'A setting of parameters for different intervention types.

- `1` corresponds to no intervention and an R0 of 3.7
- `2` corresponds to weak intervention with social distancing only and an R0 of 1.7
- `3` corresponds to strong intervention with shelter in place orders and R0 of 1.1 for 4 weeks, 1.0 for 4 weeks and 0.8 for four weeks
- `4 corresponds to a dynamic measure of intervention based on observed policies (where availible). The R0 value is inferred from recent cases, hospitalizations, and deaths in each state';
COMMENT ON COLUMN data.actnow_timeseries.fips is E'The 5 digit US fips code for the county or 2 digit code for a US state.';
COMMENT ON COLUMN data.actnow_timeseries.variable_id is E'The ID of the variable for this row. See `meta.act_now_timeseries_variables` for a description. Potential variables are

- cumulative_confirmed_cases
- cumulative_deaths
- cumulative_negative_tests
- cumulative_positive_tests
- hospital_beds_capacity
- hospital_beds_current_usage_covid
- hospital_beds_current_usage_total
- hospital_beds_total_capacity
- hospital_beds_typical_usage_rate
- icu_beds_capacity
- icu_beds_current_usage_covid
- icu_beds_current_usage_total
- icu_beds_total_capacity
- icu_beds_typical_usage_rate
';
COMMENT ON COLUMN data.actnow_county_timeseries.value is E'The value of the variable for the state (or county), date, as of vintage, assuming a particular intervention time';

DROP TABLE IF EXISTS data.actnow_actual;
CREATE TABLE data.actnow_actual (
    "date" DATE,
    "vintage" DATE,
    "intervention_id" smallint references meta.actnow_intervention_types(id),
    "fips" int references meta.us_fips(fips),
    "variable_id" smallint references meta.actnow_timeseries_variables,
    "value" real,
    PRIMARY KEY (vintage, date, fips, variable_id)
);

COMMENT ON TABLE data.actnow_actual is E'This table includes the output of the COVID ActNow model for COVID-19. The model is built by a cross-disciplinary team of experts and provides projected values for the number of cases, deaths, hopsital load, and transmission rate at state and county levels.

For more information see the Covid ActNow website at https://covidactnow.org/

NOTE that all data in this table is the output of a model. Even for rows where date <= vintage the reported values are an interpolation to the real data by the model.

To see actual values as an input to the model please see the `data.actnow_actual` table.
';

COMMENT ON COLUMN data.actnow_actual.date is E'The projection date.';
COMMENT ON COLUMN data.actnow_actual.vintage is E'The date on which all projections were made.';
COMMENT ON COLUMN data.actnow_actual.intervention_id is E'A setting of parameters for different intervention types.

- `1` corresponds to no intervention and an R0 of 3.7
- `2` corresponds to weak intervention with social distancing only and an R0 of 1.7
- `3` corresponds to strong intervention with shelter in place orders and R0 of 1.1 for 4 weeks, 1.0 for 4 weeks and 0.8 for four weeks
- `4 corresponds to a dynamic measure of intervention based on observed policies (where availible). The R0 value is inferred from recent cases, hospitalizations, and deaths in each state';
COMMENT ON COLUMN data.actnow_actual.fips is E'The 5 digit US fips code for the county or 2 digit code for a US state.';
COMMENT ON COLUMN data.actnow_actual.variable_id is E'The ID of the variable for this row. See `meta.act_now_timeseries_variables` for a description. Potential variables are

- cumulative_confirmed_cases
- cumulative_deaths
- cumulative_negative_tests
- cumulative_positive_tests
- hospital_beds_capacity
- hospital_beds_current_usage_covid
- hospital_beds_current_usage_total
- hospital_beds_total_capacity
- hospital_beds_typical_usage_rate
- icu_beds_capacity
- icu_beds_current_usage_covid
- icu_beds_current_usage_total
- icu_beds_total_capacity
- icu_beds_typical_usage_rate
';
COMMENT ON COLUMN data.actnow_county_timeseries.value is E'The value of the variable for the state (or county), date, as of a particular vintage';
