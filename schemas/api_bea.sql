CREATE OR REPLACE VIEW api.bea AS
    SELECT * FROM CROSSTAB(
        $$
        SELECT d.fips, v.{name}, d.value
        FROM data.bea_gdp d
        LEFT JOIN meta.bea_variables v
        ON d.id = v.id
        ORDER BY 1,2
        $$,
        $$
        SELECT {sectors} FROM {???}
        $$
    ) AS (...);

