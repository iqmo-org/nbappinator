from typing import Callable, Literal, Optional

import ipyaggrid as ag
import pandas as pd

from .datagrid import ColMd, DataGrid


def display_ag(
    input_df: pd.DataFrame,
    is_tree: bool,
    pathcol: Optional[str] = "path",
    pathdelim="/",
    col_md: Optional[list[ColMd]] = None,
    showindex: bool = False,
    action: Optional[Callable] = None,
    num_toppinned_rows: int = 0,
    grid_options: Optional[dict] = None,
    flatten_columns: bool = True,
    default_precision: int = 2,
    select_mode: Optional[Literal["single", "multiple"]] = None,
) -> ag.Grid:
    if col_md is None:
        col_md = []
    if grid_options is None:
        grid_options = {}

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
