DROP TABLE IF EXISTS data.cex_state_lex;

CREATE TABLE data.cex_state_lex (
    "date" date,
    "s_prev" char(2),
    "s_today" char(2),
    "lex" numeric(10, 8),
    PRIMARY KEY ("date", "s_prev", "s_today")
);

COMMENT ON TABLE data.cex_state_lex IS E'Among smartphones that pinged in a given state today, what share of those devices pinged in each state at least once during the previous 14 days? The daily state-level LEX is a 51-by-51 matrix in which each cell reports, among devices that pinged today in the column state, the share of devices that pinged in the row state at least once during the previous 14 days. Source: https://github.com/COVIDExposureIndices/COVIDExposureIndices';

COMMENT ON COLUMN data.cex_state_lex.s_prev IS E'The state for which a device was found in the previous 14 days.';

COMMENT ON COLUMN data.cex_state_lex.s_today IS E'The state for which a device was found on the given date';

COMMENT ON COLUMN data.cex_state_lex.lex IS E'The LEX number';

COMMENT ON COLUMN data.cex_state_lex. "date" IS E'The date for which the data applies';

DROP TABLE IF EXISTS data.cex_county_lex;

CREATE TABLE data.cex_county_lex (
    "date" timestamp WITHOUT time zone,
    "c_prev" char(5),
    "c_today" char(5),
    "lex" numeric(10, 8),
    PRIMARY KEY ("date", "c_prev", "c_today")
);

COMMENT ON TABLE data.cex_county_lex IS E'Among smartphones that pinged in a given county today, what share of those devices pinged in each county at least once during the previous 14 days? The daily county-level LEX is an approximately 2000-by-2000 matrix in which each cell reports, among devices that pinged today in the column county, the share of devices that pinged in the row county at least once during the previous 14 days. Source: https://github.com/COVIDExposureIndices/COVIDExposureIndices';

COMMENT ON COLUMN data.cex_county_lex.c_prev IS E'The county for which a device was found in the previous 14 days';

COMMENT ON COLUMN data.cex_county_lex.c_today IS E'The county for which a device was found on the given date';

COMMENT ON COLUMN data.cex_county_lex.lex IS E'The LEX number';

COMMENT ON COLUMN data.cex_county_lex. "date" IS E'The date for which the data applies';

