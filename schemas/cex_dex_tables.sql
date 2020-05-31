DROP TABLE IF EXISTS data.cex_state_dex CASCADE;

CREATE TABLE data.mobility_dex (
    "dt" DATE,
    "fips" SMALLINT references meta.us_fips (fips),
    "variable" TEXT,
    "value" REAL,
    PRIMARY KEY ("dt", "fips", "variable")
);

COMMENT ON TABLE data.mobility_dex is E'For a smartphone residing in a given geography, how many distinct devices also visited any of the commercial venues that this device visited today?
The county-level DEX reports the county-level average of this number across all devices residing in the county that day. The DEX values are necessarily only a fraction of the number of distinct individuals that also visited any of the commercial venues visited by a device, since only a fraction of individuals, venues, and visits are in the device sample.

The state-level DEX reports the state-level average of this number across all devices residing in the state that day. The DEX values are necessarily only a fraction of the number of distinct individuals that also visited any of the commercial venues visited by a device, since only a fraction of individuals, venues, and visits are in the device sample.

In the context of the ongoing pandemic, the DEX measure may be biased if devices sheltering-in-place are not in the sample due to lack of movement. We report adjusted DEX values to help address this selection bias. DEX-adjusted is computed assuming that the number of devices has not declined since the early-2020 peak and that unobserved devices did not visit any commercial venues.

This index is produced by Victor Couture, Jonathan Dingel, Allison Green, Jessie Handbury, and Kevin Williams with assistance from Hayden Parsley and Serena Xu. They are derived from anonymized, aggregated smartphone movement data provided by PlaceIQ. We are grateful to the authors and to PlaceIQ for making this data available to us.

