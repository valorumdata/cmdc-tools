/* DEX view */
CREATE OR REPLACE VIEW api.mobility_dex AS
  SELECT csd.dt, csd.fips, csd.variable, csd.value
  FROM data.mobility_dex csd
;

COMMENT ON VIEW api.mobility_dex IS E'The DEX, or device exposure index, is an index that measures how much movement there is within a particular state or county.

For a smartphone residing in a given state, how many distinct devices also visited any of the commercial venues that this device visited today? The state-level DEX reports the state-level average of this number across all devices residing in the state that day. The DEX values are necessarily only a fraction of the number of distinct individuals that also visited any of the commercial venues visited by a device, since only a fraction of individuals, venues, and visits are in the device sample.

In the context of the ongoing pandemic, the DEX measure may be biased if devices sheltering-in-place are not in the sample due to lack of movement. We report adjusted DEX values to help address this selection bias. DEX-adjusted is computed assuming that the number of devices has not declined since the early-2020 peak and that unobserved devices did not visit any commercial venues.

This index is produced by Victor Couture, Jonathan Dingel, Allison Green, Jessie Handbury, and Kevin Williams with assistance from Hayden Parsley and Serena Xu. They are derived from anonymized, aggregated smartphone movement data provided by PlaceIQ. We are grateful to the authors and to PlaceIQ for making this data available to us.

If you use this dataset, we recommend seeing the [notes for users of the DEX dataset](https://github.com/COVIDExposureIndices/COVIDExposureIndices/blob/master/documentation/DEX_notes.md) and [DEX documentation](https://github.com/COVIDExposureIndices/COVIDExposureIndices/blob/master/documentation/DEX.pdf) produced by the original authors.

Source: https://github.com/COVIDExposureIndices/COVIDExposureIndices
';

/* TODO: Incoporate the demographic DEXes later...
CREATE OR REPLACE VIEW api.cex_state_dex_demographics AS
  SELECT csd.date, csd.state as fips,
    csd.dex as dex_baseline, csd.num_devices as num_devices_baseline,
    csd.dex_a as dex_adjusted, csd.num_devices_a as num_devices_adjusted
  FROM data.cex_state_dex
;
*/


CREATE OR REPLACE VIEW api.cex_state_lex AS
    SELECT csl.dt, csl.s_prev as state_previous, csl.s_today as state_today, csl.lex
    FROM data.cex_state_lex csl
;


CREATE OR REPLACE VIEW api.cex_county_lex AS
    SELECT ccl.dt, ccl.c_prev as county_previous, ccl.c_today as county_today, ccl.lex
    FROM data.cex_county_lex ccl
;

