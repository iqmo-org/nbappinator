import logging
import json
import pandas as pd
from dataclasses import dataclass

import ipyaggrid as ag
from typing import List, Dict, Literal, Optional
from typing import Any, Callable, Tuple, Union

logger = logging.getLogger(__name__)

# Set this to enable Enterprise features
LICENSE = "community"


def get_license():
    return LICENSE


@dataclass
class ColMd:
    name: str
    label: Optional[str] = None
    format: str = "default"  # percent, decimal, mag_si (convert to K/M/G suffixes)
    pinned: bool = False
    hidden: bool = False
    precision: Optional[int] = None

    def __post_init__(self):
        if not isinstance(self.name, str):
            self.name = str(self.name)
        if self.label is None:
            self.label = self.name.title().replace("_", " ")


def _addcol(
    md: ColMd,
    allcols: Dict[str, Dict[str, object]],
    autodetect: bool = True,
    precision: int = 2,
):
    col = md.name
    if col not in allcols:
        precision = md.precision if md.precision is not None else precision

        if autodetect and md.format == "default":
            if col.endswith("perc"):
                md.format = "perc"
                md.precision = precision

        if md.format.startswith("perc"):
            allcols[col] = {
                "field": col,
                "width": 150,
                "minWidth": 100,
                "hide": md.hidden,
                "cellStyle": {"text-align": "right"},
                "valueFormatter": """
                function (node) {
                    try {
                        if (node === null || node.value === null) {
                            return null;
                        } else {
                            return node.value.toLocaleString(undefined, { style: 'percent', minimumFractionDigits: """
                + str(precision)
                + """ });
                        }
                    } catch (error) {
                        return node.value;
                    }
                }""",
            }
        elif md.format.startswith("dec"):
            formatter = (
                """function (node) {
                    try {
                        if (node === null || node.value === null) {
                            return null;
                        } 
                        else if (node.value == 0) {
                            return node.value;
                        }
                        else {
                            return node.value.toLocaleString(undefined, { minimumFractionDigits: """
                + str(precision)
                + """, maximumFractionDigits: """
                + str(precision)
                + """  });
                        }
                    } catch (error) {
                        return node.value;
                    }
                }
                """
            )
            allcols[col] = {
                "field": col,
                "width": 150,
                "minWidth": 100,
                "cellStyle": {"text-align": "right"},
                "valueFormatter": formatter,
            }
        elif md.format == "mag_si":
            formatter = (
                """function (node) {
                    try {
                        if (node === null || node.value === null) {
                            return null;
                        } 
                        
                        let result = null;
                        let suffix = null;
                        if (node.value >= 0 && node.value <1000) {
                            result = node.value;
                            suffix = "";
                        }
                        else if (node.value >= 1000 && node.value <1000000) {
                            result = node.value/1000;
                            suffix = "K";
                        }
                        else if (node.value >= 1000000 && node.value <=1000000000) {
                            result = node.value/1000000;
                            suffix = "M";
                        }
                        else {
                            result = node.value/1000000000;
                            suffix = "B";
                        }
                        let result_round = result.toLocaleString(undefined, { minimumFractionDigits: """
                + str(precision)
                + """, maximumFractionDigits: """
                + str(precision)
                + """  }) + suffix;
                            
                        return result_round;                    
                    } catch (error) {
                        console.log(error);
                        return node.value;
                    }
                }
                """
            )
            allcols[col] = {
                "field": col,
                "width": 150,
                "minWidth": 100,
                "cellStyle": {"text-align": "right"},
                "valueFormatter": formatter,
            }
        else:
            allcols[col] = {
                "field": col,
                "width": 150,
                "minWidth": 100,
                "cellStyle": {"text-align": "right"},
                "valueFormatter": f"""function (node) {{
                    try {{
                        if (node === null || node.value === null) {{
                            return null;
                        }} else {{
                            return node.value.toLocaleString(undefined, {{ minimumFractionDigits: {str(precision)}, maximumFractionDigits: {str(precision)}  }});
                        }}
                    }} catch (error) {{
                        return node.value;
                    }}
                }}
                """,
            }

        # pinned = collower in pinned
        if md.pinned:
            allcols[col]["pinned"] = True
        if md.hidden:
            allcols[col]["hide"] = True
        allcols[col]["headerName"] = md.label


