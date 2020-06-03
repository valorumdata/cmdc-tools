from cmdc.datasets.official.arcgis import Arcgis


def DataForArkansas():
   return Arcgis(resource_id="PwY9ZuZRDiI5nXUB", dashboard_name="ADH_COVID19_Positive_Test_Results", server_id="").df()
