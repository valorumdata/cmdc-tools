import pandas as pd

from .. import DatasetBaseNoDate, InsertWithTempTable


class WEI(InsertWithTempTable, DatasetBaseNoDate):
    """
    The weekly economic index (WEI) is an index developed and
    published by Jim Stock. It can be found online on his blog at
    https://www.jimstock.org/ --- The description of the data
    that follows comes from his blog.

    The WEI is a composite of 6 weekly economic indicators:
      * Redbook same-store sales
      * Rasmussen Consumer Confidence
      * new claims for unemployment insurance
      * the American Staffing Association Staffing Index
      * steel production
      * wholesale sales of gasoline, diesel, and jet fuel

    All series are represented as year-over-year percentage changes.
    These series are combined into a single index of weekly economic
    activity. The index closely tracks monthly industrial production
    and quarterly GDP. Of these six series, five are available by
    Thursday morning for the week ending the previous Saturday.
    """

    pk = '("dt")'
    table_name = "weeklyeconomicindex"

    def get(self):
        """
        Fetches and updates the weekly economic index published by Jim
        Stock on his website at https://www.jimstock.org/

        Returns
        -------
        wei : pd.DataFrame
            A DataFrame that contains the weekly economic index
        """
        url = (
            "https://www.newyorkfed.org/medialibrary/research/"
            "interactives/wei/downloads/weekly-economic-index_data.xlsx"
        )
        df = pd.read_excel(url, sheet_name="2008-current", skiprows=4, usecols=[0, 1])
        return df.rename(columns={"Date": "dt", "WEI": "wei"})
