import time


def MT_General_Stats():
    mt = Arcgis("qnjIrwR8z5Izc0ij", "COVID_Cases_Production_View", "")
    df = mt.df()
    count = 0
    while df.columns.length <= 1:
        # Only try up to 10 times
        if count > 10:
            break
        # TODO: Make this function async 
        # Wait a few seconds and call .df() again
        time.sleep(5)
        df = mt.df()
        count += 1

    return mt.df()
