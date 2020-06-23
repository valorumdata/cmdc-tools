DROP TABLE IF EXISTS meta.npi_variables;
CREATE TABLE meta.npi_variables (
    id serial primary key,
    name text UNIQUE
);

COMMENT ON TABLE meta.npi_variables IS E'This table contains a list of variables and their corresponding identifiers used in `data.npi`. The variables include:

* closing_of_public_venues
* lockdown
* non-essential_services_closure
* religious_gatherings_banned
* shelter_in_place
* social_distancing
* gathering_size_10_0
* gathering_size_25_11
* gathering_size_100_25
* gathering_size_500_101
';

INSERT INTO meta.npi_variables (name) VALUES
  ('closing_of_public_venues'),
  ('lockdown'),
  ('non-essential_services_closure'),
  ('religious_gatherings_banned'),
  ('shelter_in_place'),
  ('social_distancing'),
  ('gathering_size_10_0'),
  ('gathering_size_25_11'),
  ('gathering_size_100_25'),
  ('gathering_size_500_101');


DROP TABLE IF EXISTS data.npi_interventions;

CREATE TABLE data.npi_interventions (
    vintage DATE,
    dt date,
    location INT references meta.us_fips(fips),
    variable_id SMALLINT REFERENCES meta.npi_variables(id),
    value BOOLEAN,
    PRIMARY KEY (vintage, dt, location, variable_id)
);
