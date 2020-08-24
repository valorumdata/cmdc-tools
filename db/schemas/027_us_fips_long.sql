CREATE  OR REPLACE VIEW meta.us_fips_long as
select fips, state, county, name, 'area' as variable, area as value
from meta.us_fips
union all
select fips, state, county, name, 'latitude' as variable, latitude as value
from meta.us_fips
union all
select fips, state, county, name, 'longitude' as variable, longitude as value
from meta.us_fips;


COMMENT on view meta.us_fips_long is E'A view of the meta.us_fips table with area, latitude, longitude converted to long form';

COMMENT ON COLUMN meta.us_fips_long.fips IS E'The fips code associated with this geography';

COMMENT ON COLUMN meta.us_fips_long.name IS E'The name of the state or county. This is simply the word tract with the fips number for tracts.';

COMMENT ON COLUMN meta.us_fips_long.variable IS E'The name of the variable in this row';

COMMENT ON COLUMN meta.us_fips_long.value IS E'The value of the associated variable for this row';

COMMENT ON COLUMN meta.us_fips.state IS E'The state fips code. This is stored as an integer and if it is less than 2 digits it should be padded by leading 0\'s to form a proper fips code';

COMMENT ON COLUMN meta.us_fips.county IS E'The county fips code. This is stored as an integer and if it is less than 3 digits it should be padded by leading 0\'s to form a proper fips code';
