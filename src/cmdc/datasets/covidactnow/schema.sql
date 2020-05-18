CREATE TABLE meta.actnow_intervention_types (
    id smallint primary key,
    name text
);

INSERT INTO meta.actnow_intervention_types (id, name) VALUES
(1, 'NO_INTERVENTION'), (2, 'WEAK_INTERVENTION'), (3, 'STRONG_INTERVENTION'), (4, 'OBSERVED_INTERVENTION');

DROP TABLE IF EXISTS data.actnow_county_timeseries;
CREATE TABLE data.actnow_county_timeseries (
    "date" DATE,
    "vintage" DATE,
    "intervention_id" smallint references meta.actnow_intervention_types(id),
    "fips" int references data.us_counties(fips),
    "hospital_beds_required" INT,
    "hospital_bed_capacity" INT,
    "icu_beds_in_use" INT,
    "icu_bed_capacity" INT,
    "ventilators_in_use" INT,
    "ventilator_capacity" INT,
    "rt_indicator" numeric(12, 6),
    "rt_indicator_ci_90" numeric(12, 6),
    "cumulative_deaths" INT,
    "cumulative_infected" INT,
    "cumulative_positive_tests" INT,
    "cumulative_negative_tests" INT,
    PRIMARY KEY (date, vintage, intervention_id, fips)
);

COMMENT ON TABLE data.actnow_county_timeseries is E'This table includes the output of the COVID ActNow model for COVID-19. The model is built by a cross-disciplinary team of experts and provides projected values for the number of cases, deaths, hopsital load, and transmission rate at the county level.

For more information see the Covid ActNow website at https://covidactnow.org/

NOTE that all data in this table is the output of a model. Even for rows where date <= vintage the reported values are an interpolation to the real data by the model.

To see actual values as an input to the model please see the actnow_county_actual table.
';

COMMENT ON COLUMN data.actnow_county_timeseries.date is E'The projection date.';
COMMENT ON COLUMN data.actnow_county_timeseries.vintage is E'The date on which all projections were made.';
COMMENT ON COLUMN data.actnow_county_timeseries.intervention_id is E'A setting of parameters for different intervention types.

