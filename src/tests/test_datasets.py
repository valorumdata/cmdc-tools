from cmdc import datasets
import pytest
import pandas as pd


@pytest.mark.parametrize("cls", datasets.DatasetBaseNoDate.__subclasses__())
def test_no_date_datasets(cls):
    if cls is datasets.WEI:
        print("Skipping!")
        assert True
        return
    d = cls()
    out = d.get()
    assert isinstance(out, pd.DataFrame)
    assert out.shape[0] > 0


@pytest.mark.parametrize("cls", datasets.DatasetBaseNeedsDate.__subclasses__())
def test_need_date_datasets(cls):
    d = cls()
    out = d.get("2020-05-25")
    assert isinstance(out, pd.DataFrame)
    assert out.shape[0] > 0