class DataGrid(ag.Grid):
    message_handlers: List[Tuple[Callable[[Dict], None], Union[str, None]]]
    current_selection: Optional[Dict] = None
    _select_mode: Optional[Literal["single", "multiple"]]

    def __init__(
        self,
        grid_data: Union[List, pd.DataFrame],
        is_tree: bool = False,
        select_mode: Optional[Literal["single", "multiple"]] = "single",
        events=None,
        pathcol: Optional[str] = "path",
        pathdelim="/",
        col_md: List[ColMd] = [],
        showindex: bool = False,
        js_post_grid: List = [],
        js_pre_grid: List = [],
        grid_options: Dict = {},
        num_toppinned_rows=0,
        flatten_columns=True,
        default_precision=2,
        *argv,
        **kargv,
    ):
        license = get_license()
        # if pathcol is not None:
        #    pathcol = pathcol.title()
        sortcols = False
        if isinstance(grid_data, pd.DataFrame) and flatten_columns:
            input_df = grid_data.copy()
            input_df.columns = [str(col) for col in input_df.columns]
        else:
            input_df = pd.DataFrame(grid_data)

        if showindex:
            input_df = input_df.reset_index()

        allcols = {}

        if select_mode is not None:
            self._select_mode = select_mode
        else:
            self._select_mode = "single"

        # Handle MD's first
        for md in col_md:
            _addcol(md, allcols, precision=default_precision)

            if md.format == "perc_div":
                input_df[md.name] = input_df[md.name] / 100

        # Handle rest of columns not in MDs
        if is_tree:
            hidecols = [
                "index",
                pathcol,
                "date",
                "cast('t' as boolean)",
                "label",
                "full_label",
                "path_nodate",
                "path",
            ]
        else:
            hidecols = []
        for col in input_df.columns:
            if col not in col_md:
                md = ColMd(name=col, hidden=col in hidecols)
                _addcol(md, allcols, precision=default_precision)

        columns = list(allcols.values())

        splitfunc = f"""function(data) {{ 
                try {{
                    if (data === null || data.{pathcol} === null) 
                        return [];
                    else return data.{pathcol}.split('{pathdelim}');
                }} catch (error) {{
                    console.log(error);
                    console.log(data);
                    return [];
                }}}}
                
                """

        # Create a GridOptions object

        if num_toppinned_rows == 0:
            grid_data_df = input_df
            pinned_top_row_data_df = None

        else:
            grid_data_df = input_df[num_toppinned_rows:]
            pinned_top_row_data_df = input_df[0:num_toppinned_rows].to_dict(
                orient="records"
            )  # type: ignore

        args = {
            "license": license,
            "grid_data": grid_data_df,
            "grid_options": {
                "pinnedTopRowData": pinned_top_row_data_df,
                "columnDefs": columns,
                "defaultColDef": {
                    "sortable": "true",
                    "filter": "true",
                    "resizable": "true",
                },
                "enableRangeSelection": False,
                "rowSelection": select_mode,
                "treeData": is_tree,
                "getDataPath": splitfunc,
                "sideBar": {
                    "toolPanels": [
                        {
                            "id": "columns",
                            "labelDefault": "Columns",
                            "labelKey": "columns",
                            "iconKey": "columns",
                            "toolPanel": "agColumnsToolPanel",
                            "toolPanelParams": {
                                "suppressRowGroups": True,
                                "suppressValues": True,
                                "suppressPivots": True,
                                "suppressPivotMode": True,
                                "suppressColumnMove": True,
                            },
                        },
                        {
                            "id": "filters",
                            "labelDefault": "Filters",
                            "labelKey": "filters",
                            "iconKey": "filter",
                            "toolPanel": "agFiltersToolPanel",
                        },
                    ]
                },
                "autoGroupColumnDef": {
                    "headerName": "Path",
                    "pinned": "left",
                    "width": 300,
                    "suppressSizeToFit": True,
                    "suppressAutoSize": True,
                },
                **grid_options,
            },
            "quick_filter": True,
            "show_toggle_edit": False,
            "theme": "ag-theme-balham",
            "show_toggle_delete": False,
            "columns_fit": "auto",
            "index": sortcols,
            "keep_multiindex": showindex,
            "height": 500,  # px
            "width": "100%",
            "js_post_grid": [
                f"""
                let events={json.dumps(events)}
                //always include cell clicked so we can set the selected row
                if(!events){{
                    events=['cellClicked']
                }}
                else if(events.indexOf('cellClicked') < 0){{
                    events.push('cellClicked')
                }}

                events.forEach(eventName=>{{
                    console.log("Adding listener for",eventName)
                    view.gridOptions.api.addEventListener(eventName,(e)=>{{
                        console.log("Sending message for",eventName,e)
                        view.send({{
                            type: "gridEvent", 
                            event_type:eventName, 
                            col_clicked: e.column ? e.column.colId : undefined,
                            row_clicked: e.rowIndex,
                            value_clicked: e.value,
                            currentSelection:view.gridOptions.api.getSelectedNodes().map(n=>({{
                                key: n.key,
                                id: n.id,
                                data: n.data,
                                field:n.field,
                                leafData:n.allLeafChildren ? n.allLeafChildren.map(c=>c.data): undefined
                            }}))
                            }})
                        console.log("Sent message for",eventName)
                    }})
                    console.log("Added listener for",eventName)
                }})""",
                *js_post_grid,
            ],
            "js_pre_grid": [
                """
                console.log('******here***********',gridOptions);
                /*this isnt working, because the grid has no size 
                gridOptions.onFirstDataRendered = function onFirstDataRendered(params) {
                params.columnApi.autoSizeAllColumns();
                }*/
                let first=true;
                gridOptions.onGridSizeChanged=  function onFirstDataRendered(params) {
                
                if(first){
                      params.columnApi.autoSizeAllColumns();
                }
                }
                """,
                *js_pre_grid,
            ],
            **kargv,
        }

        super().__init__(*argv, **args)

        self.message_handlers = []

        def msg_rx(
            _, msg, buffers
        ):  # pragma: no cover  # bypassing because only reached from js
            try:
                self.process_message(msg)
            except Exception as e:
                logger.info("Unable to send msg")
                logger.exception(e)

        self.on_msg(msg_rx)

    def process_message(self, msg: Any):
        logger.debug("Widget got message: %s", msg)
        pMsg = msg

        # make sure its one of our events
        if "type" not in pMsg or pMsg["type"] != "gridEvent" and "event_type" in pMsg:
            return

        if self._select_mode is not None:
            if pMsg["event_type"] == "cellClicked" and "currentSelection" in pMsg:
                self.current_selection = pMsg["currentSelection"]

        logger.debug("Checking message handler for %s", len(self.message_handlers))
        for handler, handle_msg_type in self.message_handlers:
            logger.debug(
                "Checking message handler for %s and message type %s",
                handle_msg_type,
                pMsg["type"],
            )
            if handle_msg_type is None or pMsg["event_type"] == handle_msg_type:
                logger.debug("Calling handler")
                handler(pMsg)

    def on(
        self,
        msg_type: str,
        handler: Callable[[Dict], None],
    ):
        self.message_handlers.append((handler, msg_type))

    def remove_message_handler(self, handler: Callable[[Dict], None]):
        for handler_tuple in self.message_handlers:
            if handler_tuple[0] == handler:
                self.message_handlers.remove(handler_tuple)
                return True
        return False
