DROP TABLE IF EXISTS data.owid_locations CASCADE;

CREATE TABLE data.owid_locations (
"iso_code" TEXT primary key,
"continent" TEXT,
"location" TEXT,
"population" REAL,
"population_density" REAL,
"median_age" REAL,
"aged_65_older" REAL,
"aged_70_older" REAL,
"gdp_per_capita" REAL,
"extreme_poverty" REAL,
"cvd_death_rate" REAL,
"diabetes_prevalence" REAL,
"female_smokers" REAL,
"male_smokers" REAL,
"handwashing_facilities" REAL,
"hospital_beds_per_thousand" REAL,
"life_expectancy" REAL
);

drop table if exists data.owid_covid;
CREATE TABLE data.owid_covid (
iso_code text references data.owid_locations(iso_code),
"dt" date,
"total_cases" int,
"new_cases" int,
"total_deaths" int,
"new_deaths" int,
"total_cases_per_million" REAL,
"new_cases_per_million" REAL,
"total_deaths_per_million" REAL,
"new_deaths_per_million" REAL,
"total_tests" int,
"new_tests" int,
"new_tests_smoothed" REAL,
"total_tests_per_thousand" REAL,
"new_tests_per_thousand" REAL,
"new_tests_smoothed_per_thousand" REAL,
"tests_units" TEXT,
"stringency_index" REAL,
    primary key (iso_code, dt)
);
