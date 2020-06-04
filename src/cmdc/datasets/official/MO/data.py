import time

from cmdc.datasets.official.arcgis import Arcgis


def MO_Hospital_Data():
    hospital = Arcgis("Bd4MACzvEukoZ9mR", "MHA_COVID_19_Patient_Layer", "6")
    hdf = hospital.df()
    # Check and wait for response to come back
    count = 0
    while hdf.columns.length <= 1:
        # Only try up to 10 times
        if count > 10:
            break
        # TODO: Make this function async 
        # Wait a few seconds and call .df() again
        time.sleep(5)
        hdf = hospital.df()
        count += 1
    
    return hdf