- `1` corresponds to no intervention and an R0 of 3.7
- `2` corresponds to weak intervention with social distancing only and an R0 of 1.7
- `3` corresponds to strong intervention with shelter in place orders and R0 of 1.1 for 4 weeks, 1.0 for 4 weeks and 0.8 for four weeks
- `4 corresponds to a dynamic measure of intervention based on observed policies (where availible). The R0 value is inferred from recent cases, hospitalizations, and deaths in each state';
COMMENT ON COLUMN data.actnow_county_timeseries.fips is E'The 5 digit US fips code for the county.';
COMMENT ON COLUMN data.actnow_county_timeseries.hospital_beds_required is E'The projected number of hopstial beds needed based on predicted number of active cases.';
COMMENT ON COLUMN data.actnow_county_timeseries.hospital_bed_capacity is E'The total known number of hopsital beds.';
COMMENT ON COLUMN data.actnow_county_timeseries.icu_beds_in_use is E'The number of projected ICU beds expected to be in use.';
COMMENT ON COLUMN data.actnow_county_timeseries.icu_bed_capacity is E'The total number of known ICU beds potentially available.';
COMMENT ON COLUMN data.actnow_county_timeseries.ventilators_in_use is E'The number of ventilators predicted to be in use';
COMMENT ON COLUMN data.actnow_county_timeseries.ventilator_capacity is E'The total known number of ventilators.';
COMMENT ON COLUMN data.actnow_county_timeseries.rt_indicator is E'The dynamic value of the re-infection rate.';
COMMENT ON COLUMN data.actnow_county_timeseries.rt_indicator_ci_90 is E'The 90th percentile confidence interval for the upper bound on the value of rt';
COMMENT ON COLUMN data.actnow_county_timeseries.cumulative_deaths is E'The proejcted number of cumulative COVID-19 deaths';
COMMENT ON COLUMN data.actnow_county_timeseries.cumulative_infected is E'The projected, cumulative number of persons infected with COVID-19.';
COMMENT ON COLUMN data.actnow_county_timeseries.cumulative_positive_tests is E'The projected, cumulative number of people who have tested positive for COVID-19.';
COMMENT ON COLUMN data.actnow_county_timeseries.cumulative_negative_tests is E'The projected, cumulative number of people who have tested negative for COVID-19.';


DROP TABLE IF EXISTS data.actnow_state_timeseries;
CREATE TABLE data.actnow_state_timeseries (
    "date" DATE,
    "vintage" DATE,
    "intervention_id" smallint references meta.actnow_intervention_types(id),
    "fips" int references data.us_states(fips),
    "hospital_beds_required" INT,
    "hospital_bed_capacity" INT,
    "icu_beds_in_use" INT,
    "icu_bed_capacity" INT,
    "ventilators_in_use" INT,
    "ventilator_capacity" INT,
    "rt_indicator" numeric(12, 6),
    "rt_indicator_ci_90" numeric(12, 6),
    "cumulative_deaths" INT,
    "cumulative_infected" INT,
    "cumulative_positive_tests" INT,
    "cumulative_negative_tests" INT,
    PRIMARY KEY (date, vintage, intervention_id, fips)
);

COMMENT ON TABLE data.actnow_state_timeseries is E'This table includes the output of the COVID ActNow model for COVID-19. The model is built by a cross-disciplinary team of experts and provides projected values for the number of cases, deaths, hopsital load, and transmission rate at the state level.

For more information see the Covid ActNow website at https://covidactnow.org/

NOTE that all data in this table is the output of a model. Even for rows where date <= vintage the reported values are an interpolation to the real data by the model.

To see actual values as an input to the model please see the actnow_state_actual table.';

COMMENT ON COLUMN data.actnow_state_timeseries.date is E'The projection date.';
COMMENT ON COLUMN data.actnow_state_timeseries.vintage is E'The date on which all projections were made.';
COMMENT ON COLUMN data.actnow_state_timeseries.intervention_id is E'A setting of parameters for different intervention types.

- `1` corresponds to no intervention and an R0 of 3.7
- `2` corresponds to weak intervention with social distancing only and an R0 of 1.7
- `3` corresponds to strong intervention with shelter in place orders and R0 of 1.1 for 4 weeks, 1.0 for 4 weeks and 0.8 for four weeks
- `4 corresponds to a dynamic measure of intervention based on observed policies (where availible). The R0 value is inferred from recent cases, hospitalizations, and deaths in each state';
COMMENT ON COLUMN data.actnow_state_timeseries.fips is E'The 2 digit US fips code for the state.';
COMMENT ON COLUMN data.actnow_state_timeseries.hospital_beds_required is E'The projected number of hopstial beds needed based on predicted number of active cases.';
COMMENT ON COLUMN data.actnow_state_timeseries.hospital_bed_capacity is E'The total known number of hopsital beds.';
COMMENT ON COLUMN data.actnow_state_timeseries.icu_beds_in_use is E'The number of projected ICU beds expected to be in use.';
COMMENT ON COLUMN data.actnow_state_timeseries.icu_bed_capacity is E'The total number of known ICU beds potentially available.';
COMMENT ON COLUMN data.actnow_state_timeseries.ventilators_in_use is E'The number of ventilators predicted to be in use';
COMMENT ON COLUMN data.actnow_state_timeseries.ventilator_capacity is E'The total known number of ventilators.';
COMMENT ON COLUMN data.actnow_state_timeseries.rt_indicator is E'The dynamic value of the re-infection rate.';
COMMENT ON COLUMN data.actnow_state_timeseries.rt_indicator_ci_90 is E'The 90th percentile confidence interval for the upper bound on the value of rt';
COMMENT ON COLUMN data.actnow_state_timeseries.cumulative_deaths is E'The proejcted number of cumulative COVID-19 deaths';
COMMENT ON COLUMN data.actnow_state_timeseries.cumulative_infected is E'The projected, cumulative number of persons infected with COVID-19.';
COMMENT ON COLUMN data.actnow_state_timeseries.cumulative_positive_tests is E'The projected, cumulative number of people who have tested positive for COVID-19.';
COMMENT ON COLUMN data.actnow_state_timeseries.cumulative_negative_tests is E'The projected, cumulative number of people who have tested negative for COVID-19.';

