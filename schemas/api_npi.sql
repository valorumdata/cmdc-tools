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


