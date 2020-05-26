CREATE OR REPLACE VIEW api.county_gdp AS
    SELECT bg.year, bg.fips, bv.description as industry, bg.value as gdp
    FROM data.bea_gdp bg
    LEFT JOIN meta.bea_variables bv
    ON bv.id=bg.id
;


CREATE OR REPLACE VIEW api.wei AS
    SELECT "date", "wei"
    FROM data.weeklyeconomicindex
;

