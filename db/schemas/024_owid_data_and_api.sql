DROP TABLE IF EXISTS data.owid_locations CASCADE;

CREATE TABLE data.owid_locations
(
    "iso_code"                   text PRIMARY KEY,
    "continent"                  text,
    "location"                   text,
    "population"                 real,
    "population_density"         real,
    "median_age"                 real,
    "aged_65_older"              real,
    "aged_70_older"              real,
    "gdp_per_capita"             real,
    "extreme_poverty"            real,
    "cvd_death_rate"             real,
    "diabetes_prevalence"        real,
    "female_smokers"             real,
    "male_smokers"               real,
    "handwashing_facilities"     real,
    "hospital_beds_per_thousand" real,
    "life_expectancy"            real
);

DROP TABLE IF EXISTS data.owid_covid;

CREATE TABLE data.owid_covid
(
    iso_code                          text REFERENCES data.owid_locations (iso_code),
    "dt"                              date,
    "total_cases"                     int,
    "new_cases"                       int,
    "total_deaths"                    int,
    "new_deaths"                      int,
    "total_cases_per_million"         real,
    "new_cases_per_million"           real,
    "total_deaths_per_million"        real,
    "new_deaths_per_million"          real,
    "total_tests"                     int,
    "new_tests"                       int,
    "new_tests_smoothed"              real,
    "total_tests_per_thousand"        real,
    "new_tests_per_thousand"          real,
    "new_tests_smoothed_per_thousand" real,
    "tests_units"                     text,
    "stringency_index"                real,
    PRIMARY KEY (iso_code, dt)
);

DROP VIEW IF EXISTS api.covid_global;

CREATE VIEW api.covid_global AS
SELECT "iso_code",
       "continent",
       "location",
       "dt",
       "total_cases",
       "new_cases",
       "total_deaths",
       "new_deaths",
       "total_cases_per_million",
       "new_cases_per_million",
       "total_deaths_per_million",
       "new_deaths_per_million",
       "total_tests",
       "new_tests",
       "new_tests_smoothed",
       "total_tests_per_thousand",
       "new_tests_per_thousand",
       "new_tests_smoothed_per_thousand",
       "tests_units",
       "stringency_index",
       "population",
       "population_density",
       "median_age",
       "aged_65_older",
       "aged_70_older",
       "gdp_per_capita",
       "extreme_poverty",
       "cvd_death_rate",
       "diabetes_prevalence",
       "female_smokers",
       "male_smokers",
       "handwashing_facilities",
       "hospital_beds_per_thousand",
       "life_expectancy"
FROM data.owid_covid
         LEFT JOIN data.owid_locations USING (iso_code);

COMMENT ON VIEW api.covid_global IS E'This table contains the complete Our World in Data\'s COVID-19 dataset. Please see the [original source](https://ourworldindata.org/coronavirus-data) for more information.

All of Our World in Data is completely open access and all work is licensed under the Creative Commons BY license. You have the permission to use, distribute, and reproduce in any medium, provided the source and authors are credited.

This data has been collected, aggregated, and documented by Diana Beltekian, Daniel Gavrilov, Charlie Giattino, Joe Hasell, Bobbie Macdonald, Edouard Mathieu, Esteban Ortiz-Ospina, Hannah Ritchie, Max Roser.

