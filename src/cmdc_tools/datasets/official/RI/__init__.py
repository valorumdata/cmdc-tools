from .data import RhodeIsland

# Note: The following code generates the `ri_citytown_to_county.json` file
# # import geopandas as gpd
# # import json


# # This file comes from TIGER Census ShapeFiles
# # and can be found at
# # https://www2.census.gov/geo/tiger/TIGER2019/COUSUB/tl_2019_44_cousub.zip
# gdf = gpd.read_file("tl_2019_44_cousub.shp")
# gdf["fips"] = (gdf["STATEFP"] + gdf["COUNTYFP"]).astype(int)

# # city/town -> county fips dictionary
# ct_to_f = gdf[["NAME", "fips"]].set_index("NAME").to_dict()["fips"]

# with open("ri_citytown_to_county.json", "w") as f:
#     json.dump(ct_to_f, f)
