CREATE OR REPLACE VIEW api.economics AS
    SELECT to_date(bg.year::text, 'YYYY') as dt, bg.fips, 'GDP_' || bv.description, bg.value
    FROM data.bea_gdp bg
    LEFT JOIN meta.bea_variables bv
    on bv.id=bg.id
    UNION
    SELECT dt, 0::INT, 'wei'::TEXT, wei
    FROM data.weeklyeconomicindex
;

