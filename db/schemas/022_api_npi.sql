CREATE OR REPLACE VIEW api.npi_us AS
WITH last_vintage as (
  SELECT dt, location, variable_id, max(vintage) as vintage
  from data.npi_interventions
  group by (dt, location, variable_id)
)
 SELECT npus.dt, npus.location, nv.name AS variable, npus.value
   FROM last_vintage lv
   LEFT JOIN data.npi_interventions npus USING (vintage, dt, location, variable_id)
   LEFT JOIN meta.npi_variables nv ON nv.id = npus.variable_id;


COMMENT ON VIEW api.npi_us IS E'This table contains information on the nonpharmaceutical interventions (NPIs) that were taken in the United States in response to COVID

The data begins on March 1, 2020 and covers approximately 650 different US geographies (states and counties). There are 10 different NPIs covered in this dataset which include:

* closing_of_public_venues: Public venues closed. A government order closing gathering venues for in-person service, such as restaurants, bars, and theaters.
* lockdown: Lock down
* non-essential_services_closure: Non-essential services closure
* religious_gatherings_banned: Cancelling of religious gatherings, either explicitly or implicitly by applying gathering size/shelter-in-place limitations to religious gatherings as well
* shelter_in_place: An order indicating that people should shelter in their homes except for essential reasons
* social_distancing: Social distancing mandate of at least 6 ft between people
* gathering_size_10_0: Gatherings are limited to between 0 and 10 people
* gathering_size_25_11: Gatherings are limited to between 11 and 25 people
* gathering_size_100_25: Gatherings are limited to between 26 and 100 people
* gathering_size_500_101: Gatherings are limited to between 101 and 500 people

The original data was collected by Keystone Strategy and is distributed under the Creative Commons Attribution 4.0 International Public License.

Keystone Strategy COVID page: https://www.keystonestrategy.com/coronavirus-covid19-intervention-dataset-model/
Source: https://github.com/Keystone-Strategy/covid19-intervention-data
';

COMMENT ON COLUMN api.npi_us.dt IS E'The date at which the intervention is evaluated';
COMMENT ON COLUMN api.npi_us.location IS E'The FIPS code for the geography';
COMMENT ON COLUMN api.npi_us.variable IS E'The NPI being considered';
COMMENT ON COLUMN api.npi_us.value IS E'Whether the intervention from `variable` was active in geography `location` on date `dt`';
