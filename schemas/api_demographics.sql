/* TODO: Need to determine which other variables to use */
CREATE OR REPLACE VIEW api.demographics AS
    SELECT uf.fips, uf.name, uf.area,
        population,
        population / uf.area AS population_density,
        (population_65to69 + population_70to74 + population_75to79 + population_80to84 + population_85O) / population as population_65O
    FROM CROSSTAB(
        $$
        SELECT d.fips, v.census_id, d.value
        FROM data.acs_data
        LEFT JOIN meta.acs_variables v
        ON d.id = v.id
        ORDER BY 1,2
        $$,
        $$
        SELECT unnest(
            '{S0101_C01_001E,S0101_C01_015E,S0101_C01_016E,S0101_C01_017E,S0101_C01_018E,S0101_C01_019E}'::VARCHAR(20)[]
        )
        $$
    ) AS ct (
        fips BIGINT,
        population REAL, population_65to69 REAL, population_70to74 REAL,
        population_75to79 REAL, population_80to84 REAL, population_85O REAL
    )
    LEFT JOIN meta.us_fips uf
    ON uf.fips=ct.fips
;