DROP TABLE IF EXISTS data.actnow_county_actuals;
CREATE TABLE data.actnow_county_actuals (
    "vintage" DATE,
    "date" DATE,
    "fips" int references data.us_counties(fips),
    "intervention_id" smallint references meta.actnow_intervention_types(id),
    "cumulative_confirmed_cases" INT,
    "cumulative_positive_tests" INT,
    "cumulative_negative_tests" INT,
    "cumulative_deaths" INT,
    "hospital_beds_capacity" INT,
    "hospital_beds_total_capacity" INT,
    "hospital_beds_current_usage_covid" INT,
    "hospital_beds_current_usage_total" INT,
    "hospital_beds_typical_usage_rate" INT,
    "icu_beds_capacity" INT,
    "icu_beds_total_capacity" INT,
    "icu_beds_current_usage_covid" INT,
    "icu_beds_current_usage_total" INT,
    "icu_beds_typical_usage_rate" INT,
    PRIMARY KEY ("vintage", "date", "fips")
);

COMMENT ON TABLE data.actnow_county_actuals is E'';

COMMENT ON COLUMN data.actnow_county_actuals.intervention_id is E'A setting of parameters for different intervention types.

- `1` corresponds to no intervention and an R0 of 3.7
- `2` corresponds to weak intervention with social distancing only and an R0 of 1.7
- `3` corresponds to strong intervention with shelter in place orders and R0 of 1.1 for 4 weeks, 1.0 for 4 weeks and 0.8 for four weeks
- `4 corresponds to a dynamic measure of intervention based on observed policies (where availible). The R0 value is inferred from recent cases, hospitalizations, and deaths in each state';
COMMENT ON COLUMN data.actnow_county_actuals.cumulative_confirmed_cases is E'Cumulative number of confirmed COVID-19 cases';
COMMENT ON COLUMN data.actnow_county_actuals.cumulative_positive_tests is E'Cumulative number of positive test cases.';
COMMENT ON COLUMN data.actnow_county_actuals.cumulative_negative_tests is E'Cumulative number of negative test cases.';
COMMENT ON COLUMN data.actnow_county_actuals.cumulative_deaths is E'Cumulative number of COVID-19 related deaths.';
COMMENT ON COLUMN data.actnow_county_actuals."date" is E'The date for which the data applies';
COMMENT ON COLUMN data.actnow_county_actuals.fips is E'The 5 digit FIPS code for the US county.';
COMMENT ON COLUMN data.actnow_county_actuals.vintage is E'The date on which the data was reported.';
COMMENT ON COLUMN data.actnow_county_actuals.hospital_beds_capacity is E'The known capacity of hospital beds';
COMMENT ON COLUMN data.actnow_county_actuals.hospital_beds_total_capacity is E'';
COMMENT ON COLUMN data.actnow_county_actuals.hospital_beds_current_usage_covid is E'The number of hopsital beds known to be used by COVID-19 patients.';
COMMENT ON COLUMN data.actnow_county_actuals.hospital_beds_current_usage_total is E'The total number of hospital beds currently in use.';
COMMENT ON COLUMN data.actnow_county_actuals.hospital_beds_typical_usage_rate is E'The typical usage rate of hopsital beds.';
COMMENT ON COLUMN data.actnow_county_actuals.icu_beds_capacity is E'The known capacity of ICU beds';
COMMENT ON COLUMN data.actnow_county_actuals.icu_beds_total_capacity is E'';
COMMENT ON COLUMN data.actnow_county_actuals.icu_beds_current_usage_covid is E'The number of hopsital beds known to be used by COVID-19 patients.';
COMMENT ON COLUMN data.actnow_county_actuals.icu_beds_current_usage_total is E'The total number of ICU beds currently in use.';
COMMENT ON COLUMN data.actnow_county_actuals.icu_beds_typical_usage_rate is E'The typical usage rate of hopsital beds.';

DROP TABLE IF EXISTS data.actnow_state_actuals;
CREATE TABLE data.actnow_state_actuals (
    "vintage" DATE,
    "date" DATE,
    "fips" int references data.us_states(fips),
    "intervention_id" smallint references meta.actnow_intervention_types(id),
    "cumulative_confirmed_cases" INT,
    "cumulative_positive_tests" INT,
    "cumulative_negative_tests" INT,
    "cumulative_deaths" INT,
    "hospital_beds_capacity" INT,
    "hospital_beds_total_capacity" INT,
    "hospital_beds_current_usage_covid" INT,
    "hospital_beds_current_usage_total" INT,
    "hospital_beds_typical_usage_rate" INT,
    "icu_beds_capacity" INT,
    "icu_beds_total_capacity" INT,
    "icu_beds_current_usage_covid" INT,
    "icu_beds_current_usage_total" INT,
    "icu_beds_typical_usage_rate" INT,
    PRIMARY KEY ("vintage", "date", "fips")
);

COMMENT ON TABLE data.actnow_state_actuals is E'';

COMMENT ON COLUMN data.actnow_state_actuals.intervention_id is E'A setting of parameters for different intervention types.

- `1` corresponds to no intervention and an R0 of 3.7
- `2` corresponds to weak intervention with social distancing only and an R0 of 1.7
- `3` corresponds to strong intervention with shelter in place orders and R0 of 1.1 for 4 weeks, 1.0 for 4 weeks and 0.8 for four weeks
- `4 corresponds to a dynamic measure of intervention based on observed policies (where availible). The R0 value is inferred from recent cases, hospitalizations, and deaths in each state';
COMMENT ON COLUMN data.actnow_state_actuals.cumulative_confirmed_cases is E'Cumulative number of confirmed COVID-19 cases';
COMMENT ON COLUMN data.actnow_state_actuals.cumulative_positive_tests is E'Cumulative number of positive test cases.';
COMMENT ON COLUMN data.actnow_state_actuals.cumulative_negative_tests is E'Cumulative number of negative test cases.';
COMMENT ON COLUMN data.actnow_state_actuals.cumulative_deaths is E'Cumulative number of COVID-19 related deaths.';
COMMENT ON COLUMN data.actnow_state_actuals."date" is E'The date for which the data applies';
COMMENT ON COLUMN data.actnow_state_actuals.fips is E'The 2 digit FIPS code for the US state.';
COMMENT ON COLUMN data.actnow_state_actuals.vintage is E'The date on which the data was reported.';
COMMENT ON COLUMN data.actnow_state_actuals.hospital_beds_capacity is E'The known capacity of hospital beds';
COMMENT ON COLUMN data.actnow_state_actuals.hospital_beds_total_capacity is E'';
COMMENT ON COLUMN data.actnow_state_actuals.hospital_beds_current_usage_covid is E'The number of hopsital beds known to be used by COVID-19 patients.';
COMMENT ON COLUMN data.actnow_state_actuals.hospital_beds_current_usage_total is E'The total number of hospital beds currently in use.';
COMMENT ON COLUMN data.actnow_state_actuals.hospital_beds_typical_usage_rate is E'The typical usage rate of hopsital beds.';
COMMENT ON COLUMN data.actnow_state_actuals.icu_beds_capacity is E'The known capacity of ICU beds';
COMMENT ON COLUMN data.actnow_state_actuals.icu_beds_total_capacity is E'';
COMMENT ON COLUMN data.actnow_state_actuals.icu_beds_current_usage_covid is E'The number of hopsital beds known to be used by COVID-19 patients.';
COMMENT ON COLUMN data.actnow_state_actuals.icu_beds_current_usage_total is E'The total number of ICU beds currently in use.';
COMMENT ON COLUMN data.actnow_state_actuals.icu_beds_typical_usage_rate is E'The typical usage rate of hopsital beds.';
