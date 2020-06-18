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
  ), states AS (
      SELECT * FROM meta.us_fips WHERE fips < 100
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
  SELECT
    s.location,
    CASE
      WHEN usf.name=st.name THEN usf.name
    ELSE
      usf.name || ', ' || st.name
    END
    AS name,
    s.score
  FROM scores s
  LEFT JOIN meta.us_fips usf ON s.location=usf.fips
  LEFT JOIN states st ON usf.state=st.state
  ORDER BY s.score DESC
;


CREATE OR REPLACE VIEW public.state_scores AS
  SELECT s.location, s.name, s.score
  FROM public.scores s
  WHERE s.location < 100
;


CREATE OR REPLACE VIEW public.county_scores AS
  SELECT s.location, s.name, s.score
  FROM public.scores s
  WHERE s.location > 1000
;