If you use this dataset, we recommend seeing the [notes for users of the DEX dataset](https://github.com/COVIDExposureIndices/COVIDExposureIndices/blob/master/documentation/DEX_notes.md) and [DEX documentation](https://github.com/COVIDExposureIndices/COVIDExposureIndices/blob/master/documentation/DEX.pdf) produced by the original authors.

Source: https://github.com/COVIDExposureIndices/COVIDExposureIndices';

COMMENT ON COLUMN data.mobility_dex.dt is E'The date on which the DEX value was reported';
COMMENT ON COLUMN data.mobility_dex.fips is E'The state for which the DEX is reported.';
COMMENT ON COLUMN data.mobility_dex.variable is E'The variable for which you are retrieving data. More information on availble data can be found in the table documentation and on the dataset home page.';
COMMENT ON COLUMN data.mobility_dex.value is E'The value for the (dt, fips, variable) combination.';

/*
COMMENT ON COLUMN data.cex_state_dex.dex is E'the DEX value';
COMMENT ON COLUMN data.cex_state_dex.num_devices is E'The number of devices in this state that are part of the sample.';
COMMENT ON COLUMN data.cex_state_dex.dex_a is E'Adjusted dex in state on that date';
COMMENT ON COLUMN data.cex_state_dex.num_devices_a is E'Adjusted num_devices in state on that date';
COMMENT ON COLUMN data.cex_state_dex.dex_income_1 is E'DEX for devices residing in bottom quartile of the block group median income distribution in state on that date';
COMMENT ON COLUMN data.cex_state_dex.num_devices_income_1 is E'Number of devices residing in bottom quartile of the block group median income distribution in state on that date';
COMMENT ON COLUMN data.cex_state_dex.dex_income_1_a is E'Adjusted dex_income_1 in state on that date';
COMMENT ON COLUMN data.cex_state_dex.num_devices_income_1_a is E'Adjusted num_devices_income_1 in state on that date';
COMMENT ON COLUMN data.cex_state_dex.dex_income_2 is E'DEX for devices residing in second quartile of the block group median income distribution in state on that date';
COMMENT ON COLUMN data.cex_state_dex.num_devices_income_2 is E'Number of devices residing in second quartile of the block group median income distribution in state on that date';
COMMENT ON COLUMN data.cex_state_dex.dex_income_2_a is E'Adjusted dex_income_2 in state on that date';
COMMENT ON COLUMN data.cex_state_dex.num_devices_income_2_a is E'Adjusted num_devices_income_2 in state on that date';
COMMENT ON COLUMN data.cex_state_dex.dex_income_3 is E'DEX for devices residing in third quartile of the block group median income distribution in state on that date';
COMMENT ON COLUMN data.cex_state_dex.num_devices_income_3 is E'Number of devices residing in third quartile of the block group median income distribution in state on that date';
COMMENT ON COLUMN data.cex_state_dex.dex_income_3_a is E'Adjusted dex_income_3 in state on that date';
COMMENT ON COLUMN data.cex_state_dex.num_devices_income_3_a is E'Adjusted num_devices_income_3 in state on that date';
COMMENT ON COLUMN data.cex_state_dex.dex_income_4 is E'DEX for devices residing in upper quartile of the block group median income distribution in state on that date';
COMMENT ON COLUMN data.cex_state_dex.num_devices_income_4 is E'Number of devices residing in upper quartile of the block group median income distribution in state on that date';
COMMENT ON COLUMN data.cex_state_dex.dex_income_4_a is E'Adjusted dex_income_4 in state on that date';
COMMENT ON COLUMN data.cex_state_dex.num_devices_income_4_a is E'Adjusted num_devices_income_4 in state on that date';
COMMENT ON COLUMN data.cex_state_dex.dex_education_1 is E'DEX for devices residing in bottom quartile of the block group college share distribution in state on that date';
COMMENT ON COLUMN data.cex_state_dex.num_devices_education_1 is E'Number of devices residing in bottom quartile of the block group college share distribution in state on that date';
COMMENT ON COLUMN data.cex_state_dex.dex_education_1_a is E'Adjusted dex_education_1 in state on that date';
COMMENT ON COLUMN data.cex_state_dex.num_devices_education_1_a is E'Adjusted num_devices_education_1 in state on that date';
COMMENT ON COLUMN data.cex_state_dex.dex_education_2 is E'DEX for devices residing in second quartile of the block group college share distribution in state on that date';
COMMENT ON COLUMN data.cex_state_dex.num_devices_education_2 is E'Number of devices residing in second quartile of the block group college share distribution in state on that date';
COMMENT ON COLUMN data.cex_state_dex.dex_education_2_a is E'Adjusted dex_education_2 in state on that date';
COMMENT ON COLUMN data.cex_state_dex.num_devices_education_2_a is E'Adjusted num_devices_education_2 in state on that date';
COMMENT ON COLUMN data.cex_state_dex.dex_education_3 is E'DEX for devices residing in third quartile of the block group college share distribution in state on that date';
COMMENT ON COLUMN data.cex_state_dex.num_devices_education_3 is E'Number of devices residing in third quartile of the block group college share distribution in state on that date';
COMMENT ON COLUMN data.cex_state_dex.dex_education_3_a is E'Adjusted dex_education_3 in state on that date';
COMMENT ON COLUMN data.cex_state_dex.num_devices_education_3_a is E'Adjusted num_devices_education_3 in state on that date';
COMMENT ON COLUMN data.cex_state_dex.dex_education_4 is E'DEX for devices residing in upper quartile of the block group college share distribution in state on that date';
COMMENT ON COLUMN data.cex_state_dex.num_devices_education_4 is E'Number of devices residing in upper quartile of the block group college share distribution in state on that date';
COMMENT ON COLUMN data.cex_state_dex.dex_education_4_a is E'Adjusted dex_education_4 in state on that date';
COMMENT ON COLUMN data.cex_state_dex.num_devices_education_4_a is E'Adjusted num_devices_education_4 in state on that date';
COMMENT ON COLUMN data.cex_state_dex.dex_race_asian is E'DEX in state on that date, with weights on each device equal to share of residents of its block group who are Asian.';
COMMENT ON COLUMN data.cex_state_dex.num_devices_race_asian is E'Number of devices in state on that date, with weights on each device equal to share of residents of its block group who are Asian.';
COMMENT ON COLUMN data.cex_state_dex.dex_race_asian_a is E'Adjusted dex_race_asian in state on that date';
COMMENT ON COLUMN data.cex_state_dex.num_devices_race_asian_a is E'Adjusted num_devices_race_asian in state on that date';
COMMENT ON COLUMN data.cex_state_dex.dex_race_black is E'DEX in state on that date, with weights on each device equal to share of residents of its block group who are Black.';
COMMENT ON COLUMN data.cex_state_dex.num_devices_race_black is E'Number of devices in state on that date, with weights on each device equal to share of residents of its block group who are Black.';
COMMENT ON COLUMN data.cex_state_dex.dex_race_black_a is E'Adjusted dex_race_black in state on that date';
COMMENT ON COLUMN data.cex_state_dex.num_devices_race_black_a is E'Adjusted num_devices_race_black in state on that date';
COMMENT ON COLUMN data.cex_state_dex.dex_race_hispanic is E'DEX in state on that date, with weights on each device equal to share of residents of its block group who are Hispanic.';
COMMENT ON COLUMN data.cex_state_dex.num_devices_race_hispanic is E'Number of devices in state on that date, with weights on each device equal to share of residents of its block group who are Hispanic.';
COMMENT ON COLUMN data.cex_state_dex.dex_race_hispanic_a is E'Adjusted dex_race_hispanic in state on that date';
COMMENT ON COLUMN data.cex_state_dex.num_devices_race_hispanic_a is E'Adjusted num_devices_race_hispanic in state on that date';
COMMENT ON COLUMN data.cex_state_dex.dex_race_white is E'DEX in state on that date, with weights on each device equal to share of residents of its block group who are White.';
COMMENT ON COLUMN data.cex_state_dex.num_devices_race_white is E'Number of devices in state on that date, with weights on each device equal to share of residents of its block group who are White.';
COMMENT ON COLUMN data.cex_state_dex.dex_race_white_a is E'Adjusted dex_race_white in state on that date';
COMMENT ON COLUMN data.cex_state_dex.num_devices_race_white_a is E'Adjusted num_devices_race_white in state on that date';
*/
