import pandas as pd

from .bfs import CensusBFS
from .census import ACS1, ACS5


#
# Lists of relavant demographic features
#
population_counts = {
    "S0101_C01_001E": "Population",
    "S0101_C01_002E": "TotalPopulation_5U",
    "S0101_C01_003E": "TotalPopulation_5to9",
    "S0101_C01_004E": "TotalPopulation_9to14",
    "S0101_C01_005E": "TotalPopulation_15to19",
    "S0101_C01_006E": "TotalPopulation_20to24",
    "S0101_C01_007E": "TotalPopulation_25to29",
    "S0101_C01_008E": "TotalPopulation_30to34",
    "S0101_C01_009E": "TotalPopulation_35to39",
    "S0101_C01_010E": "TotalPopulation_40to44",
    "S0101_C01_011E": "TotalPopulation_45to49",
    "S0101_C01_012E": "TotalPopulation_50to54",
    "S0101_C01_013E": "TotalPopulation_55to59",
    "S0101_C01_014E": "TotalPopulation_60to64",
    "S0101_C01_015E": "TotalPopulation_65to69",
    "S0101_C01_016E": "TotalPopulation_70to74",
    "S0101_C01_017E": "TotalPopulation_75to79",
    "S0101_C01_018E": "TotalPopulation_80to84",
    "S0101_C01_019E": "TotalPopulation_85O",
    "S0101_C03_001E": "TotalPopulation_male",
    "S0101_C05_001E": "TotalPopulation_female",
}

commute_percentages = {
    "S0801_C01_002E": "Commute_Car",
    "S0801_C01_009E": "Commute_PublicTransport",
    "S0801_C01_010E": "Commute_Walked",
    "S0801_C01_011E": "Commute_Bicycle"
}

education_percentages = {
    "S0501_C01_039E": "Percent_LTHS",
    "S0501_C01_040E": "Percent_HS",
    "S0501_C01_041E": "Percent_SomeCollege",
    "S0501_C01_042E": "Percent_CollegeDegree",
    "S0501_C01_043E": "Percent_GraduateDegree"
}

race_percentages = {
    "S0501_C01_015E": "Percent_White",
    "S0501_C01_016E": "Percent_Black",
    "S0501_C01_017E": "Percent_NativeAmerican_AlaskaNative",
    "S0501_C01_018E": "Percent_Asian",
    "S0501_C01_019E": "Percent_NativeHawaiian_PacificIslander",
    "S0501_C01_020E": "Percent_OtherRace",
    "S0501_C01_021E": "Percent_TwoOrMoreRaces",
    "S0501_C01_022E": "Percent_HispanicLatino_AnyRace",
    "S0501_C01_023E": "Percent_White_NotHispanicLatino",
}

other_statistics = {
    "S0101_C01_032E": "MedianAge",
    "S0501_C01_101E": "MedianHHIncome",
    "S0501_C01_104E": "PercentPoverty",
}

