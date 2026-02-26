"""
Example:
    import nbappinator as nb

    app = nb.App(tabs=["Chart"], header="Config", footer="Messages")

    app.config.select("source", options=["a", "b"], default="a")
    app.config.button("Draw", on_click=draw_chart, status=True)

    def draw_chart(app):
        app.status("Drawing...")
        source = app["source"]

        app.tab("Chart").clear()
        app.tab("Chart").plotly(fig)

        app.done()

    app.display()
"""

import io
import logging
from functools import wraps
from typing import Any, Callable, List, Optional, Union

import ipyvuetify as v
import ipywidgets
from IPython.display import display

from . import aggrid_anywidget, graphvizgraph, networkgraph, plotly_charts, treew
from .browser_title import BrowserTitle
from .datagrid import ColMd

logger = logging.getLogger(__name__)


class Page:
    """A page/section in the app that can contain widgets."""

    def __init__(self, app: "App", name: str, widget: Any):
        self._app = app
        self._name = name
        self._widget = widget  # Container widget with children attribute

    def clear(self) -> "Page":
        """Clear all widgets from this page."""
        self._widget.children = []
        return self

    def _add_widget(self, widget: ipywidgets.Widget, name: Optional[str] = None) -> "Page":
        """Add a widget to this page."""
        self._widget.children = (*self._widget.children, widget)
        if name:
            self._app._widgets[name] = widget
        return self

    def select(
        self,
        name: str,
        options: List,
        default=None,
        label: Optional[str] = None,
        on_change: Optional[Callable] = None,
        multiple: bool = False,
        disabled: bool = False,
    ) -> "Page":
        """Add a dropdown select widget."""
        w = v.Select(
            label=label or name,
            items=options,
            v_model=default,
            multiple=multiple,
            disabled=disabled,
        )
        if on_change:
            w.on_event("change", self._app._wrap_callback(on_change, name))
        return self._add_widget(w, name)

    def combobox(
        self,
        name: str,
        options: List,
        default=None,
        label: Optional[str] = None,
        on_change: Optional[Callable] = None,
        multiple: bool = False,
        disabled: bool = False,
    ) -> "Page":
        """Add a combobox (select with text input)."""
        w = v.Combobox(
            label=label or name,
            items=options,
            v_model=default,
            multiple=multiple,
            disabled=disabled,
        )
        if on_change:
            w.on_event("change", self._app._wrap_callback(on_change, name))
        return self._add_widget(w, name)

    def slider(
        self,
        name: str,
        min_val: int,
        max_val: int,
        default: Optional[int] = None,
        label: Optional[str] = None,
        on_change: Optional[Callable] = None,
        step: int = 1,
        disabled: bool = False,
    ) -> "Page":
        """Add a slider widget."""
        w = v.Slider(
            label=label or name,
            min=min_val,
            max=max_val,
            v_model=default if default is not None else min_val,
            step=step,
            thumb_label=True,
            disabled=disabled,
        )
        if on_change:
            w.on_event("change", self._app._wrap_callback(on_change, name))
        return self._add_widget(w, name)

    def radio(
        self,
        name: str,
        options: List,
        default=None,
        label: Optional[str] = None,
        on_change: Optional[Callable] = None,
        horizontal: bool = False,
        disabled: bool = False,
    ) -> "Page":
        """Add radio buttons."""
        children = [v.Radio(label=str(o), value=str(o)) for o in options]
        w = v.RadioGroup(
            label=label or name,
            children=children,
            v_model=default,
            row=horizontal,
            disabled=disabled,
        )
        if on_change:
            w.on_event("change", self._app._wrap_callback(on_change, name))
        return self._add_widget(w, name)

    def text(
        self,
        name: str,
        default: str = "",
        label: Optional[str] = None,
        on_change: Optional[Callable] = None,
        multiline: bool = False,
        disabled: bool = False,
    ) -> "Page":
        """Add a text input (single line or multiline)."""
        if multiline:
            w = v.Textarea(label=label or name, v_model=default, disabled=disabled)
        else:
            w = v.TextField(label=label or name, v_model=default, disabled=disabled)
        if on_change:
            w.on_event("change", self._app._wrap_callback(on_change, name))
        return self._add_widget(w, name)

    def checkbox(
        self,
        name: str,
        default: bool = False,
        label: Optional[str] = None,
        on_change: Optional[Callable] = None,
        disabled: bool = False,
    ) -> "Page":
        """Add a checkbox widget."""
        w = v.Checkbox(label=label or name, v_model=default, disabled=disabled)
        if on_change:
            w.on_event("change", self._app._wrap_callback(on_change, name))
        return self._add_widget(w, name)

    def button(
        self,
        name: str,
        on_click: Callable,
        label: Optional[str] = None,
        status: bool = False,
        disabled: bool = False,
    ) -> "Page":
        """Add a button.

        Args:
            name: Widget name for reference
            on_click: Callback function (receives app as only argument)
            label: Button label (defaults to name)
            status: If True, adds a status display next to the button
            disabled: If True, button starts disabled
        """
        btn_label = label or name

        if status:
            # Create container for button + status
            container = v.Html(tag="div", class_="d-flex flex-column", children=[])
            btn = v.Btn(children=[btn_label], disabled=disabled, outlined=True)

            status_field = v.TextField(
                v_model="Ready",
                disabled=True,
                solo=True,
                flat=True,
                class_="for-progress",
            )
            progress = v.ProgressLinear(
                class_="progress-bar",
                color="blue",
                indeterminate=True,
            )
            progress.hide()

            container.children = [btn, status_field, progress]

            # Store references
            self._app._widgets[name] = btn
            self._app._status_widgets[name] = {
                "field": status_field,
                "progress": progress,
            }

            btn.on_event("click", self._app._wrap_callback(on_click, name))
            return self._add_widget(container)
        else:
            btn = v.Btn(children=[btn_label], disabled=disabled, outlined=True)
            btn.on_event("click", self._app._wrap_callback(on_click, name))
            self._app._widgets[name] = btn
            return self._add_widget(btn, name)

    # --- Display widgets ---

    def label(self, text: str, name: Optional[str] = None) -> "Page":
        """Add a static text label."""
        w = v.CardText(children=[text])
        return self._add_widget(w, name)

    def pre(self, text: str, name: Optional[str] = None) -> "Page":
        """Add preformatted text."""
        w = v.Html(tag="pre", children=[text], style_="max-height:80vh")
        return self._add_widget(w, name)

    def html(self, content: str, name: Optional[str] = None) -> "Page":
        """Add raw HTML content."""
        w = v.Html(tag="div", children=[content])
        return self._add_widget(w, name)

    def separator(self, color: str = "gray") -> "Page":
        """Add a horizontal separator line."""
        w = v.Html(tag="hr", style_=f"border: none; border-top: 5px solid {color};")
        return self._add_widget(w)

    def output(self, name: str, max_lines: Optional[int] = None) -> "Page":
        """Add an output area for print statements."""
        w = ipywidgets.Output()
        if max_lines:
            w.max_outputs = max_lines
        return self._add_widget(w, name)

    # --- Data/Chart widgets ---

    def dataframe(
        self,
        name: str,
        df,
        on_click: Optional[Callable] = None,
        tree: bool = False,
        tree_column: Optional[str] = None,
        tree_delimiter: str = "~",
        columns: Optional[List[ColMd]] = None,
        show_index: bool = False,
        pinned_rows: int = 0,
        precision: int = 2,
        multiselect: bool = False,
        grid_options: Optional[dict] = None,
        height: int = 500,
        enterprise: bool = False,
        license_key: str = "",
    ) -> "Page":
        """Add an AG Grid dataframe display.

        Args:
            name: Widget name for referencing
            df: DataFrame to display
            on_click: Callback for cell click events
            tree: Enable tree data mode (requires enterprise=True)
            tree_column: Column containing tree path
            tree_delimiter: Delimiter for tree paths
            columns: Column metadata for formatting (list of ColMd)
            show_index: Show DataFrame index as column
            pinned_rows: Number of rows to pin at top
            precision: Default decimal precision
            multiselect: Enable multiple row selection
            grid_options: Additional AG Grid options
            height: Grid height in pixels
            enterprise: Enable AG Grid Enterprise features
            license_key: AG Grid Enterprise license key

        Returns:
            Page instance for chaining
        """
        if tree and tree_column and tree_column not in df.columns:
            raise ValueError(f"tree_column '{tree_column}' not found in DataFrame columns")

        w = aggrid_anywidget.create_grid(
            df,
            is_tree=tree,
            pathcol=tree_column or "path",
            pathdelim=tree_delimiter,
            col_md=columns or [],
            showindex=show_index,
            action=on_click,
            num_toppinned_rows=pinned_rows,
            grid_options=grid_options or {},
            default_precision=precision,
            select_mode="multiple" if multiselect else "single",
            height=height,
            enterprise=enterprise,
            license_key=license_key,
        )
        return self._add_widget(w, name)

    def plotly(
        self,
        fig,
        name: Optional[str] = None,
        height: Optional[int] = None,
        width: Optional[int] = None,
    ) -> "Page":
        """Add a Plotly figure."""
        w = plotly_charts.create_widget(fig=fig, height=height, width=width)
        return self._add_widget(w, name)

    def matplotlib(
        self,
        fig,
        name: Optional[str] = None,
        width: int = 1024,
        height: int = 1024,
    ) -> "Page":
        """Add a matplotlib figure."""
        buf = io.BytesIO()
        fig.savefig(buf, format="png")
        w = ipywidgets.Image(value=buf.getvalue(), format="png", width=width, height=height)
        return self._add_widget(w, name)

    def networkx(
        self,
        graph,
        name: Optional[str] = None,
        width: int = 800,
        height: int = 600,
        layout: networkgraph.LayoutType = "force",
        charge_strength: int = -200,
        link_distance: int = 80,
        show_labels: bool = True,
        node_color: str = "#69b3a2",
        directed: bool = False,
        node_size: int = 8,
        size_by_degree: bool = False,
    ) -> "Page":
        """Add a NetworkX graph visualization.

        Args:
            graph: NetworkX graph object
            name: Optional widget name for reference
            width: Canvas width in pixels
            height: Canvas height in pixels
            layout: Layout algorithm
            charge_strength: Node repulsion force (negative). More negative = more spread.
            link_distance: Target distance between connected nodes.
            show_labels: Whether to show node labels.
            node_color: Node fill color (CSS color string).
            directed: Whether to show directional arrows on edges.
            node_size: Node radius in pixels.
            size_by_degree: Scale node size by degree.
        """
        w = networkgraph.create_graph_d3(
            nx_graph=graph,
            width=width,
            height=height,
            layout=layout,
            charge_strength=charge_strength,
            link_distance=link_distance,
            show_labels=show_labels,
            node_color=node_color,
            directed=directed,
            node_size=node_size,
            size_by_degree=size_by_degree,
        )
        return self._add_widget(w, name)

    def graphviz(
        self,
        graph,
        name: Optional[str] = None,
        width: int = 800,
        height: int = 600,
        engine: graphvizgraph.LayoutEngine = "dot",
        node_attr: Optional[dict] = None,
        edge_attr: Optional[dict] = None,
        graph_attr: Optional[dict] = None,
        scale: float = 0.75,
        fit_width: bool = True,
        show_labels: bool = True,
    ) -> "Page":
        """Add a Graphviz graph visualization.

        Args:
            graph: NetworkX graph object
            name: Optional widget name for reference
            width: Canvas width in pixels (used when fit_width=False)
            height: Minimum canvas height in pixels
            engine: Graphviz layout engine:
                - dot: Hierarchical layout (default, best for DAGs)
                - neato: Spring model layout (similar to force-directed)
                - fdp: Force-directed placement
                - sfdp: Scalable force-directed (for large graphs)
                - circo: Circular layout
                - twopi: Radial layout
                - osage: Clustered layout
                - patchwork: Squarified treemap
            node_attr: Default attributes for all nodes (e.g., {"shape": "box"})
            edge_attr: Default attributes for all edges (e.g., {"color": "blue"})
            graph_attr: Graph-level attributes (e.g., {"rankdir": "LR"})
            scale: Zoom scale (default 0.75 to zoom out). 1.0 = 100%, 0.5 = 50%
            fit_width: If True, graph fills container width (default True)
            show_labels: If True, show node/edge labels (default True)
        """
        w = graphvizgraph.create_graphviz(
            nx_graph=graph,
            width=width,
            height=height,
            engine=engine,
            node_attr=node_attr,
            edge_attr=edge_attr,
            graph_attr=graph_attr,
            scale=scale,
            fit_width=fit_width,
            show_labels=show_labels,
        )
        return self._add_widget(w, name)

    def tree(
        self,
        name: str,
        paths: List[str],
        delimiter: str = "~",
    ) -> "Page":
        """Add a tree widget from paths."""
        w = treew.w_tree_paths(paths=paths, pathdelim=delimiter)
        return self._add_widget(w, name)

    # --- Layout ---

    def row(self, name: Optional[str] = None) -> "Page":
        """Add a horizontal container. Returns the new container as a Page."""
        w = v.Html(tag="div", class_="d-flex flex-row", children=[])
        self._add_widget(w, name)
        if name:
            self._app._containers[name] = w
        return Page(self._app, name or "", w)

    def column(self, name: Optional[str] = None) -> "Page":
        """Add a vertical container. Returns the new container as a Page."""
        w = v.Html(tag="div", class_="d-flex flex-column", children=[])
        self._add_widget(w, name)
        if name:
            self._app._containers[name] = w
        return Page(self._app, name or "", w)


