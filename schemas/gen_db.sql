DROP SCHEMA IF EXISTS data CASCADE;
DROP SCHEMA IF EXISTS meta CASCADE;
DROP SCHEMA IF EXISTS api CASCADE;

CREATE SCHEMA meta;
CREATE SCHEMA data;
CREATE SCHEMA api;

/* Create all of the base level tables */
\i usgeo_tables.sql;
\i cex_dex_tables.sql;
\i cex_lex_tables.sql;
\i uscensus_tables.sql;
\i bea_tables.sql;
\i wei_tables.sql;

/*
\i can_tables.sql;
\i jhu_tables.sql;
*/

/* Create the API interface */

\i api_cex.sql
\i api_demographics.sql
\i api_economics.sql

/*
*/

