import pandas as pd

def main():
    url = "https://raw.githubusercontent.com/kjhealy/fips-codes/master/state_and_county_fips_master.csv"
    df = (
        pd.read_csv(url)
        .rename(columns=dict(name="county_name", state="state_abbr"))
        .assign(
            state=lambda x: x["fips"].astype(str).str.zfill(5).str[:2].astype(int),
            county=lambda x: x["fips"].astype(str).str.zfill(5).str[3:].astype(int)
        )
        .fillna(dict(state_abbr="NA"))
    )

    return df
