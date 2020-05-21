DROP TABLE IF EXISTS data.jhu_locations;

CREATE TABLE data.jhu_locations (
    uid int PRIMARY KEY,
    iso2 char(2),
    iso3 char(3),
    code3 int,
    fips int,
    admin2 text,
    province_state text,
    country_region text,
    lat numeric(8, 5),
    lon numeric(8, 5),
    combined_key text,
    population int
);

COMMENT ON TABLE data.jhu_locations IS E'Metadata table provided by JHU with details about geographic coordinates and population of regions that appear in COVID data';

COMMENT ON COLUMN data.jhu_locations.uid IS E'Unique identifier for the region';

COMMENT ON COLUMN data.jhu_locations.iso2 IS E'Two character ISO name for country';

COMMENT ON COLUMN data.jhu_locations.iso3 IS E'Three character ISO name for country';

COMMENT ON COLUMN data.jhu_locations.code3 IS E'Country Code';

COMMENT ON COLUMN data.jhu_locations.fips IS E'FIPS code identifying county in USA';

COMMENT ON COLUMN data.jhu_locations.admin2 IS E'Additional name about region. For US counties it is the county name. For countries it is the country name';

COMMENT ON COLUMN data.jhu_locations.province_state IS E'Name of US state or Canadian province';

COMMENT ON COLUMN data.jhu_locations.country_region IS E'';

COMMENT ON COLUMN data.jhu_locations.lat IS E'Latitude coordinate for region.';

COMMENT ON COLUMN data.jhu_locations.lon IS E'Longitude coordinate for region.';

COMMENT ON COLUMN data.jhu_locations.combined_key IS E'Textual representation of the region name';

COMMENT ON COLUMN data.jhu_locations.population IS E'Population of the region';

DROP TABLE IF EXISTS data.jhu_daily_reports;

CREATE TABLE data.jhu_daily_reports (
    uid int REFERENCES data.jhu_locations(uid),
    "date" DATE,
    "date_updated" timestamptz,
    "confirmed" int,
    "deaths" int,
    "recovered" int,
    "active" int,
    PRIMARY KEY (uid, date)
);

COMMENT ON TABLE data.jhu_daily_reports IS E'Daily case reports. https://github.com/CSSEGISandData/COVID-19/tree/dce1b48f54bd7551295c27a2878701cf2c58a1c8/csse_covid_19_data/csse_covid_19_daily_reports';

COMMENT ON COLUMN data.jhu_daily_reports.date IS E'Date for which data applies. This is the file name on github';

COMMENT ON COLUMN data.jhu_daily_reports.date_updated IS E'MM/DD/YYYY HH:mm:ss (24 hour format, in UTC). This is the field in the dataset itself.';

COMMENT ON COLUMN data.jhu_daily_reports.confirmed IS E'Confirmed cases include presumptive positive cases and probable cases, in accordance with CDC guidelines as of April 14.';

COMMENT ON COLUMN data.jhu_daily_reports.deaths IS E'Death totals in the US include confirmed and probable, in accordance with CDC guidelines as of April 14.';

COMMENT ON COLUMN data.jhu_daily_reports.recovered IS E'Recovered cases outside China are estimates based on local media reports, and state and local reporting when available, and therefore may be substantially lower than the true number. US state-level recovered cases are from COVID Tracking Project.';

COMMENT ON COLUMN data.jhu_daily_reports.active IS E'Active cases = total confirmed - total recovered - total deaths.';

DROP TABLE IF EXISTS data.jhu_daily_reports_us;

CREATE TABLE data.jhu_daily_reports_us (
    "fips" int references data.us_states(fips),
    "date" DATE,
    "date_updated" timestamptz,
    "confirmed" int,
    "deaths" int,
    "recovered" int,
    "active" int,
    "incident_rate" numeric(12, 6),
    "people_tested" int,
    "people_hospitalized" int,
    "mortality_rate" numeric(12, 6),
    "testing_rate" numeric(12, 6),
    "hospitalization_rate" numeric(12, 6),
    PRIMARY KEY (fips, date)
);

COMMENT ON TABLE data.jhu_daily_reports_us IS E'This table contains an aggregation of each US State level data.';

COMMENT ON COLUMN data.jhu_daily_reports_us.fips IS 'FIPS code identifying county in USA';

COMMENT ON COLUMN data.jhu_daily_reports_us.date IS E'The data corresponding to the data (the date of the filename in GitHub).';

COMMENT ON COLUMN data.jhu_daily_reports_us.date_updated IS E'The most recent date the file was pushed.';

COMMENT ON COLUMN data.jhu_daily_reports_us.confirmed IS E'Aggregated confirmed case count for the state.';

COMMENT ON COLUMN data.jhu_daily_reports_us.deaths IS E'Aggregated Death case count for the state.';

COMMENT ON COLUMN data.jhu_daily_reports_us.recovered IS E'Aggregated Recovered case count for the state.';

COMMENT ON COLUMN data.jhu_daily_reports_us.active IS E'Aggregated confirmed cases that have not been resolved (Active = Confirmed - Recovered - Deaths).';

COMMENT ON COLUMN data.jhu_daily_reports_us.incident_rate IS E'confirmed cases per 100,000 persons.';

COMMENT ON COLUMN data.jhu_daily_reports_us.people_tested IS E'Total number of people who have been tested.';

COMMENT ON COLUMN data.jhu_daily_reports_us.people_hospitalized IS E'Total number of people hospitalized.';

COMMENT ON COLUMN data.jhu_daily_reports_us.mortality_rate IS E'Number recorded deaths * 100/ Number confirmed cases.';

COMMENT ON COLUMN data.jhu_daily_reports_us.testing_rate IS E'Total number of people tested per 100,000 persons.';

COMMENT ON COLUMN data.jhu_daily_reports_us.hospitalization_rate IS E'Total number of people hospitalized * 100/ Number of confirmed cases.';

