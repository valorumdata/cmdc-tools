DROP TABLE IF EXISTS data.mobility_lex;
CREATE TABLE data.mobility_lex (
    "dt" date,
    "fips_prev" INT references meta.us_fips(fips),
    "fips_today" INT references meta.us_fips(fips),
    "lex" REAL,
    PRIMARY KEY ("dt", "fips_prev", "fips_today")
);

COMMENT ON TABLE data.mobility_lex IS E'Among smartphones that pinged in a given state (county) today, what share of those devices pinged in each state (county) at least once during the previous 14 days? The daily state-level (county-level) LEX is a 51-by-51 (ncounties-by-ncounties) matrix in which each cell reports, among devices that pinged today in the column state (county), the share of devices that pinged in the row state (county) at least once during the previous 14 days. It is important to note that a cell phone can ping in more than a single state (county) which means that these shares will not necessarily sum to 1.

This index is produced by Victor Couture, Jonathan Dingel, Allison Green, Jessie Handbury, and Kevin Williams with assistance from Hayden Parsley and Serena Xu. They are derived from anonymized, aggregated smartphone movement data provided by PlaceIQ. We are grateful to the authors and to PlaceIQ for making this data available to us.

If you use this dataset, we recommend seeing the [notes for users of the LEX dataset](https://github.com/COVIDExposureIndices/COVIDExposureIndices/blob/master/documentation/LEX_notes.md) and [LEX documentation](https://github.com/COVIDExposureIndices/COVIDExposureIndices/blob/master/documentation/LEX.pdf) produced by the original authors.

Source: https://github.com/COVIDExposureIndices/COVIDExposureIndices';

COMMENT ON COLUMN data.mobility_lex.fips_prev IS E'The state (county) for which a device was found in the previous 14 days.';

COMMENT ON COLUMN data.mobility_lex.fips_today IS E'The state (county) for which a device was found on the given date';

COMMENT ON COLUMN data.mobility_lex.lex IS E'The LEX number';

COMMENT ON COLUMN data.mobility_lex.dt IS E'The date for which the data applies';
