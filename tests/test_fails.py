import pytest
import pandas as pd
import nbappinator
import nbappinator.plotly_charts
import plotly.express as px


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


def test_fail_plotlypng():
    df = pd.DataFrame({"col1": range(10), "col2": range(10)})
    fig = px.line(df, x="col1", y="col2")
    with pytest.raises(ValueError):
        nbappinator.plotly_charts.create_widget(fig=fig, setcolors=True, png=True)
