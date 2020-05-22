DROP TABLE IF EXISTS data.cex_state_dex;

CREATE TABLE data.cex_state_dex (
    "state" SMALLINT references meta.us_fips (fips),
    "date" DATE,
    "dex" numeric(12, 6),
    "num_devices" INT,
    "dex_a" numeric(12, 6),
    "num_devices_a" INT,
    "dex_income_1" numeric(12, 6),
    "num_devices_income_1" INT,
    "dex_income_1_a" numeric(12, 6),
    "num_devices_income_1_a" INT,
    "dex_income_2" numeric(12, 6),
    "num_devices_income_2" INT,
    "dex_income_2_a" numeric(12, 6),
    "num_devices_income_2_a" INT,
    "dex_income_3" numeric(12, 6),
    "num_devices_income_3" INT,
    "dex_income_3_a" numeric(12, 6),
    "num_devices_income_3_a" INT,
    "dex_income_4" numeric(12, 6),
    "num_devices_income_4" INT,
    "dex_income_4_a" numeric(12, 6),
    "num_devices_income_4_a" INT,
    "dex_education_1" numeric(12, 6),
    "num_devices_education_1" INT,
    "dex_education_1_a" numeric(12, 6),
    "num_devices_education_1_a" INT,
    "dex_education_2" numeric(12, 6),
    "num_devices_education_2" INT,
    "dex_education_2_a" numeric(12, 6),
    "num_devices_education_2_a" INT,
    "dex_education_3" numeric(12, 6),
    "num_devices_education_3" INT,
    "dex_education_3_a" numeric(12, 6),
    "num_devices_education_3_a" INT,
    "dex_education_4" numeric(12, 6),
    "num_devices_education_4" INT,
    "dex_education_4_a" numeric(12, 6),
    "num_devices_education_4_a" INT,
    "dex_race_asian" numeric(12, 6),
    "num_devices_race_asian" numeric(12, 6),
    "dex_race_asian_a" numeric(12, 6),
    "num_devices_race_asian_a" numeric(12, 6),
    "dex_race_black" numeric(12, 6),
    "num_devices_race_black" numeric(12, 6),
    "dex_race_black_a" numeric(12, 6),
    "num_devices_race_black_a" numeric(12, 6),
    "dex_race_hispanic" numeric(12, 6),
    "num_devices_race_hispanic" numeric(12, 6),
    "dex_race_hispanic_a" numeric(12, 6),
    "num_devices_race_hispanic_a" numeric(12, 6),
    "dex_race_white" numeric(12, 6),
    "num_devices_race_white" INT,
    "dex_race_white_a" numeric(12, 6),
    "num_devices_race_white_a" INT,
    PRIMARY KEY ("date", "state")
);

COMMENT ON TABLE data.cex_state_dex is E'For a smartphone residing in a given state, how many distinct devices also visited any of the commercial venues that this device visited today? The state-level DEX reports the state-level average of this number across all devices residing in the state that day. The DEX values are necessarily only a fraction of the number of distinct individuals that also visited any of the commercial venues visited by a device, since only a fraction of individuals, venues, and visits are in the device sample.

In the context of the ongoing pandemic, the DEX measure may be biased if devices sheltering-in-place are not in the sample due to lack of movement. We report adjusted DEX values to help address this selection bias. DEX-adjusted is computed assuming that the number of devices has not declined since the early-2020 peak and that unobserved devices did not visit any commercial venues.

This index is produced by Victor Couture, Jonathan Dingel, Allison Green, Jessie Handbury, and Kevin Williams with assistance from Hayden Parsley and Serena Xu. They are derived from anonymized, aggregated smartphone movement data provided by PlaceIQ. We are grateful to the authors and to PlaceIQ for making this data available to us.

If you use this dataset, we recommend seeing the [notes for users of the DEX dataset](https://github.com/COVIDExposureIndices/COVIDExposureIndices/blob/master/documentation/DEX_notes.md) and [DEX documentation](https://github.com/COVIDExposureIndices/COVIDExposureIndices/blob/master/documentation/DEX.pdf) produced by the original authors.

Source: https://github.com/COVIDExposureIndices/COVIDExposureIndices';

COMMENT ON COLUMN data.cex_state_dex.state is E'The state for which the DEX is reported.';
COMMENT ON COLUMN data.cex_state_dex."date" is E'The date on which the DEX value was reported';
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

DROP TABLE IF EXISTS data.cex_county_dex;
CREATE TABLE data.cex_county_dex (
    "county" INT references meta.us_fips(fips),
    "date" DATE,
    "dex" numeric(12, 6),
    "num_devices" INT,
    "dex_a" numeric(12, 6),
    "num_devices_a" INT,
    PRIMARY KEY ("date", county)
);

COMMENT ON TABLE data.cex_county_dex is E'For a smartphone residing in a given county, how many distinct devices also visited any of the commercial venues that this device visited today? The county-level DEX reports the county-level average of this number across all devices residing in the county that day. The DEX values are necessarily only a fraction of the number of distinct individuals that also visited any of the commercial venues visited by a device, since only a fraction of individuals, venues, and visits are in the device sample.

In the context of the ongoing pandemic, the DEX measure may be biased if devices sheltering-in-place are not in the sample due to lack of movement. We report adjusted DEX values to help address this selection bias. DEX-adjusted is computed assuming that the number of devices has not declined since the early-2020 peak and that unobserved devices did not visit any commercial venues.

This index is produced by Victor Couture, Jonathan Dingel, Allison Green, Jessie Handbury, and Kevin Williams with assistance from Hayden Parsley and Serena Xu. They are derived from anonymized, aggregated smartphone movement data provided by PlaceIQ. We are grateful to the authors and to PlaceIQ for making this data available to us.

If you use this dataset, we recommend seeing the [notes for users of the DEX dataset](https://github.com/COVIDExposureIndices/COVIDExposureIndices/blob/master/documentation/DEX_notes.md) and [DEX documentation](https://github.com/COVIDExposureIndices/COVIDExposureIndices/blob/master/documentation/DEX.pdf) produced by the original authors.

Source: https://github.com/COVIDExposureIndices/COVIDExposureIndices';

COMMENT ON COLUMN data.cex_county_dex.county is E'County code (5-digit FIPS)';
COMMENT ON COLUMN data.cex_county_dex.date is E'The date on which the DEX value was reported';
COMMENT ON COLUMN data.cex_county_dex.dex is E'The DEX value in county on that date';
COMMENT ON COLUMN data.cex_county_dex.num_devices is E'Number of devices residing in county on that date';
COMMENT ON COLUMN data.cex_county_dex.dex_a is E'Adjusted dex in county on that date';
COMMENT ON COLUMN data.cex_county_dex.num_devices_a is E'Adjusted num_devices in county on that date';
