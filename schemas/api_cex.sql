/* DEX view */
CREATE OR REPLACE VIEW api.mobility_devices AS
  SELECT csd.dt, csd.fips as location, csd.variable, csd.value
  FROM data.mobility_dex csd
;

COMMENT ON VIEW api.mobility_devices IS E'The DEX, or device exposure index, is an index that measures how much movement there is within a particular geography (state or county). This data is currently only available for the US.

The DEX answers the question, for a smartphone residing in a given geography, how many distinct devices also visited any of the commercial venues that this device visited today?

The state-level (county-level) DEX reports the state-level average of this number across all devices residing in the state (county) that day. The DEX values are necessarily only a fraction of the number of distinct individuals that also visited any of the commercial venues visited by a device, since only a fraction of individuals, venues, and visits are in the device sample.

In the context of the ongoing pandemic, the DEX measure may be biased if devices sheltering-in-place are not in the sample due to lack of movement. We report adjusted DEX values to help address this selection bias. DEX-adjusted is computed assuming that the number of devices has not declined since the early-2020 peak and that unobserved devices did not visit any commercial venues.

Both the county and state level DEX have information on the number of devices in the sample and the adjusted DEX values as described above. Additionally, the state DEX has information in which the data has been separated into geographic regions that share demographic characteristics...

This data is produced by Victor Couture, Jonathan Dingel, Allison Green, Jessie Handbury, and Kevin Williams with assistance from Hayden Parsley and Serena Xu. They are derived from anonymized, aggregated smartphone movement data provided by PlaceIQ. We are grateful to the authors and to PlaceIQ for making this data available to us.

If you use this dataset, we recommend seeing the [notes for users of the DEX dataset](https://github.com/COVIDExposureIndices/COVIDExposureIndices/blob/master/documentation/DEX_notes.md) and [DEX documentation](https://github.com/COVIDExposureIndices/COVIDExposureIndices/blob/master/documentation/DEX.pdf) produced by the original authors.

Source: https://github.com/COVIDExposureIndices/COVIDExposureIndices
';

COMMENT ON COLUMN api.mobility_devices.dt is E'The date.';
COMMENT ON COLUMN api.mobility_devices.location is E'The fips code.';
COMMENT ON COLUMN api.mobility_devices.variable is E'The variable associated with the DEX value --- This will either be a number of devices or a DEX value.';
COMMENT ON COLUMN api.mobility_devices.value is E'The value of the variable on date `dt` in geography `fips`.';


DROP VIEW IF EXISTS api.mobility_locations;
CREATE VIEW api.mobility_locations as
SELECT dt, fips_prev, fips_today, lex
from data.mobility_lex;


COMMENT ON VIEW api.mobility_locations IS E'The Location Exposure Index (LEX) is a measure of how much exposure there is across different geographies. This data is currently only available for the US.

Among smartphones that pinged in a given state (county) today, what share of those devices pinged in each state (county) at least once during the previous 14 days? The daily state-level (county-level) LEX is a 51-by-51 (ncounties-by-ncounties) matrix in which each cell reports, among devices that pinged today in the column state (county), the share of devices that pinged in the row state (county) at least once during the previous 14 days. It is important to note that a cell phone can ping in more than a single state (county) which means that these shares will not necessarily sum to 1.

This index is produced by Victor Couture, Jonathan Dingel, Allison Green, Jessie Handbury, and Kevin Williams with assistance from Hayden Parsley and Serena Xu. They are derived from anonymized, aggregated smartphone movement data provided by PlaceIQ. We are grateful to the authors and to PlaceIQ for making this data available to us.

If you use this dataset, we recommend seeing the [notes for users of the LEX dataset](https://github.com/COVIDExposureIndices/COVIDExposureIndices/blob/master/documentation/LEX_notes.md) and [LEX documentation](https://github.com/COVIDExposureIndices/COVIDExposureIndices/blob/master/documentation/LEX.pdf) produced by the original authors.

Source: https://github.com/COVIDExposureIndices/COVIDExposureIndices';

COMMENT ON COLUMN api.mobility_locations.fips_prev IS E'The state (county) for which a device was found in the previous 14 days.';

COMMENT ON COLUMN api.mobility_locations.fips_today IS E'The state (county) for which a device was found on the given date';

COMMENT ON COLUMN api.mobility_locations.lex IS E'The LEX number';

COMMENT ON COLUMN api.mobility_locations.dt IS E'The date for which the data applies';
