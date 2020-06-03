import asyncio
import pandas as pd

from ... import CountyData
from ....puppet import with_page
from .... import DatasetBaseNoDate


def _class_check(cls):
    return f"contains(concat(' ',normalize-space(@class),' '),' {cls} ')"


async def find_chart_data(page, div_id, colname="y", name_search="number of"):
    data = None
    tries = 25

    for i in range(tries):
        chart_div = await page.waitForSelector(f"#{div_id}")
        data = await page.evaluate("gd => gd.data", chart_div)
        layout = await page.evaluate("gd => gd.layout", chart_div)
        await asyncio.sleep(1)
        if data is not None:
            break
    else:
        raise ValueError("Did not find data!")

    # find the trace:
    assert isinstance(data, list)
    for trace in data:
        if name_search.lower() in trace["name"].lower():
            out = pd.DataFrame(
                {"date": pd.to_datetime(trace["x"]), colname: trace["y"],}
            )

            return out

    raise ValueError(f"Could not find trace with data {div_id}")

    return dict(data=data, layout=layout)


async def test_data():
    async with with_page() as page:
        await page.goto(
            "https://lacdph.shinyapps.io/covid19_surveillance_dashboard/",
            {"waitUntil": "networkidle2"},
        )

        # get cases info
        await page.waitForXPath("//div[@id='myplot']/div")
        cum_cases = await find_chart_data(page, "myplot", "cases_total", "cases")
        cum_deaths = await find_chart_data(page, "myplot", "deaths_total", "deaths")

        # move to testing page
        await (await page.waitForXPath(r"//a[@data-value='testing']")).click()

        # wait for chart to appear -- now we know we can change to Daily
        await page.waitForXPath("//div[@id='test_plot']/div")
        test = await find_chart_data(page, "test_plot", "tests", "tested")
        pos = await find_chart_data(
            page, "test_plot", "positive_tests_total", "cumulative positive"
        )

    data = (
        test.merge(pos, on="date")
        .merge(cum_cases, on="date")
        .merge(cum_deaths, on="date")
        .set_index("date")
        .assign(negative_tests_total=lambda x: x.eval("tests - positive_tests_total"))
    )
    return data[
        ["negative_tests_total", "positive_tests_total", "cases_total", "deaths_total"]
    ]


class LA(CountyData, DatasetBaseNoDate):
    def get(self):
        df = asyncio.run(test_data())
        return (
            df.reset_index()
            .rename(columns=dict(date="dt"))
            .assign(fips=6037, vintage=pd.Timestamp.today().normalize(),)
            .melt(id_vars=["vintage", "dt", "fips"], var_name="variable_name")
        )
