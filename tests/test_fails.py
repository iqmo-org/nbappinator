import pytest
import pandas as pd
import nbappinator

# TODO: Remove the next two lines and activate externally
import coverage

coverage.process_startup()


def test_fail_invalidselectoption():
    myapp = nbappinator.TabbedUiModel(
        pages=["Page 1"],
        title="Some Title That'll Only Show Up in Voila",
        log_footer="Messages",
        headers=["Config"],
    )

    with pytest.raises(ValueError):
        myapp.get_page(0).add_select(label="Foo", type=9)  # type: ignore


def test_fail_invalidpathcol():
    myapp = nbappinator.TabbedUiModel(
        pages=["First Tab"], log_footer="Messages", headers=["Config"]
    )
    df = pd.DataFrame({"col1": [1, 2, 3]})
    with pytest.raises(ValueError):

        myapp.get_page(0).add_df(
            df=df, tree=True, pathcol="Doesn't Exist", pathdelim="/"
        )


def test_fail_notapage():
    myapp = nbappinator.TabbedUiModel(
        pages=["First Tab"], log_footer="Messages", headers=["Config"]
    )
    with pytest.raises(ValueError):
        myapp.get_page("asdasdTable")
