import os
import pandas as pd
import sqlalchemy as sa

CONN_STR = os.environ.get("PG_CONN_STR", None)


def test_provider_trigger():
    if CONN_STR is None:
        assert True
        return
    conn = sa.create_engine(CONN_STR)

    def _get_table():
        return pd.read_sql_table("us_covid", conn, schema="data")

    def _insert(variable_id, value, provider):
        sql = f"""
        INSERT INTO data.us_covid
        (vintage, dt, fips, variable_id, value, provider)
        VALUES ('2020-07-07', '2020-07-06', 25, {variable_id}, {value}, '{provider}')
        """
        conn.execute(sql)

    for p in ["us", "ctp", "nyt", "usafacts"]:
        conn.execute(f"TRUNCATE TABLE data.{p}_covid")

    # insert first couple rows
    _insert(3, 100, "state")
    _insert(6, 5, "nyt")

    df = _get_table()
    assert df.shape[0] == 2
    assert {"state", "nyt"} == set(list(df["provider"]))
    assert {100, 5} == set(list(df["value"]))

    # insert into ctp_covid table
    conn.execute(
        """
    INSERT INTO data.ctp_covid
    (vintage, dt, fips, variable_id, value)
    VALUES ('2020-07-07', '2020-07-06', 25, 6, 142);
    """
    )
    df = _get_table()
    assert df.shape[0] == 2
    assert {"state", "ctp"} == set(list(df["provider"]))
    assert {100, 142} == set(list(df["value"]))

    # insert a new row -- different fips
    conn.execute(
        """
    INSERT INTO data.ctp_covid
    (vintage, dt, fips, variable_id, value)
    VALUES ('2020-07-07', '2020-07-06', 12, 6, 142);
    """
    )
    df = _get_table()
    assert df.shape[0] == 3
    assert {"state", "ctp"} == set(list(df["provider"]))
    assert {100, 142} == set(list(df["value"]))

    # insert exising row for lower priority and ensure provider doesn't change
    for provider in ["usafacts", "nyt", "ctp"]:
        conn.execute(
            f"""
        INSERT INTO data.{provider}_covid
        (vintage, dt, fips, variable_id, value)
        VALUES ('2020-07-07', '2020-07-06', 25, 3, 142);
        """
        )
        df = _get_table()
        assert df.shape[0] == 3
        assert {"state", "ctp"} == set(list(df["provider"]))
        assert {100, 142} == set(list(df["value"]))