class App:
    """
    Example:
        app = App(tabs=["Chart"], header="Config", footer="Messages")

        app.config.select("source", options=["a", "b"])
        app.config.button("Draw", on_click=draw_chart, status=True)

        def draw_chart(app):
            app.status("Drawing...")
            source = app["source"]
            app.tab("Chart").clear().plotly(fig)
            app.done()

        app.display()
    """

    def __init__(
        self,
        tabs: List[str],
        header: Optional[str] = None,
        footer: Optional[str] = "Messages",
        title: Optional[str] = None,
    ):
        """Create a new app.

        Args:
            tabs: List of tab names
            header: Optional collapsible header section name
            footer: Optional collapsible footer section name (default: "Messages")
            title: Optional browser title
        """
        self._tabs = tabs
        self._header_name = header
        self._footer_name = footer
        self._title = title

        self._widgets: dict = {}
        self._containers: dict = {}
        self._status_widgets: dict = {}  # name -> {field, progress}
        self._pages: dict[str, Page] = {}
        self._current_caller: Optional[str] = None  # Track which button triggered callback

        # Build UI structure
        self._tab_widget: Optional[v.Tabs] = None
        self._header_widget: Optional[v.ExpansionPanels] = None
        self._footer_widget: Optional[v.ExpansionPanels] = None
        self._messages: Optional[ipywidgets.Output] = None

        self._build_ui()

    def _build_ui(self):
        """Build the UI structure."""
        from ipyvuetify import Tab, TabItem

        # Header
        if self._header_name:
            header_content = v.ExpansionPanelContent(children=[])
            self._pages[self._header_name] = Page(self, self._header_name, header_content)
            self._header_widget = v.ExpansionPanels(
                children=[
                    v.ExpansionPanel(
                        children=[
                            v.ExpansionPanelHeader(children=[self._header_name]),
                            header_content,
                        ]
                    )
                ],
                v_model=[0],
                multiple=True,
            )

        # Tabs
        tab_children = []
        for tab_name in self._tabs:
            tab = Tab(children=[tab_name])
            tab_item = TabItem(children=[], style_="padding-left: 20px; padding-right: 20px;")
            tab_children.extend([tab, tab_item])
            self._pages[tab_name] = Page(self, tab_name, tab_item)
        self._tab_widget = v.Tabs(v_model=[0], children=tab_children)

        # Footer
        if self._footer_name:
            footer_content = v.ExpansionPanelContent(children=[])
            self._pages[self._footer_name] = Page(self, self._footer_name, footer_content)
            self._footer_widget = v.ExpansionPanels(
                children=[
                    v.ExpansionPanel(
                        children=[
                            v.ExpansionPanelHeader(children=[self._footer_name]),
                            footer_content,
                        ]
                    )
                ]
            )
            # Add output widget to footer
            self._messages = ipywidgets.Output()
            self._messages.max_outputs = 100  # type: ignore[attr-defined]
            footer_content.children = [self._messages]
            self._widgets["_messages"] = self._messages

    def _wrap_callback(self, func: Callable, caller_name: str) -> Callable:
        """Wrap a user callback to simplify its signature."""

        @wraps(func)
        def wrapper(*args, **kwargs):
            self._current_caller = caller_name
            try:
                return func(self)
            finally:
                self._current_caller = None

        return wrapper

    # --- Value access ---

    def __getitem__(self, name: str):
        """Get widget value by name: app['widget_name']"""
        return self.get(name)

    def __setitem__(self, name: str, value):
        """Set widget value by name: app['widget_name'] = value"""
        self.set(name, value)

    def get(self, name: str):
        """Get the current value of a widget."""
        w = self._widgets.get(name)
        if w is None:
            raise KeyError(f"No widget named '{name}'")

        # Handle different widget types
        if hasattr(w, "current_selection"):  # DataGrid
            return w.current_selection
        if hasattr(w, "value") and callable(w.value):  # Tree
            return w.value()
        if hasattr(w, "v_model"):
            return w.v_model
        return None

    def set(self, name: str, value):
        """Set the value of a widget."""
        w = self._widgets.get(name)
        if w is None:
            raise KeyError(f"No widget named '{name}'")
        if hasattr(w, "v_model"):
            w.v_model = value

    # --- Page access ---

    @property
    def config(self) -> Page:
        """Access the header/config section."""
        if self._header_name:
            return self._pages[self._header_name]
        raise ValueError("No header configured. Use header='Config' in App()")

    def tab(self, name: Union[str, int]) -> Page:
        """Access a tab by name or index."""
        if isinstance(name, int):
            name = self._tabs[name]
        if name not in self._pages:
            raise KeyError(f"No tab named '{name}'")
        return self._pages[name]

    @property
    def footer(self) -> Page:
        """Access the footer section."""
        if self._footer_name:
            return self._pages[self._footer_name]
        raise ValueError("No footer configured")

    @property
    def messages(self):
        """Access the messages output widget."""
        return self._messages

    # --- Status helpers ---

    def status(self, message: str, caller: Optional[str] = None):
        """Update status for the current (or specified) button.

        Call this from within a button callback to show progress.
        """
        name = caller or self._current_caller
        if not name or name not in self._status_widgets:
            return

        status = self._status_widgets[name]
        status["field"].v_model = message
        status["progress"].show()

    def done(self, message: str = "Done", caller: Optional[str] = None):
        """Mark the current (or specified) button as done.

        Call this at the end of a button callback.
        """
        name = caller or self._current_caller
        if not name or name not in self._status_widgets:
            return

        status = self._status_widgets[name]
        status["field"].v_model = message
        status["progress"].hide()

    def display(self):
        """Display the app."""
        display(_ThemeFixer())
        if self._title:
            display(BrowserTitle(self._title))

        children = []
        if self._header_widget:
            children.append(self._header_widget)
        if self._tab_widget:
            children.append(self._tab_widget)
        if self._footer_widget:
            children.append(self._footer_widget)

        return v.Html(
            tag="div",
            children=[
                v.Html(tag="style", children=[_STYLES]),
                v.Container(children=children),
            ],
        )


