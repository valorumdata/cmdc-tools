DROP FUNCTION IF EXISTS clamp;

CREATE FUNCTION clamp (real, real, real)
       RETURNS real IMMUTABLE STRICT
       LANGUAGE sql
       AS $$
       SELECT
              GREATEST ($2, LEAST ($3, $1));

$$;

CREATE OR REPLACE VIEW public.scores AS
WITH demo_pop AS (
       SELECT
              demographics.location,
              demographics.value AS population
       FROM
              api.demographics
       WHERE
              demographics.variable = 'Total population'::text
),
demo_65p AS (
       SELECT
              demographics.location,
              demographics.value AS frac65p
       FROM
              api.demographics
       WHERE
              demographics.variable = 'Fraction of population over 65'::text
),
daily_case_avg AS (
       SELECT
              usafacts_covid.fips,
              (max(usafacts_covid.value) - min(usafacts_covid.value))::real / 30::double precision AS recent_cases
       FROM
              data.usafacts_covid
       WHERE
              usafacts_covid.dt > (now() - '30 days'::interval)
              AND usafacts_covid.variable_id = (
                     SELECT
                            id
                     FROM
                            meta.covid_variables
                     WHERE
                            name = 'cases_total')
              GROUP BY
                     usafacts_covid.fips
),
states AS (
       SELECT
              us_fips.id,
              us_fips.fips,
              us_fips.name,
              us_fips.area,
              us_fips.latitude,
              us_fips.longitude,
              us_fips.state,
              us_fips.county
       FROM
              meta.us_fips
       WHERE
              us_fips.fips < 100
),
scores AS (
       SELECT
              demo_pop.location,
              clamp (demo_pop.population, 0.0::real, 500.0::real) + 10::real * demo_65p.frac65p + daily_case_avg.recent_cases::real AS score
       FROM
              demo_pop
              LEFT JOIN demo_65p ON demo_pop.location = demo_65p.location
              LEFT JOIN daily_case_avg ON demo_pop.location = daily_case_avg.fips
)
SELECT
       s.location,
       CASE WHEN usf.name::text = st.name::text THEN
              usf.name::text
       ELSE
              (usf.name::text || ', '::text) || st.name::text
       END AS name,
       s.score
FROM
       scores s
       LEFT JOIN meta.us_fips usf ON s.location = usf.fips
       LEFT JOIN states st ON usf.state = st.state;

CREATE OR REPLACE VIEW public.state_scores AS
SELECT
       s.location,
       s.name,
       s.score
FROM
       public.scores s
WHERE
       s.location < 100;

CREATE OR REPLACE VIEW public.county_scores AS
SELECT
       s.location,
       s.name,
       s.score
FROM
       public.scores s
WHERE
       s.location > 1000;

