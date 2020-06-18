-- CREATE FUNCTION clamp(REAL, REAL, REAL) RETURNS REAL
--   AS 'select GREATEST($2, LEAST($3, $1));'
--   LANGUAGE SQL
--   IMMUTABLE
--   RETURNS 0.0::REAL ON NULL INPUT;
--


CREATE OR REPLACE VIEW public.scores AS
  WITH demo_pop AS (
	  SELECT location, value AS population FROM api.demographics WHERE variable = 'Total population'
  ), demo_65p AS (
	  SELECT location, value AS frac65p FROM api.demographics WHERE variable = 'Fraction of population over 65'
  ), daily_case_avg AS (
	  SELECT fips, (MAX(value) - MIN(value))::REAL / 30 AS recent_cases FROM api.usafacts_covid WHERE dt > NOW() - INTERVAL '30 days' AND variable='cases_total' GROUP BY fips
  ), scores AS (
    SELECT
      demo_pop.location,
      clamp(demo_pop.population::REAL, 0.0::REAL, 500.0::REAL)
      + 10::REAL*demo_65p.frac65p::REAL
      + daily_case_avg.recent_cases::REAL
	  AS score
    FROM demo_pop
    LEFT JOIN demo_65p ON demo_pop.location=demo_65p.location
    LEFT JOIN daily_case_avg ON demo_pop.location=daily_case_avg.fips
    ORDER BY score DESC
  )
  SELECT s.location, s.score
  FROM scores s
;

CREATE OR REPLACE VIEW public.state_scores AS
  SELECT s.location, s.score
  FROM public.scores s
  WHERE s.location < 100
;


CREATE OR REPLACE VIEW public.county_scores AS
  SELECT s.location, s.score
  FROM public.scores s
  WHERE s.location > 1000
;
