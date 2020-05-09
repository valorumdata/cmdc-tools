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

COMMENT ON TABLE data.jhu_locations IS 'Metadata table provided by JHU with details about geographic coordinates and population of regions that appear in COVID data';

COMMENT ON COLUMN data.jhu_locations.uid IS 'Unique identifier for the region';

COMMENT ON COLUMN data.jhu_locations.iso2 IS 'Two character ISO name for country';

COMMENT ON COLUMN data.jhu_locations.iso3 IS 'Three character ISO name for country';

COMMENT ON COLUMN data.jhu_locations.code3 IS 'Country Code';

COMMENT ON COLUMN data.jhu_locations.fips IS 'FIPS code identifying county in USA';

COMMENT ON COLUMN data.jhu_locations.admin2 IS 'Additional name about region. For US counties it is the county name. For countries it is the country name';

COMMENT ON COLUMN data.jhu_locations.province_state IS 'Name of US state or Canadian province';

COMMENT ON COLUMN data.jhu_locations.country_region IS '';

COMMENT ON COLUMN data.jhu_locations.lat IS 'Latitude coordinate for region.';

COMMENT ON COLUMN data.jhu_locations.lon IS 'Longitude coordinate for region.';

COMMENT ON COLUMN data.jhu_locations.combined_key IS 'Textual representation of the region name';

COMMENT ON COLUMN data.jhu_locations.population IS 'Population of the region';

DROP TABLE IF EXISTS data.jhu_daily_reports;

CREATE TABLE data.jhu_daily_reports (
    "fips" numeric(12, 6),
    "admin2" text,
    "province_state" text,
    "country_region" text,
    "date" timestamptz,
    "date_updated" timestamptz,
    "lat" numeric(12, 6),
    "lon" numeric(12, 6),
    "confirmed" int,
    "deaths" int,
    "recovered" int,
    "active" int,
    "combined_key" text,
    PRIMARY KEY (combined_key, date)
);

COMMENT ON TABLE data.jhu_daily_reports IS E'Daily case reports. https://github.com/CSSEGISandData/COVID-19/tree/dce1b48f54bd7551295c27a2878701cf2c58a1c8/csse_covid_19_data/csse_covid_19_daily_reports';

COMMENT ON COLUMN data.jhu_daily_reports.fips IS E'US only. Federal Information Processing Standards code that uniquely identifies counties within the USA.';

COMMENT ON COLUMN data.jhu_daily_reports.admin2 IS E'County name. US only.';

COMMENT ON COLUMN data.jhu_daily_reports.province_state IS E'Province, state or dependency name.';

COMMENT ON COLUMN data.jhu_daily_reports.country_region IS E'Country, region or sovereignty name. The names of locations included on the Website correspond with the official designations used by the U.S. Department of State.';

COMMENT ON COLUMN data.jhu_daily_reports.date IS E'Date for which data applies. This is the file name on github';

COMMENT ON COLUMN data.jhu_daily_reports.date_updated IS E'MM/DD/YYYY HH:mm:ss (24 hour format, in UTC). This is the field in the dataset itself.';

COMMENT ON COLUMN data.jhu_daily_reports.lat IS E'Dot locations on the dashboard. All points (except for Australia) shown on the map are based on geographic centroids, and are not representative of a specific address, building or any location at a spatial scale finer than a province/state. Australian dots are located at the centroid of the largest city in each state.';

COMMENT ON COLUMN data.jhu_daily_reports.lon IS E'See lat.';

COMMENT ON COLUMN data.jhu_daily_reports.confirmed IS E'Confirmed cases include presumptive positive cases and probable cases, in accordance with CDC guidelines as of April 14.';

COMMENT ON COLUMN data.jhu_daily_reports.deaths IS E'Death totals in the US include confirmed and probable, in accordance with CDC guidelines as of April 14.';

COMMENT ON COLUMN data.jhu_daily_reports.recovered IS E'Recovered cases outside China are estimates based on local media reports, and state and local reporting when available, and therefore may be substantially lower than the true number. US state-level recovered cases are from COVID Tracking Project.';

COMMENT ON COLUMN data.jhu_daily_reports.active IS E'Active cases = total confirmed - total recovered - total deaths.';

COMMENT ON COLUMN data.jhu_daily_reports.combined_key IS E'';

DROP TABLE IF EXISTS data.jhu_daily_reports_us;

CREATE TABLE data.jhu_daily_reports_us (
    "province_state" text,
    "country_region" text,
    "date_updated" timestamptz,
    "lat" numeric(12, 6),
    "lon" numeric(12, 6),
    "confirmed" int,
    "deaths" int,
    "recovered" int,
    "active" int,
    "fips" int,
    "incident_rate" numeric(12, 6),
    "people_tested" int,
    "people_hospitalized" int,
    "mortality_rate" numeric(12, 6),
    "uid" int,
    "iso3" text,
    "testing_rate" numeric(12, 6),
    "hospitalization_rate" numeric(12, 6),
    "date" timestamp WITHOUT time zone,
    PRIMARY KEY (fips, date)
);

COMMENT ON TABLE data.jhu_daily_reports_us IS E'This table contains an aggregation of each US State level data.';

COMMENT ON COLUMN data.jhu_daily_reports_us.province_state IS E'The name of the State within the USA.';

COMMENT ON COLUMN data.jhu_daily_reports_us.country_region IS E'The name of the Country (US).';

COMMENT ON COLUMN data.jhu_daily_reports_us.date_updated IS E'The most recent date the file was pushed.';

COMMENT ON COLUMN data.jhu_daily_reports_us.lat IS E'Latitude.';

COMMENT ON COLUMN data.jhu_daily_reports_us.lon IS E'Longitude.';

COMMENT ON COLUMN data.jhu_daily_reports_us.confirmed IS E'Aggregated confirmed case count for the state.';

COMMENT ON COLUMN data.jhu_daily_reports_us.deaths IS E'Aggregated Death case count for the state.';

COMMENT ON COLUMN data.jhu_daily_reports_us.recovered IS E'Aggregated Recovered case count for the state.';

COMMENT ON COLUMN data.jhu_daily_reports_us.active IS E'Aggregated confirmed cases that have not been resolved (Active = Confirmed - Recovered - Deaths).';

COMMENT ON COLUMN data.jhu_daily_reports_us.fips IS E'Federal Information Processing Standards code that uniquely identifies counties within the USA.';

COMMENT ON COLUMN data.jhu_daily_reports_us.incident_rate IS E'confirmed cases per 100,000 persons.';

COMMENT ON COLUMN data.jhu_daily_reports_us.people_tested IS E'Total number of people who have been tested.';

COMMENT ON COLUMN data.jhu_daily_reports_us.people_hospitalized IS E'Total number of people hospitalized.';

COMMENT ON COLUMN data.jhu_daily_reports_us.mortality_rate IS E'Number recorded deaths * 100/ Number confirmed cases.';

COMMENT ON COLUMN data.jhu_daily_reports_us.uid IS E'Unique Identifier for each row entry.';

COMMENT ON COLUMN data.jhu_daily_reports_us.iso3 IS E'Officialy assigned country code identifiers.';

COMMENT ON COLUMN data.jhu_daily_reports_us.testing_rate IS E'Total number of people tested per 100,000 persons.';

COMMENT ON COLUMN data.jhu_daily_reports_us.hospitalization_rate IS E'Total number of people hospitalized * 100/ Number of confirmed cases.';

COMMENT ON COLUMN data.jhu_daily_reports_us.date IS E'The data corresponding to the data (the date of the filename in GitHub).';

