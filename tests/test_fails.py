import pandas as pd
import plotly.express as px
import pytest

import nbappinator
import nbappinator.plotly_charts


def test_fail_invalidpathcol():
    myapp = nbappinator.App(tabs=["First Tab"], footer="Messages", header="Config")
    df = pd.DataFrame({"col1": [1, 2, 3]})
    with pytest.raises(ValueError):
        myapp.tab(0).dataframe("df1", df, tree=True, tree_column="Doesn't Exist", tree_delimiter="/")


def test_fail_notapage():
    myapp = nbappinator.App(tabs=["First Tab"], footer="Messages", header="Config")
    with pytest.raises(KeyError):
        myapp.tab("asdasdTable")


def test_fail_plotlypng():
    df = pd.DataFrame({"col1": range(10), "col2": range(10)})
    fig = px.line(df, x="col1", y="col2")
    with pytest.raises(ValueError):
        nbappinator.plotly_charts.create_widget(fig=fig, setcolors=True, png=True)
