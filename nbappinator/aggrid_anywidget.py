"""AG Grid implementation using anywidget (no ipyaggrid dependency)."""

import json
from typing import Any, Callable, Dict, List, Literal, Optional, Tuple

import anywidget
import pandas as pd
import traitlets

# Default AG Grid version
DEFAULT_AGGRID_VERSION = "latest"

# Built-in format types
FORMAT_DEFAULT = "default"
FORMAT_DECIMAL = "decimal"
FORMAT_PERCENT = "percent"
FORMAT_MAG_SI = "mag_si"


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

    # Styling
    spacing = traitlets.Int(4).tag(sync=True)  # Cell padding
    font_size = traitlets.Int(12).tag(sync=True)  # Font size in pixels
    row_height = traitlets.Int(28).tag(sync=True)  # Row height in pixels
    header_height = traitlets.Int(32).tag(sync=True)  # Header height in pixels

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
    function injectNotebookStyles(isDark) {
        const styleId = 'ag-grid-notebook-fix';
        if (document.getElementById(styleId)) return;  // Already injected

        const style = document.createElement('style');
        style.id = styleId;
        style.textContent = `
            .cell-output-ipywidget-background,
            .cell-output-ipywidget-background > * {
                background-color: ${isDark ? '#181d1f' : '#fff'} !important;
            }
        `;
        document.head.appendChild(style);
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

            // Handle string valueFormatter FIRST - user's custom formatter takes precedence
            // This allows custom formatters like: "params => params.value.toFixed(2) + '%'"
            if (typeof col.valueFormatter === 'string') {
                try {
                    // Use Function constructor to safely evaluate the arrow function string
                    processed.valueFormatter = new Function('return ' + col.valueFormatter)();
                    // Skip _format processing since user provided custom formatter
                    delete processed._format;
                    delete processed._precision;
                } catch (e) {
                    console.warn('Invalid valueFormatter string:', e);
                    delete processed.valueFormatter;
                }
            }
            // Only use _format if no custom valueFormatter was provided
            else if (col._format) {
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
                    const ag = await import(`https://cdn.jsdelivr.net/npm/ag-grid-enterprise@${version}/+esm`);
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
                    const ag = await import(`https://cdn.jsdelivr.net/npm/ag-grid-community@${version}/+esm`);
                    createGrid = ag.createGrid;
                    themeQuartz = ag.themeQuartz;
                    colorSchemeDark = ag.colorSchemeDark;
                    colorSchemeLight = ag.colorSchemeLight;

                    if (ag.ModuleRegistry && ag.AllCommunityModule) {
                        ag.ModuleRegistry.registerModules([ag.AllCommunityModule]);
                    }
                }

                // Build theme using Theming API with configurable styling
                const spacing = model.get("spacing") || 4;
                const fontSize = model.get("font_size") || 12;
                const rowHeight = model.get("row_height") || 28;
                const headerHeight = model.get("header_height") || 32;

                const gridTheme = themeQuartz
                    .withPart(isDark ? colorSchemeDark : colorSchemeLight)
                    .withParams({
                        spacing: spacing,
                        fontSize: fontSize,
                        headerFontSize: fontSize,
                        rowHeight: rowHeight,
                        headerHeight: headerHeight,
                    });

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
                // Use explicit background color to avoid white gaps
                const darkBgColor = "#181d1f";  // AG Grid quartz dark theme background
                const lightBgColor = "#fff";     // AG Grid quartz light theme background
                const bgColor = isDark ? darkBgColor : lightBgColor;

                el.innerHTML = "";
                el.style.backgroundColor = bgColor;
                el.style.width = width;

                const container = document.createElement("div");
                container.style.height = `${height}px`;
                container.style.width = "100%";
                container.style.backgroundColor = bgColor;
                el.appendChild(container);

                injectNotebookStyles(isDark);

                // Convert selection mode to new object format (v32.2.1+)
                // checkboxes: false to avoid showing checkbox column
                const rowSelectionConfig = selectMode === "multiple"
                    ? { mode: "multiRow", checkboxes: false }
                    : { mode: "singleRow", checkboxes: false };

                const gridOptions = {
                    theme: gridTheme,
                    themeStyleContainer: document.body,  // Use body to ensure styles load after app styles
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

                // Force layout refresh after theme CSS applies
                requestAnimationFrame(() => {
                    requestAnimationFrame(() => {
                        if (gridApi) {
                            gridApi.refreshHeader();
                            // Trigger full layout recalculation
                            const currentHeight = container.style.height;
                            container.style.height = '0px';
                            container.offsetHeight;  // Force reflow
                            container.style.height = currentHeight;
                        }
                    });
                });

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

                // Custom context menu (works without Enterprise)
                const contextMenu = document.createElement("div");
                contextMenu.style.cssText = `
                    display: none;
                    position: fixed;
                    background: ${isDark ? '#2d2d2d' : '#fff'};
                    border: 1px solid ${isDark ? '#555' : '#ccc'};
                    border-radius: 4px;
                    box-shadow: 2px 2px 8px rgba(0,0,0,0.2);
                    z-index: 10000;
                    min-width: 150px;
                    font-size: 12px;
                    color: ${isDark ? '#e0e0e0' : '#333'};
                `;

                const menuItems = [
                    { label: "Copy Cell", action: "copyCell" },
                    { label: "Copy Row", action: "copyRow" },
                    { label: "---", action: "separator" },
                    { label: "Export CSV", action: "exportCsv" },
                ];

                menuItems.forEach(item => {
                    if (item.action === "separator") {
                        const sep = document.createElement("div");
                        sep.style.cssText = `height: 1px; background: ${isDark ? '#555' : '#ddd'}; margin: 4px 0;`;
                        contextMenu.appendChild(sep);
                    } else {
                        const menuItem = document.createElement("div");
                        menuItem.textContent = item.label;
                        menuItem.dataset.action = item.action;
                        menuItem.style.cssText = `
                            padding: 6px 12px;
                            cursor: pointer;
                        `;
                        menuItem.onmouseenter = () => menuItem.style.background = isDark ? '#404040' : '#f0f0f0';
                        menuItem.onmouseleave = () => menuItem.style.background = 'transparent';
                        contextMenu.appendChild(menuItem);
                    }
                });

                document.body.appendChild(contextMenu);

                let contextCell = null;

                container.addEventListener("contextmenu", (e) => {
                    e.preventDefault();
                    const cell = e.target.closest(".ag-cell");
                    if (cell) {
                        contextCell = cell;
                        contextMenu.style.display = "block";
                        contextMenu.style.left = e.clientX + "px";
                        contextMenu.style.top = e.clientY + "px";
                    }
                });

                document.addEventListener("click", () => {
                    contextMenu.style.display = "none";
                });

                contextMenu.addEventListener("click", (e) => {
                    const action = e.target.dataset.action;
                    if (!action) return;

                    if (action === "copyCell" && contextCell) {
                        const text = contextCell.textContent || "";
                        navigator.clipboard.writeText(text);
                    } else if (action === "copyRow") {
                        const focusedCell = gridApi.getFocusedCell();
                        if (focusedCell) {
                            const rowNode = gridApi.getDisplayedRowAtIndex(focusedCell.rowIndex);
                            if (rowNode && rowNode.data) {
                                const values = Object.values(rowNode.data).join("\\t");
                                navigator.clipboard.writeText(values);
                            }
                        }
                    } else if (action === "exportCsv") {
                        gridApi.exportDataAsCsv({ fileName: "export.csv" });
                    }

                    contextMenu.style.display = "none";
                });

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
                    if (contextMenu && contextMenu.parentNode) {
                        contextMenu.parentNode.removeChild(contextMenu);
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


def get_column_defs(
    df: pd.DataFrame,
    precision: int = 2,
) -> List[Dict[str, Any]]:
    """
    Generate AG Grid columnDefs from a DataFrame.

    Returns native AG Grid column definitions that can be customized
    before passing to create_grid().

    Args:
        df: Source DataFrame
        precision: Default decimal precision for numeric columns

    Returns:
        List of AG Grid columnDef dictionaries
    """
    column_defs = []

    for col in df.columns:
        col_str = str(col)
        col_def: Dict[str, Any] = {
            "field": col_str,
            "headerName": col_str.replace("_", " ").title(),
        }

        # Infer type-appropriate defaults for numeric columns
        if pd.api.types.is_numeric_dtype(df[col]):
            col_def["type"] = "numericColumn"
            col_def["cellStyle"] = {"textAlign": "right"}
            col_def["_format"] = "default"
            col_def["_precision"] = precision

        column_defs.append(col_def)

    return column_defs


def apply_format(
    col_def: Dict[str, Any],
    format_type: str = FORMAT_DEFAULT,
    precision: int = 2,
) -> Dict[str, Any]:
    """
    Apply a built-in format to a column definition.

    Args:
        col_def: AG Grid column definition dictionary
        format_type: Format type - FORMAT_DEFAULT, FORMAT_DECIMAL, FORMAT_PERCENT, FORMAT_MAG_SI
        precision: Decimal precision

    Returns:
        The modified col_def (also modifies in place)
    """
    col_def["_format"] = format_type
    col_def["_precision"] = precision
    col_def["cellStyle"] = {"textAlign": "right"}
    return col_def


def create_grid(
    input_df: pd.DataFrame,
    is_tree: bool = False,
    pathcol: str = "path",
    pathdelim: str = "/",
    column_defs: Optional[List[Dict[str, Any]]] = None,
    showindex: bool = False,
    action: Optional[Callable] = None,
    num_toppinned_rows: int = 0,
    grid_options: Optional[Dict] = None,
    flatten_columns: bool = True,
    default_precision: int = 2,
    select_mode: Optional[Literal["single", "multiple"]] = "single",
    height: int = 500,
    width: str = "100%",
    auto_size_columns: bool = False,
    size_columns_to_fit: bool = False,
    theme: str = "ag-theme-balham",
    aggrid_version: str = DEFAULT_AGGRID_VERSION,
    enterprise: bool = False,
    license_key: str = "",
    spacing: int = 4,
    font_size: int = 12,
    row_height: int = 28,
    header_height: int = 32,
) -> AGGridWidget:
    """
    Create an AG Grid widget using anywidget (no ipyaggrid dependency).

    Args:
        input_df: DataFrame to display
        is_tree: Enable tree data mode
        pathcol: Column containing tree path
        pathdelim: Delimiter for tree paths
        column_defs: AG Grid column definitions (use get_column_defs() to generate, then customize)
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
        spacing: Cell padding in pixels (default: 4)
        font_size: Font size in pixels (default: 12)
        row_height: Row height in pixels (default: 28)
        header_height: Header height in pixels (default: 32)

    Returns:
        AGGridWidget instance

    Example:
        >>> # Basic usage - auto-generated columns
        >>> grid = create_grid(df)

        >>> # Custom columns with formatting
        >>> cols = get_column_defs(df)
        >>> apply_format(cols[1], FORMAT_MAG_SI)  # Apply MAG_SI to second column
        >>> cols[0]["pinned"] = "left"  # Pin first column
        >>> grid = create_grid(df, column_defs=cols)

        >>> # Custom JS formatter
        >>> cols = get_column_defs(df)
        >>> cols[2]["valueFormatter"] = "params => '$' + params.value.toFixed(2)"
        >>> grid = create_grid(df, column_defs=cols)
    """
    if grid_options is None:
        grid_options = {}

    df = input_df.copy()
    if flatten_columns:
        df.columns = [str(col) for col in df.columns]
    if showindex:
        df = df.reset_index()

    # Generate column definitions if not provided
    if column_defs is None:
        column_defs = get_column_defs(df, precision=default_precision)
        # Hide tree columns when enterprise mode is enabled
        if is_tree and enterprise:
            tree_cols = {"index", pathcol, "path", "label", "full_label"}
            for col_def in column_defs:
                if col_def.get("field") in tree_cols:
                    col_def["hide"] = True

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
        spacing=spacing,
        font_size=font_size,
        row_height=row_height,
        header_height=header_height,
    )

    if action is not None:
        widget.on("cellClicked", action)

    widget.df = df

    return widget


_original_dataframe_repr_html = None


def register_grid_renderer(height: int = 400, **grid_kwargs) -> None:
    """
    Register create_grid as the default renderer for pandas DataFrames.

    After calling this, any DataFrame displayed in a notebook cell will
    automatically render as an AG Grid instead of the default HTML table.

    Args:
        height: Default grid height in pixels
        **grid_kwargs: Additional arguments passed to create_grid (e.g., enterprise, license_key)
    """
    global _original_dataframe_repr_html

    # Save original _repr_html_ method
    if _original_dataframe_repr_html is None:
        _original_dataframe_repr_html = pd.DataFrame._repr_html_

    def _grid_repr_html_(self):
        from IPython.display import display

        grid = create_grid(self, height=height, **grid_kwargs)
        display(grid)
        return ""  # Return empty string to suppress default output

    # Monkey-patch DataFrame's _repr_html_
    pd.DataFrame._repr_html_ = _grid_repr_html_


def unregister_grid_renderer() -> None:
    """
    Restore default pandas DataFrame rendering.
    """
    global _original_dataframe_repr_html

    if _original_dataframe_repr_html is not None:
        pd.DataFrame._repr_html_ = _original_dataframe_repr_html
        _original_dataframe_repr_html = None
