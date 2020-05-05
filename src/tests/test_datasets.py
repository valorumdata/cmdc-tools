from cmdc.datasets.db_util import draft_sql_ddl_statement
import pandas as pd


class TestDraftSqlDdl:
    df1 = pd.DataFrame(
        dict(
            x=[1, 2, 3],
            y=[1.0, 2.0, 3.0],
            z=pd.date_range("2020-01-01", freq="D", periods=3),
            w=list("abc"),
        )
    )

    def test_df1(self):
        want = """
        CREATE
        """
