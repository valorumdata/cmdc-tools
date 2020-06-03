from cmdc.datasets.official.arcgis import Arcgis


def TotalsForMaryaland():
    """
    Returns a DF for the total number of cases divided by different counties, age groups, gender and race
    """
    my = Arcgis(resource_id="njFNhDsUCentVYJW", dashboard_name="MASTERTotalsTracker", server_id="")
    return my.df()

def CasesForMaryland():
    """
    Returns a DF for the daily case reports including:
    * Total number of cases (state wide and county level)
    * Positive tests
    * Negatives tests
    * ICU bed usage/availabilty
    """

    my = Arcgis(resource_id="njFNhDsUCentVYJW", dashboard_name="MASTERCaseTracker", server_id="")

    return my.df()
