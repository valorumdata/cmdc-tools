DROP TABLE IF EXISTS data.weeklyeconomicindex;

CREATE TABLE data.weeklyeconomicindex (
    "date" DATE PRIMARY KEY,
    wei REAL
);

COMMENT ON TABLE data.weeklyeconomicindex IS
  'A table with weekly information abou the state of the economy. It is pulled from the weekly economic index published by Jim Stock, see https://www.jimstock.org/';

COMMENT ON COLUMN data.weeklyeconomicindex.date IS 'The date for the weekly economic index. The date is recorded as the Saturday of each week.';

COMMENT ON COLUMN data.weeklyeconomicindex.wei IS 'The weekly economic index. This index is computed using a combination of weekly economic series such as steel production, retail purchases, and unemployment claims.';

