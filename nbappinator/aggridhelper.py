import ipyaggrid as ag
import pandas as pd
from .datagrid import ColMd, DataGrid
from typing import Optional, Callable, Literal


def display_ag(
    input_df: pd.DataFrame,
    is_tree: bool,
    pathcol: Optional[str] = "path",
    pathdelim="/",
    col_md: list[ColMd] = [],  # noqa: F821
    showindex: bool = False,
    action: Optional[Callable] = None,
    num_toppinned_rows: int = 0,
    grid_options: dict = {},
    flatten_columns: bool = True,
    default_precision: int = 2,
    select_mode: Optional[Literal["single", "multiple"]] = None,
) -> ag.Grid:

    grid = DataGrid(
        grid_data=input_df,
        is_tree=is_tree,
        pathcol=pathcol,
        pathdelim=pathdelim,
        col_md=col_md,
        showindex=showindex,
        num_toppinned_rows=num_toppinned_rows,
        grid_options=grid_options,
        default_precision=default_precision,
        flatten_columns=flatten_columns,
        select_mode=select_mode,
    )

    if action is not None:
        grid.on("cellClicked", action)

    grid.df = input_df  # type: ignore
    return grid