The mission of _Our World in Data_ is to make data and research on the world’s largest problems understandable and accessible. [Read more about our mission](https://ourworldindata.org/about).

The following documentation is taken from the Our World in Data [COVID-19 page](https://ourworldindata.org/coronavirus-data) and the corresponding [GitHub repository](https://github.com/owid/covid-19-data/tree/master/public/data):

The complete COVID-19 dataset is a collection of the COVID-19 data maintained by Our World in Data. It is updated daily and includes data on confirmed cases, deaths, and testing, as well as other variables of potential interest.

- **Confirmed cases and deaths:** our data comes from the [European Centre for Disease Prevention and Control](https://www.ecdc.europa.eu/en/publications-data/download-todays-data-geographic-distribution-covid-19-cases-worldwide) (ECDC). We discuss how and when the ECDC collects and publishes this data [here](https://ourworldindata.org/coronavirus-source-data). The cases & deaths dataset is updated daily. *Note: the number of cases or deaths reported by any institution—including the ECDC, the WHO, Johns Hopkins and others—on a given day does not necessarily represent the actual number on that date. This is because of the long reporting chain that exists between a new case/death and its inclusion in statistics. This also means that negative values in cases and deaths can sometimes appear when a country sends a correction to the ECDC, because it had previously overestimated the number of cases/deaths.*
- **Testing for COVID-19:** this data is collected by the _Our World in Data_ team from official reports; you can find further details in our post on COVID-19 testing, including our [checklist of questions to understand testing data](https://ourworldindata.org/coronavirus-testing#our-checklist-for-covid-19-testing-data), information on [geographical and temporal coverage](https://ourworldindata.org/coronavirus-testing#which-countries-do-we-have-testing-data-for), and [detailed country-by-country source information](https://ourworldindata.org/coronavirus-testing#our-checklist-for-covid-19-testing-data). The testing dataset is updated around twice a week.
- **Other variables:** this data is collected from a variety of sources (United Nations, World Bank, Global Burden of Disease, Blavatnik School of Government, etc.). More information is available in [our codebook](https://github.com/owid/covid-19-data/tree/master/public/data/owid-covid-data-codebook.md).
';

COMMENT ON COLUMN api.covid_global.iso_code IS E'ISO 3166-1 alpha-3 – three-letter country codes|International Organization for Standardization';

COMMENT ON COLUMN api.covid_global.continent IS E'Continent of the geographical location|Our World in Data';

COMMENT ON COLUMN api.covid_global.location IS E'Geographical location|Our World in Data';

COMMENT ON COLUMN api.covid_global.dt IS E'Date of observation|Our World in Data';

COMMENT ON COLUMN api.covid_global.total_cases IS E'Total confirmed cases of COVID-19|European Centre for Disease Prevention and Control';

COMMENT ON COLUMN api.covid_global.new_cases IS E'New confirmed cases of COVID-19|European Centre for Disease Prevention and Control';

COMMENT ON COLUMN api.covid_global.total_deaths IS E'Total deaths attributed to COVID-19|European Centre for Disease Prevention and Control';

COMMENT ON COLUMN api.covid_global.new_deaths IS E'New deaths attributed to COVID-19|European Centre for Disease Prevention and Control';

COMMENT ON COLUMN api.covid_global.total_cases_per_million IS E'Total confirmed cases of COVID-19 per 1,000,000 people|European Centre for Disease Prevention and Control';

COMMENT ON COLUMN api.covid_global.new_cases_per_million IS E'New confirmed cases of COVID-19 per 1,000,000 people|European Centre for Disease Prevention and Control';

COMMENT ON COLUMN api.covid_global.total_deaths_per_million IS E'Total deaths attributed to COVID-19 per 1,000,000 people|European Centre for Disease Prevention and Control';

COMMENT ON COLUMN api.covid_global.new_deaths_per_million IS E'New deaths attributed to COVID-19 per 1,000,000 people|European Centre for Disease Prevention and Control';

COMMENT ON COLUMN api.covid_global.total_tests IS E'Total tests for COVID-19|National government reports';

COMMENT ON COLUMN api.covid_global.new_tests IS E'New tests for COVID-19|National government reports';

COMMENT ON COLUMN api.covid_global.new_tests_smoothed IS E'ew tests for COVID-19 (7-day smoothed). For countries that do not report testing data on a daily basis, we assume that testing changed equally on a daily basis over any periods in which no data was reported. This produces a complete series of daily figures, which is then averaged over a rolling 7-day window|National government reports';

COMMENT ON COLUMN api.covid_global.total_tests_per_thousand IS E'Total tests for COVID-19 per 1,000 people|National government reports';

COMMENT ON COLUMN api.covid_global.new_tests_per_thousand IS E'New tests for COVID-19 per 1,000 people|National government reports';

COMMENT ON COLUMN api.covid_global.new_tests_smoothed_per_thousand IS E'New tests for COVID-19 (7-day smoothed) per 1,000 people|National government reports';

COMMENT ON COLUMN api.covid_global.tests_units IS E'Units used by the location to report its testing data|National government reports';

COMMENT ON COLUMN api.covid_global.stringency_index IS E'Government Response Stringency Index: composite measure based on 9 response indicators including school closures, workplace closures, and travel bans, rescaled to a value from 0 to 100 (100 = strictest response)|Oxford COVID-19 Government Response Tracker, Blavatnik School of Government';

COMMENT ON COLUMN api.covid_global.population IS E'Population in 2020|United Nations, Department of Economic and Social Affairs, Population Division, World Population Prospects: The 2019 Revision';

COMMENT ON COLUMN api.covid_global.population_density IS E'Number of people divided by land area, measured in square kilometers, most recent year available|World Bank – World Development Indicators, sourced from Food and Agriculture Organization and World Bank estimates';

COMMENT ON COLUMN api.covid_global.median_age IS E'Median age of the population, UN projection for 2020|UN Population Division, World Population Prospects, 2017 Revision';

COMMENT ON COLUMN api.covid_global.aged_65_older IS E'hare of the population that is 65 years and older, most recent year available|World Bank – World Development Indicators, based on age/sex distributions of United Nations Population Division\'s World Population Prospects: 2017 Revision';

COMMENT ON COLUMN api.covid_global.aged_70_older IS E'Share of the population that is 70 years and older in 2015|United Nations, Department of Economic and Social Affairs, Population Division (2017), World Population Prospects: The 2017 Revision';

COMMENT ON COLUMN api.covid_global.gdp_per_capita IS E'Gross domestic product at purchasing power parity (constant 2011 international dollars), most recent year available|World Bank – World Development Indicators, source from World Bank, International Comparison Program database';

COMMENT ON COLUMN api.covid_global.extreme_poverty IS E'Share of the population living in extreme poverty, most recent year available since 2010|World Bank – World Development Indicators, sourced from World Bank Development Research Group';

COMMENT ON COLUMN api.covid_global.cvd_death_rate IS E'Death rate from cardiovascular disease in 2017|Global Burden of Disease Collaborative Network, Global Burden of Disease Study 2017 Results';

COMMENT ON COLUMN api.covid_global.diabetes_prevalence IS E'Diabetes prevalence (% of population aged 20 to 79) in 2017|World Bank – World Development Indicators, sourced from International Diabetes Federation, Diabetes Atlas';

COMMENT ON COLUMN api.covid_global.female_smokers IS E'Share of women who smoke, most recent year available|World Bank – World Development Indicators, sourced from World Health Organization, Global Health Observatory Data Repository';

COMMENT ON COLUMN api.covid_global.male_smokers IS E'Share of men who smoke, most recent year available|World Bank – World Development Indicators, sourced from World Health Organization, Global Health Observatory Data Repository';

COMMENT ON COLUMN api.covid_global.handwashing_facilities IS E'Share of the population with basic handwashing facilities on premises, most recent year available|United Nations Statistics Division';

COMMENT ON COLUMN api.covid_global.hospital_beds_per_thousand IS E'Hospital beds per 1,000 people, most recent year available since 2010|OECD, Eurostat, World Bank, national government records and other sources';

COMMENT ON COLUMN api.covid_global.life_expectancy IS E'Life expectancy at birth in 2019|James C. Riley, Clio Infra, United Nations Population Division';

