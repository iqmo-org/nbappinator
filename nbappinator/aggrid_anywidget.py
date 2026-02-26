"""AG Grid implementation using anywidget (no ipyaggrid dependency)."""

import json
from typing import Any, Callable, Dict, List, Literal, Optional, Tuple

import anywidget
import pandas as pd
import traitlets

from .datagrid import ColMd

# Default AG Grid version
DEFAULT_AGGRID_VERSION = "latest"


class AGGridWidget(anywidget.AnyWidget):
    """AG Grid widget using anywidget and AG Grid Community via CDN."""

    row_data = traitlets.Unicode("[]").tag(sync=True)
    column_defs = traitlets.Unicode("[]").tag(sync=True)
    grid_options = traitlets.Unicode("{}").tag(sync=True)
    pinned_top_rows = traitlets.Unicode("[]").tag(sync=True)

    # Layout
    height = traitlets.Int(500).tag(sync=True)
    width = traitlets.Unicode("100%").tag(sync=True)  # Can be "100%", "500px", etc.
    theme = traitlets.Unicode("ag-theme-balham").tag(sync=True)
    auto_size_columns = traitlets.Bool(False).tag(sync=True)  # Auto-fit columns to content
    size_columns_to_fit = traitlets.Bool(False).tag(sync=True)  # Fit columns to grid width

    # Tree data
    is_tree = traitlets.Bool(False).tag(sync=True)
    path_col = traitlets.Unicode("path").tag(sync=True)
    path_delim = traitlets.Unicode("/").tag(sync=True)

    # Selection
    select_mode = traitlets.Unicode("single").tag(sync=True)

    # AG Grid version
    aggrid_version = traitlets.Unicode(DEFAULT_AGGRID_VERSION).tag(sync=True)

    # Enterprise mode
    enterprise = traitlets.Bool(False).tag(sync=True)
    license_key = traitlets.Unicode("").tag(sync=True)

    # Events from JS
    selected_rows = traitlets.Unicode("[]").tag(sync=True)
    clicked_cell = traitlets.Unicode("{}").tag(sync=True)

    _esm = """
    // Inject structural CSS into a specific container (not document.head)
    // This fixes layout issues in Jupyter where head styles don't cascade properly
    function injectStructuralCSS(container) {
        const style = document.createElement("style");
        style.textContent = `
            .ag-root-wrapper {
                display: flex;
                flex-direction: column;
                overflow: hidden;
                position: relative;
            }
            .ag-root-wrapper-body {
                display: flex;
                flex: 1 1 auto;
                overflow: hidden;
                position: relative;
            }
            .ag-root {
                display: flex;
                flex-direction: column;
                flex: 1 1 auto;
                overflow: hidden;
            }
            .ag-header {
                flex: none;
                position: relative;
                z-index: 1;
            }
            .ag-body {
                display: flex;
                flex: 1 1 auto;
                flex-direction: column;
                overflow: hidden;
                position: relative;
            }
            .ag-body-viewport {
                flex: 1 1 auto;
                overflow: auto;
                position: relative;
            }
        `;
        container.appendChild(style);
    }

    // Create value formatter based on format type
    function createValueFormatter(format, precision) {
        if (!format || format === "default") {
            return (params) => {
                if (params.value == null) return null;
                if (typeof params.value === "number") {
                    return params.value.toLocaleString(undefined, {
                        minimumFractionDigits: precision,
                        maximumFractionDigits: precision
                    });
                }
                return params.value;
            };
        }
        if (format.startsWith("perc")) {
            return (params) => {
                if (params.value == null) return null;
                return (params.value * 100).toFixed(precision) + "%";
            };
        }
        if (format.startsWith("dec")) {
            return (params) => {
                if (params.value == null) return null;
                if (typeof params.value === "number") {
                    return params.value.toLocaleString(undefined, {
                        minimumFractionDigits: precision,
                        maximumFractionDigits: precision
                    });
                }
                return params.value;
            };
        }
        if (format === "mag_si") {
            return (params) => {
                if (params.value == null) return null;
                const v = params.value;
                if (v >= 1e9) return (v / 1e9).toFixed(precision) + "B";
                if (v >= 1e6) return (v / 1e6).toFixed(precision) + "M";
                if (v >= 1e3) return (v / 1e3).toFixed(precision) + "K";
                return v.toFixed(precision);
            };
        }
        return null;
    }

    // Process column definitions to add formatters
    function processColumnDefs(columnDefs) {
        return columnDefs.map(col => {
            const processed = { ...col };
            if (col._format) {
                const formatter = createValueFormatter(col._format, col._precision || 2);
                if (formatter) {
                    processed.valueFormatter = formatter;
                }
                delete processed._format;
                delete processed._precision;
            }
            return processed;
        });
    }

    export default {
        async render({ model, el }) {
            const version = model.get("aggrid_version") || "latest";
            const isEnterprise = model.get("enterprise") || false;
            const licenseKey = model.get("license_key") || "";

            // Detect dark mode from body background color
            const bgColor = window.getComputedStyle(document.body).backgroundColor;
            const rgbMatch = bgColor.match(/\\d+/g);
            const isDark = rgbMatch
                ? rgbMatch.slice(0, 3).reduce((sum, v) => sum + parseInt(v), 0) < 384
                : false;

            // Show loading state
            const modeLabel = isEnterprise ? "Enterprise" : "Community";
            el.innerHTML = `<div style="padding: 20px; color: ${isDark ? '#ccc' : '#666'};">Loading AG Grid ${modeLabel} (${version})...</div>`;

            try {
                let createGrid, themeQuartz, colorSchemeDark, colorSchemeLight;

                if (isEnterprise) {
                    const ag = await import(`https://esm.sh/ag-grid-enterprise@${version}?bundle-deps`);
                    createGrid = ag.createGrid;
                    themeQuartz = ag.themeQuartz;
                    colorSchemeDark = ag.colorSchemeDark;
                    colorSchemeLight = ag.colorSchemeLight;

                    if (ag.ModuleRegistry && ag.AllEnterpriseModule) {
                        ag.ModuleRegistry.registerModules([ag.AllEnterpriseModule]);
                    }
                    if (ag.LicenseManager && licenseKey) {
                        ag.LicenseManager.setLicenseKey(licenseKey);
                    }
                } else {
                    const ag = await import(`https://esm.sh/ag-grid-community@${version}`);
                    createGrid = ag.createGrid;
                    themeQuartz = ag.themeQuartz;
                    colorSchemeDark = ag.colorSchemeDark;
                    colorSchemeLight = ag.colorSchemeLight;

                    if (ag.ModuleRegistry && ag.AllCommunityModule) {
                        ag.ModuleRegistry.registerModules([ag.AllCommunityModule]);
                    }
                }

                // Build theme using Theming API
                const gridTheme = themeQuartz.withPart(isDark ? colorSchemeDark : colorSchemeLight);

                const height = model.get("height");
                const width = model.get("width") || "100%";
                const isTree = model.get("is_tree");
                const pathCol = model.get("path_col");
                const pathDelim = model.get("path_delim");
                const selectMode = model.get("select_mode");
                const autoSizeColumns = model.get("auto_size_columns");
                const sizeColumnsToFit = model.get("size_columns_to_fit");

                const rowData = JSON.parse(model.get("row_data"));
                const rawColumnDefs = JSON.parse(model.get("column_defs"));
                const columnDefs = processColumnDefs(rawColumnDefs);
                const pinnedTopRows = JSON.parse(model.get("pinned_top_rows"));
                const extraOptions = JSON.parse(model.get("grid_options"));

                // Clear loading message and create container
                el.innerHTML = "";
                const container = document.createElement("div");
                container.style.height = `${height}px`;
                container.style.width = width;
                el.appendChild(container);

                // Inject structural CSS into container (fixes Jupyter layout issues)
                injectStructuralCSS(container);

                // Convert selection mode to new object format (v32.2.1+)
                // checkboxes: false to avoid showing checkbox column
                const rowSelectionConfig = selectMode === "multiple"
                    ? { mode: "multiRow", checkboxes: false }
                    : { mode: "singleRow", checkboxes: false };

                const gridOptions = {
                    theme: gridTheme,
                    themeStyleContainer: container,  // Inject CSS into container, not document.head (fixes Jupyter)
                    rowData: rowData,
                    columnDefs: columnDefs,
                    defaultColDef: {
                        sortable: true,
                        filter: true,
                        resizable: true,
                    },
                    rowSelection: rowSelectionConfig,
                    animateRows: true,
                    onCellClicked: (event) => {
                        const cellData = {
                            event_type: "cellClicked",
                            col_clicked: event.column ? event.column.colId : null,
                            row_clicked: event.rowIndex,
                            value_clicked: event.value,
                            data: event.data,
                            _ts: Date.now(),  // Unique timestamp for dedupe
                        };
                        model.set("clicked_cell", JSON.stringify(cellData));
                        model.save_changes();
                    },
                    onSelectionChanged: (event) => {
                        const api = event.api;
                        const selectedNodes = api.getSelectedNodes();
                        const selectedData = selectedNodes.map(node => ({
                            key: node.key,
                            id: node.id,
                            data: node.data,
                        }));
                        model.set("selected_rows", JSON.stringify(selectedData));
                        model.save_changes();
                    },
                    ...extraOptions,
                };

                if (pinnedTopRows && pinnedTopRows.length > 0) {
                    gridOptions.pinnedTopRowData = pinnedTopRows;
                }

                if (isTree) {
                    if (!isEnterprise) {
                        // Tree Data is an Enterprise feature - show warning
                        console.warn("AG Grid Tree Data requires Enterprise. Enable enterprise=True with a valid license.");
                        // Add a visible warning above the grid
                        const warning = document.createElement("div");
                        warning.style.cssText = "padding: 8px; background: #fff3cd; color: #856404; border: 1px solid #ffc107; margin-bottom: 8px; border-radius: 4px; font-size: 12px;";
                        warning.textContent = "Tree Data requires AG Grid Enterprise. Data shown as flat table.";
                        container.parentNode.insertBefore(warning, container);
                    } else {
                        gridOptions.treeData = true;
                        gridOptions.getDataPath = (data) => {
                            if (!data || !data[pathCol]) return [];
                            return data[pathCol].split(pathDelim);
                        };
                        gridOptions.autoGroupColumnDef = {
                            headerName: "Path",
                            pinned: "left",
                            width: 300,
                            suppressSizeToFit: true,
                        };
                    }
                }

                // Create grid
                const gridApi = createGrid(container, gridOptions);

                // Size columns after data renders
                setTimeout(() => {
                    if (gridApi) {
                        if (sizeColumnsToFit) {
                            // Fit columns to fill grid width
                            gridApi.sizeColumnsToFit();
                        } else if (autoSizeColumns) {
                            // Auto-size columns to fit content
                            gridApi.autoSizeAllColumns();
                        }
                    }
                }, 200);

                // Handle data updates
                model.on("change:row_data", () => {
                    const newData = JSON.parse(model.get("row_data"));
                    if (gridApi.setGridOption) {
                        gridApi.setGridOption("rowData", newData);
                    } else if (gridApi.setRowData) {
                        gridApi.setRowData(newData);
                    }
                });

                // Cleanup on destroy
                return () => {
                    if (gridApi && gridApi.destroy) {
                        gridApi.destroy();
                    }
                };

            } catch (error) {
                el.innerHTML = `<div style="padding: 20px; color: red;">Error loading AG Grid: ${error.message}</div>`;
                console.error("AG Grid error:", error);
            }
        }
    };
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.message_handlers: List[Tuple[Callable[[Dict], None], Optional[str]]] = []
        self.current_selection: Optional[List[Dict]] = None
        self._df: Optional[pd.DataFrame] = None
        self._last_click: Optional[str] = None  # Dedupe clicks

        self.observe(self._on_selection_change, names=["selected_rows"])
        self.observe(self._on_cell_click, names=["clicked_cell"])

    def _on_selection_change(self, change):
        try:
            self.current_selection = json.loads(change["new"])
        except (json.JSONDecodeError, TypeError):
            self.current_selection = None

    def _on_cell_click(self, change):
        try:
            new_val = change["new"]
            # Dedupe - only process if value changed
            if new_val == self._last_click:
                return
            self._last_click = new_val

            msg = json.loads(new_val)
            if msg:
                self._dispatch_message(msg)
        except (json.JSONDecodeError, TypeError):
            pass

    def _dispatch_message(self, msg: Dict):
        for handler, msg_type in self.message_handlers:
            if msg_type is None or msg.get("event_type") == msg_type:
                handler(msg)

    def on(self, msg_type: str, handler: Callable[[Dict], None]):
        """Register a message handler."""
        self.message_handlers.append((handler, msg_type))

    def process_message(self, msg: Any):
        """Process a message (for compatibility with ipyaggrid DataGrid)."""
        if isinstance(msg, str):
            msg = json.loads(msg)
        self._dispatch_message(msg)

    @property
    def df(self) -> Optional[pd.DataFrame]:
        return self._df

    @df.setter
    def df(self, value: pd.DataFrame):
        self._df = value


def _build_column_def(
    col: str,
    md: Optional[ColMd] = None,
    precision: int = 2,
) -> Dict:
    """Build AG Grid column definition from ColMd."""
    if md is None:
        md = ColMd(name=col)

    col_def = {
        "field": col,
        "headerName": md.label or col.title().replace("_", " "),
        "width": 150,
        "minWidth": 100,
    }

    if md.hidden:
        col_def["hide"] = True

    if md.pinned:
        col_def["pinned"] = "left"

    prec = md.precision if md.precision is not None else precision

    # Pass format metadata - JS will create the actual formatter
    if md.format in ("perc", "percent", "perc_div"):
        col_def["_format"] = "perc"
        col_def["_precision"] = prec
        col_def["cellStyle"] = {"textAlign": "right"}
    elif md.format.startswith("dec"):
        col_def["_format"] = "dec"
        col_def["_precision"] = prec
        col_def["cellStyle"] = {"textAlign": "right"}
    elif md.format == "mag_si":
        col_def["_format"] = "mag_si"
        col_def["_precision"] = prec
        col_def["cellStyle"] = {"textAlign": "right"}
    else:
        col_def["_format"] = "default"
        col_def["_precision"] = prec
        col_def["cellStyle"] = {"textAlign": "right"}

    return col_def


def create_grid(
    input_df: pd.DataFrame,
    is_tree: bool = False,
    pathcol: str = "path",
    pathdelim: str = "/",
    col_md: Optional[List[ColMd]] = None,
    showindex: bool = False,
    action: Optional[Callable] = None,
    num_toppinned_rows: int = 0,
    grid_options: Optional[Dict] = None,
    flatten_columns: bool = True,
    default_precision: int = 2,
    select_mode: Optional[Literal["single", "multiple"]] = "single",
    height: int = 500,
    width: str = "100%",
    auto_size_columns: bool = True,
    size_columns_to_fit: bool = True,
    theme: str = "ag-theme-balham",
    aggrid_version: str = DEFAULT_AGGRID_VERSION,
    enterprise: bool = False,
    license_key: str = "",
) -> AGGridWidget:
    """
    Create an AG Grid widget using anywidget (no ipyaggrid dependency).

    Args:
        input_df: DataFrame to display
        is_tree: Enable tree data mode
        pathcol: Column containing tree path
        pathdelim: Delimiter for tree paths
        col_md: Column metadata for formatting
        showindex: Show DataFrame index as column
        action: Callback for cell click events
        num_toppinned_rows: Number of rows to pin at top
        grid_options: Additional AG Grid options
        flatten_columns: Flatten MultiIndex columns
        default_precision: Default decimal precision
        select_mode: Row selection mode ('single' or 'multiple')
        height: Grid height in pixels
        width: Grid width (e.g., "100%", "600px", "50vw")
        auto_size_columns: Auto-size columns to fit their content (default: True)
        size_columns_to_fit: Size columns to fit grid width (overrides auto_size_columns)
        theme: AG Grid theme class
        aggrid_version: AG Grid version to load from CDN (default: "latest")
                       Examples: "latest", "35.1.0"
        enterprise: Enable AG Grid Enterprise features (requires valid license)
        license_key: AG Grid Enterprise license key

    Returns:
        AGGridWidget instance
    """
    if col_md is None:
        col_md = []
    if grid_options is None:
        grid_options = {}

    df = input_df.copy()
    if flatten_columns:
        df.columns = [str(col) for col in df.columns]
    if showindex:
        df = df.reset_index()

    col_md_map = {md.name: md for md in col_md}
    column_defs = []

    for md in col_md:
        if md.name in df.columns:
            column_defs.append(_build_column_def(md.name, md, default_precision))

    for col in df.columns:
        if col not in col_md_map:
            md = ColMd(name=col)
            # Only hide tree columns when enterprise mode is enabled (tree will actually work)
            if is_tree and enterprise and col in ["index", pathcol, "path", "label", "full_label"]:
                md.hidden = True
            column_defs.append(_build_column_def(col, md, default_precision))

    for md in col_md:
        if md.format == "perc_div" and md.name in df.columns:
            df[md.name] = df[md.name] / 100

    if num_toppinned_rows > 0:
        pinned_data = df.iloc[:num_toppinned_rows].to_dict(orient="records")
        row_data = df.iloc[num_toppinned_rows:].to_dict(orient="records")
    else:
        pinned_data = []
        row_data = df.to_dict(orient="records")

    widget = AGGridWidget(
        row_data=json.dumps(row_data, default=str),
        column_defs=json.dumps(column_defs),
        grid_options=json.dumps(grid_options),
        pinned_top_rows=json.dumps(pinned_data, default=str),
        height=height,
        width=width,
        auto_size_columns=auto_size_columns,
        size_columns_to_fit=size_columns_to_fit,
        theme=theme,
        is_tree=is_tree,
        path_col=pathcol,
        path_delim=pathdelim,
        select_mode=select_mode or "single",
        aggrid_version=aggrid_version,
        enterprise=enterprise,
        license_key=license_key,
    )

    if action is not None:
        widget.on("cellClicked", action)

    widget.df = df

    return widget