class _ThemeFixer:
    """Fixes theme issues and enables dark mode detection for ipyvuetify."""

    def _repr_html_(self) -> str:
        return """<script>
            (function() {
                // Detect dark mode from body background color
                const bgColor = window.getComputedStyle(document.body).backgroundColor;
                const rgbMatch = bgColor.match(/\\d+/g);
                const isDark = rgbMatch
                    ? rgbMatch.slice(0, 3).reduce((sum, v) => sum + parseInt(v), 0) < 384
                    : false;

                // Set ipyvuetify theme
                if (typeof Jupyter !== 'undefined' && Jupyter.notebook) {
                    // Classic notebook
                    if (window.vuetify) {
                        window.vuetify.framework.theme.dark = isDark;
                    }
                }

                // Set CSS class for theme detection by other widgets
                if (isDark) {
                    document.body.classList.add('theme-dark');
                    document.body.classList.remove('theme-light');
                } else {
                    document.body.classList.add('theme-light');
                    document.body.classList.remove('theme-dark');
                }

                // Voila specific fixes
                if (window.location.href.indexOf('voila') >= 0) {
                    if (!isDark) {
                        const l = document.createElement('link');
                        l.setAttribute('rel', 'stylesheet');
                        l.setAttribute('type', 'text/css');
                        l.setAttribute('href', `${window.location.href.split('/').slice(0,7).join('/')}/static/theme-light.css`);
                        document.body.appendChild(l);
                    }
                }
            })();
        </script>"""


_STYLES = """
.vuetify-styles code, .vuetify-styles kbd, .vuetify-styles samp{
    color: inherit !important;
}

.jupyter-widgets.widget-output{
    color: var(--jp-ui-font-color1, inherit);
}

/* Dark mode text colors */
.theme-dark .jupyter-widgets.widget-output,
.theme-dark .v-expansion-panel-content,
.theme-dark .v-card__text,
.theme-dark pre {
    color: #e0e0e0 !important;
}

.theme-dark .v-expansion-panel,
.theme-dark .v-expansion-panel-header {
    color: #e0e0e0 !important;
}

.v-tabs div{
    transition: none !important;
}

.for-progress .v-text-field__details{
    display: none !important;
}

.for-progress .v-input__control{
    min-height: 0px !important;
}

.for-progress input{
    text-align: center;
}

.progress-bar{
    margin-left: 10px
}

.vuetify-styles .v-container{
    min-width: 80vw
}

.ag-header {
    position: relative;
}
"""
